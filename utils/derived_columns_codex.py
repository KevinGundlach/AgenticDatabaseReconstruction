"""Fill only missing context fields on in-memory copies of enriched observations.

    filled, calculations = fill_missing_values(document, context)
    normalized, conversions = normalize_units(filled, context)

Run filling before final unit normalization: an explicitly reported at% balance
must be resolved before converting the whole alloy to wt%. Existing reported
values (including an unconvertible measurement) are never overwritten. No file
or database I/O occurs. Diagnostic records preserve the original calculation
inputs and distinguish calculated fields from converted reported fields.

Individual calculations return ``(result, limitations)`` or raise
ConversionError. Only central values are combined; bounds/uncertainty are not
propagated, and bounds-only measurements never supply invented midpoints.

Context is described in unit_conversions.py, with these additional options:
* ``chloride_representation``: explicitly choose ``ion`` or ``salts`` if both
  describe the same solution (otherwise double counting is blocked).
* For pH, ``ideal_solution=True`` and ``recipe_complete=True`` explicitly accept
  a complete ideal, fully dissociated aqueous strong-acid/base model. Water
  must be reported as solvent, or supplied via ``aqueous=True``. A documented
  ``kw`` mapping supplies ``value`` (mol/L squared), ``temperature_c``, ``source``;
  it must match the reported test temperature, or a caller-supplied
  ``temperature_c``. No default 25 °C, pH 7, or Kw is assumed.

pH is an activity quantity. This helper provides only an ideal concentration-
based estimate, including water autoionization, not equilibrium speciation:
https://water.usgs.gov/water-resources/software/PHREEQC/documentation/phreeqc3-html/phreeqc3-48.htm
Buffers, weak/polyprotic acids, hydrolysing salts and unspecified adjustments
are unsupported. Seawater composition is never supplied from a template.
"""

from collections.abc import Mapping
from copy import deepcopy
import math

from utils.unit_conversions import (
    COMPOUNDS, ConversionError, _alloy_unit, _assumption,
    _central, _clean, _finite, _uncertainty_limitations,
    convert_concentration, convert_measurement, diagnostic, molar_mass,
    observation_context, solute_formula,
)


def calculate_balance(composition, *, context=None):
    """Resolve one explicit balance on a consistent wt%/at% basis.

    An absent element is not a balance. Missing other amounts or incomplete
    bounds cannot be silently treated as zero. Other entries stay unchanged.
    """
    context = context or {}
    balances = [i for i, c in enumerate(composition) if c.get("amount") == "balance"]
    if len(balances) != 1:
        raise ConversionError("Exactly one explicitly stated balance is required")
    symbols = [c["element_symbol"] for c in composition]
    if len(symbols) != len(set(symbols)):
        raise ConversionError("Duplicate alloy elements")
    measurements = [c.get("amount") for i, c in enumerate(composition) if i != balances[0]]
    if not measurements or any(not isinstance(m, Mapping) for m in measurements):
        raise ConversionError("Balance requires known amounts for every other listed element")
    units = [_alloy_unit(m.get("unit", ""), context) for m in measurements]
    if len({basis for basis, _ in units}) != 1 or units[0][0] not in {"wt%", "at%"}:
        raise ConversionError("Balance requires consistent mass or atomic percentages")
    remainder = 100 - math.fsum(_central(m) * scale for m, (_, scale) in zip(measurements, units))
    if not 0 <= remainder <= 100:
        raise ConversionError("Calculated balance is outside 0–100%; composition is inconsistent")
    result = deepcopy(composition)
    result[balances[0]]["amount"] = {"value": remainder, "unit": units[0][0]}
    return result, _uncertainty_limitations(measurements)


def _components(solution, context):
    if not solution.get("composition"):
        raise ConversionError("No solution composition was supplied")
    resolved = []
    seen = set()
    for component in solution["composition"]:
        formula = solute_formula(component["solute"], context)
        if formula in seen:
            raise ConversionError(f"Repeated {formula} entries may duplicate the same ingredient")
        seen.add(formula)
        resolved.append((formula, component.get("amount")))
    return resolved


def calculate_chloride(solution, *, context=None):
    """Estimate stoichiometric total chloride in mol/L from supported solutes.

    Chloride salts and explicitly listed Cl- are alternative representations
    unless the caller establishes which to use. Perchlorate is not chloride.
    Unknown ingredient names block the calculation, rather than being assumed
    chloride-free. Missing amounts of known chloride-free ingredients can be
    ignored for this calculation only.
    """
    context = context or {}
    components = _components(solution, context)
    donors = [(formula, amount) for formula, amount in components
              if "Cl" in COMPOUNDS[formula] and formula not in {"NaClO4", "HClO4"}]
    if not donors:
        raise ConversionError("No quantified chloride source; absence of a listed source does not establish zero")
    has_ion = any(formula == "Cl-" for formula, _ in donors)
    has_salt = any(formula != "Cl-" for formula, _ in donors)
    limitations = ["Stoichiometric total chloride from listed dissolved components; free-ion activity/speciation is not calculated."]
    if has_ion and has_salt:
        choice = _assumption(context, "chloride_representation")
        if choice not in {"ion", "salts"}:
            raise ConversionError("chloride_representation must be ion or salts")
        donors = [(f, m) for f, m in donors if (f == "Cl-") == (choice == "ion")]
        limitations.append(f"Used {choice} representation to avoid counting salt and ion descriptions twice.")
    measurements = []
    contributions = []
    for formula, amount in donors:
        if not isinstance(amount, Mapping):
            raise ConversionError(f"Chloride source {formula} has no amount")
        concentration = convert_concentration(amount, molar_mass_g_per_mol=molar_mass(formula), context=context)
        contributions.append(_central(concentration) * COMPOUNDS[formula]["Cl"])
        measurements.append(amount)
    result = {"value": _finite(math.fsum(contributions), "chloride concentration"), "unit": "mol/L"}
    limitations.extend(_uncertainty_limitations(measurements))
    return result, limitations


