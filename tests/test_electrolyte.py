"""Run: python -B -m unittest discover -s tests -p test_electrolyte.py -v"""

import math
import unittest

from models.observation_enrichment import TestSolution
from utils.electrolyte import estimate_cl, estimate_ph


def amount(value, unit):
    return {"value": value, "unit": unit}


def solution(*components, solvent="water", ph=None, chloride=None):
    return TestSolution(
        preparation="", solvent=solvent,
        composition=[{"solute": name, "amount": value} for name, value in components],
        ph=ph, chloride_concentration=chloride,
    )


class ChlorideEstimationTests(unittest.TestCase):
    def test_sums_chloride_stoichiometry(self):
        sample = solution(("NaCl", amount(0.1, "M")), ("MgCl2", amount(0.2, "M")),
                          ("CaCl2", amount(0.3, "M")), ("HCl", amount(0.01, "M")))
        self.assertAlmostEqual(estimate_cl(sample), 1.11)

    def test_recognizes_names_unicode_and_observed_annotations(self):
        for name in ("sodium chloride", " NaCl ", "NaCl (source of stated chloride)"):
            with self.subTest(name=name):
                self.assertEqual(estimate_cl(solution((name, amount(0.5, "M")))), 0.5)
        for name in ("Cl-", "Cl−", "Cl⁻", "chloride ion", "Cl− (prepared using NaCl)"):
            with self.subTest(name=name):
                self.assertEqual(estimate_cl(solution((name, amount(0.5, "M")))), 0.5)
        self.assertEqual(estimate_cl(solution(("MgCl₂", amount(0.5, "M")))), 1)

    def test_molar_units_and_prefixes(self):
        for unit in ("M", "mol/L", "mol/l", "mol L^-1", "mol L⁻¹", "mol dm^-3", "mol dm⁻³"):
            with self.subTest(unit=unit):
                self.assertEqual(estimate_cl(solution(("NaCl", amount(0.1, unit)))), 0.1)
        for unit, expected in (("mM", 0.001), ("mmol/L", 0.001), ("µM", 1e-6), ("μM", 1e-6)):
            with self.subTest(unit=unit):
                self.assertEqual(estimate_cl(solution(("NaCl", amount(1, unit)))), expected)

    def test_mass_per_volume_uses_the_listed_species_mass(self):
        for name, value, unit, expected in [
            ("NaCl", 58.44, "g/L", 1),
            ("NaCl", 58.44, "mg/l", 0.001),
            ("Cl−", 35.45, "mg/L", 0.001),
            ("CaCl2", 110.98, "g/L", 2),
            ("NaCl", 5.844, "% (w/v)", 1),
        ]:
            with self.subTest(name=name, unit=unit):
                self.assertAlmostEqual(estimate_cl(solution((name, amount(value, unit)))), expected)

    def test_normality_is_supported_only_for_unambiguous_one_equivalent_sources(self):
        for name in ("NaCl", "KCl", "LiCl", "HCl"):
            with self.subTest(name=name):
                self.assertEqual(estimate_cl(solution((name, amount(0.1, "N")))), 0.1)
        self.assertIsNone(estimate_cl(solution(("CaCl2", amount(0.1, "N")))))

    def test_does_not_guess_density_basis_or_convert_activities(self):
        for unit in ("", "%", "wt%", "wt.%", "ppm", "m", "mol/kg", "M (activity)"):
            with self.subTest(unit=unit):
                self.assertIsNone(estimate_cl(solution(("NaCl", amount(1, unit)))))
        self.assertIsNone(estimate_cl(solution(("NaCl (activity, not concentration)", amount(1, "M")))))

    def test_chloride_free_ingredients_do_not_contribute_or_require_amounts(self):
        sample = solution(("NaCl", amount(0.5, "M")), ("NaClO4", amount(1, "M")),
                          ("H2SO4", None), ("NaOH (pH adjustment)", None))
        self.assertEqual(estimate_cl(sample), 0.5)

    def test_unknown_ingredients_duplicates_and_ion_salt_overlap_are_unavailable(self):
        cases = [
            solution(("NaCl", amount(0.5, "M")), ("Artificial sea salt", None)),
            solution(("NaCl", amount(0.5, "M")), ("sodium chloride", amount(0.5, "M"))),
            solution(("NaCl", amount(0.5, "M")), ("Cl−", amount(0.5, "M"))),
            solution(("MgCl2·6H2O", amount(1, "g/L"))),
        ]
        for sample in cases:
            with self.subTest(sample=sample):
                self.assertIsNone(estimate_cl(sample))

    def test_missing_negative_and_bounds_only_sources_are_unavailable(self):
        for missing in (None, amount(-1, "M"), {"min": 0.1, "max": 0.2, "unit": "M"}):
            with self.subTest(amount=missing):
                self.assertIsNone(estimate_cl(solution(("NaCl", missing))))

    def test_absence_is_unknown_but_explicit_zero_is_zero(self):
        self.assertIsNone(estimate_cl(solution()))
        self.assertIsNone(estimate_cl(solution(("NaBr", amount(1, "M")))))
        self.assertEqual(estimate_cl(solution(("NaCl", amount(0, "M")))), 0)


