"""Run: python -B -m unittest discover -s tests -p test_benchmark_plots.py -v"""

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace as Object
import unittest
from unittest.mock import patch

from matplotlib.figure import Figure
from PIL import Image

from reporting.benchmark_plots import plot_gap_count_bars, plot_gap_histogram, plot_gaps_by_field


def inputs():
    return Object(pdf=Object(filename="paper.pdf", sha256="a" * 64),
                  registry=Object(filename="registry.json", sha256="b" * 64))


def observation(identifier, rows=(), candidates=()):
    return Object(observation_id=identifier,
                  matches=[Object(citrine_no=no) for no in rows],
                  candidates=[Object(citrine_no=no) for no in candidates])


def corpus():
    # The same observation ID in two papers denotes different observations.
    a, b, c = [Object(observation_id=oid) for oid in ("obs_001", "obs_007", "obs_001")]
    enriched = [Object(reference_number=1, inputs=inputs(), experiments=[a, b]),
                Object(reference_number=2, inputs=inputs(), experiments=[c])]
    aligned = [Object(reference_number=1, inputs=inputs(), observations=[
        observation("obs_001", [10]),
        observation("obs_002", [12, 13]),
        observation("obs_003", [12]),  # Shared with a multi-row observation.
        observation("obs_004", [14]),
        observation("obs_005", [14]),  # Two singly linked observations share 14.
        observation("obs_006", candidates=[10]),  # Candidate-only is not assigned.
        observation("obs_007", [15], candidates=[10]),
    ]), Object(reference_number=2, inputs=inputs(), observations=[observation("obs_001", [11])])]
    # Deliberately out of ID/CSV order: joins must use No., not list position.
    rows = [{"No.": 15, "Reference": 1, "gaps": 4},
            {"No.": 11, "Reference": 2, "gaps": 6},
            {"No.": 10, "Reference": 1, "gaps": 3}]
    return enriched, aligned, rows


