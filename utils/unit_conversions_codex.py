"""In-memory conversions of enriched experiment dictionaries to CRA units.

Typical use (no files are read or written here)::

    filled, calculations = fill_missing_values(document)  # derived_columns
    normalized, conversions = normalize_units(filled)
    inventory = collect_units([document, another_document])

Both bulk operations return ``(deep_copy, diagnostics)``. Unsupported values stay
in their original units; inspect diagnostics before treating an entire column as
normalized. Canonical extraction JSON and its schemas are deliberately unchanged.

``context`` is an optional dictionary. Its values apply to this document; entries
under ``by_observation`` override them for a registry-scoped observation ID. Use
separate calls for different papers. Assumptions need a nonblank ``source`` (a
paper passage or explicit caller justification). Supported context keys:

* ``alloy_basis``: ``wt%`` or ``at%`` for otherwise ambiguous percent units;
  ``composition_complete=True`` confirms a complete atomic ratio/composition.
* ``ppm_basis``: ``mass`` (mg/kg solution) or explicitly justified ``mg/L``;
  ``density_kg_per_litre`` is required for mass-based solution concentrations.
* ``solution_percent_basis``: ``mass`` or ``mass_per_volume`` for bare ``%``;
  ``solvent_kg_per_litre`` converts molality without assuming a density of 1.
* ``normality_equivalents_per_mole``: reaction-specific equivalents per mole.
* ``solute_aliases``: explicit name-to-formula mappings for qualified names.
* ``potential_reference``: recover a missing electrode identity/filling solution.
  ``reference_conversion`` supplies ``from``, ``to`` (SCE), ``offset_mv``,
  ``temperature_c``, and ``source``. Offset means E_SCE = E_source + offset.
  No universal electrode offset or filling solution is assumed. Known test
  temperatures must agree with the supplied calibration temperature.

Single-measurement helpers raise ConversionError instead of guessing. Combined
composition conversion returns ``(composition, limitations)``; its central-value
calculation does not propagate bounds or uncertainties.

Atomic weights: frozen CIAAW *Abridged Standard Atomic Weights 2024* central
values, https://ciaaw.org/abridged-atomic-weights.htm (accessed 2026-11-09).
Reference filling solutions are distinct; see Gamry's conversion resource:
https://www.gamry.com/resources-2/electrochemical-calculators-tools/convert-potentials-to-another-reference-electrode/
"""

from collections import defaultdict
from collections.abc import Iterable, Mapping
from copy import deepcopy
import math
import re
import unicodedata

from models.observation_enrichment import Measurement


class ConversionError(ValueError):
    """The supplied information does not justify this conversion/calculation."""


ATOMIC_WEIGHT_SOURCE = "CIAAW Abridged Standard Atomic Weights 2024"
ATOMIC_WEIGHTS = {
    "H": 1.0080, "He": 4.0026, "Li": 6.94, "Be": 9.0122, "B": 10.81,
    "C": 12.011, "N": 14.007, "O": 15.999, "F": 18.998, "Ne": 20.180,
    "Na": 22.990, "Mg": 24.305, "Al": 26.982, "Si": 28.085, "P": 30.974,
    "S": 32.06, "Cl": 35.45, "Ar": 39.95, "K": 39.098, "Ca": 40.078,
    "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 51.996, "Mn": 54.938,
    "Fe": 55.845, "Co": 58.933, "Ni": 58.693, "Cu": 63.546, "Zn": 65.38,
    "Ga": 69.723, "Ge": 72.630, "As": 74.922, "Se": 78.971, "Br": 79.904,
    "Kr": 83.798, "Rb": 85.468, "Sr": 87.62, "Y": 88.906, "Zr": 91.222,
    "Nb": 92.906, "Mo": 95.95, "Ru": 101.07, "Rh": 102.91, "Pd": 106.42,
    "Ag": 107.87, "Cd": 112.41, "In": 114.82, "Sn": 118.71, "Sb": 121.76,
    "Te": 127.60, "I": 126.90, "Xe": 131.29, "Cs": 132.91, "Ba": 137.33,
    "La": 138.91, "Ce": 140.12, "Pr": 140.91, "Nd": 144.24, "Sm": 150.36,
    "Eu": 151.96, "Gd": 157.25, "Tb": 158.93, "Dy": 162.50, "Ho": 164.93,
    "Er": 167.26, "Tm": 168.93, "Yb": 173.05, "Lu": 174.97, "Hf": 178.49,
    "Ta": 180.95, "W": 183.84, "Re": 186.21, "Os": 190.23, "Ir": 192.22,
    "Pt": 195.08, "Au": 196.97, "Hg": 200.59, "Tl": 204.38, "Pb": 207.2,
    "Bi": 208.98, "Th": 232.04, "Pa": 231.04, "U": 238.03,
}

