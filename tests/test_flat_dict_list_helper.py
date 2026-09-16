import unittest

from flat_file_renderers.flat_dict_list_helper import FlatDictListHelper


class Record:
    """Plain object (no dict) to exercise the duck-typed __dict__ record path."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ExtractRowsAndColumnsTestCase(unittest.TestCase):
    def test_dataset_as_list(self):
        rows, cols = FlatDictListHelper.extract_rows_and_columns({"dataset": [{"name": "Alice"}]})
        self.assertEqual(rows, [{"name": "Alice"}])
        self.assertEqual(cols, [])

    def test_dataset_as_tuple(self):
        rows, cols = FlatDictListHelper.extract_rows_and_columns({"dataset": ({"name": "Alice"},)})
        self.assertEqual(rows, [{"name": "Alice"}])

    def test_dataset_as_dict_with_rows_and_cols(self):
        dataset = {"rows": [{"name": "Alice"}], "cols": ["name"]}
        rows, cols = FlatDictListHelper.extract_rows_and_columns({"dataset": dataset})
        self.assertEqual(rows, [{"name": "Alice"}])
        self.assertEqual(cols, ["name"])

    def test_dataset_as_generic_iterable(self):
        def gen():
            yield {"name": "Alice"}
            yield {"name": "Bob"}

        rows, cols = FlatDictListHelper.extract_rows_and_columns({"dataset": gen()})
        self.assertEqual(rows, [{"name": "Alice"}, {"name": "Bob"}])
        self.assertEqual(cols, [])

    def test_missing_dataset_key_raises(self):
        with self.assertRaises(ValueError):
            FlatDictListHelper.extract_rows_and_columns({})

    def test_unsupported_dataset_type_raises(self):
        with self.assertRaises(ValueError):
            FlatDictListHelper.extract_rows_and_columns({"dataset": "not-a-valid-dataset"})

    def test_none_dataset_raises(self):
        with self.assertRaises(ValueError):
            FlatDictListHelper.extract_rows_and_columns({"dataset": None})


class ExpandRowTestCase(unittest.TestCase):
    def test_simple_values_are_untouched(self):
        row = {"name": "Alice", "age": 30}
        self.assertEqual(FlatDictListHelper.expand_row(row), row)

    def test_expands_list_of_dicts_with_dot_index_notation(self):
        row = {"name": "Alice", "contacts": [{"phone": "1234"}, {"phone": "5678"}]}
        expected = {"name": "Alice", "contacts.1.phone": "1234", "contacts.2.phone": "5678"}
        self.assertEqual(FlatDictListHelper.expand_row(row), expected)

    def test_list_of_non_dicts_is_kept_as_is(self):
        row = {"name": "Alice", "tags": ["a", "b"]}
        self.assertEqual(FlatDictListHelper.expand_row(row), row)

    def test_empty_list_is_kept_as_is(self):
        row = {"name": "Alice", "contacts": []}
        self.assertEqual(FlatDictListHelper.expand_row(row), row)


class DeepFlattenTestCase(unittest.TestCase):
    def test_expands_list_of_dicts(self):
        row = {"name": "Alice", "contacts": [{"phone": "1234"}, {"phone": "5678"}]}
        expected = {"name": "Alice", "contacts.1.phone": "1234", "contacts.2.phone": "5678"}
        self.assertEqual(FlatDictListHelper.deep_flatten(row), expected)

    def test_flattens_nested_dict_with_dot_notation(self):
        row = {"name": "Alice", "address": {"street": "Street A", "number": 10}}
        expected = {"name": "Alice", "address.street": "Street A", "address.number": 10}
        self.assertEqual(FlatDictListHelper.deep_flatten(row), expected)

    def test_flattens_dict_nested_inside_expanded_list(self):
        row = {"contacts": [{"address": {"street": "Street A"}}]}
        expected = {"contacts.1.address.street": "Street A"}
        self.assertEqual(FlatDictListHelper.deep_flatten(row), expected)


class NormalizeKeyTestCase(unittest.TestCase):
    def test_replaces_double_underscore_with_dot(self):
        self.assertEqual(FlatDictListHelper.normalize_key("address__street"), "address.street")
        self.assertEqual(
            FlatDictListHelper.normalize_key("person__contacts__1__phone"),
            "person.contacts.1.phone",
        )

    def test_key_without_double_underscore_is_untouched(self):
        self.assertEqual(FlatDictListHelper.normalize_key("name"), "name")


class ExtractFlatColumnsTestCase(unittest.TestCase):
    def test_simple_rows(self):
        rows = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        self.assertEqual(FlatDictListHelper.extract_flat_columns(rows), ["age", "name"])

    def test_expands_list_of_dicts_columns_per_row_using_the_max_length_seen(self):
        rows = [
            {"name": "Alice", "contacts": [{"phone": "1234"}, {"phone": "5678"}]},
            {"name": "Bob", "contacts": [{"phone": "9999"}]},
        ]
        cols = FlatDictListHelper.extract_flat_columns(rows)
        self.assertEqual(cols, ["contacts.1.phone", "contacts.2.phone", "name"])

    def test_normalizes_double_underscore_keys(self):
        rows = [{"address__street": "Street A"}]
        self.assertEqual(FlatDictListHelper.extract_flat_columns(rows), ["address.street"])

    def test_accepts_record_objects_via_dict(self):
        rows = [Record(name="Alice", age=30)]
        self.assertEqual(FlatDictListHelper.extract_flat_columns(rows), ["age", "name"])


class FlattenDatasetTestCase(unittest.TestCase):
    def test_flattens_rows_and_returns_sorted_columns(self):
        context = {
            "dataset": [
                {"name": "Bob", "contacts": [{"phone": "9999"}]},
                {"name": "Alice", "contacts": [{"phone": "1234"}, {"phone": "5678"}]},
            ]
        }
        rows, cols = FlatDictListHelper.flatten_dataset(context)
        self.assertEqual(cols, sorted(cols))
        self.assertEqual(
            rows,
            [
                {"name": "Bob", "contacts.1.phone": "9999"},
                {"name": "Alice", "contacts.1.phone": "1234", "contacts.2.phone": "5678"},
            ],
        )

    def test_dataset_as_dict_with_rows_key(self):
        context = {"dataset": {"rows": [{"name": "Alice"}], "cols": ["name"]}}
        rows, cols = FlatDictListHelper.flatten_dataset(context)
        self.assertEqual(rows, [{"name": "Alice"}])
        self.assertEqual(cols, ["name"])

    def test_accepts_record_objects(self):
        context = {"dataset": [Record(name="Alice", age=30)]}
        rows, cols = FlatDictListHelper.flatten_dataset(context)
        self.assertEqual(rows, [{"name": "Alice", "age": 30}])
        self.assertEqual(cols, ["age", "name"])
