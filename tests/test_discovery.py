import tempfile
import unittest
from pathlib import Path

from corrosion_plot_digitizer.discovery import classify_caption, discover_figures


class DiscoveryTests(unittest.TestCase):
    def test_explicit_pitting_caption_is_relevant(self) -> None:
        relevant, _, review = classify_caption(
            "Fig. 1. Pitting potentials for fresh and aged AlNb alloys."
        )
        self.assertTrue(relevant)
        self.assertTrue(review)

    def test_current_density_caption_is_not_relevant(self) -> None:
        relevant, _, review = classify_caption(
            "Fig. 6. Anodic pit current density as a function of growth potential."
        )
        self.assertFalse(relevant)
        self.assertFalse(review)

    def test_discovers_mineru_style_image_and_caption(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            images = root / "images"
            images.mkdir()
            (images / "figure.jpg").write_bytes(b"not-used")
            markdown = root / "paper.md"
            markdown.write_text(
                "![](images/figure.jpg)  \nFig. 1. Pitting potential vs. Nb concentration.\n",
                encoding="utf-8",
            )
            figures = discover_figures(markdown, "80")
            self.assertEqual(len(figures), 1)
            self.assertEqual(figures[0].figure_id, "1")
            self.assertTrue(figures[0].relevant)


if __name__ == "__main__":
    unittest.main()