# Deliberately a small explicit catalogue, not a general chemistry parser.
COMPOUNDS = {
    "NaCl": {"Na": 1, "Cl": 1}, "KCl": {"K": 1, "Cl": 1},
    "LiCl": {"Li": 1, "Cl": 1}, "HCl": {"H": 1, "Cl": 1},
    "MgCl2": {"Mg": 1, "Cl": 2}, "CaCl2": {"Ca": 1, "Cl": 2},
    "SrCl2": {"Sr": 1, "Cl": 2}, "AlCl3": {"Al": 1, "Cl": 3},
    "FeCl3": {"Fe": 1, "Cl": 3}, "FeCl2": {"Fe": 1, "Cl": 2},
    "MgCl2·6H2O": {"Mg": 1, "Cl": 2, "H": 12, "O": 6},
    "CaCl2·2H2O": {"Ca": 1, "Cl": 2, "H": 4, "O": 2},
    "NaOH": {"Na": 1, "O": 1, "H": 1},
    "KOH": {"K": 1, "O": 1, "H": 1}, "LiOH": {"Li": 1, "O": 1, "H": 1},
    "HNO3": {"H": 1, "N": 1, "O": 3},
    "HClO4": {"H": 1, "Cl": 1, "O": 4},
    "NaClO4": {"Na": 1, "Cl": 1, "O": 4},
    "NaNO3": {"Na": 1, "N": 1, "O": 3},
    "KNO3": {"K": 1, "N": 1, "O": 3},
    "H2SO4": {"H": 2, "S": 1, "O": 4},
    "Na2SO4": {"Na": 2, "S": 1, "O": 4},
    "NaHCO3": {"Na": 1, "H": 1, "C": 1, "O": 3},
    "NaBr": {"Na": 1, "Br": 1}, "KBr": {"K": 1, "Br": 1},
    "KI": {"K": 1, "I": 1}, "H2S": {"H": 2, "S": 1},
    "Na2S2O3": {"Na": 2, "S": 2, "O": 3},
    "Na2S2O3·5H2O": {"Na": 2, "S": 2, "O": 8, "H": 10},
    "Cl-": {"Cl": 1},
}
_SOLUTE_NAMES = {
    "sodium chloride": "NaCl", "potassium chloride": "KCl",
    "magnesium chloride": "MgCl2", "calcium chloride": "CaCl2",
    "hydrochloric acid": "HCl", "sodium hydroxide": "NaOH",
    "potassium hydroxide": "KOH", "chloride": "Cl-",
    "chloride ion": "Cl-", "chloride ions": "Cl-",
}


def _clean(unit):
    return unicodedata.normalize("NFKC", unit).replace("−", "-").strip()


def _compact(unit):
    return re.sub(r"\s+", "", _clean(unit))


def _finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ConversionError(f"{name} must be a finite number")
    return float(value)


def _assumption(context, key):
    if key not in context or not str(context.get("source", "")).strip():
        raise ConversionError(f"{key} and a nonblank context source are required")
    return context[key]


def _positive(context, key):
    value = _finite(_assumption(context, key), key)
    if value <= 0:
        raise ConversionError(f"{key} must be positive")
    return value


def _checked(measurement):
    try:
        Measurement.model_validate(measurement)
    except ValueError as exc:
        raise ConversionError(str(exc)) from exc
    return deepcopy(dict(measurement))


