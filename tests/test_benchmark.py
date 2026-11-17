"""Run: python -B -m unittest discover -s tests -p test_benchmark.py -v"""

from copy import deepcopy
import math
import unittest

from benchmark import benchmark_experiment, count_gaps
from models.observation_enrichment import AlloyComponent, EnrichedExperiment, Measurement, SolutionComponent


def measurement(value, unit):
    return {"value": value, "unit": unit}


def example():
    experiment = EnrichedExperiment.model_validate({
        "observation_id": "obs_001",
        "alloy": {"preparation": "", "microstructure": "", "material_class": "Fe Alloy",
                  "composition": [{"element_symbol": el, "amount": measurement(v, "wt%")}
                                  for el, v in (("Fe", 72), ("Cr", 18), ("Ni", 10))]},
        "test_temperature": measurement(25, "°C"),
        "test_solution": {"preparation": "", "solvent": "water",
                          "composition": [{"solute": "NaCl", "amount": measurement(0.5, "M")}],
                          "ph": 7, "chloride_concentration": measurement(0.5, "M")},
        "test_method": {"test_types": [], "procedure_description": "", "scan_rate": None,
                        "potential_step": None, "step_hold_duration": None, "pitting_criterion": ""},
        "pitting_potential": measurement(0.3, "V (SCE)"),
        "result_note": "", "failure_notes": "",
    })
    cra = {"No.": "1", "Fe": "72", "Cr": "18", "Ni": "10", "W": "0",
           "Avg Epit mV (SCE)": "300", "Min Epit mV (SCE)": "NA", "Max Epit mV (SCE)": "NA",
           "Test Temp C": "25", "Test Solution": "0.5 M NaCl", "CL- [M]": "0.5",
           "pH": "7", "Material class": "Fe Alloy"}
    return experiment, cra


