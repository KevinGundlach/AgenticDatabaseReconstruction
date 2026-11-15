"""Simple composition-based estimates; reported pH/chloride fields are never read.

Both public functions return a float, or None when the composition is unsupported
or insufficient. They do not modify the TestSolution. Concentrations must describe
the final solution, not stock solutions or quantities added before dilution.
"""

import math

from models.observation_enrichment import Measurement, TestSolution


# Rounded molar masses in g/mol; formula weights from NIST Chemistry WebBook.
# https://webbook.nist.gov/chemistry/
_MOLAR_MASSES = {
    "cl-": 35.45, "hcl": 36.46, "nacl": 58.44, "kcl": 74.55,
    "licl": 42.39, "mgcl2": 95.21, "cacl2": 110.98,
    "fecl2": 126.75, "fecl3": 162.20, "nh4cl": 53.49,
    "hno3": 63.01, "hclo4": 100.46,
    "naoh": 40.00, "koh": 56.11, "lioh": 23.95,
}
_CHLORIDE_COUNTS = {
    "cl-": 1, "hcl": 1, "nacl": 1, "kcl": 1, "licl": 1,
    "mgcl2": 2, "cacl2": 2, "fecl2": 2, "fecl3": 3, "nh4cl": 1,
}
_ACIDS = {"hcl", "hno3", "hclo4"}
_BASES = {"naoh", "koh", "lioh"}
_NEUTRAL_SALTS = {"nacl", "kcl", "licl", "nabr", "kbr", "ki", "nano3", "kno3", "naclo4"}

# Known chloride-free ingredients can be ignored for chloride accounting, even
# if their amounts are unknown. Unknown ingredients cannot be assumed Cl-free.
_CHLORIDE_FREE = (_ACIDS - {"hcl"}) | _BASES | (_NEUTRAL_SALTS - _CHLORIDE_COUNTS.keys()) | {
    "h2so4", "na2so4", "nahco3", "na2cro4", "naio3",
    "sodium acetate", "sodium benzoate", "ammonium tartrate",
    "ca2+", "mg2+", "na+", "k+", "sr2+", "hco3-", "so42-", "br-", "f-", "cu++",
    "s2o3^2- (added using na2s2o3·5h2o)", "moo4^2- (added as na2moo4)",
    "wo42-", "h2s (gas partial pressure)",
}
_ALIASES = {
    "sodium chloride": "nacl", "potassium chloride": "kcl", "lithium chloride": "licl",
    "magnesium chloride": "mgcl2", "calcium chloride": "cacl2",
    "ammonium chloride": "nh4cl", "hydrochloric acid": "hcl",
    "nitric acid": "hno3", "perchloric acid": "hclo4",
    "sodium hydroxide": "naoh", "potassium hydroxide": "koh", "lithium hydroxide": "lioh",
    "chloride": "cl-", "chloride ion": "cl-", "cl^-": "cl-",
    "cl- (prepared using nacl)": "cl-", "nacl (source of stated chloride)": "nacl",
    "naoh (ph adjustment)": "naoh",
}
_SUBSCRIPTS_AND_CHARGES = str.maketrans("₀₁₂₃₄₅₆₇₈₉⁺⁻−¹²³", "0123456789+--123")


def _solute_name(name: str) -> str:
    name = name.strip().casefold().translate(_SUBSCRIPTS_AND_CHARGES)
    return _ALIASES.get(name, name)


def _molarity(amount: Measurement | None, solute: str) -> float | None:
    """Convert a central concentration to mol/L without assuming a density."""
    if amount is None or amount.value is None or not math.isfinite(amount.value) or amount.value < 0:
        return None
    unit = amount.unit.strip().replace(" ", "").translate(_SUBSCRIPTS_AND_CHARGES)
    molar_units = {
        "M": 1, "mol/L": 1, "mol/l": 1, "molL^-1": 1, "molL-1": 1,
        "moldm^-3": 1, "moldm-3": 1,
        "mM": 1e-3, "mmol/L": 1e-3, "mmol/l": 1e-3,
        "uM": 1e-6, "µM": 1e-6, "μM": 1e-6,
    }
    if unit in molar_units:
        concentration = amount.value * molar_units[unit]
    elif unit == "N" and solute in _ACIDS | _BASES | {"nacl", "kcl", "licl", "cl-"}:
        # One equivalent per mole for these acid/base or chloride reactions.
        # Normality of multivalent salts is reaction-dependent, so not inferred.
        concentration = amount.value
    elif unit.casefold() in {"g/l", "mg/l", "%w/v", "%(w/v)"}:
        grams_per_litre = {"g/l": 1, "mg/l": 1e-3, "%w/v": 10, "%(w/v)": 10}[unit.casefold()]
        concentration = amount.value / _MOLAR_MASSES[solute] * grams_per_litre
    else:
        # In particular, m is molality, not M; wt%, ppm and bare % need more information.
        return None
    return concentration if math.isfinite(concentration) else None


