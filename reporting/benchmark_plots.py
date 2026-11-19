"""Plots of the current saved benchmark data; run from the project directory."""

from collections import Counter
from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from benchmark import CRA_ELEMENTS, benchmark_experiment, count_gaps
from utils.cra_electrolyte_parsing import TestSolutionParsingError, parse_test_solution
from reporting.database_reports import (
    load_aligned_observations,
    load_cra_records,
    load_enriched_observations,
)


def _one_to_one_pairs():
    """Load the same validated, supported one-to-one pairs for all plots."""
    enriched = load_enriched_observations()
    aligned = load_aligned_observations()
    cra_records = load_cra_records()
    documents = {doc.reference_number: doc for doc in enriched}
    experiments = {(doc.reference_number, exp.observation_id): exp
                   for doc in enriched for exp in doc.experiments}
    cra_rows = {int(row["No."]): row for row in cra_records}
    if len(cra_rows) != len(cra_records):
        raise ValueError("CRA No. identifiers must be unique")

    row_uses = Counter(link.citrine_no for doc in aligned
                       for observation in doc.observations for link in observation.matches)
    pairs = []
    for alignment in aligned:
        reference = alignment.reference_number
        eligible = [obs for obs in alignment.observations
                    if len(obs.matches) == 1 and row_uses[obs.matches[0].citrine_no] == 1]
        if not eligible:
            continue
        document = documents.get(reference)
        if document is None:
            raise ValueError(f"Missing enrichment for paper {reference}")
        for kind in ("pdf", "registry"):
            left, right = getattr(alignment.inputs, kind), getattr(document.inputs, kind)
            if (left.filename, left.sha256) != (right.filename, right.sha256):
                raise ValueError(f"Paper {reference}: matching/enrichment {kind} inputs differ")
        for observation in eligible:
            key = (reference, observation.observation_id)
            if key not in experiments:
                raise ValueError(f"Missing enriched experiment: paper {reference}, {observation.observation_id}")
            no = observation.matches[0].citrine_no
            if no not in cra_rows:
                raise ValueError(f"CRA No. {no} is absent from the dataset")
            if int(cra_rows[no]["Reference"]) != reference:
                raise ValueError(f"CRA No. {no} belongs to a different paper")
            pairs.append((experiments[key], cra_rows[no]))

    if not pairs:
        raise ValueError("No experiments have a supported one-to-one CRA mapping")
    return pairs


def _relative_tolerance_note(options):
    relative = options.get("relative_tolerance")
    if relative is None:
        return ""
    return f"Tolerance: {100 * relative:g}% of |CRA value|; absolute tolerances retained.\n"


def plot_gap_histogram(
    output_path: str | Path = "plots/gap_histogram.png",
    **benchmark_options,
) -> list[int]:
    """Save a 10-bin histogram and return the plotted experiment gap counts.

    Keep an observation only if it has exactly one supported CRA link and no
    other observation has a supported link to that row. Count reverse links
    across all alignments before filtering, including multi-row observations.
    Unresolved candidates do not count as assignments.

    Load the current corpus through database_reports, joining by paper and
    observation ID, and CRA No. rather than CSV position. Check PDF/registry
    lineage before scoring. Forward options such as assume_percent_is_weight
    and tolerances to count_gaps; defaults are unchanged. Unscored fields are
    excluded from gap counts according to benchmark.py's rules.

    Run from the project root, as required by the existing loading helpers.
    Create output directories as needed; replace the specified image on rerun.
    No source datasets or database contents are modified. No GUI is opened.
    """
    gap_counts = [count_gaps(experiment, row, **benchmark_options)
                  for experiment, row in _one_to_one_pairs()]

    figure = Figure(figsize=(8, 5), layout="constrained")
    axes = figure.subplots()
    axes.hist(gap_counts, bins=10, color="#4C78A8", edgecolor="white")
    axes.set_xlabel("Number of gaps")
    axes.set_ylabel("Number of experiments")
    axes.set_title(f"Gap counts for one-to-one CRA matches (n={len(gap_counts)})")
    axes.xaxis.set_major_locator(MaxNLocator(integer=True))
    axes.yaxis.set_major_locator(MaxNLocator(integer=True))
    axes.set_axisbelow(True)
    axes.grid(axis="y", alpha=0.2)
    figure.supxlabel(_relative_tolerance_note(benchmark_options)
                     + "Unscored comparisons are excluded from gap counts.", fontsize=9)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=200)
    return gap_counts


