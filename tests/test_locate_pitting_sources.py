"""Read-only row selection and source-report coverage checks."""
import csv
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = Path(os.environ.get('LOCATE_PITTING_SKILL_ROOT', ROOT / '.agents/skills/locate-pitting-sources'))
spec = importlib.util.spec_from_file_location('select_rows', SKILL / 'scripts/select_rows.py')
selector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selector)
spec = importlib.util.spec_from_file_location('locate_validate_report', SKILL / 'scripts/validate_report.py')
checker = importlib.util.module_from_spec(spec)
# The validator's CLI imports its sibling, so supply that same module during test loading.
previous_selector = sys.modules.get('select_rows')
sys.modules['select_rows'] = selector
try:
    spec.loader.exec_module(checker)
finally:
    if previous_selector is None:
        del sys.modules['select_rows']
    else:
        sys.modules['select_rows'] = previous_selector


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'input.csv'

    def write(self, rows, columns=None):
        columns = columns or [*selector.REQUIRED_COLUMNS, 'Comments']
        with self.path.open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def row(identifier='1', reference='71', value='-65', comments=''):
        return {'No.': identifier, 'Reference': reference,
                selector.TARGET_COLUMNS[0]: value, selector.TARGET_COLUMNS[1]: 'NA',
                selector.TARGET_COLUMNS[2]: '', 'Comments': comments}

    def test_multiline_quoting_strings_order_and_input_unchanged(self):
        comments = 'First line, "quoted"\r\nSecond line | with symbol μ'
        rows = [self.row('9', comments=comments), self.row('2', value='-65'), self.row('3', '49')]
        self.write(rows)
        original = self.path.read_bytes()
        result = selector.select_rows(self.path, 71)
        self.assertEqual([item['row'] for item in result['rows']], rows[:2])
        self.assertEqual(result['rows'][0]['csv_record'], 1)
        self.assertEqual(result['rows'][0]['row']['Comments'], comments)
        self.assertEqual(self.path.read_bytes(), original)

    def test_real_paper_counts(self):
        for reference, count in [(49, 65), (71, 38)]:
            with self.subTest(reference=reference):
                result = selector.select_rows(ROOT / 'citrine_database/pitting_potential.csv', reference)
                self.assertEqual(result['selected_row_count'], count)
                self.assertEqual(len({x['row']['No.'] for x in result['rows']}), count)

    def test_repeated_target_values_are_not_deduplicated(self):
        self.write([self.row('1'), self.row('2')])
        self.assertEqual(selector.select_rows(self.path, 71)['selected_row_count'], 2)

    def test_empty_identifier_is_rejected(self):
        self.write([self.row('  ')])
        with self.assertRaisesRegex(ValueError, 'empty No.'):
            selector.select_rows(self.path, 71)

    def test_duplicate_selected_identifier_is_rejected(self):
        self.write([self.row('1'), self.row(' 1 ')])
        with self.assertRaisesRegex(ValueError, 'Duplicate selected'):
            selector.select_rows(self.path, 71)

    def test_identifiers_in_other_papers_do_not_conflict(self):
        self.write([self.row('1'), self.row('1', '49')])
        self.assertEqual(selector.select_rows(self.path, 71)['selected_row_count'], 1)

    def test_no_matching_reference_is_an_empty_selection(self):
        self.write([self.row()])
        self.assertEqual(selector.select_rows(self.path, 80)['rows'], [])

    def test_missing_required_column_is_rejected(self):
        self.path.write_text('No.,Reference\n1,71\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Missing required'):
            selector.select_rows(self.path, 71)

    def test_malformed_record_is_rejected(self):
        self.path.write_text(','.join(selector.REQUIRED_COLUMNS)+'\n1,71,-65,NA,NA,extra\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Malformed CSV'):
            selector.select_rows(self.path, 71)

    def test_duplicate_headers_are_rejected(self):
        self.path.write_text(','.join([*selector.REQUIRED_COLUMNS, 'No.'])+'\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'unique column'):
            selector.select_rows(self.path, 71)

    def test_reference_resolution_and_conflict(self):
        pdf = self.path.with_name('71_test.pdf')
        pdf.write_bytes(b'Contents need not be a readable PDF for filename resolution')
        self.assertEqual(selector.resolve_reference(pdf, None), 71)
        self.assertEqual(selector.resolve_reference(pdf, 71), 71)
        with self.assertRaisesRegex(ValueError, 'conflict'):
            selector.resolve_reference(pdf, 49)
        with self.assertRaisesRegex(ValueError, 'Cannot infer'):
            selector.resolve_reference(None, None)

    def test_explicit_reference_for_unnumbered_pdf(self):
        pdf = self.path.with_name('paper.pdf')
        pdf.touch()
        self.assertEqual(selector.resolve_reference(pdf, 71), 71)

    def test_invalid_reference_values(self):
        for value in ['0', '-1', 'NaN', 'Infinity', '7.1', 'NA']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                selector.positive_reference(value)

    def test_cli_errors_are_nonzero_with_no_result(self):
        self.write([self.row('')])
        result = subprocess.run([sys.executable, str(SKILL/'scripts/select_rows.py'),
                                 '--csv',str(self.path),'--reference','71'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertIn('empty No.', result.stderr)


class ReportCoverageTests(unittest.TestCase):
    def selection(self):
        rows = [dict(SelectionTests.row('1'), Nb='0.5'), dict(SelectionTests.row('2'), Nb='0.5')]
        return {'rows': [{'row': row, 'target_display': selector.target_display(row)} for row in rows]}

    def report(self, statuses=('Strong candidate', 'Ambiguous')):
        selection = self.selection()
        text = checker.HEADER+'\n|---|---|---|---|---|---|---|\n'
        for item, status in zip(selection['rows'], statuses):
            if status in ('Not assessed', 'Not located'):
                source, variables, comparison = status, status, 'Not comparable: '+status.lower()
            else:
                source = '-0.065 V (SCE), printed'
                variables = 'Nb: paper=0.005 mass fraction; Citrine=0.5 wt%'
                comparison = 'Epit: -0.065 x 1000 = -65 mV (SCE), exact; Nb: 0.005 x 100 = 0.5 wt%, exact'
            text += (f'| {item["row"]["No."]} | {item["target_display"]} | {source} | {variables} '
                     f'| PDF p. 3, Table II, same observation allowed | {comparison} | {status} |\n')
        text += '\nAssessment totals: '+ '; '.join(f'{name}={statuses.count(name)}' for name in checker.ASSESSMENTS)+'\n\n'
        return text

    def test_complete_report_with_duplicate_source_is_valid(self):
        self.assertEqual(checker.validate_report(self.report(), self.selection()), [])

    def test_row_omission_and_duplicate_entry_are_detected(self):
        lines = self.report().splitlines()
        second = next(line for line in lines if line.startswith('| 2 |'))
        for text in [self.report().replace(second+'\n', ''),
                     self.report().replace(second, second+'\n'+second)]:
            self.assertTrue(checker.validate_report(text, self.selection()))

    def test_old_verbose_details_are_not_required_or_accepted(self):
        self.assertEqual(checker.validate_report(self.report(), self.selection()), [])
        errors = checker.validate_report(self.report()+'### Citrine No. 1\nRepeated narrative.\n', self.selection())
        self.assertTrue(any('Per-row detail' in error for error in errors))

    def test_source_values_and_comparison_are_required(self):
        for content in ('-0.065 V (SCE), printed',
                        'Epit: -0.065 x 1000 = -65 mV (SCE), exact; Nb: 0.005 x 100 = 0.5 wt%, exact',
                        'Nb: paper=0.005 mass fraction; Citrine=0.5 wt%'):
            with self.subTest(content=content):
                text = self.report().replace('| '+content+' |', '| |', 1)
                self.assertTrue(checker.validate_report(text, self.selection()))

    def test_supporting_variables_must_pair_paper_and_citrine_values(self):
        for value in ('Nb=0.5 wt%', 'Nb: paper=0.005 mass fraction',
                      'Nb: Citrine=0.5 wt%', 'Nb: paper= ; Citrine=0.5 wt%',
                      'Nb: paper=0.005 mass fraction; Citrine= ',
                      'Nb: paper=0.005 mass fraction; Citrine=0.5 wt%<br>pH=7'):
            with self.subTest(value=value):
                text = self.report().replace('Nb: paper=0.005 mass fraction; Citrine=0.5 wt%', value, 1)
                self.assertTrue(checker.validate_report(text, self.selection()))
        text = self.report().replace('Nb: paper=0.005 mass fraction; Citrine=0.5 wt%',
                                    'Nb: paper=0.005 mass fraction; Citrine=0.5 wt%<br>pH: paper=7; Citrine=7')
        self.assertEqual(checker.validate_report(text, self.selection()), [])

    def test_bounds_and_underdetermined_conversions_can_be_reported(self):
        text = self.report(('Ambiguous', 'Ambiguous')).replace(
            'Nb: paper=0.005 mass fraction; Citrine=0.5 wt%', 'Nb: paper=<0.5 at%; Citrine=0.5 wt%')
        text = text.replace('Epit: -0.065 x 1000 = -65 mV (SCE), exact; Nb: 0.005 x 100 = 0.5 wt%, exact',
                            'Epit: same reference, exact; Nb: not comparable, remainder composition unspecified')
        self.assertEqual(checker.validate_report(text, self.selection()), [])

    def test_report_cli_validates_without_pdf_or_rewriting_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path, report_path = root/'input.csv', root/'report.md'
            rows = [item['row'] for item in self.selection()['rows']]
            with csv_path.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            report_path.write_text(self.report(), encoding='utf-8')
            originals = [path.read_bytes() for path in (csv_path, report_path)]
            result = subprocess.run([sys.executable, str(SKILL/'scripts/validate_report.py'),
                                     '--csv', str(csv_path), '--reference', '71', '--report', str(report_path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('VALID COVERAGE: 2 rows', result.stdout)
            self.assertEqual([path.read_bytes() for path in (csv_path, report_path)], originals)

    def test_value_only_candidate_can_remain_ambiguous(self):
        text = self.report(('Ambiguous', 'Ambiguous')).replace(
            'Nb: paper=0.005 mass fraction; Citrine=0.5 wt%', 'None established: unresolved alloy identity')
        self.assertEqual(checker.validate_report(text, self.selection()), [])
        text = self.report().replace('Nb: paper=0.005 mass fraction; Citrine=0.5 wt%', 'None established')
        self.assertTrue(checker.validate_report(text, self.selection()))

    def test_target_corruption_is_detected(self):
        self.assertTrue(checker.validate_report(self.report().replace('-65', '65', 1), self.selection()))

    def test_order_and_unknown_assessment_are_detected(self):
        text = self.report().replace('| 1 |', '| 2 |', 1)
        self.assertTrue(checker.validate_report(text, self.selection()))
        self.assertTrue(checker.validate_report(self.report().replace('| Ambiguous |','| Confirmed |'), self.selection()))

    def test_inconsistent_totals_are_detected(self):
        self.assertTrue(checker.validate_report(self.report().replace('Ambiguous=1','Ambiguous=0'), self.selection()))

    def test_blocked_rows_remain_in_report(self):
        self.assertEqual(checker.validate_report(self.report(('Not assessed','Not assessed')),self.selection()),[])

    def test_zero_row_report(self):
        text = checker.HEADER+'\n|---|---|---|---|---|---|---|\n\nAssessment totals: '+ '; '.join(f'{name}=0' for name in checker.ASSESSMENTS)
        self.assertEqual(checker.validate_report(text, {'rows': []}), [])

    def test_escaped_pipe_and_linked_identifier(self):
        selection = self.selection()
        text = self.report().replace('| 1 |','| [1](#row-1) |',1).replace('same observation allowed','same \\| observation allowed')
        self.assertEqual(checker.validate_report(text, selection), [])


if __name__ == '__main__':
    unittest.main()