def _nonnegative(measurement):
    if any(measurement.get(k) is not None and measurement[k] < 0 for k in ("value", "min", "max")):
        raise ConversionError("Concentration or composition cannot be negative")


def _affine(measurement, scale, offset, unit):
    result = _checked(measurement)
    for key in ("value", "min", "max", "plus_minus"):
        if result.get(key) is not None:
            result[key] = result[key] * scale + (0 if key == "plus_minus" else offset)
    result["unit"] = unit
    return _checked(result)


def observation_context(context, observation_id):
    """Resolve document defaults and a shallow per-observation override."""
    result = deepcopy(dict(context or {}))
    overrides = result.pop("by_observation", {})
    result.update(deepcopy(overrides.get(observation_id, {})))
    return result


def diagnostic(observation_id, field, status, original, result, *, reason="", limitations=(), context=None):
    """Ordinary, JSON-compatible metadata; never inserted into extraction fields."""
    return deepcopy({
        "observation_id": observation_id, "field": field, "status": status,
        "original": original, "result": result, "reason": reason,
        "limitations": list(limitations), "context": dict(context or {}),
    })


def solute_formula(solute, context=None):
    """Resolve only exact formula/name aliases; qualified prose needs caller help."""
    context = context or {}
    if solute in context.get("solute_aliases", {}):
        solute = _assumption(context, "solute_aliases")[solute]
    name = _clean(solute)
    formula = _SOLUTE_NAMES.get(name.casefold(), name)
    if formula not in COMPOUNDS:
        raise ConversionError(f"Unsupported solute {solute!r}; provide an explicit solute_aliases entry if justified")
    return formula


def molar_mass(solute, context=None):
    """Return g/mol for a supported dissolved compound (including named hydrates)."""
    return math.fsum(ATOMIC_WEIGHTS[e] * n for e, n in COMPOUNDS[solute_formula(solute, context)].items())


def convert_concentration(measurement, *, molar_mass_g_per_mol=None, context=None):
    """Convert a concentration to mol/L; M is molarity, lowercase m is molality.

    Mass concentrations refer to the supplied species, not automatically to Cl-.
    molar_mass_g_per_mol must therefore describe that same species.
    """
    context = context or {}
    original = _checked(measurement)
    _nonnegative(original)
    raw = _compact(original.get("unit", ""))
    if raw in {"M", "mol/L", "mol/l", "mol/dm3", "moldm^-3", "moldm-3", "molL^-1", "molL-1", "moll^-1"}:
        scale = 1.0
    elif raw in {"mM", "mmol/L", "mmol/l"}:
        scale = 1e-3
    elif raw in {"µM", "μM", "uM", "µmol/L", "μmol/L", "umol/L"}:
        scale = 1e-6
    elif raw in {"m", "mol/kg", "mol/kgw", "mol/kgwater"}:
        scale = _positive(context, "solvent_kg_per_litre")
    elif raw == "N":
        scale = 1 / _positive(context, "normality_equivalents_per_mole")
    else:
        mass_unit = raw.casefold()
        if mass_unit in {"g/l", "mg/l", "µg/l", "μg/l", "ug/l"}:
            grams_per_litre = {"g/l": 1, "mg/l": 1e-3, "µg/l": 1e-6, "μg/l": 1e-6, "ug/l": 1e-6}[mass_unit]
        elif mass_unit in {"wt%", "wt.%", "mass%", "%w/w", "g/100g"}:
            grams_per_litre = 10 * _positive(context, "density_kg_per_litre")
        elif mass_unit in {"%w/v", "g/100ml"}:
            grams_per_litre = 10
        elif raw == "%":
            basis = _assumption(context, "solution_percent_basis")
            if basis not in {"mass", "mass_per_volume"}:
                raise ConversionError("solution_percent_basis must be mass or mass_per_volume")
            grams_per_litre = 10 * (_positive(context, "density_kg_per_litre") if basis == "mass" else 1)
        elif mass_unit in {"ppm", "mg/kg"}:
            basis = "mass" if mass_unit == "mg/kg" else _assumption(context, "ppm_basis")
            if basis not in {"mass", "mg/L"}:
                raise ConversionError("ppm_basis must be mass or mg/L")
            grams_per_litre = 1e-3 * (_positive(context, "density_kg_per_litre") if basis == "mass" else 1)
        else:
            raise ConversionError(f"Unsupported concentration unit {original.get('unit', '')!r}; activity is not concentration")
        mass = _finite(molar_mass_g_per_mol, "molar_mass_g_per_mol")
        if mass <= 0:
            raise ConversionError("molar_mass_g_per_mol must be positive")
        scale = grams_per_litre / mass
    return _affine(original, scale, 0, "mol/L")


