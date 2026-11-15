"""Run: python -B -m unittest discover -s tests -p test_experiment_conversions.py -v"""

import unittest

from models.observation_enrichment import Measurement
from utils.experiment_conversions import PittingPotentialConversionError, standardize_pitting_potential


class PittingPotentialConversionTests(unittest.TestCase):
    def test_all_observed_sce_spellings(self):
        for unit in ("mV (SCE)", "mV vs SCE", "mV (S.C.E.)", "mV (SCE, saturated KCl)"):
            with self.subTest(unit=unit):
                converted = standardize_pitting_potential(Measurement(value=500, unit=unit))
                self.assertEqual(converted.value, 500)
                self.assertEqual(converted.unit, "mV (SCE)")
        for unit in ("V (SCE)", "VOLT VERSUS SCE", "V vs SCE", "v vs. SCE",
                     "V vs. SCE", "V (S.C.E.)", "V versus SCE"):
            with self.subTest(unit=unit):
                self.assertEqual(standardize_pitting_potential(Measurement(value=0.5, unit=unit)).value, 500)

    def test_all_observed_explicit_hydrogen_spellings(self):
        for unit in ("V (SHE)", "V (NHE)", "V (normal hydrogen electrode)",
                     "V_H (Normalwasserstoff-Skala)", "V (Std. H2 scale)", "V (S.H.E.)"):
            with self.subTest(unit=unit):
                self.assertEqual(standardize_pitting_potential(Measurement(value=0.5, unit=unit)).value, 259)
        for unit in ("mV (SHE)", "mV (NHE)", "mV (normal hydrogen electrode)",
                     "mV (standard hydrogen electrode)", "mV (S.H.E.)"):
            with self.subTest(unit=unit):
                self.assertEqual(standardize_pitting_potential(Measurement(value=500, unit=unit)).value, 259)

    def test_reference_offsets_have_the_correct_direction(self):
        # Gamry: 0 mV vs NHE/SHE is -241 mV vs saturated calomel.
        self.assertEqual(standardize_pitting_potential(Measurement(value=0, unit="V (SHE)")).value, -241)
        # Gamry: 0 mV vs Ag/AgCl (3.5 M KCl) is -36 mV vs saturated calomel.
        for value, expected in ((0, -36), (500, 464), (-500, -536)):
            with self.subTest(value=value):
                converted = standardize_pitting_potential(Measurement(value=value, unit="mV (Ag/AgCl, 3.5 M KCl)"))
                self.assertEqual(converted.value, expected)

    def test_values_bounds_and_uncertainty_transform_differently(self):
        source = Measurement(value=0.5, min=0.4, max=0.6, plus_minus=0.02, unit="V (SHE)")
        actual = standardize_pitting_potential(source)
        self.assertEqual(actual.model_dump(), {
            "value": 259, "min": 159, "max": 359, "plus_minus": 20, "unit": "mV (SCE)",
        })
        silver = standardize_pitting_potential(Measurement(value=500, min=400, max=600,
                                                         plus_minus=20, unit="mV (Ag/AgCl, 3.5 M KCl)"))
        self.assertEqual(silver.model_dump(), {
            "value": 464, "min": 364, "max": 564, "plus_minus": 20, "unit": "mV (SCE)",
        })

    def test_bounds_only_do_not_acquire_a_central_value(self):
        for source, expected in [
            ({"min": 0.4, "unit": "V (SHE)"}, {"min": 159, "unit": "mV (SCE)"}),
            ({"max": 1.2, "unit": "V (SCE)"}, {"max": 1200, "unit": "mV (SCE)"}),
            ({"min": -0.1, "max": 0.2, "unit": "V (SCE)"},
             {"min": -100, "max": 200, "unit": "mV (SCE)"}),
        ]:
            with self.subTest(source=source):
                actual = standardize_pitting_potential(Measurement.model_validate(source))
                self.assertEqual(actual.model_dump(exclude_unset=True), expected)

    def test_explicit_nulls_and_omitted_fields_are_preserved(self):
        source = Measurement(value=0.5, min=None, plus_minus=None, unit="V (SCE)")
        actual = standardize_pitting_potential(source)
        self.assertEqual(actual.model_fields_set, source.model_fields_set)
        self.assertEqual(actual.model_dump(exclude_unset=True),
                         {"value": 500, "min": None, "plus_minus": None, "unit": "mV (SCE)"})

    def test_does_not_round_results_or_modify_input(self):
        source = Measurement(value=0.123456789, unit="V (SCE)")
        before = source.model_dump(exclude_unset=True)
        converted = standardize_pitting_potential(source)
        self.assertAlmostEqual(converted.value, 123.456789, places=10)
        converted.value = 999
        self.assertEqual(source.model_dump(exclude_unset=True), before)

    def test_already_standardized_measurements_are_copied_and_idempotent(self):
        source = Measurement(value=-100, plus_minus=0, unit="mV (SCE)")
        converted = standardize_pitting_potential(source)
        self.assertIsNot(converted, source)
        self.assertEqual(converted.model_dump(exclude_unset=True), source.model_dump(exclude_unset=True))
        self.assertEqual(standardize_pitting_potential(converted), converted)

    def test_surrounding_and_repeated_whitespace_is_allowed(self):
        source = Measurement(value=0.5, unit=" \tV   vs.  SCE \n")
        self.assertEqual(standardize_pitting_potential(source).value, 500)

    def test_all_observed_ambiguous_units_raise_with_a_reason(self):
        cases = {
            "V": "reference electrode is missing", "v": "reference electrode is missing",
            "Volts": "reference electrode is missing", "mV": "reference electrode is missing",
            "V (H2 scale)": "hydrogen scale", "mV_H": "hydrogen scale",
            "V (Ag/AgCl)": "filling solution", "mV (Ag/AgCl, saturated)": "filling electrolyte",
            "V (SHE(T))": "temperature-dependent",
        }
        for unit, reason in cases.items():
            with self.subTest(unit=unit), self.assertRaises(PittingPotentialConversionError) as caught:
                standardize_pitting_potential(Measurement(value=0.5, unit=unit))
            self.assertIn(repr(unit), str(caught.exception))
            self.assertIn(reason, str(caught.exception))

    def test_unknown_units_and_references_are_not_guessed(self):
        for unit in ("", "unknown", "MV (SCE)", "V (RHE)", "V (SHE, 60 C)",
                     "mV (Ag/AgCl, 3.5 m KCl)", "V (SCE, 3 M KCl)"):
            with self.subTest(unit=unit), self.assertRaises(PittingPotentialConversionError):
                standardize_pitting_potential(Measurement(value=0.5, unit=unit))
        with self.assertRaises(ValueError):
            standardize_pitting_potential(Measurement(value=0.5, unit="V"))

    def test_nonfinite_conversion_result_raises(self):
        source = Measurement(value=1e308, unit="V (SCE)")
        with self.assertRaisesRegex(PittingPotentialConversionError, "invalid"):
            standardize_pitting_potential(source)


if __name__ == "__main__":
    unittest.main()
