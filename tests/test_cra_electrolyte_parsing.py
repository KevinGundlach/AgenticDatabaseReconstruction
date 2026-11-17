"""Run: python -B -m unittest discover -s tests -p test_cra_parsing.py -v"""

import unittest

from models.observation_enrichment import TestSolution
from utils.cra_electrolyte_parsing import TestSolutionParsingError, parse_test_solution


def recipe(solution):
    return [
        (component.solute, None if component.amount is None else
         (component.amount.value, component.amount.unit))
        for component in solution.composition
    ]


class TestSolutionParsingTests(unittest.TestCase):
    def test_simple_and_mixed_concentrations(self):
        for text in (
            "0.1M H2SO4 + 0.4 M Na2SO4 + 0.12M NaCl",
            "0.1 M H2SO4, 0.4M Na2SO4, 0.12 M NaCl",
            "0.1M H2SO4 and 0.4M Na2SO4 and 0.12M NaCl",
        ):
            with self.subTest(text=text):
                parsed = parse_test_solution(text)
                self.assertIsInstance(parsed, TestSolution)
                self.assertEqual(recipe(parsed), [
                    ("H2SO4", (0.1, "M")), ("Na2SO4", (0.4, "M")),
                    ("NaCl", (0.12, "M")),
                ])
                self.assertEqual(parsed.solvent, "")
                self.assertIsNone(parsed.ph)
                self.assertIsNone(parsed.chloride_concentration)

    def test_concentration_units_remain_distinct(self):
        for raw, expected in (
            ("M", "M"), ("N", "N"), ("m", "m"), ("ppm", "ppm"),
            ("%", "%"), ("wt%", "wt%"), ("wt.%", "wt%"), ("wt. %", "wt%"),
        ):
            with self.subTest(unit=raw):
                self.assertEqual(recipe(parse_test_solution(f"3.5 {raw} NaCl")),
                                 [("NaCl", (3.5, expected))])

    def test_deaeration_prefixes_suffixes_and_export_misspellings(self):
        for text, condition in (
            ("Deaerated 0.1M NaCl", "Deaerated"),
            ("0.1 M NaCl Deaerated N2", "Deaerated N2"),
            ("Deaerated (nitrogen purge) 0.1M NaCl", "Deaerated (nitrogen purge)"),
            ("0.1M NaCl (N2 purged)", "N2 purged"),
            ("de-aerated 0.1M NaCl", "de-aerated"),
            ("deareated (by H2) 0.1M NaCl", "deareated (by H2)"),
            ("0.1M NaCl, H2 deaerated", "H2 deaerated"),
        ):
            with self.subTest(text=text):
                parsed = parse_test_solution(text)
                self.assertEqual(recipe(parsed), [("NaCl", (0.1, "M"))])
                self.assertEqual(parsed.preparation, condition)

    def test_saturation_and_partial_pressure_are_preparation(self):
        for gas in ("Argon", "Hydrogen", "Nitrogen", "Oxygen"):
            with self.subTest(gas=gas):
                parsed = parse_test_solution(f"{gas}-saturated 1 M NaCl")
                self.assertEqual(parsed.preparation, f"{gas}-saturated")
                self.assertEqual(recipe(parsed), [("NaCl", (1, "M"))])
        parsed = parse_test_solution("deaerated 5 wt.% NaCl + 0.01 atm H2S")
        self.assertEqual(recipe(parsed), [("NaCl", (5, "wt%"))])
        self.assertEqual(parsed.preparation, "deaerated; H2S gas partial pressure: 0.01 atm")

    def test_ph_annotations_and_unquantified_adjustment(self):
        for annotation, expected in (("pH 6", 6), ("PH=3", 3), ("(pH 5.4)", 5.4),
                                     ("pH -0.5", -0.5)):
            with self.subTest(annotation=annotation):
                parsed = parse_test_solution(f"1M NaCl {annotation}")
                self.assertEqual(parsed.ph, expected)
                self.assertEqual(recipe(parsed), [("NaCl", (1, "M"))])
        parsed = parse_test_solution("1000 ppm NaCl, pH=5 by acetic acid")
        self.assertEqual(parsed.ph, 5)
        self.assertEqual(recipe(parsed), [("NaCl", (1000, "ppm")), ("acetic acid", None)])
        self.assertEqual(parsed.preparation, "pH=5 by acetic acid")

    def test_explicit_chloride_is_preserved_without_guessing_a_salt(self):
        parsed = parse_test_solution("0.1 M ChlorideDeaerated pH 5.8")
        self.assertEqual(recipe(parsed), [("Cl-", (0.1, "M"))])
        self.assertEqual(parsed.ph, 5.8)
        self.assertEqual(parsed.preparation, "Deaerated")
        self.assertEqual(parsed.chloride_concentration.value, 0.1)
        self.assertEqual(parsed.chloride_concentration.unit, "M")
        self.assertIsNot(parsed.chloride_concentration, parsed.composition[0].amount)
        self.assertIsNone(parse_test_solution("0.1M NaCl").chloride_concentration)

    def test_known_export_formula_spellings(self):
        for raw, expected in (("NaCI", "NaCl"), ("HCI", "HCl"), ("H CI", "HCl"),
                              ("NaCIO4", "NaClO4"), ("W04", "WO4")):
            with self.subTest(raw=raw):
                self.assertEqual(recipe(parse_test_solution(f"0.5 N{raw}")),
                                 [(expected, (0.5, "N"))])

    def test_all_other_observed_solutes(self):
        for solute in ("NaBr", "KCl", "HCl", "H2SO4", "Na2SO4", "Na2S2O3",
                       "NaHCO3", "MgCl2", "NaClO4", "WO4"):
            with self.subTest(solute=solute):
                self.assertEqual(recipe(parse_test_solution(f"0.1M {solute}")),
                                 [(solute, (0.1, "M"))])

    def test_named_seawater_does_not_invent_a_recipe_or_dilution_basis(self):
        for name in ("Sea Water 1:30", "Seawater Natural", "synthetic sea water"):
            with self.subTest(name=name):
                parsed = parse_test_solution(f"deaerated {name}")
                self.assertEqual(parsed.preparation, f"deaerated; {name}")
                self.assertEqual(parsed.solvent, "")
                self.assertEqual(parsed.composition, [])
                self.assertIsNone(parsed.ph)
                self.assertIsNone(parsed.chloride_concentration)

    def test_explicit_water_and_unquantified_solute(self):
        for solvent in ("water", "distilled water", "deionized water"):
            with self.subTest(solvent=solvent):
                parsed = parse_test_solution(solvent)
                self.assertEqual(parsed.solvent, solvent)
                self.assertEqual(parsed.composition, [])
        self.assertEqual(recipe(parse_test_solution("NaCl")), [("NaCl", None)])

    def test_distilled_water_entry_preserves_both_reported_chloride_representations(self):
        text = ("distilled water adjusted to pH 4(6.25 x 10–5 M H2SO4) "
                "containing 200 ppm Cl- (5.5 x 10-3 NaCl)")
        parsed = parse_test_solution(text)
        self.assertEqual(parsed.solvent, "distilled water")
        self.assertEqual(parsed.preparation, text)
        self.assertEqual(parsed.ph, 4)
        self.assertEqual(recipe(parsed), [("H2SO4", (6.25e-5, "M")), ("NaCl", (5.5e-3, ""))])
        self.assertEqual(parsed.chloride_concentration.value, 200)
        self.assertEqual(parsed.chloride_concentration.unit, "ppm")

    def test_scientific_notation_unicode_and_whitespace(self):
        parsed = parse_test_solution("  1e+2 ppm NaCl\n + 6.25 × 10−5 M H₂SO₄  ")
        self.assertEqual(recipe(parsed), [("NaCl", (100, "ppm")), ("H2SO4", (6.25e-5, "M"))])

    def test_rejects_missing_unknown_or_unaccounted_text(self):
        for text in (None, 5, "", "  ", "nan", "N/A", "unknown solution", "pH 7",
                     "deaerated", "0.01 atm H2S", "0.1 g NaCl", "0.1M UnknownSalt",
                     "0.1M NaCl mystery", "0.1M NaCl +", "0.1M NaCl + + 0.2M HCl",
                     "0.1M NaCl pH 5 pH 6", "0.1M NaCl + 0.2M NaCI",
                     "-1 M NaCl", "1e999 M NaCl", "0.1M NaCl pH 1e999",
                     "1 atm NaCl", "NaCl + acetic acid pH 5 by acetic acid"):
            with self.subTest(text=text):
                with self.assertRaises(TestSolutionParsingError):
                    parse_test_solution(text)

    def test_results_are_independent_and_validate_with_the_project_model(self):
        first = parse_test_solution("0.1M NaCl")
        first.composition[0].amount.value = 99
        second = parse_test_solution("0.1M NaCl")
        self.assertEqual(second.composition[0].amount.value, 0.1)
        self.assertEqual(TestSolution.model_validate(second.model_dump()), second)


if __name__ == "__main__":
    unittest.main()
