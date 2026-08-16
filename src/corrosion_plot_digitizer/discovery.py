"""Discover figure references and screen captions for pitting-potential plots."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?P<path>[^)]+)\)")
FIGURE_RE = re.compile(
    r"\b(?:fig(?:ure)?\.?\s*)(?P<number>\d+(?:[A-Za-z]|\.\d+)?)", re.I
)

PITTING_TERMS = (
    "pitting potential",
    "pitting potentials",
    "pit potential",
)
IRRELEVANT_TERMS = (
    "anodic pit current density",
    "pit current density",
    "current density as a function",
)


@dataclass(frozen=True)
class FigureCandidate:
    paper_id: str
    figure_id: str
    image_path: str
    caption: str
    relevant: bool
    screening_reason: str
    requires_agent_review: bool


def classify_caption(caption: str) -> tuple[bool, str, bool]:
    lowered = " ".join(caption.lower().split())
    has_pitting = any(term in lowered for term in PITTING_TERMS)
    has_irrelevant = any(term in lowered for term in IRRELEVANT_TERMS)
    if has_pitting:
        reason = "caption explicitly mentions pitting potential"
        if has_irrelevant:
            reason += "; mixed metrics require series-level filtering"
        return True, reason, True
    if has_irrelevant:
        return False, "caption describes pit/current-density behavior, not Epit", False
    return False, "caption does not explicitly identify pitting potential", True


def discover_figures(markdown_path: Path, paper_id: str) -> list[FigureCandidate]:
    text = markdown_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    candidates: list[FigureCandidate] = []

    for index, line in enumerate(lines):
        image_match = IMAGE_RE.search(line)
        if not image_match:
            continue

        trailing = line[image_match.end() :].strip()
        caption_parts = [trailing] if trailing else []
        for following in lines[index + 1 : index + 6]:
            stripped = following.strip()
            if not stripped:
                continue
            if IMAGE_RE.search(stripped) or stripped.startswith("#"):
                break
            caption_parts.append(stripped)
            if FIGURE_RE.search(" ".join(caption_parts)):
                break

        caption = " ".join(caption_parts).strip()
        figure_match = FIGURE_RE.search(caption)
        figure_id = figure_match.group("number") if figure_match else f"image-{len(candidates) + 1}"
        image = (markdown_path.parent / image_match.group("path")).resolve()
        relevant, reason, review = classify_caption(caption)
        candidates.append(
            FigureCandidate(
                paper_id=str(paper_id),
                figure_id=figure_id,
                image_path=str(image),
                caption=caption,
                relevant=relevant,
                screening_reason=reason,
                requires_agent_review=review,
            )
        )

    return candidates


def write_manifest(
    candidates: list[FigureCandidate], output_path: Path, source_markdown: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "source_markdown": str(source_markdown.resolve()),
        "figures": [asdict(candidate) for candidate in candidates],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