def _reference_name(reference):
    key = _compact(reference).casefold().replace(".", "")
    names = {
        "sce": "SCE", "sce,saturatedkcl": "SCE", "sce,sat'dkcl": "SCE",
        "she": "SHE", "standardhydrogenelectrode": "SHE",
        "nhe": "NHE", "normalhydrogenelectrode": "NHE",
        "h2scale": "H2 scale", "stdh2scale": "SHE",
        "normalwasserstoff-skala": "NHE", "she(t)": "SHE(T)",
        "ag/agcl": "Ag/AgCl", "ag/agcl,saturated": "Ag/AgCl, saturated",
        "ag/agcl,saturatedkcl": "Ag/AgCl, saturated KCl",
        "ag/agcl,sat'dkcl": "Ag/AgCl, saturated KCl",
        "ag/agcl,35mkcl": "Ag/AgCl, 3.5 M KCl",
        "ag/agcl,3mkcl": "Ag/AgCl, 3 M KCl",
        "ag/agcl,1mkcl": "Ag/AgCl, 1 M KCl",
    }
    return names.get(key, reference.strip())


def convert_potential(measurement, *, context=None):
    """Convert voltage and a justified reference calibration to mV (SCE)."""
    context = context or {}
    raw = _clean(measurement.get("unit", ""))
    match = re.fullmatch(r"(mV|Volts?|V)(.*)", raw, re.IGNORECASE)
    if not match:
        raise ConversionError(f"Unsupported potential unit {raw!r}")
    scale = 1 if match[1].casefold() == "mv" else 1000
    tail = re.sub(r"^(?:versus|vs\.?)\s*", "", match[2].strip(), flags=re.IGNORECASE)
    if tail.startswith("_H "):
        tail = tail[3:].strip()
    if tail == "_H":
        reference = "H2 scale"
    else:
        if tail.startswith("(") and tail.endswith(")"):
            tail = tail[1:-1]
        reference = _reference_name(tail)
    if "potential_reference" in context:
        supplied = _reference_name(_assumption(context, "potential_reference"))
        can_clarify = ((reference in {"Ag/AgCl", "Ag/AgCl, saturated"}
                        and supplied.startswith("Ag/AgCl,")
                        and (reference == "Ag/AgCl" or supplied == "Ag/AgCl, saturated KCl"))
                       or (reference == "H2 scale" and supplied in {"SHE", "NHE"}))
        if reference and reference != supplied and not can_clarify:
            raise ConversionError("potential_reference conflicts with the reported electrode")
        reference = supplied
    if reference == "SCE":
        offset = 0
    else:
        if not reference or reference in {"Ag/AgCl", "Ag/AgCl, saturated"}:
            raise ConversionError("Reference electrode and (for Ag/AgCl) filling solution are required")
        calibration = context.get("reference_conversion", {})
        if (not str(calibration.get("source", "")).strip()
                or _reference_name(calibration.get("from", "")) != reference
                or _reference_name(calibration.get("to", "")) != "SCE"):
            raise ConversionError(f"A documented reference_conversion from {reference!r} to SCE is required")
        offset = _finite(calibration.get("offset_mv"), "offset_mv")
        temperature = _finite(calibration.get("temperature_c"), "calibration temperature_c")
        if "temperature_c" in context and not math.isclose(temperature, _finite(context["temperature_c"], "temperature_c"), abs_tol=1e-6):
            raise ConversionError("Reference calibration and test temperatures disagree")
    return _affine(measurement, scale, offset, "mV (SCE)")


