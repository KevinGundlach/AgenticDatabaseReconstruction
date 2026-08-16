"""Deterministic chemistry and electrochemical unit conversions.

LLM-produced artifacts must contain raw values only. This module is the sole
authority for normalized composition and potential values in phase one.
"""

from __future__ import annotations

from math import isfinite
from typing import Mapping


ATOMIC_WEIGHTS_VERSION = "conventional-atomic-weights-2021:v1"

# Conventional/abridged standard atomic weights suitable for engineering unit
# conversion. Values are fixed here so rerunning an experiment cannot silently
# change results when an external chemistry package updates its constants.
ATOMIC_WEIGHTS: dict[str, float] = {
    "H": 1.008,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998403163,
    "Na": 22.98976928,
    "Mg": 24.305,
    "Al": 26.9815385,
    "Si": 28.085,
    "P": 30.973761998,
    "S": 32.06,
    "Cl": 35.45,
    "Ti": 47.867,
    "V": 50.9415,
    "Cr": 51.9961,
    "Mn": 54.938044,
    "Fe": 55.845,
    "Co": 58.933194,
    "Ni": 58.6934,
    "Cu": 63.546,
    "Y": 88.90584,
    "Nb": 92.90637,
    "Mo": 95.95,
    "Gd": 157.25,
    "Ta": 180.94788,
    "W": 183.84,
    "Re": 186.207,
    "Ce": 140.116,
}

ATOMIC_TO_WEIGHT_CONVERSION_ID = (
    f"atomic_percent_to_weight_percent:{ATOMIC_WEIGHTS_VERSION}"
)
BINARY_ATOMIC_TO_WEIGHT_CONVERSION_ID = (
    f"binary_atomic_percent_to_weight_percent:{ATOMIC_WEIGHTS_VERSION}"
)
POTENTIAL_CONVERSION_ID = "potential_to_mv_sce:sce_241mv_at_25c:v1"


class ConversionError(ValueError):
    """Raised when a deterministic conversion cannot be performed safely."""


def _canonical_element(symbol: str) -> str:
    cleaned = symbol.strip()
    if not cleaned:
        raise ConversionError("Element symbols cannot be empty")
    canonical = cleaned[0].upper() + cleaned[1:].lower()
    if canonical not in ATOMIC_WEIGHTS:
        raise ConversionError(f"No pinned atomic weight for element {symbol!r}")
    return canonical


def atomic_percent_to_weight_percent(
    composition_at_percent: Mapping[str, float],
) -> dict[str, float]:
    """Convert a multi-element atomic composition to normalized weight percent.

    Inputs may sum to 1, 100, or any other positive total because the formula
    normalizes by total molar mass contribution. Negative and non-finite values
    are rejected rather than silently repaired.
    """

    if not composition_at_percent:
        raise ConversionError("Composition must contain at least one element")

    mass_contributions: dict[str, float] = {}
    for raw_symbol, raw_value in composition_at_percent.items():
        symbol = _canonical_element(raw_symbol)
        value = float(raw_value)
        if not isfinite(value) or value < 0:
            raise ConversionError(
                f"Atomic percentage for {symbol} must be finite and non-negative"
            )
        if symbol in mass_contributions:
            raise ConversionError(f"Duplicate element after normalization: {symbol}")
        mass_contributions[symbol] = value * ATOMIC_WEIGHTS[symbol]

    total_mass = sum(mass_contributions.values())
    if total_mass <= 0:
        raise ConversionError("Composition must have a positive total")

    return {
        symbol: contribution / total_mass * 100.0
        for symbol, contribution in mass_contributions.items()
    }


def binary_atomic_percent_to_weight_percent(
    base_element: str,
    solute_element: str,
    solute_at_percent: float,
) -> dict[str, float]:
    """Convert a binary alloy coordinate such as Al-5 at.% Nb to wt.%."""

    base = _canonical_element(base_element)
    solute = _canonical_element(solute_element)
    if base == solute:
        raise ConversionError("Base and solute elements must differ")
    solute_value = float(solute_at_percent)
    if not isfinite(solute_value) or not 0.0 <= solute_value <= 100.0:
        raise ConversionError("Solute atomic percentage must be between 0 and 100")
    return atomic_percent_to_weight_percent(
        {base: 100.0 - solute_value, solute: solute_value}
    )


def potential_to_mv_sce(
    value: float,
    *,
    unit: str,
    reference: str,
    reference_vs_she_mv: float | None = None,
    sce_vs_she_mv: float = 241.0,
) -> float:
    """Convert an electrode potential to mV vs. SCE deterministically.

    Ag/AgCl and other concentration-dependent references require an explicit
    `reference_vs_she_mv`; the function never asks a model to guess that offset.
    """

    numeric_value = float(value)
    if not isfinite(numeric_value):
        raise ConversionError("Potential must be finite")

    unit_key = unit.strip().lower().replace(" ", "")
    if unit_key in {"mv", "millivolt", "millivolts"}:
        value_mv = numeric_value
    elif unit_key in {"v", "volt", "volts"}:
        value_mv = numeric_value * 1000.0
    else:
        raise ConversionError(f"Unsupported potential unit: {unit!r}")

    reference_key = reference.strip().lower().replace(" ", "")
    if reference_key in {"sce", "saturatedcalomelelectrode"}:
        offset_vs_she = sce_vs_she_mv
    elif reference_key in {"she", "nhe", "standardhydrogenelectrode"}:
        offset_vs_she = 0.0
    elif reference_vs_she_mv is not None:
        offset_vs_she = float(reference_vs_she_mv)
        if not isfinite(offset_vs_she):
            raise ConversionError("Reference-electrode offset must be finite")
    else:
        raise ConversionError(
            f"Reference {reference!r} requires an explicit offset vs. SHE"
        )

    value_vs_she_mv = value_mv + offset_vs_she
    return value_vs_she_mv - sce_vs_she_mv

