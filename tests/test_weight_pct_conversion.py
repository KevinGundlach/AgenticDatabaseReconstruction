"""Run: python -B -m unittest discover -s tests -p test_weight_pct_conversion.py -v"""

import unittest

from models.observation_enrichment import Alloy
from utils.weight_pct_conversion import (
    ATOMIC_RATIO_UNITS, ATOMIC_PERCENT_UNITS, WEIGHT_PERCENT_UNITS,
    AlloyCompositionErrorReason, InvalidAlloyCompositionError,
    to_weight_percent, to_weight_percent_strict,
)


def alloy(*components):
    return Alloy(
        preparation="", microstructure="", material_class="",
        composition=[{"element_symbol": element, "amount": amount} for element, amount in components],
    )


def amount(value, unit, **extras):
    return {"value": value, "unit": unit, **extras}


class WeightPercentConversionTests(unittest.TestCase):
    def test_observed_weight_percent_spellings(self):
        for unit in WEIGHT_PERCENT_UNITS:
            with self.subTest(unit=unit):
                result = to_weight_percent_strict(alloy(("Fe", amount(80, unit)), ("Cr", amount(20, "wt%"))))
                self.assertEqual(result, {"Fe": 80.0, "Cr": 20.0})

    def test_rounding_tolerance_does_not_rescale_reported_mass_values(self):
        for iron in (79.9, 80.0, 80.1):
            with self.subTest(iron=iron):
                self.assertEqual(to_weight_percent_strict(alloy(("Fe", amount(iron, "wt%")), ("Cr", amount(20, "wt%")))),
                                 {"Fe": iron, "Cr": 20})
        for iron in (79.8, 80.2, 70):
            with self.subTest(iron=iron), self.assertRaisesRegex(InvalidAlloyCompositionError, "totals"):
                to_weight_percent_strict(alloy(("Fe", amount(iron, "wt%")), ("Cr", amount(20, "wt%"))))

    def test_atomic_percent_mass_weighting(self):
        for unit in ATOMIC_PERCENT_UNITS:
            with self.subTest(unit=unit):
                result = to_weight_percent_strict(alloy(("Fe", amount(50, unit)), ("Cr", amount(50, unit))))
                self.assertAlmostEqual(result["Fe"], 100 * 55.845 / (55.845 + 51.996))
                self.assertAlmostEqual(sum(result.values()), 100)

    def test_atomic_percent_requires_a_complete_total(self):
        with self.assertRaisesRegex(InvalidAlloyCompositionError, "totals"):
            to_weight_percent_strict(alloy(("Fe", amount(50, "at%")), ("Cr", amount(20, "at%"))))

    def test_nominal_atomic_ratios(self):
        for unit in ATOMIC_RATIO_UNITS:
            with self.subTest(unit=unit):
                result = to_weight_percent_strict(alloy(("Al", amount(0.3, unit)), ("Co", amount(1, unit)),
                                                  ("Cr", amount(1, unit)), ("Fe", amount(1, unit)),
                                                  ("Ni", amount(1, unit))))
                expected_al = 100 * 0.3 * 26.982 / (0.3 * 26.982 + 58.933 + 51.996 + 55.845 + 58.693)
                self.assertAlmostEqual(result["Al"], expected_al)
                self.assertAlmostEqual(sum(result.values()), 100)

    def test_explicit_balance_in_weight_and_atomic_percent(self):
        for unit in ("wt%", "at%"):
            with self.subTest(unit=unit):
                actual = to_weight_percent_strict(alloy(("Fe", "balance"), ("Cr", amount(20, unit))))
                explicit = to_weight_percent_strict(alloy(("Fe", amount(80, unit)), ("Cr", amount(20, unit))))
                self.assertEqual(actual, explicit)

    def test_ambiguous_units_raise(self):
        for unit in ("", "%", "pct", "nominal %", "ppm", "% (purity)", "% (foil purity)", "something else"):
            with self.subTest(unit=unit), self.assertRaisesRegex(InvalidAlloyCompositionError, "unit"):
                to_weight_percent_strict(alloy(("Fe", amount(100, unit))))

    def test_missing_amount_or_central_value_raises(self):
        for missing in (None, {"min": 10, "max": 20, "unit": "wt%"}):
            with self.subTest(missing=missing), self.assertRaisesRegex(InvalidAlloyCompositionError, "central"):
                to_weight_percent_strict(alloy(("Fe", amount(80, "wt%")), ("Cr", missing)))

    def test_central_value_is_used_without_bounds_or_uncertainty_processing(self):
        result = to_weight_percent_strict(alloy(("Fe", amount(80, "wt%", min=79, max=81, plus_minus=1)),
                                         ("Cr", amount(20, "wt%"))))
        self.assertEqual(result, {"Fe": 80, "Cr": 20})

    def test_mixed_bases_raise(self):
        for second in ("at%", "nominal formula coefficient"):
            with self.subTest(second=second), self.assertRaisesRegex(InvalidAlloyCompositionError, "mixed"):
                to_weight_percent_strict(alloy(("Fe", amount(80, "wt%")), ("Cr", amount(20, second))))

    def test_invalid_elements_duplicates_negative_and_over_100_raise(self):
        cases = [
            alloy(("Unknown", amount(100, "wt%"))),
            alloy(("Fe", amount(50, "wt%")), ("Fe", amount(50, "wt%"))),
            alloy(("Fe", amount(101, "wt%"))),
            alloy(("Fe", amount(-1, "wt%")), ("Cr", amount(100, "wt%"))),
        ]
        for invalid in cases:
            with self.subTest(invalid=invalid), self.assertRaises(InvalidAlloyCompositionError):
                to_weight_percent_strict(invalid)

    def test_invalid_balances_raise(self):
        cases = [
            alloy(("Fe", "balance")),
            alloy(("Fe", "balance"), ("Cr", "balance")),
            alloy(("Fe", "balance"), ("Cr", amount(60, "wt%")), ("Ni", amount(50, "wt%"))),
            alloy(("Fe", "balance"), ("Cr", amount(1, "nominal formula coefficient"))),
        ]
        for invalid in cases:
            with self.subTest(invalid=invalid), self.assertRaises(InvalidAlloyCompositionError):
                to_weight_percent_strict(invalid)

    def test_empty_and_zero_compositions_raise(self):
        for invalid in (alloy(), alloy(("Fe", amount(0, "nominal formula coefficient")))):
            with self.subTest(invalid=invalid), self.assertRaises(InvalidAlloyCompositionError):
                to_weight_percent_strict(invalid)

    def test_input_is_not_modified(self):
        original = alloy(("Fe", "balance"), ("Cr", amount(20, "at%")))
        snapshot = original.model_dump()
        result = to_weight_percent_strict(original)
        result["Cr"] = -1
        self.assertEqual(original.model_dump(), snapshot)

    def test_each_error_has_the_expected_enum_reason(self):
        reasons = AlloyCompositionErrorReason
        ratio = "nominal formula coefficient"
        cases = [
            (alloy(), reasons.EMPTY_COMPOSITION),
            (alloy(("Unknown", amount(100, "wt%"))), reasons.UNKNOWN_ELEMENT),
            (alloy(("Fe", amount(50, "wt%")), ("Fe", amount(50, "wt%"))), reasons.DUPLICATE_ELEMENT),
            (alloy(("Fe", "balance"), ("Cr", "balance")), reasons.MULTIPLE_BALANCES),
            (alloy(("Fe", None)), reasons.MISSING_AMOUNT),
            (alloy(("Fe", {"min": 10, "max": 20, "unit": "wt%"})), reasons.MISSING_CENTRAL_VALUE),
            (alloy(("Fe", amount(-1, "wt%"))), reasons.INVALID_AMOUNT),
            (alloy(("Fe", amount(100, "%"))), reasons.UNSUPPORTED_UNIT),
            (alloy(("Fe", amount(80, "wt%")), ("Cr", amount(20, "at%"))), reasons.MIXED_BASES),
            (alloy(("Fe", amount(101, "wt%"))), reasons.PERCENTAGE_OUT_OF_RANGE),
            (alloy(("Fe", amount(1e308, ratio)), ("Cr", amount(1e308, ratio))), reasons.NONFINITE_TOTAL),
            (alloy(("Fe", "balance")), reasons.INVALID_BALANCE_BASIS),
            (alloy(("Fe", "balance"), ("Cr", amount(60, "wt%")), ("Ni", amount(50, "wt%"))), reasons.NEGATIVE_BALANCE),
            (alloy(("Fe", amount(0, ratio))), reasons.NONPOSITIVE_TOTAL),
            (alloy(("Fe", amount(80, "wt%")), ("Cr", amount(10, "wt%"))), reasons.TOTAL_NOT_100),
        ]
        observed = set()
        for invalid, expected_reason in cases:
            with self.subTest(reason=expected_reason):
                with self.assertRaises(InvalidAlloyCompositionError) as caught:
                    to_weight_percent_strict(invalid)
                self.assertIs(caught.exception.reason, expected_reason)
                observed.add(caught.exception.reason)
        self.assertEqual(observed, set(AlloyCompositionErrorReason))

    def test_exception_retains_readable_value_error_message(self):
        with self.assertRaises(ValueError) as caught:
            to_weight_percent_strict(alloy(("Fe", None)))
        error = caught.exception
        self.assertIs(error.reason, AlloyCompositionErrorReason.MISSING_AMOUNT)
        self.assertEqual(str(error), "Fe: a central numerical amount is required")
        self.assertEqual(error.args, (str(error),))

    def test_reason_reports_first_issue_in_component_order(self):
        missing = ("Fe", None)
        ambiguous = ("Cr", amount(20, "%"))
        for components, expected in [
            ((missing, ambiguous), AlloyCompositionErrorReason.MISSING_AMOUNT),
            ((ambiguous, missing), AlloyCompositionErrorReason.UNSUPPORTED_UNIT),
        ]:
            with self.subTest(expected=expected), self.assertRaises(InvalidAlloyCompositionError) as caught:
                to_weight_percent_strict(alloy(*components))
            self.assertIs(caught.exception.reason, expected)


