"""Convert an Alloy to element -> weight percent without modifying the input.

to_weight_percent preserves indeterminate listed elements as None, with options
to retain explicit 'balance' markers and interpret bare '%' as weight percent.
to_weight_percent_strict requires a complete composition and raises a categorized
InvalidAlloyCompositionError. Both use central values only; neither interprets
bounds as points. Nominal ratios remain nominal after conversion.
"""

from collections import Counter
import math
from enum import StrEnum

from models.observation_enrichment import Alloy, Measurement
from typing import List, Literal


class AlloyCompositionErrorReason(StrEnum):
    """Categories for counting the first conversion error found in each alloy."""

    EMPTY_COMPOSITION = "empty_composition"
    UNKNOWN_ELEMENT = "unknown_element"
    DUPLICATE_ELEMENT = "duplicate_element"
    MULTIPLE_BALANCES = "multiple_balances"
    MISSING_AMOUNT = "missing_amount"
    MISSING_CENTRAL_VALUE = "missing_central_value"
    INVALID_AMOUNT = "invalid_amount"
    UNSUPPORTED_UNIT = "unsupported_unit"
    MIXED_BASES = "mixed_bases"
    PERCENTAGE_OUT_OF_RANGE = "percentage_out_of_range"
    NONFINITE_TOTAL = "nonfinite_total"
    INVALID_BALANCE_BASIS = "invalid_balance_basis"
    NEGATIVE_BALANCE = "negative_balance"
    NONPOSITIVE_TOTAL = "nonpositive_total"
    TOTAL_NOT_100 = "total_not_100"


class InvalidAlloyCompositionError(ValueError):
    """The alloy cannot be converted to a complete weight-percent composition."""

    def __init__(self, reason: AlloyCompositionErrorReason, message: str):
        self.reason = reason
        super().__init__(message)


# Absolute tolerance in percentage points, not a relative tolerance.
TOTAL_TOLERANCE = 0.1

# Spellings observed in the "enriched observations". Ambiguous %, pct, purity and ppm
# are deliberately excluded when no explicit basis is given for them.
WEIGHT_PERCENT_UNITS = {
    "% wt", "Wt%", "mass %", "mass%", "w/o", "weight %", "weight percent",
    "wt%", "wt-%", "wt. %", "wt.%",
}
ATOMIC_PERCENT_UNITS = {"at%", "at.%", "atom %"}
ATOMIC_RATIO_UNITS = {
    "nominal atomic-ratio coefficient", "nominal equiatomic formula coefficient",
    "nominal formula coefficient",
}

# Frozen CIAAW Abridged Standard Atomic Weights 2024, central values.
# https://ciaaw.org/abridged-atomic-weights.htm
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


def to_weight_percent_strict(alloy: Alloy) -> dict[str, float]:
    """Return the listed elements' weight percentages, or raise on ambiguity.

    Weight and atomic percentages must total 100 +/- TOTAL_TOLERANCE percentage
    points. Weight percentages are returned without rescaling; atomic amounts
    are mass-weighted using the complete composition. Atomic ratios may have any
    positive total and are treated as the complete nominal formula supplied.

    One explicit 'balance' is calculated on the other elements' percentage basis.
    Missing elements are never invented; mixed mass/atomic bases are rejected.
    On failure, exception.reason identifies the first issue encountered in input
    order, not every issue that might exist in the composition.
    """
    if not alloy.composition:
        raise InvalidAlloyCompositionError(
            AlloyCompositionErrorReason.EMPTY_COMPOSITION, "The alloy has no composition entries"
        )

    amounts = {}
    seen = set()
    basis = None
    balance_element = None

    for component in alloy.composition:
        element = component.element_symbol
        if element not in ATOMIC_WEIGHTS:
            raise InvalidAlloyCompositionError(
                AlloyCompositionErrorReason.UNKNOWN_ELEMENT,
                f"Unknown or unsupported element symbol: {element!r}",
            )
        if element in seen:
            raise InvalidAlloyCompositionError(
                AlloyCompositionErrorReason.DUPLICATE_ELEMENT, f"Duplicate element: {element}"
            )
        seen.add(element)

        amount = component.amount
        if amount == "balance":
            if balance_element is not None:
                raise InvalidAlloyCompositionError(
                    AlloyCompositionErrorReason.MULTIPLE_BALANCES,
                    "More than one element is marked as balance",
                )
            balance_element = element
            continue
        if amount is None:
            raise InvalidAlloyCompositionError(
                AlloyCompositionErrorReason.MISSING_AMOUNT,
                f"{element}: a central numerical amount is required",
            )
        if amount.value is None:
            raise InvalidAlloyCompositionError(
                AlloyCompositionErrorReason.MISSING_CENTRAL_VALUE,
                f"{element}: a central numerical amount is required",
            )
        if not math.isfinite(amount.value) or amount.value < 0:
            raise InvalidAlloyCompositionError(
                AlloyCompositionErrorReason.INVALID_AMOUNT,
                f"{element}: amount must be finite and nonnegative",
            )

        unit = amount.unit.strip()
        if unit in WEIGHT_PERCENT_UNITS:
            element_basis = "weight percent"
        elif unit in ATOMIC_PERCENT_UNITS:
            element_basis = "atomic percent"
        elif unit in ATOMIC_RATIO_UNITS:
            element_basis = "atomic ratio"
        else:
            raise InvalidAlloyCompositionError(
                AlloyCompositionErrorReason.UNSUPPORTED_UNIT,
                f"{element}: unsupported or ambiguous unit {unit!r}",
            )
        if basis is not None and element_basis != basis:
            raise InvalidAlloyCompositionError(
                AlloyCompositionErrorReason.MIXED_BASES,
                f"{element}: mixed composition bases ({basis} and {element_basis})",
            )
        basis = element_basis
        if basis != "atomic ratio" and amount.value > 100:
            raise InvalidAlloyCompositionError(
                AlloyCompositionErrorReason.PERCENTAGE_OUT_OF_RANGE,
                f"{element}: percentage exceeds 100",
            )
        amounts[element] = amount.value

    total = sum(amounts.values())
    if not math.isfinite(total):
        raise InvalidAlloyCompositionError(
            AlloyCompositionErrorReason.NONFINITE_TOTAL, "Composition total is not finite"
        )

    if balance_element is not None:
        if basis not in {"weight percent", "atomic percent"}:
            raise InvalidAlloyCompositionError(
                AlloyCompositionErrorReason.INVALID_BALANCE_BASIS,
                "Balance requires other amounts expressed as percentages",
            )
        if total > 100:
            raise InvalidAlloyCompositionError(
                AlloyCompositionErrorReason.NEGATIVE_BALANCE,
                f"No nonnegative balance remains: other amounts total {total:g}%",
            )
        amounts[balance_element] = 100 - total
        total = 100.0

    if total <= 0:
        raise InvalidAlloyCompositionError(
            AlloyCompositionErrorReason.NONPOSITIVE_TOTAL, "Composition total must be positive"
        )
    if basis != "atomic ratio" and not math.isclose(total, 100, rel_tol=0, abs_tol=TOTAL_TOLERANCE):
        raise InvalidAlloyCompositionError(
            AlloyCompositionErrorReason.TOTAL_NOT_100,
            f"Composition totals {total:g}%, expected 100% within {TOTAL_TOLERANCE} percentage point"
        )

    if basis == "weight percent":
        return amounts

    # Dividing first keeps the atomic fractions bounded even for large ratios.
    masses = {element: value / total * ATOMIC_WEIGHTS[element] for element, value in amounts.items()}
    total_mass = sum(masses.values())
    return {element: 100 * mass / total_mass for element, mass in masses.items()}


