import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / 'converter1.0.py'
FIXTURES = Path(__file__).resolve().parent / 'fixtures'


def load_converter():
    code = compile(SOURCE.read_text(), str(SOURCE), 'exec')
    namespace = {'__name__': 'synthetic_converter'}
    with patch('builtins.open', side_effect=AssertionError('Import must not open game files')):
        exec(code, namespace)
    return namespace


class ConverterTest(unittest.TestCase):
    def setUp(self):
        self.converter = load_converter()

    def test_import_has_no_game_io(self):
        self.assertTrue(callable(self.converter['main']))

    def test_canonical_time_boundaries_and_roundtrip(self):
        rows = self.converter['parse_rows'](['09 55 A', '00 00 B', '23 59 C'])
        self.assertEqual(rows, [[0, 595, 'A'], [1, 0, 'B'], [2, 1439, 'C']])
        for score in [595, 0, 1439]:
            hour, minute = self.converter['scoretotime'](score)
            self.assertEqual(self.converter['timetoscore'](hour, minute), score)

    def test_whitespace_and_blank_lines(self):
        rows = self.converter['parse_rows'](['\n', ' 09  55 A \n', '\t', '10\t00\tB'])
        self.assertEqual(rows, [[0, 595, 'A'], [1, 600, 'B']])

    def test_malformed_rows_report_original_line_number(self):
        cases = ['09 55', '09 55 A extra', 'bad 55 A', '24 00 A',
                 '-1 00 A', '09 60 A', '09 -1 A']
        for row in cases:
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, r'^Line 3:'):
                self.converter['parse_rows'](['09 55 A', '', row])

    def test_canonical_simulation_output_matches_unmodified_baseline(self):
        rows = self.converter['parse_rows']((FIXTURES / 'canonical-input.txt').read_text().splitlines())
        output = io.StringIO()
        self.converter['convert'](rows, output)
        self.assertEqual(output.getvalue().encode(), (FIXTURES / 'canonical-output.txt').read_bytes())

    def test_cli_canonical_output(self):
        with tempfile.TemporaryDirectory(prefix='queuegame-synthetic-') as directory:
            root = Path(directory)
            (root / 'bd').write_bytes((FIXTURES / 'canonical-input.txt').read_bytes())
            result = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / 'out').read_bytes(), (FIXTURES / 'canonical-output.txt').read_bytes())

    def test_cli_rejects_malformed_input_before_output_is_touched(self):
        with tempfile.TemporaryDirectory(prefix='queuegame-synthetic-') as directory:
            root = Path(directory)
            (root / 'bd').write_text('09 55 A\n09 bad B\n')
            for existing in [False, True]:
                with self.subTest(existing=existing):
                    if existing:
                        (root / 'out').write_text('SYNTHETIC_SENTINEL')
                    result = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn('Line 2: hour and minute must be integers', result.stderr)
                    self.assertNotIn('Traceback', result.stderr)
                    if existing:
                        self.assertEqual((root / 'out').read_text(), 'SYNTHETIC_SENTINEL')
                    else:
                        self.assertFalse((root / 'out').exists())


if __name__ == '__main__':
    unittest.main()
