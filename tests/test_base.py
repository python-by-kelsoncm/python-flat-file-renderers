import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

from flat_file_renderers.base import BaseRenderer, ZipFileEntry


class DummyRenderer(BaseRenderer):
    _extension = "dummy"


class ExtensionAndDefaultFilenameTestCase(unittest.TestCase):
    def test_extension_falls_back_to_dat_when_not_set(self):
        renderer = BaseRenderer({})
        self.assertEqual(renderer.extension, "dat")

    def test_extension_uses_subclass_attribute(self):
        renderer = DummyRenderer({})
        self.assertEqual(renderer.extension, "dummy")

    def test_default_filename_uses_extension(self):
        renderer = DummyRenderer({})
        self.assertTrue(renderer.default_filename.endswith(".dummy"))
        self.assertTrue(renderer.default_filename.startswith("dataset_"))


class WriteZipfileTestCase(unittest.TestCase):
    @staticmethod
    def _tmp_file(content: bytes) -> str:
        with NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(content)
            return tmp.name

    def test_writes_all_entries_with_their_alias(self):
        renderer = DummyRenderer({})
        tmp_files = [
            ("a.txt", Path(self._tmp_file(b"content a"))),
            ("b.txt", Path(self._tmp_file(b"content b"))),
        ]

        entries = [ZipFileEntry(zipfilealias=name, osfilepath=path) for name, path in tmp_files]
        zip_path = renderer.write_zipfile(entries)

        try:
            with ZipFile(zip_path) as zf:
                self.assertEqual(sorted(zf.namelist()), ["a.txt", "b.txt"])
                self.assertEqual(zf.read("a.txt"), b"content a")
                self.assertEqual(zf.read("b.txt"), b"content b")
        finally:
            zip_path.unlink(missing_ok=True)
            for _, path in tmp_files:
                path.unlink(missing_ok=True)
