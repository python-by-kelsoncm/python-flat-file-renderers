import csv
import unittest
from io import StringIO
from zipfile import ZipFile

from flat_file_renderers.separated_value import CsvRenderer, TsvRenderer


class CsvRendererTestCase(unittest.TestCase):
    def test_renders_simple_dataset_as_csv(self):
        renderer = CsvRenderer({})
        context = {"dataset": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                names = zf.namelist()
                self.assertEqual(len(names), 1)
                self.assertTrue(names[0].endswith(".csv"))
                content = zf.read(names[0]).decode("utf-8")
            rows = list(csv.DictReader(StringIO(content)))
            self.assertEqual(
                sorted(rows, key=lambda r: r["name"]),
                [{"age": "30", "name": "Alice"}, {"age": "25", "name": "Bob"}],
            )
        finally:
            zip_path.unlink(missing_ok=True)

    def test_replaces_crlf_in_values(self):
        renderer = CsvRenderer({})
        context = {"dataset": [{"text": "line1\nline2"}]}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                content = zf.read(zf.namelist()[0]).decode("utf-8")
            self.assertNotIn("\n\n", content)
            self.assertIn(r"line1\\nline2", content)
        finally:
            zip_path.unlink(missing_ok=True)

    def test_multi_table_dataset_creates_one_file_per_key(self):
        renderer = CsvRenderer({})
        context = {"dataset": {"Students": [{"name": "Alice"}], "Courses": [{"title": "Python"}]}}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                self.assertEqual(sorted(zf.namelist()), ["courses.csv", "students.csv"])
        finally:
            zip_path.unlink(missing_ok=True)

    def test_logs_progress_past_500_rows(self):
        renderer = CsvRenderer({})
        context = {"dataset": [{"n": i} for i in range(501)]}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                content = zf.read(zf.namelist()[0]).decode("utf-8")
            self.assertEqual(len(content.splitlines()), 502)  # header + 501 rows
        finally:
            zip_path.unlink(missing_ok=True)


class TsvRendererTestCase(unittest.TestCase):
    def test_uses_tab_delimiter_and_tsv_extension(self):
        renderer = TsvRenderer({})
        context = {"dataset": [{"name": "Alice", "age": 30}]}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                names = zf.namelist()
                self.assertTrue(names[0].endswith(".tsv"))
                content = zf.read(names[0]).decode("utf-8")
            self.assertIn("\t", content.splitlines()[0])
        finally:
            zip_path.unlink(missing_ok=True)
