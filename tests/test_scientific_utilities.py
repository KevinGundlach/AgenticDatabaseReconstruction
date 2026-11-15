"""Focused, synthetic tests; no database, corpus rewriting, or network access.

Run: python -B -m unittest discover -s tests -p test_scientific_utilities.py -v
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from models.observation_enrichment import ObservationEnrichment
from utils.derived_columns_codex import (
    calculate_balance, calculate_chloride, calculate_ph, fill_missing_values,
)
from utils.unit_conversions_codex import (
    ATOMIC_WEIGHTS, ConversionError, collect_units, convert_alloy_composition,
    convert_concentration, convert_measurement, convert_potential, molar_mass,
    normalize_units,
)


def measurement(value, unit, **extras):
    return {"value": value, "unit": unit, **extras}


def solution(*components, **extras):
    return {
        "preparation": "", "solvent": "water",
        "composition": [{"solute": name, "amount": amount} for name, amount in components],
        "ph": None, "chloride_concentration": None, **extras,
    }


def document():
    return {
        "schema_version": "1.0", "paper_name": "invented.pdf", "reference_number": 1,
        "inputs": {name: {"filename": f"invented.{suffix}", "sha256": "0" * 64}
                   for name, suffix in (("pdf", "pdf"), ("registry", "json"))},
        "experiments": [{
            "observation_id": "obs_017",
            "alloy": {"preparation": "", "composition": [
                {"element_symbol": "Fe", "amount": "balance"},
                {"element_symbol": "Cr", "amount": measurement(20, "wt.%")},
            ], "microstructure": "", "material_class": "Fe Alloy"},
            "test_temperature": measurement(298.15, "K"),
            "test_solution": solution(("NaCl", measurement(0.1, "M"))),
            "test_method": {"test_types": ["potentiodynamic polarization"],
                            "procedure_description": "", "scan_rate": measurement(60, "mV/min"),
                            "potential_step": None, "step_hold_duration": None, "pitting_criterion": ""},
            "pitting_potential": measurement(0.3, "V (SCE)", plus_minus=0.02),
            "result_note": "A source qualification.", "failure_notes": "",
        }],
    }


def ideal_context(**extra):
    # Explicit test fixture, not a default scientific calibration.
    return {"source": "Synthetic complete ideal aqueous recipe at 25 °C",
            "ideal_solution": True, "recipe_complete": True,
            "kw": {"value": 1e-14, "temperature_c": 25, "source": "Synthetic test ion product"}, **extra}


class UnitConversionTests(unittest.TestCase):
    def test_temperature_affine_bounds_and_uncertainty(self):
        original = measurement(298.15, "K", min=288.15, max=308.15, plus_minus=2)
        converted = convert_measurement(original, "temperature")
        for key, expected in {"value": 25, "min": 15, "max": 35, "plus_minus": 2}.items():
            self.assertAlmostEqual(converted[key], expected)
        fahrenheit = convert_measurement(measurement(68, "°F", plus_minus=9), "temperature")
        self.assertAlmostEqual(fahrenheit["value"], 20)
        self.assertAlmostEqual(fahrenheit["plus_minus"], 5)
        self.assertEqual(original["unit"], "K")

    def test_potential_scaling_preserves_optional_field_presence(self):
        for unit in ("V (SCE)", "v vs. SCE", "VOLT VERSUS SCE", "Volts (S.C.E.)"):
            with self.subTest(unit=unit):
                converted = convert_potential({"max": 1.2, "unit": unit})
                self.assertEqual(converted, {"max": 1200, "unit": "mV (SCE)"})
        self.assertEqual(convert_potential(measurement(200, "mV (SCE, saturated KCl)"))["value"], 200)

    def test_reference_offset_affects_bounds_not_uncertainty(self):
        context = {"reference_conversion": {"from": "SHE", "to": "SCE", "offset_mv": -240,
                                           "temperature_c": 25, "source": "Synthetic calibration"}}
        converted = convert_potential(measurement(0.5, "V (SHE)", min=0.4, max=0.6, plus_minus=0.02), context=context)
        self.assertEqual(converted, measurement(260, "mV (SCE)", min=160, max=360, plus_minus=20))
        with self.assertRaisesRegex(ConversionError, "temperatures disagree"):
            convert_potential(measurement(0.5, "V (SHE)"), context={**context, "temperature_c": 60})
        with self.assertRaises(ConversionError):
            convert_potential(measurement(0.5, "V (NHE)"), context=context)

    def test_hydrogen_scale_aliases_keep_reference_identity(self):
        context = {"reference_conversion": {"from": "NHE", "to": "SCE", "offset_mv": -240,
                                           "temperature_c": 25, "source": "Synthetic calibration"}}
        result = convert_potential(measurement(0.5, "V_H (Normalwasserstoff-Skala)"), context=context)
        self.assertEqual(result["value"], 260)
        # An unqualified hydrogen scale is not silently assumed to be SHE/NHE.
        with self.assertRaises(ConversionError):
            convert_potential(measurement(500, "mV_H"), context=context)
        result = convert_potential(measurement(500, "mV_H"), context={
            **context, "potential_reference": "NHE", "source": "Synthetic paper clarifies H scale"})
        self.assertEqual(result["value"], 260)

    def test_missing_reference_and_filling_solution_require_context(self):
        for unit in ("V", "mV (Ag/AgCl)", "mV (Ag/AgCl, saturated)", "V (SHE)", "V (SHE(T))"):
            with self.subTest(unit=unit), self.assertRaises(ConversionError):
                convert_potential(measurement(0.5, unit))
        context = {"potential_reference": "Ag/AgCl, 3.5 M KCl", "source": "Explicit caller assumption",
                   "reference_conversion": {"from": "Ag/AgCl, 3.5 M KCl", "to": "SCE", "offset_mv": -30,
                                            "temperature_c": 25, "source": "Synthetic calibration"}}
        self.assertEqual(convert_potential(measurement(100, "mV (Ag/AgCl)"), context=context)["value"], 70)
        with self.assertRaisesRegex(ConversionError, "conflicts"):
            convert_potential(measurement(100, "mV (SCE)"), context=context)

    def test_scan_rate_aliases_and_denominators(self):
        for unit, value, expected in [
            ("mV/min", 60, 1), ("mV/hr", 3600, 1), ("V·h⁻¹", 3.6, 1),
            ("V/50 min", 3, 1), ("mV/30 sec", 30, 1), ("mV/sec", 1, 1),
        ]:
            with self.subTest(unit=unit):
                self.assertAlmostEqual(convert_measurement(measurement(value, unit), "scan_rate")["value"], expected)
        for unit in ("mV", "steady state", "20mV steps by manual increment", "V/0 s"):
            with self.subTest(unit=unit), self.assertRaises(ConversionError):
                convert_measurement(measurement(20, unit), "scan_rate")
        self.assertEqual(convert_measurement(measurement(0.02, "V"), "voltage")["value"], 20)
        self.assertEqual(convert_measurement(measurement(2, "minute"), "duration")["value"], 120)

    def test_concentration_molar_aliases_and_bounds(self):
        for unit in ("M", "mol/l", "mol dm^-3", "mol dm⁻³", "mol/L"):
            with self.subTest(unit=unit):
                self.assertEqual(convert_concentration({"min": 0.1, "unit": unit}), {"min": 0.1, "unit": "mol/L"})
        self.assertEqual(convert_concentration(measurement(100, "mM"))["value"], 0.1)
        self.assertAlmostEqual(convert_concentration(measurement(10, "μM"))["value"], 1e-5)

    def test_mass_concentration_uses_the_actual_species(self):
        self.assertAlmostEqual(convert_concentration(measurement(35.45, "g/L"), molar_mass_g_per_mol=ATOMIC_WEIGHTS["Cl"])["value"], 1)
        sodium_chloride = convert_concentration(measurement(molar_mass("NaCl") * 1000, "mg/l"), molar_mass_g_per_mol=molar_mass("NaCl"))
        self.assertAlmostEqual(sodium_chloride["value"], 1)
        self.assertGreater(molar_mass("MgCl2·6H2O"), molar_mass("MgCl2"))

    def test_mass_percent_ppm_molality_and_normality_need_basis(self):
        for unit in ("%", "wt%", "ppm", "m", "N", "M (NaCl activity, as printed on lower axis)"):
            with self.subTest(unit=unit), self.assertRaises(ConversionError):
                convert_concentration(measurement(1, unit), molar_mass_g_per_mol=50)
        context = {"source": "Synthetic conversion assumptions", "ppm_basis": "mass", "density_kg_per_litre": 1.2,
                   "solvent_kg_per_litre": 0.9, "normality_equivalents_per_mole": 2,
                   "solution_percent_basis": "mass_per_volume"}
        self.assertAlmostEqual(convert_concentration(measurement(1000, "ppm"), molar_mass_g_per_mol=50, context=context)["value"], 0.024)
        self.assertAlmostEqual(convert_concentration(measurement(1, "wt%"), molar_mass_g_per_mol=50, context=context)["value"], 0.24)
        self.assertAlmostEqual(convert_concentration(measurement(1, "%"), molar_mass_g_per_mol=50, context=context)["value"], 0.2)
        self.assertEqual(convert_concentration(measurement(1, "m"), context=context)["value"], 0.9)
        self.assertEqual(convert_concentration(measurement(1, "N"), context=context)["value"], 0.5)
        with self.assertRaises(ConversionError):
            convert_concentration(measurement(1, "m"), context={"solvent_kg_per_litre": 1})

    def test_atomic_to_mass_uses_full_composition_and_atomic_weights(self):
        composition = [{"element_symbol": "Fe", "amount": measurement(50, "at.%", plus_minus=1)},
                       {"element_symbol": "Cr", "amount": measurement(50, "at%")}]
        converted, limitations = convert_alloy_composition(composition)
        expected = 100 * ATOMIC_WEIGHTS["Fe"] / (ATOMIC_WEIGHTS["Fe"] + ATOMIC_WEIGHTS["Cr"])
        self.assertAlmostEqual(converted[0]["amount"]["value"], expected)
        self.assertAlmostEqual(sum(c["amount"]["value"] for c in converted), 100)
        self.assertTrue(any("not propagated" in note for note in limitations))
        self.assertNotIn("plus_minus", converted[0]["amount"])
        self.assertIn("plus_minus", composition[0]["amount"])
        with self.assertRaises(ConversionError):
            convert_alloy_composition(composition[:1])

    def test_atomic_ratios_require_explicit_completeness(self):
        composition = [{"element_symbol": "Al", "amount": measurement(0.3, "nominal atomic-ratio coefficient")},
                       {"element_symbol": "Fe", "amount": measurement(1, "nominal atomic-ratio coefficient")}]
        with self.assertRaises(ConversionError):
            convert_alloy_composition(composition)
        converted, _ = convert_alloy_composition(composition, context={"composition_complete": True, "source": "Synthetic complete formula"})
        self.assertAlmostEqual(sum(c["amount"]["value"] for c in converted), 100)

    def test_incomplete_or_incompatible_compositions_are_not_renormalized(self):
        cases = [
            [{"element_symbol": "Fe", "amount": measurement(50, "at%")}, {"element_symbol": "Cr", "amount": None}],
            [{"element_symbol": "Fe", "amount": measurement(50, "at%")}, {"element_symbol": "Cr", "amount": "balance"}],
            [{"element_symbol": "Fe", "amount": measurement(50, "at%")}, {"element_symbol": "Cr", "amount": measurement(50, "wt%")}],
            [{"element_symbol": "Fe", "amount": measurement(50, "at%")}, {"element_symbol": "Fe", "amount": measurement(50, "at%")}],
            [{"element_symbol": "Fe", "amount": {"min": 50, "unit": "at%"}}],
            [{"element_symbol": "Fe", "amount": measurement(101, "wt%")}],
        ]
        for composition in cases:
            original = deepcopy(composition)
            with self.subTest(composition=composition), self.assertRaises(ConversionError):
                convert_alloy_composition(composition)
            self.assertEqual(composition, original)

    def test_ambiguous_percent_and_alloy_ppm(self):
        composition = [{"element_symbol": "Fe", "amount": measurement(99.9, "%")},
                       {"element_symbol": "C", "amount": measurement(1000, "ppm")}]
        with self.assertRaises(ConversionError):
            convert_alloy_composition(composition)
        converted, _ = convert_alloy_composition(composition, context={"source": "Synthetic mass basis", "alloy_basis": "wt%", "ppm_basis": "mass"})
        self.assertEqual(converted[1]["amount"]["value"], 0.1)

    def test_invalid_measurements_fail_explicitly(self):
        for invalid in (measurement(float("nan"), "M"), measurement(float("inf"), "M"),
                        measurement(True, "M"), {"min": 2, "max": 1, "unit": "M"},
                        {"plus_minus": 1, "unit": "M"}, measurement(-1, "M"),
                        measurement(1, "M", surprise="ignored?")):
            with self.subTest(invalid=invalid), self.assertRaises(ConversionError):
                convert_concentration(invalid)
        with self.assertRaises(ConversionError):
            convert_measurement(measurement(-1, "K"), "temperature")


class DerivedValueTests(unittest.TestCase):
    def test_explicit_balance_and_uncertainty_diagnostic(self):
        composition = document()["experiments"][0]["alloy"]["composition"]
        composition[1]["amount"]["plus_minus"] = 1
        converted, limitations = calculate_balance(composition)
        self.assertEqual(converted[0]["amount"], measurement(80, "wt%"))
        self.assertEqual(composition[0]["amount"], "balance")
        self.assertTrue(limitations)

    def test_balance_refuses_missing_mixed_or_impossible_amounts(self):
        base = document()["experiments"][0]["alloy"]["composition"]
        cases = [[], base[1:], base + [{"element_symbol": "Ni", "amount": "balance"}],
                 base + [{"element_symbol": "Ni", "amount": None}],
                 base + [{"element_symbol": "Ni", "amount": measurement(1, "at%")}],
                 [base[0], {"element_symbol": "Cr", "amount": {"min": 10, "max": 20, "unit": "wt%"}}],
                 [base[0], {"element_symbol": "Cr", "amount": measurement(110, "wt%")}]]
        for composition in cases:
            with self.subTest(composition=composition), self.assertRaises(ConversionError):
                calculate_balance(composition)

    def test_atomic_balance_is_filled_before_mass_conversion(self):
        data = document()
        data["experiments"][0]["alloy"]["composition"][1]["amount"]["unit"] = "at%"
        filled, _ = fill_missing_values(data)
        self.assertEqual(filled["experiments"][0]["alloy"]["composition"][0]["amount"], measurement(80, "at%"))
        normalized, _ = normalize_units(filled)
        composition = normalized["experiments"][0]["alloy"]["composition"]
        self.assertTrue(all(c["amount"]["unit"] == "wt%" for c in composition))
        self.assertAlmostEqual(sum(c["amount"]["value"] for c in composition), 100)

    def test_chloride_sums_multiple_salts_with_stoichiometry(self):
        recipe = solution(("NaCl", measurement(0.1, "M")), ("MgCl2", measurement(0.05, "M")),
                          ("HCl", measurement(0.01, "M")), ("NaClO4", measurement(1, "M")))
        converted, notes = calculate_chloride(recipe)
        self.assertAlmostEqual(converted["value"], 0.21)
        self.assertEqual(converted["unit"], "mol/L")
        self.assertTrue(any("activity" in note for note in notes))

    def test_chloride_mass_donor_and_hydrate(self):
        for formula in ("NaCl", "MgCl2·6H2O"):
            with self.subTest(formula=formula):
                converted, _ = calculate_chloride(solution((formula, measurement(molar_mass(formula), "g/L"))))
                self.assertAlmostEqual(converted["value"], 1 if formula == "NaCl" else 2)

    def test_salt_and_ion_representations_are_not_double_counted(self):
        recipe = solution(("NaCl", measurement(0.1, "M")), ("Cl−", measurement(0.1, "M")))
        with self.assertRaises(ConversionError):
            calculate_chloride(recipe)
        for choice in ("ion", "salts"):
            converted, _ = calculate_chloride(recipe, context={"chloride_representation": choice, "source": "Same solution, two descriptions"})
            self.assertEqual(converted["value"], 0.1)

    def test_chloride_unsupported_unknown_and_bounds_only(self):
        for recipe in (solution(), solution(("seawater", None)), solution(("NaClO4", measurement(1, "M"))),
                       solution(("NaCl", None)), solution(("NaCl", {"min": 0.1, "unit": "M"})),
                       solution(("NaCl", measurement(1, "M")), ("unknown additive", None)),
                       solution(("NaCl (activity, not concentration)", measurement(1, "M")))):
            with self.subTest(recipe=recipe), self.assertRaises(ConversionError):
                calculate_chloride(recipe)

    def test_chloride_uncertainty_is_flagged(self):
        converted, notes = calculate_chloride(solution(("NaCl", measurement(1, "M", plus_minus=0.1))))
        self.assertNotIn("plus_minus", converted)
        self.assertTrue(any("not propagated" in note for note in notes))

    def test_simple_ideal_strong_acid_base_and_neutralization(self):
        cases = [(solution(("HCl", measurement(0.01, "M"))), 2),
                 (solution(("NaOH", measurement(0.01, "M"))), 12),
                 (solution(("HCl", measurement(0.01, "M")), ("NaOH", measurement(0.01, "M"))), 7)]
        for recipe, expected in cases:
            with self.subTest(expected=expected):
                value, notes = calculate_ph(recipe, temperature_c=25, context=ideal_context())
                self.assertAlmostEqual(value, expected, places=7)
                self.assertTrue(any("ideal" in note for note in notes))

    def test_dilute_acid_includes_water_autoionization(self):
        value, _ = calculate_ph(solution(("HCl", measurement(1e-9, "M"))), temperature_c=25, context=ideal_context())
        self.assertLess(value, 7)
        self.assertGreater(value, 6.99)

    def test_ph_requires_complete_ideal_aqueous_temperature_context(self):
        recipe = solution(("HCl", measurement(0.01, "M")))
        for context in ({}, {"ideal_solution": True}, ideal_context(recipe_complete=False),
                        ideal_context(kw={"value": 1e-14, "temperature_c": 30, "source": "Test"}),
                        ideal_context(kw={"value": 0, "temperature_c": 25, "source": "Test"})):
            with self.subTest(context=context), self.assertRaises(ConversionError):
                calculate_ph(recipe, temperature_c=25, context=context)
        with self.assertRaises(ConversionError):
            calculate_ph(recipe, context=ideal_context())
        with self.assertRaises(ConversionError):
            calculate_ph({**recipe, "solvent": ""}, temperature_c=25, context=ideal_context())

    def test_ph_refuses_unsupported_chemistry_or_unquantified_adjustment(self):
        for solute, amount in (("H2SO4", measurement(1, "M")), ("NaHCO3", measurement(1, "M")),
                               ("MgCl2", measurement(1, "M")), ("NaOH (pH adjustment)", None),
                               ("HCl", {"max": 0.01, "unit": "M"})):
            with self.subTest(solute=solute), self.assertRaises(ConversionError):
                calculate_ph(solution((solute, amount)), temperature_c=25, context=ideal_context())


class BulkUtilityTests(unittest.TestCase):
    def test_inventory_records_raw_missing_blank_and_null_units(self):
        data = document()
        data["experiments"][0]["test_method"]["potential_step"] = {"value": 20}
        data["experiments"][0]["test_solution"]["ph"] = {"value": 7, "unit": ""}
        original = deepcopy(data)
        inventory = collect_units([data, deepcopy(data)])
        self.assertEqual(data, original)
        lookup = {(r["field"], r["unit"], r["kind"]): r for r in inventory}
        rate = lookup[("experiments[].test_method.scan_rate", "mV/min", "measurement")]
        self.assertEqual(rate["count"], 2)
        self.assertEqual(rate["examples"][0]["observation_id"], "obs_017")
        self.assertIn(("experiments[].test_method.potential_step", None, "measurement"), lookup)
        self.assertIn(("experiments[].test_method.step_hold_duration", None, "missing"), lookup)
        self.assertIn(("experiments[].test_solution.ph", "", "measurement"), lookup)

    def test_combined_processing_keeps_inputs_notes_and_schema_valid(self):
        data = document()
        original = deepcopy(data)
        filled, calculations = fill_missing_values(data, ideal_context())
        normalized, conversions = normalize_units(filled)
        row = normalized["experiments"][0]
        self.assertEqual(data, original)
        self.assertEqual(row["observation_id"], "obs_017")
        self.assertEqual(row["pitting_potential"], measurement(300, "mV (SCE)", plus_minus=20))
        self.assertAlmostEqual(row["test_solution"]["ph"], 7)
        self.assertEqual(row["test_solution"]["chloride_concentration"], measurement(0.1, "mol/L"))
        self.assertEqual(row["result_note"], original["experiments"][0]["result_note"])
        self.assertEqual(row["alloy"]["composition"][0]["amount"], measurement(80, "wt%"))
        ObservationEnrichment.model_validate(normalized)
        ph_calculation = next(d for d in calculations if d["field"] == "test_solution.ph")
        self.assertIsNone(ph_calculation["calculation_inputs"]["solution"]["ph"])
        self.assertTrue(all(d["status"] == "calculated" for d in calculations))
        self.assertTrue(all(d["status"] == "converted" for d in conversions))
        json.dumps(calculations + conversions, allow_nan=False)

    def test_existing_reported_values_always_win(self):
        data = document()
        row = data["experiments"][0]
        row["test_solution"]["ph"] = 3.5
        row["test_solution"]["chloride_concentration"] = {"max": 1, "unit": "unconvertible"}
        filled, diagnostics = fill_missing_values(data, ideal_context())
        self.assertEqual(filled["experiments"][0]["test_solution"], row["test_solution"])
        self.assertFalse(any(d["field"].startswith("test_solution") for d in diagnostics))

    def test_unsupported_conversions_remain_original_with_reasons(self):
        data = document()
        data["experiments"][0]["pitting_potential"]["unit"] = "V (Ag/AgCl)"
        converted, diagnostics = normalize_units(data)
        self.assertEqual(converted["experiments"][0]["pitting_potential"], data["experiments"][0]["pitting_potential"])
        issue = next(d for d in diagnostics if d["field"] == "pitting_potential")
        self.assertEqual(issue["status"], "unavailable")
        self.assertTrue(issue["reason"])

    def test_activity_is_not_relabelled_as_a_molar_concentration(self):
        data = document()
        component = data["experiments"][0]["test_solution"]["composition"][0]
        component["solute"] = "NaCl (activity, not concentration)"
        result, diagnostics = normalize_units(data)
        self.assertEqual(result["experiments"][0]["test_solution"]["composition"][0], component)
        self.assertTrue(any("activity" in d["reason"] for d in diagnostics))

    def test_calculation_diagnostics_retain_original_uncertainty(self):
        data = document()
        data["experiments"][0]["test_solution"]["composition"][0]["amount"]["plus_minus"] = 0.02
        _, diagnostics = fill_missing_values(data)
        item = next(d for d in diagnostics if d["field"] == "test_solution.chloride_concentration")
        self.assertEqual(item["calculation_inputs"][0]["amount"]["plus_minus"], 0.02)
        self.assertTrue(any("not propagated" in note for note in item["limitations"]))

    def test_per_observation_assumptions_do_not_leak(self):
        data = document()
        row = data["experiments"][0]
        row["alloy"]["composition"][1]["amount"]["unit"] = "%"
        second = deepcopy(row)
        second["observation_id"] = "obs_102"
        data["experiments"].append(second)
        context = {"by_observation": {"obs_017": {"source": "Synthetic paper basis", "alloy_basis": "wt%"}}}
        filled, diagnostics = fill_missing_values(data, context)
        self.assertEqual(filled["experiments"][0]["alloy"]["composition"][0]["amount"]["value"], 80)
        self.assertEqual(filled["experiments"][1]["alloy"]["composition"][0]["amount"], "balance")
        self.assertTrue(any(d["observation_id"] == "obs_102" and d["status"] == "unavailable" for d in diagnostics))

    def test_results_and_diagnostics_are_detached_from_inputs(self):
        data = document()
        context = {"source": "Test", "alloy_basis": "wt%"}
        original_context = deepcopy(context)
        converted, diagnostics = normalize_units(data, context)
        diagnostics[0]["context"]["source"] = "changed"
        converted["experiments"][0]["result_note"] = "changed"
        self.assertEqual(context, original_context)
        self.assertEqual(data, document())

    def test_empty_document(self):
        data = document()
        data["experiments"] = []
        self.assertEqual(collect_units(data), [])
        self.assertEqual(fill_missing_values(data), (data, []))
        self.assertEqual(normalize_units(data), (data, []))

    def test_reading_then_processing_does_not_change_source_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.json"
            path.write_text(json.dumps(document()), encoding="utf-8")
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            data = json.loads(path.read_text(encoding="utf-8"))
            filled, _ = fill_missing_values(data)
            normalize_units(filled)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)


if __name__ == "__main__":
    unittest.main()