def plot_gap_count_bars(
    output_path: str | Path = "plots/gap_histogram_2.png",
    **benchmark_options,
) -> dict[int, int]:
    """Save one vertical bar per integer gap count; return count -> experiments.

    Use the same one-to-one cohort and scoring options as plot_gap_histogram,
    including relative_tolerance=0.01 for 1% of each CRA value's magnitude.
    Include every integer from zero to the observed maximum, even when no
    experiments have that gap count. The maximum is not fixed at 14.
    Run from the project root; create parent directories and replace the
    specified image on rerun. Source datasets are unchanged.
    """
    frequencies = Counter(count_gaps(experiment, row, **benchmark_options)
                          for experiment, row in _one_to_one_pairs())
    counts = {gaps: frequencies[gaps] for gaps in range(max(frequencies) + 1)}

    figure = Figure(figsize=(8, 5), layout="constrained")
    axes = figure.subplots()
    bars = axes.bar(list(counts), list(counts.values()), color="#4C78A8", width=0.8)
    axes.bar_label(bars, padding=3, fontsize=9)
    axes.set_xlabel("Number of gaps")
    axes.set_ylabel("Number of experiments")
    axes.set_title(f"Gap counts for one-to-one CRA matches (n={sum(counts.values())})")
    axes.set_xticks(list(counts))
    axes.set_xlim(-0.6, max(counts) + 0.6)
    axes.yaxis.set_major_locator(MaxNLocator(integer=True))
    axes.margins(y=0.12)
    axes.set_axisbelow(True)
    axes.grid(axis="y", alpha=0.2)
    figure.supxlabel(_relative_tolerance_note(benchmark_options)
                     + "Unscored comparisons are excluded from gap counts.", fontsize=9)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=200)
    return counts


def plot_gaps_by_field(
    output_path: str | Path = "plots/gaps_by_field.png",
    **benchmark_options,
) -> dict[str, int]:
    """Save horizontal bars of total gaps per field; return the plotted totals.

    Use exactly the histogram's one-to-one cohort and benchmark options. Count
    each field once per experiment, irrespective of its gap reason. Preserve
    individual element/solute names (e.g. alloy.Cr and test_solution.NaCl).
    Sort by decreasing count, with alphabetical ties; retain zero-gap reference
    fields. A zero is not evidence of agreement if comparisons were unscored.
    Skipped/unscored comparisons are not gaps. Run from the project root.
    Pass relative_tolerance=0.01 for 1% of each CRA value's magnitude.
    Create parent directories and replace the specified image on rerun.
    """
    pairs = _one_to_one_pairs()
    totals = Counter()
    for experiment, row in pairs:
        result = benchmark_experiment(experiment, row, **benchmark_options)
        totals.update(result.gaps.keys())
        # Include reference fields even when they never generated a gap.
        for element in CRA_ELEMENTS:
            if element in row:
                totals.setdefault(f"alloy.{element}", 0)
        for field, column in (("pitting_potential", "Avg Epit mV (SCE)"),
                              ("test_temperature", "Test Temp C"),
                              ("chloride_concentration", "CL- [M]"),
                              ("ph", "pH"), ("material_class", "Material class")):
            if column in row:
                totals.setdefault(field, 0)
        try:
            solution = parse_test_solution(row.get("Test Solution"))
        except TestSolutionParsingError:
            continue  # The benchmark already records this reference limitation.
        for component in solution.composition:
            totals.setdefault(f"test_solution.{component.solute}", 0)
        if solution.solvent:
            totals.setdefault("test_solution.solvent", 0)
    counts = dict(sorted(totals.items(), key=lambda item: (-item[1], item[0])))

    figure = Figure(figsize=(10, max(5, 0.35 * len(counts) + 1.5)), layout="constrained")
    axes = figure.subplots()
    bars = axes.barh(list(counts), list(counts.values()), color="#4C78A8")
    axes.invert_yaxis()
    axes.set_xlabel("Number of gaps")
    axes.set_ylabel("Field")
    axes.set_title(f"Total gaps by field for one-to-one CRA matches (n={len(pairs)})")
    axes.xaxis.set_major_locator(MaxNLocator(integer=True))
    axes.set_axisbelow(True)
    axes.grid(axis="x", alpha=0.2)
    if counts:
        axes.bar_label(bars, padding=3, fontsize=9)
        axes.set_xlim(0, max(1, max(counts.values()) * 1.12))
    else:
        axes.set_yticks([])
        axes.text(0.5, 0.5, "No gaps found", transform=axes.transAxes, ha="center", va="center")
    figure.supxlabel(_relative_tolerance_note(benchmark_options)
                     + "Unscored comparisons are excluded; zero gaps do not imply full coverage.", fontsize=9)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=200)
    return counts
