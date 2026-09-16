import unittest
from io import BytesIO
from zipfile import ZipFile

import pyarrow.parquet as pq

from flat_file_renderers.parquet import ParquetRenderer


class ParquetRendererTestCase(unittest.TestCase):
    def _read_single_table(self, zip_path):
        with ZipFile(zip_path) as zf:
            names = zf.namelist()
            self.assertEqual(len(names), 1)
            self.assertTrue(names[0].endswith(".parquet"))
            return pq.read_table(BytesIO(zf.read(names[0])))

    def test_renders_simple_dataset(self):
        renderer = ParquetRenderer({})
        context = {"dataset": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}
        zip_path = renderer.render(context)
        try:
            table = self._read_single_table(zip_path)
            rows = table.to_pylist()
            self.assertEqual(
                sorted(rows, key=lambda r: r["name"]),
                [{"age": 30, "name": "Alice"}, {"age": 25, "name": "Bob"}],
            )
        finally:
            zip_path.unlink(missing_ok=True)

    def test_nested_list_and_dict_values_are_stringified(self):
        renderer = ParquetRenderer({})
        context = {"dataset": [{"name": "Alice", "tags": ["a", "b"]}]}
        zip_path = renderer.render(context)
        try:
            table = self._read_single_table(zip_path)
            row = table.to_pylist()[0]
            self.assertEqual(row["tags"], str(["a", "b"]))
        finally:
            zip_path.unlink(missing_ok=True)

    def test_renders_empty_dataset(self):
        renderer = ParquetRenderer({})
        zip_path = renderer.render({"dataset": []})
        try:
            table = self._read_single_table(zip_path)
            self.assertEqual(table.num_rows, 0)
        finally:
            zip_path.unlink(missing_ok=True)

    def test_missing_dataset_key_raises(self):
        renderer = ParquetRenderer({})
        with self.assertRaises(ValueError):
            renderer.render({})

    def test_multi_table_dataset_creates_one_file_per_key(self):
        renderer = ParquetRenderer({})
        context = {"dataset": {"Students": [{"name": "Alice"}], "Courses": [{"title": "Python"}]}}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                self.assertEqual(sorted(zf.namelist()), ["courses.parquet", "students.parquet"])
        finally:
            zip_path.unlink(missing_ok=True)