class PhEstimationTests(unittest.TestCase):
    def test_strong_acids_and_bases(self):
        for name in ("HCl", "HNO3", "HClO4", "hydrochloric acid"):
            with self.subTest(name=name):
                self.assertAlmostEqual(estimate_ph(solution((name, amount(0.01, "M")))), 2, places=8)
        for name in ("NaOH", "KOH", "LiOH"):
            with self.subTest(name=name):
                self.assertAlmostEqual(estimate_ph(solution((name, amount(0.01, "N")))), 12, places=8)

    def test_normalization_and_mass_conversion(self):
        self.assertAlmostEqual(estimate_ph(solution(("HCl", amount(1, "mM")))), 3, places=7)
        self.assertAlmostEqual(estimate_ph(solution(("NaOH", amount(0.04, "g/L")))), 11, places=7)

    def test_neutralization_and_water_autoionization(self):
        sample = solution(("HCl", amount(0.02, "M")), ("NaOH", amount(0.01, "M")))
        self.assertAlmostEqual(estimate_ph(sample), 2, places=8)
        cancelled = solution(("HCl", amount(0.01, "M")), ("NaOH", amount(0.01, "M")))
        self.assertEqual(estimate_ph(cancelled), 7)
        dilute = estimate_ph(solution(("HCl", amount(1e-9, "M"))))
        self.assertGreater(dilute, 6.99)
        self.assertLess(dilute, 7)

    def test_neutral_salts_do_not_supply_acid_or_base(self):
        self.assertEqual(estimate_ph(solution(("NaCl", amount(0.6, "M")))), 7)
        # Neutral-salt concentration is unnecessary under the ideal model.
        sample = solution(("NaCl", amount(3.5, "wt%")), ("HCl", amount(0.01, "M")))
        self.assertAlmostEqual(estimate_ph(sample), 2, places=8)

    def test_does_not_guess_water_or_a_complete_recipe_from_no_composition(self):
        for solvent in ("", "ethanol", "water/ethanol"):
            with self.subTest(solvent=solvent):
                self.assertIsNone(estimate_ph(solution(("HCl", amount(0.01, "M")), solvent=solvent)))
        self.assertIsNone(estimate_ph(solution()))
        self.assertEqual(estimate_ph(solution(("NaCl", amount(1, "M")), solvent="Distilled water")), 7)

    def test_unsupported_equilibria_and_unquantified_adjustments_are_unavailable(self):
        for name in ("H2SO4", "NaHCO3", "sodium acetate", "FeCl3", "MgCl2", "mystery buffer"):
            with self.subTest(name=name):
                self.assertIsNone(estimate_ph(solution((name, amount(0.1, "M")))))
        adjusted = solution(("NaCl", amount(0.6, "M")), ("NaOH (pH adjustment)", None))
        self.assertIsNone(estimate_ph(adjusted))

    def test_invalid_duplicate_and_bounds_only_acid_base_entries_are_unavailable(self):
        for value in (None, amount(-1, "M"), {"min": 0.01, "max": 0.02, "unit": "M"}, amount(1, "wt%")):
            with self.subTest(amount=value):
                self.assertIsNone(estimate_ph(solution(("HCl", value))))
        self.assertIsNone(estimate_ph(solution(("HCl", amount(1, "M")), ("hydrochloric acid", amount(1, "M")))))

    def test_extreme_inputs_do_not_return_nonfinite_results(self):
        self.assertIsNone(estimate_ph(solution(("HCl", amount(1e308, "M")), ("HNO3", amount(1e308, "M")))))
        self.assertIsNone(estimate_cl(solution(("FeCl3", amount(1e308, "M")))))
        self.assertTrue(math.isfinite(estimate_ph(solution(("NaOH", amount(1, "M"))))))

    def test_reported_fields_are_ignored_and_input_is_unchanged(self):
        for ph, chloride in [(None, None), (12.0, amount(9, "M")), ({"value": 5}, amount(123, "mg/L"))]:
            with self.subTest(ph=ph, chloride=chloride):
                sample = solution(("HCl", amount(0.01, "M")), ph=ph, chloride=chloride)
                before = sample.model_dump()
                self.assertAlmostEqual(estimate_ph(sample), 2, places=8)
                self.assertEqual(estimate_cl(sample), 0.01)
                self.assertEqual(sample.model_dump(), before)


if __name__ == "__main__":
    unittest.main()
