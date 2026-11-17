"""Run: python -B -m unittest discover -s tests -p test_cra_test_method_parsing.py -v"""

import json
import unittest

from utils.cra_test_method_parsing import CanonicalTestType as Type, estimate_test_type


class TestMethodParsingTests(unittest.TestCase):
    def test_explicit_labels_case_and_multiline_prose(self):
        for text, expected in (
            ("Potentiodynamic Polarization", Type.POTENTIODYNAMIC),
            ("Potentiodynamic Polarzation", Type.POTENTIODYNAMIC),
            ("Polarization curves were obtained potentiodynamically at 20 mV/min.", Type.POTENTIODYNAMIC),
            (" POTENTIODYNAMIC\n  POLARIZATION in a three electrode cell ", Type.POTENTIODYNAMIC),
            ("Potentiostatic Polarization for 24 hrs in deaerated Cl- solution", Type.POTENTIOSTATIC),
            ("Potentiostatic Polarization at different potentials.", Type.POTENTIOSTATIC),
        ):
            with self.subTest(text=text):
                self.assertEqual(estimate_test_type(text), expected)

    def test_unlabelled_sweeps(self):
        for text in (
            "The potential was increased rapidly to -0.5 V and thereafter at a steady rate of 1V in 50 min.",
            "Anodic polarization at a scanning rate of 20 mV/min, using a potentiostat.",
            "Pitting potential measured by potential sweep method.",
        ):
            with self.subTest(text=text):
                self.assertEqual(estimate_test_type(text), Type.POTENTIODYNAMIC)

    def test_deliberate_steps_override_generic_headings(self):
        for text in (
            "Potentiodynamic Polarization. The potential was changed in steps of 10 mV every hour.",
            "Potentiodynamic Polarization. The anodic potential was increased in steps of 20 mV, "
            "and current recorded after waiting at each set potential for 1 min.",
            "Potentiostatic Polarization. Measurements made in 10 mV steps and held until a stationary current was observed",
            "To measure the pitting potentials, the potential was stepped upwards by 25 mV every 400 s.",
        ):
            with self.subTest(text=text):
                self.assertEqual(estimate_test_type(text), Type.POTENTIAL_STEP)

    def test_final_fixed_holds_take_precedence_over_bracketing_steps(self):
        for text in (
            "Potentiostatic Polarization. The potential was advanced in stages of 50 mV. "
            "Steady-state values were obtained by holding the potential for long times at a fixed value.",
            "Potentiostatic Polarization. The potential was increased in steps of 50 mV. "
            "This was followed by longer-time runs at a single potential to determine the final value.",
        ):
            with self.subTest(text=text):
                self.assertEqual(estimate_test_type(text), Type.POTENTIOSTATIC)

    def test_scratch_criterion_takes_priority_over_potential_control(self):
        for text in (
            "Scratch",
            'The "scratch" technique was employed for determination of pitting potentials. '
            "The electrode was first polarized potentiostatically, then scratched at increasing potentials.",
        ):
            with self.subTest(text=text):
                self.assertEqual(estimate_test_type(text), Type.SCRATCH)

    def test_followup_growth_hold_is_not_the_pitting_determination(self):
        self.assertEqual(estimate_test_type(
            "Potentiodynamic Polarzation until a stable pit formed then Potentiostatic Polarization "
            "at pitting potential to monitior pit growth"
        ), Type.POTENTIODYNAMIC)

    def test_competing_unassigned_procedures_are_ambiguous(self):
        for text in (
            "Potentiodynamic Polarization. In some experiments, the potential of an actively corroding "
            "electrode was changed almost instantaneously to a selected potential in a passive range.",
            "Potentiodynamic polarization and potentiostatic polarization were performed.",
        ):
            with self.subTest(text=text):
                self.assertEqual(estimate_test_type(text), Type.AMBIGUOUS)

    def test_conditioning_and_surface_analysis_do_not_change_sweep_type(self):
        for text in (
            "Potentiodynamic Polarization. First held at OCP for 1 h then cathodically polarized for 300s.",
            "Potentiodynamic Polarization. Samples prepared for the ESCA analyses were polarized by "
            "stepping the potential from the activation potential to -75, 500 and 800 mV. Held for 2 h.",
            "Potentiodynamic Polarization. The scan direction was reversed at 25 microamps/cm2.",
            "Potentiodynamic polarization. The digital sweep is a staircase ramp; "
            "the sample is potentiostatically controlled at each point.",
        ):
            with self.subTest(text=text):
                self.assertEqual(estimate_test_type(text), Type.POTENTIODYNAMIC)

    def test_missing_vague_and_preparation_only_text_is_unknown(self):
        for text in (None, "", "  ", "nan", "N/A", "ASTM G1", "ASTMG1", "ASTMG!",
                     "Anodic polarization", "A potentiostat and a SCE were used.",
                     "Anodic polarization. Flask as specified in ASTM G 5.",
                     "Potentiostatically-controlled anodic Polarization, test solution deaerated with N2",
                     "Ground to 600 grit and immersed for 1 h."):
            with self.subTest(text=text):
                self.assertEqual(estimate_test_type(text), Type.UNKNOWN)

    def test_string_categories_work_for_comparison_and_json(self):
        result = estimate_test_type("Potentiodynamic Polarization")
        self.assertEqual(result, "potentiodynamic")
        self.assertEqual(str(result), "potentiodynamic")
        self.assertEqual(json.dumps(result), '"potentiodynamic"')
        self.assertEqual(len(Type), 6)

    def test_rejects_non_text_inputs_instead_of_guessing(self):
        for text in (42, [], {}):
            with self.subTest(text=text):
                with self.assertRaises(TypeError):
                    estimate_test_type(text)


if __name__ == "__main__":
    unittest.main()
