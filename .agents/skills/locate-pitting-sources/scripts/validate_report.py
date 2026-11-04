"""Check compact Markdown comparisons and row coverage, not scientific fidelity.

Reads inputs only. Does not verify PDF observations or conversion arithmetic.
"""
from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path
import re
import sys

from select_rows import parser, resolve_reference, select_rows

ASSESSMENTS = ('Strong candidate', 'Ambiguous', 'Not located', 'Not assessed')
COLUMNS = ('Citrine No.', 'Database target value(s)', 'Paper pitting potential(s)',
           'Other matching variables (paper / Citrine)', 'Best proposed location',
           'Conversion / comparison', 'Assessment')
HEADER = '| ' + ' | '.join(COLUMNS) + ' |'


def cells(line: str) -> list[str]:
    return [part.strip().replace('\\|', '|') for part in re.split(r'(?<!\\)\|', line.strip())[1:-1]]


def bare_identifier(value: str) -> str:
    linked = re.fullmatch(r'\[([^\]]+)\]\(#[^)]+\)', value)
    return (linked.group(1) if linked else value).strip()


def validate_report(text: str, selection: dict) -> list[str]:
    errors = []
    lines = text.splitlines()
    headers = [i for i, line in enumerate(lines) if line.strip() == HEADER]
    if len(headers) != 1:
        return ['Expected exactly one overview table with the documented header']
    index = headers[0] + 1
    separator = r'\|(?:\s*:?-+:?\s*\|){' + str(len(COLUMNS)) + '}'
    if index >= len(lines) or not re.fullmatch(separator, lines[index].strip()):
        return ['Comparison table requires a seven-column Markdown separator row']
    overview = []
    for line in lines[index+1:]:
        if not line.strip().startswith('|'):
            break
        parsed = cells(line)
        if len(parsed) != len(COLUMNS):
            errors.append('Comparison row does not have seven cells (escape literal pipes)')
        else:
            overview.append(parsed)
    expected = [item['row']['No.'].strip() for item in selection['rows']]
    actual = [bare_identifier(row[0]) for row in overview]
    if actual != expected:
        errors.append('Overview identifiers/order differ from selected CSV rows')
    targets = {item['row']['No.'].strip(): item['target_display'] for item in selection['rows']}
    counts = Counter()
    for identifier, values, paper_values, variables, location, comparison, assessment in overview:
        identifier = bare_identifier(identifier)
        if identifier in targets and values != targets[identifier].strip():
            errors.append(f'No. {identifier}: database target strings differ from CSV')
        if assessment not in ASSESSMENTS:
            errors.append(f'No. {identifier}: unknown assessment {assessment!r}')
        else:
            counts[assessment] += 1
        if not location:
            errors.append(f'No. {identifier}: best-location cell must state a locator or why none is available')
        if not paper_values:
            errors.append(f'No. {identifier}: paper-potential cell must state source values or why unavailable')
        if not comparison:
            errors.append(f'No. {identifier}: conversion/comparison cell must state agreement, discrepancy or a limitation')
        if not variables:
            errors.append(f'No. {identifier}: matching-variable cell must give paired values or an explicit limitation')
        else:
            # This verifies paired labels, not the scientific validity or completeness of the pairs.
            limitation = variables.startswith(('None established', 'Not located', 'Not assessed'))
            if limitation:
                if assessment == 'Strong candidate':
                    errors.append(f'No. {identifier}: strong candidate needs independent association evidence')
            else:
                for pair in re.split(r'<br\s*/?>', variables, flags=re.IGNORECASE):
                    match = re.search(r'\bpaper\s*=(.*?);\s*Citrine\s*=(.*)', pair)
                    if match is None or not all(value.strip() for value in match.groups()):
                        errors.append(f'No. {identifier}: each supporting-variable entry needs paper=...; Citrine=...')
                        break
    if re.search(r'^### Citrine No\. ', text, flags=re.MULTILINE):
        errors.append('Per-row detail sections have been replaced by compact comparison-table cells')
    totals = [line for line in lines if line.startswith('Assessment totals: ')]
    expected_totals = 'Assessment totals: ' + '; '.join(f'{name}={counts[name]}' for name in ASSESSMENTS)
    if totals != [expected_totals]:
        errors.append('Assessment totals line is missing, repeated or inconsistent with the overview')
    return errors


def main(argv=None) -> int:
    args_parser = parser()
    args_parser.description = __doc__
    args_parser.add_argument('--report', required=True, type=Path)
    args = args_parser.parse_args(argv)
    try:
        selection = select_rows(args.csv, resolve_reference(args.pdf, args.reference))
        errors = validate_report(args.report.read_text(encoding='utf-8-sig'), selection)
    except (OSError, ValueError, UnicodeError, csv.Error) as exc:
        print(f'Cannot check report: {exc}', file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f'VALID COVERAGE: {selection["selected_row_count"]} rows. PDF fidelity, conversions and scientific assignments not checked.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
