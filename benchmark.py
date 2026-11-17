"""Compare one enriched experiment with one already-matched CRA row, in memory.

Use count_gaps(experiment, cra_row) for an integer, or benchmark_experiment(...)
for the gaps, skipped comparisons, denominator and derived values.

Rules for this first benchmark:
* One gap per element, required solute, potential, temperature, chloride, pH or
  material class. An ingredient missing both its identity and amount is one gap.
* CRA missing cells are unscored. Unlisted zero-valued CRA alloy elements are
  unscored too: extraction is not required to enumerate every absent element.
  Explicit extracted amounts can still disagree with a CRA zero.
* Explicit balance elements are unscored unless calculate_balance=True. Bare
  alloy '%' remains ambiguous unless assume_percent_is_weight=True.
* Reported pH/chloride take precedence. Estimate only a missing field, using
  the existing electrolyte helpers and their assumptions, never CRA context.
* Compare potential central values when CRA Avg is present; otherwise compare
  explicit Min/Max bounds. Do not invent midpoints, turn uncertainties into
  ranges, or equate a distribution member with its summary. Incompatible shapes,
  qualitative/inequality CRA targets and unresolved named recipes are skipped
  with a reason. A low count with many skips is not evidence of good extraction.
* Extra solutes absent from CRA are unscored, since CRA need not list every
  constituent. Solvent is compared only when CRA explicitly names it. Solution
  preparation, test method, scan rate, microstructure, heat treatment and comments
  are outside this comparison.

Default numerical tolerance is rounding only (1e-6 absolute and relative).
``tolerances`` can supply an absolute margin for a field or field group, e.g.
{"alloy": 0.01, "pitting_potential": 5}. Units are wt percentage points, mV(SCE),
degrees C, mol/L for chloride, and pH units. Solution amounts use mol/L when
convertible, otherwise their common reported basis (wt%, %, ppm, N or mol/kg).
Neither uncertainty bars nor CRA disagreement determine a tolerance. The caller
must select digitization allowances: EnrichedExperiment has no reading_method.

This checks dataset agreement, not which source is scientifically correct, the
validity of an alignment, or the independence/statistical role of linked records.
No file/database access occurs; neither argument is modified.
"""

from collections import defaultdict
from dataclasses import dataclass, field
import math

from models.observation_enrichment import EnrichedExperiment, Measurement
from utils.cra_electrolyte_parsing import TestSolutionParsingError, parse_test_solution
from utils.electrolyte import _molarity, _solute_name, estimate_cl, estimate_ph
from utils.experiment_conversions import standardize_pitting_potential
from utils.weight_pct_conversion import to_weight_percent


CRA_ELEMENTS = "Fe Cr Ni Mo W N Nb C Si Mn Cu P S Al V Ta Re Ce Ti Co B Mg Y Gd".split()


@dataclass
class BenchmarkResult:
    gaps: dict[str, str] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)
    compared: int = 0
    derived: dict[str, float] = field(default_factory=dict)

    @property
    def gap_count(self) -> int:
        return len(self.gaps)


def _missing(value) -> bool:
    if value is None or (isinstance(value, str) and value.strip().casefold() in
                         {"", "na", "n/a", "nan", "none", "<na>"}):
        return True
    try:
        return math.isnan(value)
    except (TypeError, ValueError):
        return False


def _number(value) -> float:
    if isinstance(value, bool):
        raise ValueError("boolean is not a numerical CRA target")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("non-finite CRA target")
    return result


def _map_measurement(amount: Measurement, convert, unit: str) -> Measurement:
    values = {name: convert(getattr(amount, name)) for name in ("value", "min", "max")
              if getattr(amount, name) is not None}
    if any(v is None or not math.isfinite(v) for v in values.values()):
        raise ValueError(f"unsupported or ambiguous unit {amount.unit!r}")
    return Measurement(**values, unit=unit)


def _temperature(amount: Measurement) -> Measurement:
    unit = amount.unit.strip()
    if unit in {"°C", "C", "degC", "deg C", "Celsius"}:
        return amount
    if unit == "K":
        return _map_measurement(amount, lambda x: x - 273.15, "°C")
    if unit in {"°F", "F"}:
        return _map_measurement(amount, lambda x: (x - 32) * 5 / 9, "°C")
    raise ValueError(f"unsupported temperature unit {unit!r}")


def _molar_measurement(amount: Measurement, solute: str) -> Measurement:
    # Reuse the small conversion catalogue used by estimate_cl/estimate_ph.
    try:
        return _map_measurement(amount, lambda x: _molarity(
            Measurement(value=x, unit=amount.unit), solute), "M")
    except KeyError as exc:
        raise ValueError(f"no molar mass available for {solute!r}") from exc


