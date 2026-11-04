"""Read-only Citrine row selection; standard library only, JSON to stdout."""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import sys

TARGET_COLUMNS = ('Avg Epit mV (SCE)', 'Max Epit mV (SCE)', 'Min Epit mV (SCE)')
REQUIRED_COLUMNS = ('No.', 'Reference', *TARGET_COLUMNS)


def positive_reference(value: str | int) -> int:
    try:
        number = Decimal(str(value).strip())
        if not number.is_finite() or number <= 0 or number != number.to_integral_value():
            raise ValueError
        return int(number)
    except (InvalidOperation, ValueError, OverflowError) as exc:
        raise ValueError(f'Expected a positive integer reference, got {value!r}') from exc


def resolve_reference(pdf: Path | None, reference: int | None) -> int:
    inferred = None
    if pdf is not None:
        if not pdf.is_file():
            raise ValueError(f'PDF does not exist: {pdf}')
        if pdf.suffix.lower() != '.pdf':
            raise ValueError(f'Expected a PDF: {pdf}')
        match = re.match(r'^([1-9][0-9]*)(?=\D|$)', pdf.name)
        inferred = int(match.group(1)) if match else None
    explicit = positive_reference(reference) if reference is not None else None
    if explicit is not None and inferred is not None and explicit != inferred:
        raise ValueError(f'Reference conflict: filename gives {inferred}, explicit reference gives {explicit}; clarify before matching')
    chosen = explicit if explicit is not None else inferred
    if chosen is None:
        raise ValueError('Cannot infer reference from filename; supply --reference after clarification')
    return chosen


def target_display(row: dict[str, str]) -> str:
    return '; '.join(f'{column}: {row[column]}' for column in TARGET_COLUMNS)


def select_rows(csv_path: Path, reference: int) -> dict:
    reference = positive_reference(reference)
    selected = []
    seen = set()
    with csv_path.open('r', encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream, strict=True)
        columns = reader.fieldnames
        if not columns or len(columns) != len(set(columns)):
            raise ValueError('CSV requires nonempty, unique column headers')
        missing = [name for name in REQUIRED_COLUMNS if name not in columns]
        if missing:
            raise ValueError('Missing required CSV columns: ' + ', '.join(missing))
        for record_number, row in enumerate(reader, 1):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f'Malformed CSV data record {record_number}: field count differs from header')
            try:
                row_reference = positive_reference(row['Reference'])
            except ValueError as exc:
                raise ValueError(f'CSV data record {record_number}: {exc}') from exc
            if row_reference != reference:
                continue
            identifier = row['No.'].strip()
            if not identifier:
                raise ValueError(f'Selected CSV data record {record_number} has an empty No.')
            if identifier in seen:
                raise ValueError(f'Duplicate selected No. identifier: {identifier!r}')
            seen.add(identifier)
            selected.append({'csv_record': record_number, 'row': row, 'target_display': target_display(row)})
    return {'csv_path': str(csv_path), 'reference_number': reference, 'columns': columns,
            'selected_row_count': len(selected), 'rows': selected}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument('--csv', required=True, type=Path)
    result.add_argument('--pdf', type=Path, help='Used only for filename/reference resolution; contents are never parsed')
    result.add_argument('--reference', type=positive_reference)
    return result


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        reference = resolve_reference(args.pdf, args.reference)
        document = select_rows(args.csv, reference)
    except (OSError, ValueError, UnicodeError, csv.Error) as exc:
        print(f'Cannot select rows: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(document, ensure_ascii=True, allow_nan=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