class BenchmarkTests(unittest.TestCase):
    def test_matching_fields_and_count_api(self):
        experiment, cra = example()
        result = benchmark_experiment(experiment, cra)
        self.assertEqual(result.gap_count, 0)
        self.assertEqual(result.compared, 9)
        self.assertEqual(count_gaps(experiment, cra), 0)
        self.assertIn("alloy.W", result.skipped)

    def test_missing_and_incorrect_elements_are_separate_gaps(self):
        experiment, cra = example()
        experiment.alloy.composition = experiment.alloy.composition[:1]
        result = benchmark_experiment(experiment, cra)
        self.assertEqual(set(result.gaps), {"alloy.Cr", "alloy.Ni"})
        self.assertEqual(result.compared, 9)

    def test_alloy_zeros_are_not_required_but_explicit_contradictions_count(self):
        experiment, cra = example()
        experiment.alloy.composition.append(AlloyComponent(element_symbol="W", amount=Measurement(value=0.1, unit="wt%")))
        self.assertEqual(set(benchmark_experiment(experiment, cra).gaps), {"alloy.W"})

    def test_ambiguous_alloy_percent_requires_explicit_option(self):
        experiment, cra = example()
        for component in experiment.alloy.composition:
            component.amount.unit = "%"
        self.assertEqual(count_gaps(experiment, cra), 3)
        self.assertEqual(count_gaps(experiment, cra, assume_percent_is_weight=True), 0)
        self.assertTrue(all(c.amount.unit == "%" for c in experiment.alloy.composition))

    def test_balance_is_not_an_additional_propagated_gap_by_default(self):
        experiment, cra = example()
        experiment.alloy.composition[0].amount = "balance"
        experiment.alloy.composition[2].amount.value = 11
        result = benchmark_experiment(experiment, cra)
        self.assertEqual(set(result.gaps), {"alloy.Ni"})
        self.assertIn("alloy.Fe", result.skipped)
        self.assertEqual(count_gaps(experiment, cra, calculate_balance=True), 2)

    def test_explicit_atomic_composition_uses_existing_converter(self):
        experiment, cra = example()
        experiment.alloy.composition = [AlloyComponent(element_symbol="Fe", amount=Measurement(value=100, unit="at%"))]
        cra.update(Fe="100", Cr="0", Ni="0")
        self.assertEqual(count_gaps(experiment, cra), 0)

    def test_kelvin_chloride_mass_units_and_she_potential(self):
        experiment, cra = example()
        experiment.test_temperature = Measurement(value=298.15, unit="K")
        experiment.pitting_potential = Measurement(value=0.541, unit="V (SHE)")
        experiment.test_solution.chloride_concentration = Measurement(value=17725, unit="mg/l")
        experiment.test_solution.ph = Measurement(value=7, unit="")
        self.assertEqual(count_gaps(experiment, cra), 0)

    def test_missing_chloride_and_ph_are_derived_from_composition(self):
        experiment, cra = example()
        experiment.test_solution.chloride_concentration = None
        experiment.test_solution.ph = None
        result = benchmark_experiment(experiment, cra)
        self.assertEqual(result.gap_count, 0)
        self.assertEqual(result.derived, {"chloride_concentration": 0.5, "ph": 7})

    def test_reported_values_are_not_replaced_by_better_matching_estimates(self):
        experiment, cra = example()
        experiment.test_solution.ph = 6
        experiment.test_solution.chloride_concentration.value = 0.6
        result = benchmark_experiment(experiment, cra)
        self.assertEqual(set(result.gaps), {"ph", "chloride_concentration"})
        self.assertEqual(result.derived, {})

    def test_failed_estimates_are_gaps_and_do_not_assume_water(self):
        experiment, cra = example()
        experiment.test_solution.ph = None
        experiment.test_solution.solvent = ""
        self.assertEqual(set(benchmark_experiment(experiment, cra).gaps), {"ph"})

    def test_unsupported_extracted_units_count_as_gaps(self):
        experiment, cra = example()
        experiment.pitting_potential.unit = "V"
        experiment.test_temperature.unit = ""
        experiment.test_solution.chloride_concentration.unit = "ppm"
        result = benchmark_experiment(experiment, cra)
        self.assertEqual(set(result.gaps), {"pitting_potential", "test_temperature", "chloride_concentration"})
        self.assertTrue(all(reason.startswith("conversion:") for reason in result.gaps.values()))

    def test_missing_cra_cells_do_not_penalize_extraction(self):
        experiment, _ = example()
        for missing in (None, float("nan"), "", "NA", "nan", "N/A", "None"):
            with self.subTest(missing=missing):
                cra = {column: missing for column in ("Fe", "Cr", "Ni", "Avg Epit mV (SCE)",
                       "Test Temp C", "Test Solution", "CL- [M]", "pH", "Material class")}
                result = benchmark_experiment(experiment, cra)
                self.assertEqual(result.gap_count, 0)
                self.assertEqual(result.compared, 0)
                self.assertTrue(result.skipped)

    def test_qualitative_inequality_and_invalid_reference_targets_are_explicit_skips(self):
        experiment, cra = example()
        for target in ("Transpassive", ">800", float("inf"), True):
            with self.subTest(target=target):
                cra["Avg Epit mV (SCE)"] = target
                result = benchmark_experiment(experiment, cra)
                self.assertEqual(result.gap_count, 0)
                self.assertIn("pitting_potential", result.skipped)

    def test_ranges_compare_endpoints_without_a_midpoint(self):
        experiment, cra = example()
        cra.update({"Avg Epit mV (SCE)": None, "Min Epit mV (SCE)": "200", "Max Epit mV (SCE)": "400"})
        experiment.pitting_potential = Measurement(min=0.2, max=0.4, unit="V (SCE)")
        self.assertEqual(count_gaps(experiment, cra), 0)
        experiment.pitting_potential.max = 0.42
        self.assertEqual(set(benchmark_experiment(experiment, cra).gaps), {"pitting_potential"})

    def test_distribution_member_and_range_are_not_silently_equated(self):
        experiment, cra = example()
        cra.update({"Avg Epit mV (SCE)": None, "Min Epit mV (SCE)": "200", "Max Epit mV (SCE)": "400"})
        result = benchmark_experiment(experiment, cra)
        self.assertIn("pitting_potential", result.skipped)
        experiment.pitting_potential = Measurement(min=0.2, max=0.4, unit="V (SCE)")
        cra["Avg Epit mV (SCE)"] = "300"
        self.assertIn("pitting_potential", benchmark_experiment(experiment, cra).skipped)

    def test_uncertainty_does_not_become_an_agreement_margin(self):
        experiment, cra = example()
        experiment.pitting_potential = Measurement(value=0.305, plus_minus=0.1, unit="V (SCE)")
        self.assertEqual(count_gaps(experiment, cra), 1)
        self.assertEqual(count_gaps(experiment, cra, tolerances={"pitting_potential": 5}), 0)

    def test_field_tolerances_do_not_relax_other_fields(self):
        experiment, cra = example()
        experiment.alloy.composition[1].amount.value = 18.01
        experiment.test_temperature.value = 26
        result = benchmark_experiment(experiment, cra, tolerances={"alloy.Cr": 0.02})
        self.assertEqual(set(result.gaps), {"test_temperature"})
        for invalid in (-1, math.inf, math.nan, True):
            with self.subTest(tolerance=invalid), self.assertRaises(ValueError):
                count_gaps(experiment, cra, tolerances={"ph": invalid})
        with self.assertRaises(ValueError):
            count_gaps(experiment, cra, tolerances={"typo": 1})

    def test_solute_aliases_molar_prefixes_and_normality(self):
        experiment, cra = example()
        experiment.test_solution.composition[0].solute = "sodium chloride"
        experiment.test_solution.composition[0].amount = Measurement(value=500, unit="mM")
        self.assertEqual(count_gaps(experiment, cra), 0)
        cra["Test Solution"] = "0.5 N NaCl"
        self.assertEqual(count_gaps(experiment, cra), 0)

    def test_same_nonmolar_basis_can_match_without_density_assumptions(self):
        experiment, cra = example()
        cra["Test Solution"] = "3.5wt% NaCl"
        experiment.test_solution.composition[0].amount = Measurement(value=3.5, unit="wt.%")
        self.assertEqual(count_gaps(experiment, cra), 0)
        experiment.test_solution.composition[0].amount = Measurement(value=0.5, unit="M")
        self.assertEqual(set(benchmark_experiment(experiment, cra).gaps), {"test_solution.NaCl"})

    def test_solute_identity_and_amount_are_one_gap(self):
        experiment, cra = example()
        experiment.test_solution.composition = []
        self.assertEqual(set(benchmark_experiment(experiment, cra).gaps), {"test_solution.NaCl"})
        experiment.test_solution.composition = [SolutionComponent(solute="NaCl", amount=None)]
        self.assertEqual(count_gaps(experiment, cra), 1)

    def test_repeated_solutes_are_not_overwritten_or_added(self):
        experiment, cra = example()
        experiment.test_solution.composition.append(SolutionComponent(solute="sodium chloride", amount=Measurement(value=0.5, unit="M")))
        result = benchmark_experiment(experiment, cra)
        self.assertEqual(set(result.gaps), {"test_solution.NaCl"})
        self.assertTrue(result.gaps["test_solution.NaCl"].startswith("ambiguous:"))

    def test_extra_solutes_are_not_false_positives_for_an_incomplete_reference(self):
        experiment, cra = example()
        experiment.test_solution.composition.append(SolutionComponent(solute="HCl", amount=Measurement(value=0.01, unit="M")))
        self.assertEqual(count_gaps(experiment, cra), 0)

    def test_reference_recipe_without_ingredients_or_unparseable_text_is_skipped(self):
        experiment, cra = example()
        for text in ("synthetic sea water", "unsupported recipe"):
            with self.subTest(text=text):
                cra["Test Solution"] = text
                result = benchmark_experiment(experiment, cra)
                self.assertIn("test_solution", result.skipped)
                self.assertEqual(result.gap_count, 0)

    def test_unquantified_reference_ingredient_requires_identity_only(self):
        experiment, cra = example()
        cra["Test Solution"] = "1000 ppm NaCl, pH=5 by acetic acid"
        experiment.test_solution.composition = [
            SolutionComponent(solute="NaCl", amount=Measurement(value=1000, unit="ppm")),
            SolutionComponent(solute="acetic acid", amount=None),
        ]
        self.assertEqual(count_gaps(experiment, cra), 0)
        experiment.test_solution.composition.pop()
        self.assertEqual(set(benchmark_experiment(experiment, cra).gaps), {"test_solution.acetic acid"})

    def test_unitless_reference_ingredient_is_not_an_extraction_conversion_error(self):
        experiment, cra = example()
        cra["Test Solution"] = ("distilled water adjusted to pH 4(6.25 x 10–5 M H2SO4) "
                                "containing 200 ppm Cl- (5.5 x 10-3 NaCl)")
        experiment.test_solution.composition.append(SolutionComponent(solute="H2SO4", amount=Measurement(value=6.25e-5, unit="M")))
        result = benchmark_experiment(experiment, cra)
        self.assertIn("test_solution.NaCl", result.skipped)
        self.assertEqual(result.gap_count, 0)

    def test_material_class_and_missing_scalar_values(self):
        experiment, cra = example()
        experiment.alloy.material_class = ""
        experiment.pitting_potential = None
        experiment.test_temperature = None
        self.assertEqual(set(benchmark_experiment(experiment, cra).gaps),
                         {"material_class", "pitting_potential", "test_temperature"})

    def test_ignored_text_fields_and_no_input_mutation(self):
        experiment, cra = example()
        experiment.test_solution.ph = None
        experiment.test_solution.chloride_concentration = None
        experiment.alloy.composition[0].amount = "balance"
        cra.update({"Heat treatment": "anything", "Microstructures": "anything",
                    "Comments": "anything", "Test Method": "anything", "Scan Rate mV/s": "anything"})
        before_exp = experiment.model_dump(exclude_unset=True)
        before_cra = deepcopy(cra)
        result = benchmark_experiment(experiment, cra, calculate_balance=True)
        self.assertEqual(result.gap_count, 0)
        self.assertEqual(experiment.model_dump(exclude_unset=True), before_exp)
        self.assertEqual(cra, before_cra)


if __name__ == "__main__":
    unittest.main()