def _solute(name: str) -> str:
    name = _solute_name(name)
    return {
        "sulfuric acid": "h2so4", "sulphuric acid": "h2so4",
        "sodium sulfate": "na2so4", "sodium sulphate": "na2so4",
        "sodium bicarbonate": "nahco3", "sodium bromide": "nabr",
        "sodium perchlorate": "naclo4", "wo42-": "wo4", "wo4^2-": "wo4",
    }.get(name, name)


def _solution_unit(amount: Measurement) -> Measurement:
    """Keep common non-molar bases distinct; never infer density or % basis."""
    unit = amount.unit.replace(" ", "")
    if unit in {"wt%", "wt.%", "wt-%", "mass%", "weight%"}:
        unit = "wt%"
    if unit == "mol/kg":
        unit = "m"
    if unit not in {"%", "wt%", "ppm", "m", "N"}:
        raise ValueError(f"unsupported or ambiguous concentration unit {amount.unit!r}")
    return amount.model_copy(update={"unit": unit})


def benchmark_experiment(
    experiment: EnrichedExperiment,
    cra_row: dict,
    *,
    calculate_balance: bool = False,
    assume_percent_is_weight: bool = False,
    tolerances: dict[str, float] | None = None,
) -> BenchmarkResult:
    """Return field-level gaps and explicit exclusions for one supported link.

    Field names include alloy.Cr, test_solution.NaCl, pitting_potential,
    test_temperature, chloride_concentration, ph and material_class. Missing
    extracted values and unsupported extracted units count as gaps when CRA
    provides a usable target. Missing/unsupported reference values are skipped.
    ``compared`` counts comparison opportunities, including those with gaps.
    Multiple CRA links must be evaluated separately; this function does not pick
    the best row or deduplicate repeated observations/reference records.
    """
    margins = dict(tolerances or {})
    groups = {"alloy", "test_solution", "pitting_potential", "test_temperature",
              "chloride_concentration", "ph"}
    for name, margin in margins.items():
        if name not in groups and not name.startswith(("alloy.", "test_solution.")):
            raise ValueError(f"Unknown tolerance field: {name!r}")
        if isinstance(margin, bool) or not math.isfinite(margin) or margin < 0:
            raise ValueError(f"Tolerance for {name!r} must be finite and nonnegative")
    result = BenchmarkResult()

    def compare(name, actual, target, normalize=None):
        if target is None:
            return
        if actual is None:
            result.compared += 1
            result.gaps[name] = "missing: no extracted or calculable value"
            return
        try:
            actual = actual if isinstance(actual, Measurement) else Measurement(value=actual)
            if normalize is not None:
                actual = normalize(actual)
        except ValueError as exc:
            result.compared += 1
            result.gaps[name] = f"conversion: {exc}"
            return
        parts = ("value",) if target.value is not None else tuple(
            p for p in ("min", "max") if getattr(target, p) is not None)
        if any(getattr(actual, p) is None for p in parts):
            result.skipped[name] = "point/range/bound roles differ; needs a separate comparison"
            return
        result.compared += 1
        tolerance = margins.get(name, margins.get(name.split(".")[0], 1e-6))
        differences = [f"{p}: {getattr(actual, p):g} versus CRA {getattr(target, p):g}"
                       for p in parts if not math.isclose(getattr(actual, p), getattr(target, p),
                                                         rel_tol=1e-6, abs_tol=tolerance)]
        if differences:
            result.gaps[name] = "mismatch: " + "; ".join(differences) + f" ({target.unit})"

    def reference(name, raw, unit=""):
        if _missing(raw):
            result.skipped[name] = "CRA value is unavailable"
            return None
        try:
            return Measurement(value=_number(raw), unit=unit)
        except (TypeError, ValueError):
            result.skipped[name] = f"CRA target is not a finite scalar: {raw!r}"
            return None

    composition = to_weight_percent(experiment.alloy, calculate_balance=calculate_balance,
                                    assume_percent_is_weight=assume_percent_is_weight)
    for element in CRA_ELEMENTS:
        name = f"alloy.{element}"
        target = reference(name, cra_row.get(element), "wt%")
        if target is None:
            continue
        actual = composition.get(element)
        if actual == "balance":
            result.skipped[name] = "explicit balance retained to avoid propagated gaps"
        elif target.value == 0 and element not in composition:
            result.skipped[name] = "unlisted element with CRA zero; no explicit zero required"
        else:
            compare(name, actual, target)

    name = "pitting_potential"
    if not _missing(cra_row.get("Avg Epit mV (SCE)")):
        target = reference(name, cra_row["Avg Epit mV (SCE)"], "mV (SCE)")
    else:
        bounds = {}
        try:
            for part, column in (("min", "Min Epit mV (SCE)"), ("max", "Max Epit mV (SCE)")):
                if not _missing(cra_row.get(column)):
                    bounds[part] = _number(cra_row[column])
            target = Measurement(**bounds, unit="mV (SCE)") if bounds else None
            if target is None:
                result.skipped[name] = "CRA potential is unavailable"
        except (TypeError, ValueError):
            target = None
            result.skipped[name] = "CRA potential bounds are invalid or non-numerical"
    compare(name, experiment.pitting_potential, target, standardize_pitting_potential)
    compare("test_temperature", experiment.test_temperature,
            reference("test_temperature", cra_row.get("Test Temp C"), "°C"), _temperature)

    solution = experiment.test_solution
    for name, column, reported, estimate, normalize in (
        ("chloride_concentration", "CL- [M]", solution.chloride_concentration,
         estimate_cl, lambda m: _molar_measurement(m, "cl-")),
        ("ph", "pH", solution.ph, estimate_ph, None),
    ):
        target = reference(name, cra_row.get(column), "M" if name == "chloride_concentration" else "pH")
        if target is None:
            continue
        actual = reported
        if actual is None:
            actual = estimate(solution)
            if actual is not None:
                result.derived[name] = actual
                actual = Measurement(value=actual, unit=target.unit)
        if name == "ph" and isinstance(actual, Measurement) and actual.unit not in {"", "pH"}:
            result.compared += 1
            result.gaps[name] = f"conversion: unsupported pH unit {actual.unit!r}"
        else:
            compare(name, actual, target, normalize)

    raw_solution = cra_row.get("Test Solution")
    if _missing(raw_solution):
        result.skipped["test_solution"] = "CRA solution is unavailable"
    else:
        try:
            target_solution = parse_test_solution(raw_solution)
        except TestSolutionParsingError as exc:
            result.skipped["test_solution"] = f"CRA solution cannot be parsed: {exc}"
        else:
            if not target_solution.composition and not target_solution.solvent:
                result.skipped["test_solution"] = "CRA names a solution without an ingredient recipe"
            actual_components = defaultdict(list)
            for component in solution.composition:
                actual_components[_solute(component.solute)].append(component.amount)
            for component in target_solution.composition:
                name = f"test_solution.{component.solute}"
                amounts = actual_components.get(_solute(component.solute), [])
                if len(amounts) != 1:
                    result.compared += 1
                    result.gaps[name] = "missing: solute not extracted" if not amounts else "ambiguous: repeated solute"
                    continue
                if component.amount is None:
                    result.compared += 1  # CRA specifies identity but no quantity.
                    continue
                if not component.amount.unit:
                    result.skipped[name] = "CRA ingredient amount has no concentration unit"
                    continue
                if amounts[0] is None:
                    compare(name, None, component.amount)
                    continue
                try:
                    actual = _molar_measurement(amounts[0], _solute(component.solute))
                    target = _molar_measurement(component.amount, _solute(component.solute))
                except ValueError:
                    try:
                        actual, target = _solution_unit(amounts[0]), _solution_unit(component.amount)
                        if actual.unit != target.unit:
                            raise ValueError("concentration bases differ; no justified conversion")
                    except ValueError as exc:
                        result.compared += 1
                        result.gaps[name] = f"conversion: {exc}"
                        continue
                compare(name, actual, target)
            if target_solution.solvent:
                result.compared += 1
                # The parser's explicit solvents are all descriptions of water.
                if solution.solvent.strip().casefold() not in {
                    "water", "h2o", "aqueous", "distilled water", "deionized water", "deionised water",
                    "double-distilled water", "water (aqueous solution)", "water (explicitly aqueous)",
                }:
                    result.gaps["test_solution.solvent"] = "missing or different: CRA explicitly specifies water"

    target_class = cra_row.get("Material class")
    if _missing(target_class):
        result.skipped["material_class"] = "CRA material class is unavailable"
    else:
        result.compared += 1
        if experiment.alloy.material_class.strip().casefold() != str(target_class).strip().casefold():
            result.gaps["material_class"] = f"mismatch: {experiment.alloy.material_class!r} versus CRA {target_class!r}"
    return result


def count_gaps(experiment: EnrichedExperiment, cra_row: dict, **options) -> int:
    """Return benchmark_experiment(...).gap_count; accepts the same options."""
    return benchmark_experiment(experiment, cra_row, **options).gap_count