def estimate_ph(solution: TestSolution) -> float | None:
    """Estimate ideal aqueous pH at 25 C using only the listed composition.

    Requires a recognized water solvent and a nonempty composition. Supports
    HCl/HNO3/HClO4, NaOH/KOH/LiOH, and the neutral salts listed above. Assumes
    complete dissociation, unit activity coefficients, and no unlisted acid/base
    additions or gas effects. Neutral-salt concentrations do not enter this ideal
    model; every acid/base needs a convertible central concentration. Sulfuric
    acid, buffers, weak acids/bases and hydrolysing salts return None.

    Solving [H+] - [OH-] = acid - base with [H+][OH-] = 1e-14 includes water
    autoionization and handles neutralization and very dilute solutions.
    pH is actually an activity quantity; this is a concentration-based estimate:
    https://water.usgs.gov/water-resources/software/PHREEQC/documentation/phreeqc3-html/phreeqc3-48.htm
    """
    water_names = {
        "water", "h2o", "aqueous", "distilled water", "deionized water", "deionised water",
        "double-distilled water", "water (aqueous solution)", "water (explicitly aqueous)",
    }
    if solution.solvent.strip().casefold() not in water_names or not solution.composition:
        return None

    equivalents = []
    seen = set()
    for component in solution.composition:
        solute = _solute_name(component.solute)
        if solute in seen:
            return None
        seen.add(solute)
        if solute in _NEUTRAL_SALTS:
            if component.amount is not None and component.amount.value is not None and component.amount.value < 0:
                return None
            continue
        if solute not in _ACIDS | _BASES:
            return None
        concentration = _molarity(component.amount, solute)
        if concentration is None:
            return None
        equivalents.append(concentration if solute in _ACIDS else -concentration)

    try:
        net_acid = math.fsum(equivalents)
    except OverflowError:
        return None
    kw = 1e-14  # Approximate water ion product at 25 C, in (mol/L)^2.
    # https://www.energy.gov/sites/default/files/2026-04/DOE-HDBK-1015-93_VOL1.pdf
    root = math.hypot(net_acid, 2 * math.sqrt(kw))
    # The second expression avoids cancellation for alkaline solutions.
    hydrogen = net_acid / 2 + root / 2 if net_acid >= 0 else kw / (root / 2 - net_acid / 2)
    return -math.log10(hydrogen) if math.isfinite(hydrogen) and hydrogen > 0 else None


def estimate_cl(solution: TestSolution) -> float | None:
    """Estimate total dissolved chloride from composition, in mol/L (CRA's M).

    Sum each supported chloride source's molarity times its chloride count, e.g.
    0.1 M MgCl2 contributes 0.2 mol/L Cl-. This is stoichiometric total chloride,
    not free-ion activity or a speciation calculation. It assumes dissolution
    and final-solution concentrations. Never reads chloride_concentration or ph.

    Requires at least one chloride-source entry; an explicit zero returns 0.0,
    while no source returns None. Unknown ingredients, unquantified chloride
    sources, duplicate solutes, or mixed salt/Cl- representations return None.
    The latter avoids counting the same chloride twice. Hydrates and unlisted
    compounds are unsupported; no general chemical-formula parser is used.
    """
    contributions = []
    seen = set()
    chloride_sources = set()
    for component in solution.composition:
        solute = _solute_name(component.solute)
        if solute in seen:
            return None
        seen.add(solute)
        if solute in _CHLORIDE_FREE:
            continue
        if solute not in _CHLORIDE_COUNTS:
            return None
        concentration = _molarity(component.amount, solute)
        if concentration is None:
            return None
        chloride_sources.add(solute)
        contributions.append(concentration * _CHLORIDE_COUNTS[solute])

    if not contributions or ("cl-" in chloride_sources and len(chloride_sources) > 1):
        return None
    try:
        total = math.fsum(contributions)
    except OverflowError:
        return None
    return total if math.isfinite(total) else None