class PermissiveWeightPercentConversionTests(unittest.TestCase):
    def test_retains_known_amounts_and_unknown_keys(self):
        source = alloy(("Fe", None), ("Cr", amount(18, "wt%")),
                       ("Ni", amount(10, "%")), ("S", {"max": 0.003, "unit": "wt%"}))
        self.assertEqual(to_weight_percent(source), {"Fe": None, "Cr": 18, "Ni": None, "S": None})

    def test_known_weight_percentages_need_not_total_100(self):
        for source, expected in [
            (alloy(("Cr", amount(17, "wt%")), ("Ni", amount(25, "wt%")), ("Mo", amount(5, "wt%"))),
             {"Cr": 17, "Ni": 25, "Mo": 5}),
            (alloy(("Fe", amount(80, "wt%")), ("Cr", amount(30, "wt%"))), {"Fe": 80, "Cr": 30}),
        ]:
            with self.subTest(source=source):
                self.assertEqual(to_weight_percent(source), expected)
                with self.assertRaises(InvalidAlloyCompositionError):
                    to_weight_percent_strict(source)

    def test_ambiguous_units_remain_none(self):
        for unit in ("", "%", "pct", "nominal %", "ppm", "% (purity)", "% (foil purity)"):
            with self.subTest(unit=unit):
                self.assertEqual(to_weight_percent(alloy(("Fe", amount(100, unit)))), {"Fe": None})

    def test_percent_assumption_is_opt_in_for_complete_and_partial_compositions(self):
        source = alloy(("Fe", amount(80, "%")), ("Cr", amount(20, " % ")))
        self.assertEqual(to_weight_percent(source), {"Fe": None, "Cr": None})
        self.assertEqual(to_weight_percent(source, assume_percent_is_weight=True), {"Fe": 80, "Cr": 20})
        partial = alloy(("Fe", None), ("Cr", amount(18, "%")), ("Ni", amount(10, "wt%")))
        self.assertEqual(to_weight_percent(partial, assume_percent_is_weight=True),
                         {"Fe": None, "Cr": 18, "Ni": 10})

    def test_percent_assumption_does_not_reinterpret_other_units_or_bounds(self):
        for unit in ("", "pct", "nominal %", "ppm", "% (purity)", "% (foil purity)"):
            with self.subTest(unit=unit):
                self.assertEqual(to_weight_percent(alloy(("Fe", amount(100, unit))),
                                                   assume_percent_is_weight=True), {"Fe": None})
        bounded = alloy(("Fe", None), ("Cr", {"min": 18, "max": 20, "unit": "%"}))
        self.assertEqual(to_weight_percent(bounded, assume_percent_is_weight=True),
                         {"Fe": None, "Cr": None})

    def test_balance_markers_can_be_preserved_when_resolvable_or_unknown(self):
        cases = [
            (alloy(("Fe", "balance"), ("Cr", amount(20, "wt%"))), {"Fe": "balance", "Cr": 20}),
            (alloy(("Fe", "balance"), ("Cr", amount(20, "wt%")), ("Ni", None)),
             {"Fe": "balance", "Cr": 20, "Ni": None}),
            (alloy(("Fe", "balance")), {"Fe": "balance"}),
            (alloy(("Fe", "balance"), ("Cr", "balance"), ("Ni", amount(20, "wt%"))),
             {"Fe": "balance", "Cr": "balance", "Ni": 20}),
            (alloy(("Fe", "balance"), ("Cr", amount(60, "wt%")), ("Ni", amount(50, "wt%"))),
             {"Fe": "balance", "Cr": 60, "Ni": 50}),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(to_weight_percent(source, calculate_balance=False), expected)

    def test_atomic_conversion_uses_balance_internally_but_preserves_output_marker(self):
        source = alloy(("Fe", "balance"), ("Cr", amount(20, "at%")))
        expected = to_weight_percent_strict(source)
        actual = to_weight_percent(source, calculate_balance=False)
        self.assertEqual(actual, {"Fe": "balance", "Cr": expected["Cr"]})
        incomplete = alloy(("Fe", "balance"), ("Cr", amount(20, "at%")), ("Ni", None))
        self.assertEqual(to_weight_percent(incomplete, calculate_balance=False),
                         {"Fe": "balance", "Cr": None, "Ni": None})

    def test_balance_and_percent_options_work_independently(self):
        source = alloy(("Fe", "balance"), ("Cr", amount(20, "%")))
        for calculate, assume, expected in [
            (True, False, {"Fe": None, "Cr": None}),
            (False, False, {"Fe": "balance", "Cr": None}),
            (True, True, {"Fe": 80, "Cr": 20}),
            (False, True, {"Fe": "balance", "Cr": 20}),
        ]:
            with self.subTest(calculate_balance=calculate, assume_percent_is_weight=assume):
                self.assertEqual(to_weight_percent(source, calculate_balance=calculate,
                                                   assume_percent_is_weight=assume), expected)

    def test_options_preserve_existing_atomic_and_ratio_conversion(self):
        for unit, value in [("at%", 50), ("nominal formula coefficient", 1)]:
            source = alloy(("Fe", amount(value, unit)), ("Cr", amount(value, unit)))
            with self.subTest(unit=unit):
                self.assertEqual(to_weight_percent(source, calculate_balance=False,
                                                   assume_percent_is_weight=True),
                                 to_weight_percent_strict(source))

    def test_options_do_not_make_invalid_or_missing_amounts_known(self):
        source = alloy(("Fe", None), ("Cr", amount(101, "%")), ("Ni", amount(-1, "%")),
                       ("Unknown", "balance"), ("Co", "balance"), ("Co", amount(1, "%")))
        self.assertEqual(to_weight_percent(source, calculate_balance=False,
                                           assume_percent_is_weight=True),
                         {"Fe": None, "Cr": None, "Ni": None, "Unknown": None, "Co": None})

    def test_options_leave_input_units_and_strict_conversion_unchanged(self):
        source = alloy(("Fe", "balance"), ("Cr", amount(20, "%", min=19, max=21, plus_minus=1)))
        snapshot = source.model_dump()
        units_before = WEIGHT_PERCENT_UNITS.copy()
        for calculate in (False, True):
            with self.subTest(calculate_balance=calculate):
                result = to_weight_percent(source, calculate_balance=calculate,
                                           assume_percent_is_weight=True)
                result["Cr"] = -1
                self.assertEqual(source.model_dump(), snapshot)
        self.assertEqual(WEIGHT_PERCENT_UNITS, units_before)
        self.assertEqual(to_weight_percent(source), {"Fe": None, "Cr": None})
        with self.assertRaises(InvalidAlloyCompositionError) as caught:
            to_weight_percent_strict(source)
        self.assertIs(caught.exception.reason, AlloyCompositionErrorReason.UNSUPPORTED_UNIT)

    def test_complete_atomic_compositions_and_ratios_still_convert(self):
        for unit, value in [("at%", 50), ("nominal formula coefficient", 1)]:
            source = alloy(("Fe", amount(value, unit)), ("Cr", amount(value, unit)))
            with self.subTest(unit=unit):
                self.assertEqual(to_weight_percent(source), to_weight_percent_strict(source))

    def test_incomplete_atomic_composition_does_not_normalize_known_subset(self):
        cases = [
            alloy(("Fe", amount(50, "at%")), ("Cr", None)),
            alloy(("Fe", amount(50, "at%")), ("Cr", amount(20, "at%"))),
            alloy(("Fe", amount(1, "nominal formula coefficient")), ("Cr", None)),
        ]
        for source in cases:
            with self.subTest(source=source):
                self.assertEqual(to_weight_percent(source), {"Fe": None, "Cr": None})

    def test_mixed_bases_keep_mass_values_only(self):
        source = alloy(("Fe", amount(80, "at%")), ("Cr", amount(20, "wt%")))
        self.assertEqual(to_weight_percent(source), {"Fe": None, "Cr": 20})

    def test_explicit_balance_requires_every_other_amount_to_be_known(self):
        self.assertEqual(to_weight_percent(alloy(("Fe", "balance"), ("Cr", amount(20, "wt%")))),
                         {"Fe": 80, "Cr": 20})
        source = alloy(("Fe", "balance"), ("Cr", amount(20, "wt%")), ("Ni", None))
        self.assertEqual(to_weight_percent(source), {"Fe": None, "Cr": 20, "Ni": None})
        atomic = alloy(("Fe", "balance"), ("Cr", amount(20, "at%")))
        self.assertEqual(to_weight_percent(atomic), to_weight_percent_strict(atomic))

    def test_invalid_balances_remain_unknown(self):
        cases = [
            (alloy(("Fe", "balance")), {"Fe": None}),
            (alloy(("Fe", "balance"), ("Cr", "balance"), ("Ni", amount(20, "wt%"))),
             {"Fe": None, "Cr": None, "Ni": 20}),
            (alloy(("Fe", "balance"), ("Cr", amount(60, "wt%")), ("Ni", amount(50, "wt%"))),
             {"Fe": None, "Cr": 60, "Ni": 50}),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(to_weight_percent(source), expected)

    def test_invalid_elements_values_and_duplicates_do_not_discard_other_elements(self):
        source = alloy(("Fe", amount(70, "wt%")), ("Fe", amount(5, "wt%")),
                       ("Cr", amount(20, "wt%")), ("Ni", amount(-1, "wt%")),
                       ("Unknown", amount(1, "wt%")), ("Co", amount(101, "wt%")))
        self.assertEqual(to_weight_percent(source),
                         {"Fe": None, "Cr": 20, "Ni": None, "Unknown": None, "Co": None})

    def test_empty_alloy_returns_empty_dictionary(self):
        self.assertEqual(to_weight_percent(alloy()), {})

    def test_input_and_strict_behavior_are_unchanged(self):
        source = alloy(("Fe", None), ("Cr", amount(20, "wt%", min=19, max=21, plus_minus=1)))
        original = source.model_dump()
        result = to_weight_percent(source)
        result["Cr"] = 0
        self.assertEqual(source.model_dump(), original)
        with self.assertRaises(InvalidAlloyCompositionError) as caught:
            to_weight_percent_strict(source)
        self.assertIs(caught.exception.reason, AlloyCompositionErrorReason.MISSING_AMOUNT)


if __name__ == "__main__":
    unittest.main()