def calculate_ph(solution, *, temperature_c=None, context=None):
    """Estimate ideal pH from a complete recipe of supported strong acids/bases.

    Solve [H+] - [OH-] = acid equivalents - base equivalents and
    [H+][OH-] = Kw. A cancellation-safe expression handles very dilute cases.
    """
    context = context or {}
    for key in ("ideal_solution", "recipe_complete"):
        if _assumption(context, key) is not True:
            raise ConversionError(f"{key}=True is required for an ideal pH estimate")
    solvent = _clean(solution.get("solvent", "")).casefold()
    if solvent not in {"water", "distilled water", "deionized water", "deionised water", "aqueous", "h2o"}:
        if _assumption(context, "aqueous") is not True:
            raise ConversionError("An explicitly aqueous solvent is required")
    if temperature_c is None:
        temperature_c = _finite(_assumption(context, "temperature_c"), "temperature_c")
    temperature_c = _finite(temperature_c, "temperature_c")
    if temperature_c < -273.15:
        raise ConversionError("Temperature is below absolute zero")
    kw = context.get("kw", {})
    if not str(kw.get("source", "")).strip():
        raise ConversionError("A documented temperature-appropriate kw is required")
    ion_product = _finite(kw.get("value"), "kw.value")
    if ion_product <= 0:
        raise ConversionError("kw.value must be positive")
    if not math.isclose(temperature_c, _finite(kw.get("temperature_c"), "kw.temperature_c"), abs_tol=1e-6):
        raise ConversionError("Kw and test temperatures disagree")
    acids = {"HCl", "HNO3", "HClO4"}
    bases = {"NaOH", "KOH", "LiOH"}
    neutral = {"NaCl", "KCl", "LiCl", "NaNO3", "KNO3", "NaBr", "KBr", "KI", "NaClO4"}
    contributions = []
    measurements = []
    for formula, amount in _components(solution, context):
        if formula not in acids | bases | neutral:
            raise ConversionError(f"{formula} requires acid/base or hydrolysis chemistry outside this ideal model")
        if not isinstance(amount, Mapping):
            raise ConversionError(f"Incomplete recipe: {formula} has no amount")
        concentration = convert_concentration(amount, molar_mass_g_per_mol=molar_mass(formula), context=context)
        central = _central(concentration)
        contributions.append(central * (1 if formula in acids else -1 if formula in bases else 0))
        measurements.append(amount)
    net = math.fsum(contributions)
    root = math.hypot(net, 2 * math.sqrt(ion_product))
    hydrogen = (net / 2 + root / 2) if net >= 0 else (2 * ion_product / (root - net))
    if hydrogen <= 0 or not math.isfinite(hydrogen):
        raise ConversionError("pH calculation exceeds floating-point range")
    result = -math.log10(hydrogen)
    limitations = ["Calculated ideal aqueous pH: complete dissociation, unit activity coefficients, water autoionization; no buffer, gas-equilibrium or speciation model."]
    limitations.extend(_uncertainty_limitations(measurements))
    return result, limitations


def fill_missing_values(document, context=None):
    """Return a copy with explicit balances, missing chloride and pH filled.

    Every attempted calculation has a calculated/unavailable diagnostic. Existing
    reported fields are left alone, including measurements with no central value.
    Nonempty extraction failure/scientific notes are preserved, not interpreted.
    """
    result = deepcopy(document)
    diagnostics = []
    for experiment in result["experiments"]:
        identifier = experiment["observation_id"]
        ctx = observation_context(context, identifier)

        def calculate(container, key, field, inputs, function):
            original = container[key]
            original_inputs = deepcopy(inputs)
            try:
                calculated, limitations = function()
            except (ConversionError, OverflowError) as exc:
                item = diagnostic(identifier, field, "unavailable", original, original, reason=str(exc), context=ctx)
            else:
                container[key] = calculated
                item = diagnostic(identifier, field, "calculated", original, calculated, limitations=limitations, context=ctx)
            item["calculation_inputs"] = original_inputs
            diagnostics.append(item)

        composition = experiment["alloy"]["composition"]
        if any(c.get("amount") == "balance" for c in composition):
            calculate(experiment["alloy"], "composition", "alloy.composition", composition,
                      lambda: calculate_balance(composition, context=ctx))
        solution = experiment["test_solution"]
        if solution["chloride_concentration"] is None:
            calculate(solution, "chloride_concentration", "test_solution.chloride_concentration", solution["composition"],
                      lambda: calculate_chloride(solution, context=ctx))
        if solution["ph"] is None:
            def ph():
                temperature = experiment.get("test_temperature")
                if temperature is not None:
                    temperature = convert_measurement(temperature, "temperature")
                    known = temperature.get("value")
                else:
                    known = None
                return calculate_ph(solution, temperature_c=known, context=ctx)
            calculate(solution, "ph", "test_solution.ph",
                      {"solution": solution, "test_temperature": experiment.get("test_temperature")}, ph)
    for item in diagnostics:
        item["paper_name"] = document.get("paper_name", "")
    return result, diagnostics