class BenchmarkPlotTests(unittest.TestCase):
    def setUp(self):
        self.enriched, self.aligned, self.rows = corpus()
        temporary_root = Path(__file__).resolve().parents[1] / "tmp"
        temporary_root.mkdir(exist_ok=True)
        self.temp = TemporaryDirectory(dir=temporary_root)
        self.addCleanup(self.temp.cleanup)
        self.destination = Path(self.temp.name) / "nested" / "histogram.png"
        for name, value in (("load_enriched_observations", self.enriched),
                            ("load_aligned_observations", self.aligned),
                            ("load_cra_records", self.rows)):
            patcher = patch(f"reporting.benchmark_plots.{name}", return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch("reporting.benchmark_plots.count_gaps", side_effect=lambda exp, row, **kw: row["gaps"])
        self.score = patcher.start()
        self.addCleanup(patcher.stop)

    def test_one_to_one_filter_and_real_ten_bin_image(self):
        captured = {}
        save = Figure.savefig

        def inspect_and_save(figure, destination, **kwargs):
            axes = figure.axes[0]
            captured.update(bars=len(axes.patches), total=sum(bar.get_height() for bar in axes.patches),
                            xlabel=axes.get_xlabel(), ylabel=axes.get_ylabel())
            save(figure, destination, **kwargs)

        with patch.object(Figure, "savefig", new=inspect_and_save):
            values = plot_gap_histogram(self.destination, assume_percent_is_weight=True)
        self.assertEqual(values, [3, 4, 6])
        self.assertEqual(captured, {"bars": 10, "total": 3, "xlabel": "Number of gaps",
                                    "ylabel": "Number of experiments"})
        self.assertEqual(self.score.call_count, 3)
        self.assertIs(self.score.call_args_list[0].args[0], self.enriched[0].experiments[0])
        self.assertIs(self.score.call_args_list[2].args[0], self.enriched[1].experiments[0])
        self.assertTrue(all(call.kwargs == {"assume_percent_is_weight": True}
                            for call in self.score.call_args_list))
        with Image.open(self.destination) as image:
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.size, (1600, 1000))

    def test_empty_selection_fails_without_creating_an_image(self):
        for document in self.aligned:
            document.observations = []
        with self.assertRaisesRegex(ValueError, "No experiments"):
            plot_gap_histogram(self.destination)
        self.assertFalse(self.destination.exists())
        self.score.assert_not_called()

    def test_integer_bars_count_repeats_and_include_unobserved_gap_counts(self):
        for row in self.rows:
            row["gaps"] = {10: 0, 15: 2, 11: 2}[row["No."]]
        captured = {}
        save = Figure.savefig

        def inspect_and_save(figure, destination, **kwargs):
            axes = figure.axes[0]
            captured.update(centres=[bar.get_x() + bar.get_width() / 2 for bar in axes.patches],
                            heights=[bar.get_height() for bar in axes.patches],
                            ticks=list(axes.get_xticks()), xlabel=axes.get_xlabel(),
                            ylabel=axes.get_ylabel())
            save(figure, destination, **kwargs)

        with patch.object(Figure, "savefig", new=inspect_and_save):
            counts = plot_gap_count_bars(self.destination, tolerances={"ph": 0.1})
        self.assertEqual(counts, {0: 1, 1: 0, 2: 2})
        self.assertEqual(captured, {"centres": [0, 1, 2], "heights": [1, 0, 2],
                                    "ticks": [0, 1, 2], "xlabel": "Number of gaps",
                                    "ylabel": "Number of experiments"})
        self.assertEqual(self.score.call_count, 3)
        self.assertIs(self.score.call_args_list[0].args[0], self.enriched[0].experiments[0])
        self.assertIs(self.score.call_args_list[2].args[0], self.enriched[1].experiments[0])
        self.assertTrue(all(call.kwargs == {"tolerances": {"ph": 0.1}}
                            for call in self.score.call_args_list))
        with Image.open(self.destination) as image:
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.size, (1600, 1000))

    def test_integer_bars_handle_zero_only_and_maximum_above_fourteen(self):
        for row in self.rows:
            row["gaps"] = 0
        self.assertEqual(plot_gap_count_bars(self.destination), {0: 3})
        self.rows[0]["gaps"] = 16
        counts = plot_gap_count_bars(self.destination)
        self.assertEqual(list(counts), list(range(17)))
        self.assertEqual(counts[0], 2)
        self.assertEqual(counts[16], 1)
        self.assertEqual(sum(counts.values()), 3)

    def test_stale_input_fingerprints_are_rejected(self):
        for kind in ("pdf", "registry"):
            with self.subTest(kind=kind):
                old = deepcopy(self.enriched[0].inputs)
                getattr(self.enriched[0].inputs, kind).sha256 = "c" * 64
                with self.assertRaisesRegex(ValueError, "inputs differ"):
                    plot_gap_histogram(self.destination)
                self.enriched[0].inputs = old
        self.assertFalse(self.destination.exists())

    def test_missing_enrichment_is_not_silently_dropped(self):
        self.enriched[0].experiments = []
        with self.assertRaisesRegex(ValueError, "Missing enriched experiment"):
            plot_gap_histogram(self.destination)

    def test_missing_wrong_paper_and_duplicate_cra_rows_are_rejected(self):
        original = deepcopy(self.rows)
        self.rows.pop()
        with self.assertRaisesRegex(ValueError, "absent from"):
            plot_gap_histogram(self.destination)
        self.rows[:] = deepcopy(original)
        self.rows[-1]["Reference"] = 2
        with self.assertRaisesRegex(ValueError, "different paper"):
            plot_gap_histogram(self.destination)
        self.rows[:] = original + [deepcopy(original[0])]
        with self.assertRaisesRegex(ValueError, "must be unique"):
            plot_gap_histogram(self.destination)
        self.assertFalse(self.destination.exists())

    def test_field_totals_use_the_same_cohort_and_horizontal_axes(self):
        gaps = {10: {"ph": "missing", "alloy.Cr": "mismatch"},
                15: {"ph": "mismatch", "test_solution.NaCl": "conversion"},
                11: {"alloy.Cr": "missing"}}
        captured = {}
        save = Figure.savefig

        def inspect_and_save(figure, destination, **kwargs):
            axes = figure.axes[0]
            captured.update(labels=[tick.get_text() for tick in axes.get_yticklabels()],
                            widths=[bar.get_width() for bar in axes.patches],
                            xlabel=axes.get_xlabel(), ylabel=axes.get_ylabel(),
                            highest_first=axes.yaxis_inverted())
            save(figure, destination, **kwargs)

        with patch("reporting.benchmark_plots.benchmark_experiment", side_effect=lambda exp, row, **kw:
                   Object(gaps=gaps[row["No."]], skipped={"alloy.Ni": "unscored"})) as score:
            with patch.object(Figure, "savefig", new=inspect_and_save):
                counts = plot_gaps_by_field(self.destination, tolerances={"ph": 0.1})
        self.assertEqual(list(counts.items()), [("alloy.Cr", 2), ("ph", 2), ("test_solution.NaCl", 1)])
        self.assertEqual(captured, {"labels": list(counts), "widths": [2, 2, 1],
                                    "xlabel": "Number of gaps", "ylabel": "Field", "highest_first": True})
        self.assertEqual(score.call_count, 3)
        self.assertIs(score.call_args_list[0].args[0], self.enriched[0].experiments[0])
        self.assertIs(score.call_args_list[2].args[0], self.enriched[1].experiments[0])
        self.assertTrue(all(call.kwargs == {"tolerances": {"ph": 0.1}} for call in score.call_args_list))
        self.assertNotIn("alloy.Ni", counts)
        self.score.assert_not_called()
        with Image.open(self.destination) as image:
            self.assertEqual(image.format, "PNG")

    def test_zero_total_gaps_still_saves_a_chart(self):
        with patch("reporting.benchmark_plots.benchmark_experiment", return_value=Object(gaps={})):
            self.assertEqual(plot_gaps_by_field(self.destination), {})
        self.assertTrue(self.destination.exists())

    def test_reference_fields_with_zero_gaps_remain_visible(self):
        for row in self.rows:
            row.update({"Cr": "18", "pH": "7", "Test Solution": "0.5M NaCl"})
        with patch("reporting.benchmark_plots.benchmark_experiment", return_value=Object(gaps={})):
            counts = plot_gaps_by_field(self.destination)
        self.assertEqual(counts, {"alloy.Cr": 0, "ph": 0, "test_solution.NaCl": 0})
        self.assertTrue(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
