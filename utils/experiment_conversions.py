"""Convert reported pitting potentials without modifying the input measurement."""

from models.observation_enrichment import Measurement


class PittingPotentialConversionError(ValueError):
    """The unit/reference does not permit conversion, or the result is invalid."""


# Fixed 25 C reference convention, checked against Gamry's calculator:
# https://www.gamry.com/resources-2/electrochemical-calculators-tools/convert-potentials-to-another-reference-electrode/
# E_SCE = E_source + E_reference_vs_SHE - E_SCE_vs_SHE.
# Gamry treats explicitly named NHE and SHE as the same zero reference. This is
# a conventional comparison, not a correction for a real NHE's activity effects,
# temperature, liquid-junction potentials or individual electrode calibration.
_SCE_VS_SHE_MV = 241.0
_AG_AGCL_35M_VS_SHE_MV = 205.0

# (voltage scale to mV, reference offset in mV). Spellings are from the actual
# enriched observations, rather than a general unit/electrode-name parser.
_CONVERSIONS = {
    "mV (SCE)": (1, 0),
    "V (SCE)": (1000, 0),
    "mV vs SCE": (1, 0),
    "mV (S.C.E.)": (1, 0),
    "VOLT VERSUS SCE": (1000, 0),
    "V vs SCE": (1000, 0),
    "v vs. SCE": (1000, 0),
    "V vs. SCE": (1000, 0),
    "mV (SCE, saturated KCl)": (1, 0),
    "V (S.C.E.)": (1000, 0),
    "V versus SCE": (1000, 0),
    "V (SHE)": (1000, -_SCE_VS_SHE_MV),
    "mV (SHE)": (1, -_SCE_VS_SHE_MV),
    "mV (S.H.E.)": (1, -_SCE_VS_SHE_MV),
    "V (S.H.E.)": (1000, -_SCE_VS_SHE_MV),
    "mV (standard hydrogen electrode)": (1, -_SCE_VS_SHE_MV),
    "V (Std. H2 scale)": (1000, -_SCE_VS_SHE_MV),
    "V (NHE)": (1000, -_SCE_VS_SHE_MV),
    "mV (NHE)": (1, -_SCE_VS_SHE_MV),
    "V (normal hydrogen electrode)": (1000, -_SCE_VS_SHE_MV),
    "mV (normal hydrogen electrode)": (1, -_SCE_VS_SHE_MV),
    "V_H (Normalwasserstoff-Skala)": (1000, -_SCE_VS_SHE_MV),
    "mV (Ag/AgCl, 3.5 M KCl)": (1, _AG_AGCL_35M_VS_SHE_MV - _SCE_VS_SHE_MV),
}
_UNCONVERTIBLE_UNITS = {
    "V": "reference electrode is missing",
    "v": "reference electrode is missing",
    "Volts": "reference electrode is missing",
    "mV": "reference electrode is missing",
    "V (H2 scale)": "hydrogen scale is not identified as standard, normal or reversible",
    "mV_H": "hydrogen scale is not identified as standard, normal or reversible",
    "V (Ag/AgCl)": "Ag/AgCl filling solution is unspecified",
    "mV (Ag/AgCl, saturated)": "the saturated filling electrolyte is unspecified",
    "V (SHE(T))": "temperature-dependent SHE(T) needs information beyond this Measurement",
}


def standardize_pitting_potential(potential: Measurement) -> Measurement:
    """Return a new Measurement in mV (SCE), or raise PittingPotentialConversionError.

    Supports the unambiguous unit spellings inventoried in enriched_observations.
    Cross-reference conversions use the fixed 25 C convention above: subtract
    241 mV from explicit SHE/NHE readings, or 36 mV from Ag/AgCl (3.5 M KCl).
    Already-SCE readings only change voltage scale. This is not a temperature-
    aware or individually calibrated conversion; explicit SHE(T) is rejected.

    Transform value/min/max by scale and offset, but plus_minus by scale only.
    Bounds-only measurements remain bounds-only. Preserve omitted optional
    fields and explicit nulls; never round, invent a midpoint, or modify input.
    Bare voltages, unspecified hydrogen scales, incomplete Ag/AgCl references
    and all other unsupported spellings raise an exception containing the unit.
    """
    unit = " ".join(potential.unit.split())
    if unit not in _CONVERSIONS:
        reason = _UNCONVERTIBLE_UNITS.get(unit, "unsupported or ambiguous voltage unit/reference electrode")
        raise PittingPotentialConversionError(f"Cannot convert pitting potential unit {potential.unit!r}: {reason}")

    scale, offset = _CONVERSIONS[unit]
    converted = potential.model_dump(exclude_unset=True)
    converted["unit"] = "mV (SCE)"
    for field in ("value", "min", "max"):
        if converted.get(field) is not None:
            converted[field] = converted[field] * scale + offset
    if converted.get("plus_minus") is not None:
        converted["plus_minus"] *= scale

    try:
        return Measurement.model_validate(converted)
    except ValueError as exc:
        raise PittingPotentialConversionError(f"Converted measurement from {potential.unit!r} is invalid: {exc}") from exc
