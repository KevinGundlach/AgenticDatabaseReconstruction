"""Estimate the pitting-determination method from a CRA Test Method cell.

These small, deterministic rules follow the formats in tmp/test_methods.txt;
they do not read that file, consult papers, or use scan-rate values. They are
estimates from the supplied text, not authoritative scientific classifications.
"""

from enum import StrEnum
import re


class CanonicalTestType(StrEnum):
    """Mutually exclusive comparison categories, named for the pitting stage.

    POTENTIODYNAMIC includes forward and cyclic sweeps. POTENTIOSTATIC means
    fixed-potential testing, including final long-hold threshold confirmation.
    POTENTIAL_STEP separates deliberate incremental step-and-hold searches;
    these are also potentiostatically controlled, but are useful to distinguish
    for comparison. Ordinary digital staircase sweeps remain POTENTIODYNAMIC.
    SCRATCH takes priority when scratching defines the pitting criterion.
    AMBIGUOUS means competing procedures cannot be assigned to the result;
    UNKNOWN means the text supplies no recognizable determination method.
    """

    POTENTIODYNAMIC = "potentiodynamic"
    POTENTIOSTATIC = "potentiostatic"
    POTENTIAL_STEP = "potential_step"
    SCRATCH = "scratch"
    AMBIGUOUS = "ambiguous"
    UNKNOWN = "unknown"


def estimate_test_type(text: str | None) -> CanonicalTestType:
    """Return a string-valued category for one raw CRA Test Method cell.

    Missing values (None, blank text, or the string 'nan') return UNKNOWN.
    Bare 'anodic polarization', a potentiostat, and ASTM G1 do not establish
    the potential programme. In particular, G1 concerns specimen preparation:
    https://store.astm.org/standards/g1

    Explicit descriptions of the determination stage take precedence over a
    generic heading. Pretreatment, subsequent pit-growth holds and separate
    surface-analysis experiments do not alone change the determination type.
    Unsupported mixed procedures return AMBIGUOUS rather than picking the
    first method. No input data is modified.
    """
    if text is None:
        return CanonicalTestType.UNKNOWN
    if not isinstance(text, str):
        raise TypeError("Expected a CRA Test Method string or None")
    text = " ".join(text.casefold().split())

    if re.search(r"\bscratch(?:ing)?\b", text):
        return CanonicalTestType.SCRATCH

    # This inventory entry explicitly locates pitting before the growth hold.
    if ("potentiodynam" in text and "until a stable pit formed" in text
            and "then potentiostatic" in text and "pit growth" in text):
        return CanonicalTestType.POTENTIODYNAMIC

    # A different entry combines sweeping with separate fixed-potential runs,
    # without identifying which runs supplied the individual database values.
    if ("potentiodynam" in text and "in some experiments" in text
            and "changed almost instantaneously to a selected potential" in text):
        return CanonicalTestType.AMBIGUOUS

    # Controlled potential alone does not imply a constant-potential hold:
    # https://help.gamry.com/Framework/experiments_c_cyclicpolarization_experimentalsequence.html
    method_text = re.sub(r"potentiostatically[- ]controlled", "controlled", text)
    dynamic = bool(re.search(r"\bpotentiodynam", method_text))
    static = bool(re.search(r"\bpotentiostatic(?:ally)?\b", method_text))
    if dynamic and static:
        return CanonicalTestType.AMBIGUOUS

    # Deliberate dwell protocols in the inventory, rather than merely a
    # numerical staircase used to implement a sweep. Stepping for ESCA sample
    # preparation is not one of these pitting-determination descriptions.
    stepped = any(phrase in text for phrase in (
        "changed in steps of", "increased in steps of", "advanced in stages of",
        "potential was stepped upwards", "measurements made in 10 mv steps",
    ))
    if stepped:
        # In these two descriptions the staircase only brackets the threshold;
        # the explicitly stated final result comes from long fixed holds.
        if (("longer-time runs" in text and "final value" in text)
                or ("steady-state values" in text and "holding the potential for long times" in text)):
            return CanonicalTestType.POTENTIOSTATIC
        return CanonicalTestType.POTENTIAL_STEP

    if dynamic:
        return CanonicalTestType.POTENTIODYNAMIC
    if static:
        return CanonicalTestType.POTENTIOSTATIC

    # Unlabelled ramp descriptions present in the CRA inventory. A current
    # threshold (e.g. 10 microamps/cm²) qualifies the result, not the test type.
    if any(phrase in text for phrase in (
        "potential sweep", "scanning rate", "thereafter at a steady rate of",
    )):
        return CanonicalTestType.POTENTIODYNAMIC
    return CanonicalTestType.UNKNOWN