def to_weight_percent(
    alloy: Alloy,
    *,
    calculate_balance: bool = True,
    assume_percent_is_weight: bool = False,
) -> dict[str, float | Literal["balance"] | None]:
    """Return known weight percentages and None for indeterminate listed elements.

    Complete compositions use the strict converter, including atomic conversion
    and an explicitly stated balance. Otherwise, keep individually valid wt%
    values without rescaling or requiring a total of 100. An explicit balance
    can still be resolved when every other listed amount is known in wt%.

    Set calculate_balance=False to retain explicit 'balance' markers in the
    returned dictionary, even when the remainder cannot be determined. Atomic
    conversion still uses a resolvable balance internally to convert the other
    elements; the returned marker identifies the balance-derived entry.

    Set assume_percent_is_weight=True to interpret a unit of exactly '%' (after
    stripping whitespace) as wt%. Other ambiguous units remain unsupported.
    This interpretation is applied to a copy; the input and strict converter
    are unchanged. Missing amounts are never inferred to be balance entries.

    By default, missing/bounds-only amounts, ambiguous units (including % and ppm),
    invalid values/symbols, and duplicate elements remain None. Atomic values
    require a complete, consistent composition; they cannot be converted one
    element at a time. Unlisted elements are not added or treated as zero.
    """
    if assume_percent_is_weight:
        alloy = alloy.model_copy(deep=True)
        for component in alloy.composition:
            if isinstance(component.amount, Measurement) and component.amount.unit.strip() == "%":
                component.amount.unit = "wt%"

    counts = Counter(component.element_symbol for component in alloy.composition)
    try:
        result = to_weight_percent_strict(alloy)
    except InvalidAlloyCompositionError:
        result = {component.element_symbol: None for component in alloy.composition}
        for component in alloy.composition:
            element = component.element_symbol
            amount = component.amount
            if element not in ATOMIC_WEIGHTS or counts[element] > 1:
                continue
            if (isinstance(amount, Measurement)
                    and amount.value is not None
                    and math.isfinite(amount.value)
                    and 0 <= amount.value <= 100
                    and amount.unit.strip() in WEIGHT_PERCENT_UNITS):
                result[element] = amount.value

        balances = [c.element_symbol for c in alloy.composition if c.amount == "balance"]
        if calculate_balance and len(balances) == 1:
            element = balances[0]
            others = [value for symbol, value in result.items() if symbol != element]
            if (element in ATOMIC_WEIGHTS and counts[element] == 1
                    and others and all(value is not None for value in others)):
                remainder = 100 - sum(others)
                if 0 <= remainder <= 100:
                    result[element] = remainder

    if not calculate_balance:
        for component in alloy.composition:
            element = component.element_symbol
            if component.amount == "balance" and element in ATOMIC_WEIGHTS and counts[element] == 1:
                result[element] = "balance"
    return result


def get_alloy_units(alloys : List[Alloy]):
    
    recorded_units = set()

    for alloy in alloys:
        for element in alloy.composition:
            
            # Some amounts are None, some are the string "balance".
            if isinstance(element.amount, Measurement):

                if hasattr(element.amount, "unit"):
                    recorded_units.add(element.amount.unit) 
                
    return sorted(recorded_units)


# The units returned were:

# ''
# '%'
# '% (foil purity)'
# '% (purity)'
# '% wt'
# 'Wt%'
# 'at%'
# 'at.%'
# 'atom %'
# 'mass %'
# 'mass%'
# 'nominal %'
# 'nominal atomic-ratio coefficient'
# 'nominal equiatomic formula coefficient'
# 'nominal formula coefficient'
# 'pct'
# 'ppm'
# 'w/o'
# 'weight %'
# 'weight percent'
# 'wt%'
# 'wt-%'
# 'wt. %'
# 'wt.%'
