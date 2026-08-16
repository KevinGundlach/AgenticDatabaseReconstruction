import unittest

from corrosion_plot_digitizer.chemistry import (
    ConversionError,
    atomic_percent_to_weight_percent,
    binary_atomic_percent_to_weight_percent,
    potential_to_mv_sce,
)


class ChemistryTests(unittest.TestCase):
    def test_binary_al_nb_conversion(self) -> None:
        result = binary_atomic_percent_to_weight_percent("Al", "Nb", 5.0)
        self.assertAlmostEqual(sum(result.values()), 100.0, places=10)
        self.assertAlmostEqual(result["Nb"], 15.3423, places=4)
        self.assertAlmostEqual(result["Al"], 84.6577, places=4)

    def test_multi_element_conversion_accepts_fractional_input(self) -> None:
        result = atomic_percent_to_weight_percent({"Fe": 0.7, "Cr": 0.2, "Ni": 0.1})
        self.assertAlmostEqual(sum(result.values()), 100.0, places=10)
        self.assertGreater(result["Fe"], result["Cr"])

    def test_invalid_atomic_percentage_is_rejected(self) -> None:
        with self.assertRaises(ConversionError):
            binary_atomic_percent_to_weight_percent("Al", "Nb", 101)

    def test_she_to_sce_conversion(self) -> None:
        self.assertAlmostEqual(
            potential_to_mv_sce(1.0, unit="V", reference="SHE"), 759.0
        )

    def test_sce_identity_conversion(self) -> None:
        self.assertAlmostEqual(
            potential_to_mv_sce(-500, unit="mV", reference="SCE"), -500.0
        )


if __name__ == "__main__":
    unittest.main()
