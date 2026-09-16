import unittest

import flat_file_renderers as ffr


class PublicApiTestCase(unittest.TestCase):
    def test_dependency_free_symbols_are_exported(self):
        self.assertTrue(hasattr(ffr, "BaseRenderer"))
        self.assertTrue(hasattr(ffr, "ZipFileEntry"))
        self.assertTrue(hasattr(ffr, "FlatDictListHelper"))
        self.assertTrue(hasattr(ffr, "replace_crlf"))
        self.assertTrue(hasattr(ffr, "CsvRenderer"))
        self.assertTrue(hasattr(ffr, "TsvRenderer"))
        self.assertTrue(hasattr(ffr, "FlatDelimitedRenderer"))
        self.assertTrue(hasattr(ffr, "JsonRenderer"))
        self.assertTrue(hasattr(ffr, "HtmlRenderer"))

    def test_version_is_set(self):
        self.assertIsInstance(ffr.__version__, str)