def convert_measurement(measurement, quantity, *, context=None):
    """Convert temperature, scan_rate, voltage (steps), duration, or potential.

    Voltage steps use scaling alone. They are never interpreted as sweep rates.
    """
    if quantity == "potential":
        return convert_potential(measurement, context=context)
    raw = _compact(measurement.get("unit", ""))
    if quantity == "temperature":
        key = raw.casefold()
        if key in {"°c", "degc", "c", "celsius"}:
            scale, offset = 1, 0
        elif key in {"k", "kelvin"}:
            scale, offset = 1, -273.15
        elif key in {"°f", "degf", "fahrenheit"}:
            scale, offset = 5 / 9, -32 * 5 / 9
        else:
            raise ConversionError(f"Unsupported temperature unit {raw!r}")
        result = _affine(measurement, scale, offset, "°C")
        if any(result.get(k) is not None and result[k] < -273.15 for k in ("value", "min", "max")):
            raise ConversionError("Temperature is below absolute zero")
        return result
    if quantity == "scan_rate":
        raw = re.sub(r"[·*](s|min|h)(?:\^?-1)$", r"/\1", raw)
        match = re.fullmatch(r"(mV|V|volt)/(\d+(?:\.\d+)?)?(s|sec|second|min|minute|h|hr|hour)s?", raw, re.IGNORECASE)
        if not match:
            raise ConversionError(f"Unsupported sweep-rate unit {raw!r}; a voltage step is not a scan rate")
        denominator = float(match[2] or 1)
        if denominator <= 0:
            raise ConversionError("Sweep-rate time denominator must be positive")
        seconds = {"s": 1, "sec": 1, "second": 1, "min": 60, "minute": 60, "h": 3600, "hr": 3600, "hour": 3600}[match[3].casefold()]
        return _affine(measurement, (1 if match[1].casefold() == "mv" else 1000) / (seconds * denominator), 0, "mV/s")
    if quantity == "voltage" and raw.casefold() in {"mv", "v", "volt", "volts"}:
        return _affine(measurement, 1 if raw.casefold() == "mv" else 1000, 0, "mV")
    if quantity == "duration":
        units = {"s": 1, "sec": 1, "second": 1, "seconds": 1, "min": 60, "minute": 60, "minutes": 60, "h": 3600, "hr": 3600, "hour": 3600, "hours": 3600}
        if raw.casefold() in units:
            return _affine(measurement, units[raw.casefold()], 0, "s")
    raise ConversionError(f"Unsupported {quantity} unit {raw!r}")


def _alloy_unit(unit, context):
    key = _compact(unit).casefold()
    if key in {"wt%", "wt.%", "%wt", "weightpercent", "weight%", "mass%", "wt-%", "w/o", "%w/w"}:
        return "wt%", 1
    if key in {"at%", "at.%", "atom%", "atomic%"}:
        return "at%", 1
    if key in {"nominalformulacoefficient", "nominalequiatomicformulacoefficient", "nominalatomic-ratiocoefficient", "atomicratio"}:
        return "atomic_ratio", 1
    if key in {"%", "pct", "nominal%", "%(purity)", "%(foilpurity)", ""}:
        basis = _assumption(context, "alloy_basis")
        if basis not in {"wt%", "at%"}:
            raise ConversionError("alloy_basis must be wt% or at%")
        return basis, 1
    if key in {"ppm", "massppm", "wtppm"}:
        if key == "ppm" and _assumption(context, "ppm_basis") != "mass":
            raise ConversionError("Alloy ppm requires a mass basis")
        return "wt%", 1e-4
    if key in {"massfraction", "weightfraction"}:
        return "wt%", 100
    if key == "atomicfraction":
        return "at%", 100
    raise ConversionError(f"Unsupported alloy composition unit {unit!r}")


