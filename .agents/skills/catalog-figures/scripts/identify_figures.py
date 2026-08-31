"""Identify all charts and tables from the MinerU content_list_v2.json file."""

import argparse
import os 
import json 
import re 
from typing import Any 
from pathlib import Path

SPACE_RE = re.compile(r"\s+")

def _normalize_text(text: str) -> str:
    return SPACE_RE.sub(" ", text).strip()


def _join_text(parts: list[str]) -> str:
    return _normalize_text(" ".join(part for part in parts if part.strip()))


def flatten_text(value: Any) -> str:
    """Flatten MinerU span structures without traversing unrelated metadata."""
    if value is None:
        return ""
    if isinstance(value, str):
        return _normalize_text(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, list):
        return _join_text([flatten_text(item) for item in value])
    if not isinstance(value, dict):
        return ""

    node_type = value.get("type")
    content = value.get("content")
    if node_type == "text" and isinstance(content, str):
        return _normalize_text(content)
    if node_type in {"equation_inline", "equation_interline"} and isinstance(
        content, str
    ):
        equation = _normalize_text(content)
        return f"${equation}$" if equation else ""

    for key in (
        "paragraph_content",
        "title_content",
        "item_content",
        "list_items",
        "math_content",
        "page_number_content",
        "table_caption",
        "table_footnote",
    ):
        if key in value:
            return flatten_text(value[key])
    if isinstance(content, (str, list, dict)):
        return flatten_text(content)
    return ""


def get_figure_metadata(block):

    image_path = block['content']['image_source']['path']

    if block['type'] == 'chart':
        caption = flatten_text(block['content']['chart_caption'])
    elif block['type'] == 'table':
        caption = flatten_text(block['content']['table_caption'])
    else:
        raise ValueError('Block does not represent a tabularizable figure.')

    metadata = {
        'type': block['type'],
        'caption': caption,
        'image_path': image_path
    }

    return metadata


def find_figures(input_path : Path):

    files = os.listdir(input_path)

    content_list_file = [f for f in files 
                         if f.endswith('_content_list_v2.json')][0]

    content_list_file = input_path / content_list_file 

    with open(content_list_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    figures = [] 

    for page_number, page in enumerate(data, start=1):
        for block in page:

            if block['type'] in ['chart', 'table']:
                metadata = get_figure_metadata(block)
                metadata['page_number'] = page_number 
                figures.append(metadata)

    return figures 

def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input_path", type=Path, required=True)
    parser.add_argument("--output_file", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None):
    args = _parse_args(argv)
    input_path = args.input_path.resolve()
    output_file = args.output_file.resolve()

    figures = find_figures(input_path)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(figures, f, indent=4)

if __name__ == "__main__":
    main() 
