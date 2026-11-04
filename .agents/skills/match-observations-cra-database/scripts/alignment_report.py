"""Render a compact report from an already validated alignment; no file writes."""

from collections import Counter
from html import escape
from typing import get_args

from alignment import MatchStatus
from matching_io import shared_rows


def cell(value):
    return escape(str(value), quote=False).replace("|", r"\|").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")


def measurement(value):
    if value is None:
        return "unavailable"
    parts = []
    if value.value is not None:
        parts.append(str(value.value))
    if value.min is not None:
        parts.append(f"min={value.min}")
    if value.max is not None:
        parts.append(f"max={value.max}")
    if value.plus_minus is not None:
        parts.append(f"+/- {value.plus_minus}")
    return ", ".join(parts) + (f" {value.unit}" if value.unit else "")


def locator(location):
    prefix = f"PDF p. {location.pdf_page}"
    if location.printed_page:
        prefix += f" / printed p. {location.printed_page}"
    if location.kind == "table":
        selectors = [location.table_label, location.row_label, location.column_label]
    elif location.kind == "plot":
        selectors = [location.figure_label, location.panel_label, location.series_label]
        for coordinate in location.coordinates:
            value = measurement(coordinate.value) if not isinstance(coordinate.value, str) else coordinate.value
            selectors.append(f"{coordinate.name}={value}")
    else:
        selectors = [location.section_heading, location.text_anchor]
    return ", ".join([prefix, *(s for s in selectors if s)])


def render_report(alignment, prepared):
    """Call only after validate_alignment succeeds; the CLI enforces this order."""
    sources = {o.observation_id: o for o in prepared.registry.observations}
    counts = Counter(o.status for o in alignment.observations)
    lines = [
        "# Observation-to-CRA alignment", "",
        f"Paper: {cell(alignment.paper_name)}; reference {alignment.reference_number}. "
        f"Registry: {cell(alignment.inputs.registry.filename)}; CSV: {cell(alignment.inputs.csv.filename)}. "
        f"Supplied observations={len(alignment.observations)}; CRA rows={len(prepared.rows)}.", "",
        "These are automated alignment proposals for this exact supplied registry. "
        "Unlinked rows are unassigned in this input, not proven absent from the paper. "
        "Avg is a database column label, not evidence of a source-reported mean.", "",
        "| Observation | Registered reading / location | Supported CRA No. | Candidate CRA No. | CRA targets (mV SCE) | Evidence / conversion | Status / notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in alignment.observations:
        source = sources[item.observation_id]
        links = item.matches + item.candidates
        indices = sorted({i for link in links for i in link.location_indices}) or [source.primary_location]
        readings = []
        for index in indices:
            location = source.locations[index]
            readings.append(cell(f"loc {index}: {measurement(location.pitting_potential)} ({location.reading_method}); {locator(location)}"))
        targets, comparisons = [], []
        for link in links:
            kind = "supported" if link in item.matches else "candidate"
            targets.append(cell(
                f"{link.citrine_no} ({kind}): Avg={link.cra_potential.avg}; "
                f"Min={link.cra_potential.min}; Max={link.cra_potential.max}"
            ))
            comparisons.extend(cell(
                f"{link.citrine_no} / {e.field}: paper={e.paper_value}; CRA={e.cra_value}; {e.comparison}"
            ) for e in link.evidence)
            comparisons.append(cell(f"{link.citrine_no}: {link.potential_agreement}; {link.notes}"))
        values = [
            cell(item.observation_id), "<br>".join(readings),
            cell(", ".join(str(link.citrine_no) for link in item.matches) or "none"),
            cell(", ".join(str(link.citrine_no) for link in item.candidates) or "none"),
            "<br>".join(targets) or "—", "<br>".join(comparisons) or "—",
            cell(item.status + (f": {item.notes}" if item.notes else "")),
        ]
        lines.append("| " + " | ".join(values) + " |")
    lines += ["", "Status counts: " + "; ".join(f"{s}={counts[s]}" for s in get_args(MatchStatus)) + "."]
    for status in ("ambiguous", "unmatched", "not_assessed"):
        lines.append(f"{status} IDs: " + (", ".join(o.observation_id for o in alignment.observations if o.status == status) or "none") + ".")
    groups = shared_rows(alignment)
    lines += ["", "Supported shared-row groups: " + (
        "; ".join(f"CRA {n}: {', '.join(ids)}" for n, ids in groups.items()) or "none"
    ) + ".", "Unlinked CRA No. in this input: " + (", ".join(map(str, alignment.unlinked_citrine_nos)) or "none") + "."]
    if alignment.shared_qualifications:
        lines += ["", "Shared qualifications:", ""]
        lines.extend(f"- {cell(note)}" for note in alignment.shared_qualifications)
    lines += ["", "Visually inspected PDF pages: " + (", ".join(map(str, alignment.inspected_pdf_pages)) or "none") + "."]
    if alignment.coverage_notes:
        lines.append("Coverage/access: " + cell(alignment.coverage_notes))
    if not alignment.observations:
        lines.append("No observations were supplied; this is not a finding that the paper contains no outcomes.")
    for warning in prepared.warnings:
        lines.append("Input warning: " + cell(warning))
    lines += ["", "Structural validation: PASS against the bundled schema/model and exact supplied inputs. "
        "Scientific fidelity, conversion arithmetic/assumptions, identity and benchmark suitability are not certified. "
        "Only supported links enter default joins; shared rows must not be counted as independent benchmark rows without review."]
    return "\n".join(lines)