def _central(measurement):
    checked = _checked(measurement)
    _nonnegative(checked)
    if checked.get("value") is None:
        raise ConversionError("A central value is required; bounds are not replaced by a midpoint")
    return checked["value"]


def _uncertainty_limitations(measurements):
    if any(any(m.get(k) is not None for k in ("min", "max", "plus_minus")) for m in measurements):
        return ["Bounds/uncertainty were not propagated through this combined calculation; originals are retained in diagnostics."]
    return []


def convert_alloy_composition(composition, *, context=None):
    """Convert a composition to wt%; never normalize an incomplete atomic list.

    Atomic percentages must total 100 (floating-point tolerance only), or the
    caller must explicitly confirm composition_complete. Ratios always require
    that confirmation. Mass-basis lists can retain nulls and explicit balance.
    """
    context = context or {}
    result = deepcopy(composition)
    symbols = [c["element_symbol"] for c in composition]
    if len(set(symbols)) != len(symbols):
        raise ConversionError("Duplicate alloy elements")
    measured = [c for c in composition if isinstance(c.get("amount"), Mapping)]
    if not measured:
        if composition:
            raise ConversionError("No numeric alloy amounts to normalize")
        return result, []
    bases = [_alloy_unit(c["amount"].get("unit", ""), context) for c in measured]
    if len({b for b, _ in bases}) != 1:
        raise ConversionError("Mixed mass/atomic composition bases cannot be combined")
    basis = bases[0][0]
    if basis == "wt%":
        for component in result:
            if isinstance(component.get("amount"), Mapping):
                _, scale = _alloy_unit(component["amount"].get("unit", ""), context)
                _nonnegative(_checked(component["amount"]))
                component["amount"] = _affine(component["amount"], scale, 0, "wt%")
                if any(component["amount"].get(k) is not None and component["amount"][k] > 100 for k in ("value", "min", "max")):
                    raise ConversionError("An individual alloy percentage exceeds 100%")
        return result, []
    if len(measured) != len(composition):
        raise ConversionError("Atomic conversion requires every amount, including a resolved explicit balance")
    amounts = [_central(c["amount"]) * scale for c, (_, scale) in zip(measured, bases)]
    total = math.fsum(amounts)
    complete = context.get("composition_complete") is True
    if complete:
        _assumption(context, "composition_complete")
    if total <= 0 or (not complete and (basis == "atomic_ratio" or not math.isclose(total, 100, rel_tol=0, abs_tol=1e-8))):
        raise ConversionError("Atomic conversion requires a complete composition (100 at% or documented composition_complete)")
    if any(s not in ATOMIC_WEIGHTS for s in symbols):
        raise ConversionError("Atomic weight unavailable for an element")
    masses = [n * ATOMIC_WEIGHTS[s] for n, s in zip(amounts, symbols)]
    denominator = math.fsum(masses)
    for component, mass in zip(result, masses):
        component["amount"] = {"value": _finite(100 * mass / denominator, "weight percent"), "unit": "wt%"}
    limitations = _uncertainty_limitations([c["amount"] for c in measured])
    limitations.append(f"Closed atomic composition converted using {ATOMIC_WEIGHT_SOURCE}; atomic-weight uncertainties not propagated.")
    return result, limitations


