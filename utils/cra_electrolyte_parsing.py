"""Parse CRA test-solution text without calculating or guessing concentrations.

Supports the formats in tmp/test_solutions.txt. Concentration bases are retained:
M, N, m, ppm and bare % are distinct; wt.% is written as wt%. Only explicit
chloride-ion concentrations populate chloride_concentration. Gas conditioning
and partial pressures belong in preparation, not dissolved-solute amounts.
No I/O or dependence on the temporary inventory is needed at runtime.
"""

import math
import re

from models.observation_enrichment import Measurement, SolutionComponent, TestSolution


class TestSolutionParsingError(ValueError):
    """The text contains missing, unsupported or ambiguous solution syntax."""


_NUMBER = r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
_COMPONENT = re.compile(rf"(?P<value>{_NUMBER})\s*(?P<unit>wt\.?\s*%|ppm|atm|M|N|m|%)\s*(?P<solute>.+)")
_PH = re.compile(rf"\bpH\s*=?\s*(?P<value>[+-]?{_NUMBER})(?P<acid>\s+by\s+acetic\s+acid)?", re.IGNORECASE)
_CONDITIONING = re.compile(
    r"(?:H2\s+)?(?:de-?aerated|deareated)(?:\s*(?:N2|\((?:nitrogen\s+purge|by\s+H2)\)))?"
    r"|\(N2\s+purged\)"
    r"|(?:Argon|Hydrogen|Nitrogen|Oxygen)-saturated",
    re.IGNORECASE,
)
_DILUTE_WATER = re.compile(
    rf"(?i:distilled water adjusted to pH)\s*(?P<ph>[+-]?{_NUMBER})\s*"
    rf"\(\s*(?P<acid>{_NUMBER})\s*M\s*H2SO4\s*\)\s*"
    rf"(?i:containing)\s*(?P<chloride>{_NUMBER})\s*ppm\s*Cl-\s*"
    rf"\(\s*(?P<nacl>{_NUMBER})\s*NaCl\s*\)"
)

# Chemical labels occurring in this export. Explicitly repair its familiar
# transcription spellings NaCI/HCI/H CI/NaCIO4 and W04; do not infer ion charges
# for WO4 or infer an unnamed chloride salt from the word "Chloride".
_SOLUTES = {
    "nacl": "NaCl", "naci": "NaCl", "nabr": "NaBr", "kcl": "KCl",
    "hcl": "HCl", "hci": "HCl", "h2so4": "H2SO4",
    "na2so4": "Na2SO4", "na2s2o3": "Na2S2O3", "nahco3": "NaHCO3",
    "mgcl2": "MgCl2", "naclo4": "NaClO4", "nacio4": "NaClO4",
    "wo4": "WO4", "w04": "WO4", "chloride": "Cl-", "cl-": "Cl-",
    "h2s": "H2S", "aceticacid": "acetic acid", "ch3cooh": "acetic acid",
}


def _number(text: str) -> float:
    value = float(text)
    if not math.isfinite(value):
        raise TestSolutionParsingError(f"Non-finite numerical amount: {text!r}")
    return value


