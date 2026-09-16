import unittest
from zipfile import ZipFile

from flat_file_renderers.html import HtmlRenderer


class HtmlRendererTestCase(unittest.TestCase):
    def test_renders_dataset_as_html_table(self):
        renderer = HtmlRenderer({})
        context = {"dataset": [{"name": "Alice", "age": 30}]}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                names = zf.namelist()
                self.assertEqual(len(names), 1)
                self.assertTrue(names[0].endswith(".html"))
                html = zf.read(names[0]).decode("utf-8")
            self.assertIn("<table>", html)
            self.assertIn("<th>age</th>", html)
            self.assertIn("<th>name</th>", html)
            self.assertIn("<td>Alice</td>", html)
            self.assertIn("<td>30</td>", html)
        finally:
            zip_path.unlink(missing_ok=True)

    def test_escapes_html_special_characters_in_values(self):
        renderer = HtmlRenderer({})
        context = {"dataset": [{"name": "<script>alert(1)</script>"}]}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                html = zf.read(zf.namelist()[0]).decode("utf-8")
            self.assertNotIn("<script>alert(1)</script>", html)
            self.assertIn("&lt;script&gt;", html)
        finally:
            zip_path.unlink(missing_ok=True)

    def test_missing_dataset_key_raises(self):
        renderer = HtmlRenderer({})
        with self.assertRaises(ValueError):
            renderer.render({})

    def test_multi_table_dataset_creates_one_file_per_key(self):
        renderer = HtmlRenderer({})
        context = {"dataset": {"Students": [{"name": "Alice"}], "Courses": [{"title": "Python"}]}}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                self.assertEqual(sorted(zf.namelist()), ["courses.html", "students.html"])
        finally:
            zip_path.unlink(missing_ok=True)