def collect_units(documents):
    """Inventory actual measurement objects, grouped by field and raw unit.

    Accept one enrichment dictionary or an iterable of them. Returns rows with
    field, unit (None for an omitted unit), count, and up to five paper/ID
    examples. Blank units and null measurements have separate entries; prose
    mentioning a unit is not parsed. Paths use [] for collection indices.
    """
    if isinstance(documents, Mapping):
        documents = [documents]
    if not isinstance(documents, Iterable):
        raise TypeError("documents must be an enrichment mapping or iterable")
    groups = defaultdict(lambda: {"count": 0, "examples": []})
    scalar_measurements = {"test_temperature", "pitting_potential", "ph", "chloride_concentration", "scan_rate", "potential_step", "step_hold_duration", "amount"}

    def visit(value, path, name, example):
        if isinstance(value, Mapping):
            if name in scalar_measurements and any(k in value for k in ("value", "min", "max")):
                add(path, value.get("unit"), "measurement", example)
            else:
                for key, item in value.items():
                    visit(item, f"{path}.{key}" if path else key, key, example)
        elif isinstance(value, list):
            for item in value:
                visit(item, path + "[]", name, example)
        elif name in scalar_measurements:
            add(path, None, "missing" if value is None else "balance" if value == "balance" else "number", example)

    def add(path, unit, kind, example):
        row = groups[(path, unit, kind)]
        row["count"] += 1
        if example not in row["examples"] and len(row["examples"]) < 5:
            row["examples"].append(example)

    for document in documents:
        for experiment in document["experiments"]:
            visit(experiment, "experiments[]", "", {"paper_name": document.get("paper_name", ""), "observation_id": experiment["observation_id"]})
    return [{"field": field, "unit": unit, "kind": kind, **row}
            for (field, unit, kind), row in sorted(groups.items(), key=lambda item: tuple(str(x) for x in item[0]))]


def normalize_units(document, context=None):
    """Return a copied enrichment plus converted/unavailable field diagnostics.

    No missing values are derived. Solution solute amounts also become mol/L
    where justified. Nulls, prose and unresolvable measurements are preserved.
    """
    result = deepcopy(document)
    diagnostics = []
    for experiment in result["experiments"]:
        identifier = experiment["observation_id"]
        ctx = observation_context(context, identifier)

        def apply(container, key, field, converter):
            original = container.get(key)
            if original is None:
                return
            try:
                converted = converter(original)
            except (ConversionError, OverflowError) as exc:
                diagnostics.append(diagnostic(identifier, field, "unavailable", original, original, reason=str(exc), context=ctx))
            else:
                container[key] = converted
                diagnostics.append(diagnostic(identifier, field, "converted", original, converted, context=ctx))

        apply(experiment, "test_temperature", "test_temperature", lambda m: convert_measurement(m, "temperature"))
        temperature = experiment.get("test_temperature")
        if temperature and temperature.get("unit") == "°C" and temperature.get("value") is not None:
            ctx["temperature_c"] = temperature["value"]
        apply(experiment, "pitting_potential", "pitting_potential", lambda m: convert_potential(m, context=ctx))
        for key, quantity in (("scan_rate", "scan_rate"), ("potential_step", "voltage"), ("step_hold_duration", "duration")):
            apply(experiment["test_method"], key, f"test_method.{key}", lambda m, q=quantity: convert_measurement(m, q))
        original = experiment["alloy"]["composition"]
        if original:
            try:
                converted, limitations = convert_alloy_composition(original, context=ctx)
            except (ConversionError, OverflowError) as exc:
                diagnostics.append(diagnostic(identifier, "alloy.composition", "unavailable", original, original, reason=str(exc), context=ctx))
            else:
                experiment["alloy"]["composition"] = converted
                diagnostics.append(diagnostic(identifier, "alloy.composition", "converted", original, converted, limitations=limitations, context=ctx))
        solution = experiment["test_solution"]
        apply(solution, "chloride_concentration", "test_solution.chloride_concentration", lambda m: convert_concentration(m, molar_mass_g_per_mol=ATOMIC_WEIGHTS["Cl"], context=ctx))
        for i, component in enumerate(solution["composition"]):
            def concentration(m, solute=component["solute"]):
                if re.search(r"\bactivit(?:y|ies)\b", solute, re.IGNORECASE):
                    raise ConversionError("The solute label describes activity, not concentration")
                # Molar units need no species lookup; unknown species can still
                # be normalized if no molecular mass is required.
                try:
                    mass = molar_mass(solute, ctx)
                except ConversionError:
                    mass = None
                return convert_concentration(m, molar_mass_g_per_mol=mass, context=ctx)
            apply(component, "amount", f"test_solution.composition[{i}].amount", concentration)
    for item in diagnostics:
        item["paper_name"] = document.get("paper_name", "")
    return result, diagnostics
