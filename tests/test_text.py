import unittest

from flat_file_renderers.text import replace_crlf


class ReplaceCrlfTestCase(unittest.TestCase):
    def test_replaces_newline_and_carriage_return(self):
        self.assertEqual(replace_crlf("a\nb\rc"), r"a\\nb\\rc")

    def test_non_string_values_pass_through_unchanged(self):
        self.assertEqual(replace_crlf(30), 30)
        self.assertIsNone(replace_crlf(None))