def parse_test_solution(text: str) -> TestSolution:
    """Parse one raw CRA Test Solution cell, or raise TestSolutionParsingError.

    Accept concentration/solute lists separated by '+', ',' or 'and', with
    optional gas conditioning and pH annotations. Unknown solutes, unknown units
    and unexplained leftover text raise rather than yielding a partial recipe.
    Unquantified recognized solutes have amount=None. Missing solvent is "";
    only an explicitly named water solvent is populated. Named seawater recipes
    retain their names/ratios in preparation and have no invented composition.

    The exceptional distilled-water entry reports chloride in ppm and restates
    it as a unitless NaCl quantity: retain NaCl with unit="" and the separate
    explicit chloride measurement, without duplicating Cl- in the composition.
    No pH, density, concentration conversion or seawater recipe is calculated.
    """
    if not isinstance(text, str) or not text.strip():
        raise TestSolutionParsingError(f"Expected a nonempty test-solution string, got {text!r}")
    normalized = " ".join(text.strip().translate(str.maketrans("₀₁₂₃₄₅₆₇₈₉−–", "0123456789--")).split())
    normalized = re.sub(r"(\d+(?:\.\d+)?)\s*[x×]\s*10\s*\^?\s*([+-]\d+)", r"\1e\2", normalized)

    # Keep both reported representations of chloride, without inventing a
    # molarity for the parenthetical NaCl figure or treating them as additions.
    special = _DILUTE_WATER.fullmatch(normalized)
    if special:
        return TestSolution(
            preparation=text.strip(), solvent="distilled water",
            composition=[
                SolutionComponent(solute="H2SO4", amount=Measurement(value=_number(special["acid"]), unit="M")),
                SolutionComponent(solute="NaCl", amount=Measurement(value=_number(special["nacl"]), unit="")),
            ],
            ph=_number(special["ph"]),
            chloride_concentration=Measurement(value=_number(special["chloride"]), unit="ppm"),
        )

    preparation = []

    def keep_condition(match):
        condition = match.group().strip()
        if condition.startswith("(") and condition.endswith(")"):
            condition = condition[1:-1]
        preparation.append(condition)
        return " "

    remaining = _CONDITIONING.sub(keep_condition, normalized)
    ph = None
    additions = []
    ph_matches = list(_PH.finditer(remaining))
    if len(ph_matches) > 1:
        raise TestSolutionParsingError(f"Multiple pH annotations cannot be assigned unambiguously: {text!r}")
    if ph_matches:
        match = ph_matches[0]
        ph = _number(match["value"])
        if match["acid"]:
            preparation.append(match.group())
            additions.append(SolutionComponent(solute="acetic acid", amount=None))
        remaining = remaining[:match.start()] + " " + remaining[match.end():]
    remaining = re.sub(r"\(\s*\)", " ", remaining).strip(" ,")
    remaining = " ".join(remaining.split())

    named = re.sub(r"\s+", "", remaining).casefold()
    if named in {"seawater", "seawaternatural", "syntheticseawater", "seawater1:30"}:
        preparation.append(remaining)
        return TestSolution(preparation="; ".join(preparation), solvent="", composition=additions,
                            ph=ph, chloride_concentration=None)
    if remaining.casefold() in {"water", "distilled water", "deionized water", "deionised water"}:
        return TestSolution(preparation="; ".join(preparation), solvent=remaining, composition=additions,
                            ph=ph, chloride_concentration=None)
    if not remaining:
        raise TestSolutionParsingError(f"No solution composition or named solution was supplied: {text!r}")

    composition = []
    chloride = None
    seen = set()
    # Do not split the '+' belonging to a scientific-notation exponent.
    parts = re.split(r"\s*(?:(?<![eE])\+|,|\band\b)\s*", remaining, flags=re.IGNORECASE)
    for part in parts:
        if not part.strip():
            raise TestSolutionParsingError(f"Empty ingredient in test solution: {text!r}")
        match = _COMPONENT.fullmatch(part)
        raw_solute = match["solute"] if match else part
        solute = _SOLUTES.get(re.sub(r"\s+", "", raw_solute).casefold())
        if solute is None:
            raise TestSolutionParsingError(f"Unrecognized ingredient or leftover text {part!r} in {text!r}")

        unit = match["unit"] if match else None
        if unit == "atm":
            if solute != "H2S":
                raise TestSolutionParsingError(f"Unsupported gas partial-pressure description: {part!r}")
            _number(match["value"])
            preparation.append(f"H2S gas partial pressure: {match['value']} atm")
            continue
        if solute in seen:
            raise TestSolutionParsingError(f"Repeated solute {solute!r} cannot be combined safely: {text!r}")
        seen.add(solute)
        quantity = None
        if match:
            if unit.startswith("wt"):
                unit = "wt%"
            quantity = Measurement(value=_number(match["value"]), unit=unit)
        composition.append(SolutionComponent(solute=solute, amount=quantity))
        if solute == "Cl-" and quantity is not None:
            chloride = quantity.model_copy(deep=True)

    for addition in additions:
        if addition.solute in seen:
            raise TestSolutionParsingError(f"Repeated pH-adjusting solute {addition.solute!r}: {text!r}")
        composition.append(addition)
    if not composition:
        raise TestSolutionParsingError(f"Only gas conditioning was supplied, without a solution: {text!r}")
    return TestSolution(preparation="; ".join(preparation), solvent="", composition=composition,
                        ph=ph, chloride_concentration=chloride)
