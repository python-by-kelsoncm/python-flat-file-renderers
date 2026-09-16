import json
import unittest
from zipfile import ZipFile

from flat_file_renderers.json import JsonRenderer


class Record:
    """Plain object exercising the duck-typed __dict__ record path."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeConcreteField:
    def __init__(self, name):
        self.name = name


class FakeMeta:
    def __init__(self, field_names):
        self.concrete_fields = [FakeConcreteField(n) for n in field_names]


class FakeModel:
    """Duck-typed stand-in for a Django model instance (exposes _meta.concrete_fields)."""

    def __init__(self, **kwargs):
        self._meta = FakeMeta(list(kwargs.keys()))
        for k, v in kwargs.items():
            setattr(self, k, v)


class JsonRendererTestCase(unittest.TestCase):
    def test_renders_list_dataset_as_json(self):
        renderer = JsonRenderer({})
        context = {"dataset": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                names = zf.namelist()
                self.assertEqual(len(names), 1)
                self.assertTrue(names[0].endswith(".json"))
                data = json.loads(zf.read(names[0]))
            self.assertEqual(data, context["dataset"])
        finally:
            zip_path.unlink(missing_ok=True)

    def test_missing_dataset_key_raises(self):
        renderer = JsonRenderer({})
        with self.assertRaises(ValueError):
            renderer.render({})

    def test_multi_table_dataset_creates_one_file_per_key(self):
        renderer = JsonRenderer({})
        context = {"dataset": {"Students": [{"name": "Alice"}], "Courses": [{"title": "Python"}]}}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                self.assertEqual(sorted(zf.namelist()), ["courses.json", "students.json"])
                self.assertEqual(json.loads(zf.read("students.json")), [{"name": "Alice"}])
                self.assertEqual(json.loads(zf.read("courses.json")), [{"title": "Python"}])
        finally:
            zip_path.unlink(missing_ok=True)

    def test_non_ascii_content_is_preserved(self):
        renderer = JsonRenderer({})
        context = {"dataset": [{"name": "José"}]}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                raw = zf.read(zf.namelist()[0]).decode("utf-8")
                self.assertIn("José", raw)
                data = json.loads(raw)
            self.assertEqual(data, [{"name": "José"}])
        finally:
            zip_path.unlink(missing_ok=True)

    def test_plain_object_records_are_serialized_via_dict(self):
        renderer = JsonRenderer({})
        context = {"dataset": [Record(name="Alice", age=30)]}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                data = json.loads(zf.read(zf.namelist()[0]))
            self.assertEqual(data, [{"name": "Alice", "age": 30}])
        finally:
            zip_path.unlink(missing_ok=True)

    def test_django_style_model_records_use_meta_concrete_fields(self):
        renderer = JsonRenderer({})
        context = {"dataset": [FakeModel(name="Alice", age=30)]}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                data = json.loads(zf.read(zf.namelist()[0]))
            self.assertEqual(data, [{"name": "Alice", "age": 30}])
        finally:
            zip_path.unlink(missing_ok=True)

    def test_queryset_like_iterable_of_records(self):
        class FakeQuerySet:
            model = FakeModel

            def __init__(self, items):
                self._items = items

            def __iter__(self):
                return iter(self._items)

        renderer = JsonRenderer({})
        context = {"dataset": FakeQuerySet([Record(name="Alice")])}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                data = json.loads(zf.read(zf.namelist()[0]))
            self.assertEqual(data, [{"name": "Alice"}])
        finally:
            zip_path.unlink(missing_ok=True)

    def test_rows_cols_shaped_dataset_serializes_its_dict_values(self):
        renderer = JsonRenderer({})
        context = {"dataset": {"rows": [{"name": "Alice"}], "cols": ["name"]}}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                data = json.loads(zf.read(zf.namelist()[0]))
            self.assertEqual(data, {"rows": [{"name": "Alice"}], "cols": ["name"]})
        finally:
            zip_path.unlink(missing_ok=True)

    def test_single_non_list_non_dict_dataset_is_serialized_directly(self):
        renderer = JsonRenderer({})
        context = {"dataset": Record(name="Alice")}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                data = json.loads(zf.read(zf.namelist()[0]))
            self.assertEqual(data, {"name": "Alice"})
        finally:
            zip_path.unlink(missing_ok=True)

    def test_unrecognized_object_falls_back_to_str(self):
        class NoDict:
            __slots__ = ()

            def __str__(self):
                return "no-dict-as-string"

        renderer = JsonRenderer({})
        context = {"dataset": [{"value": NoDict()}]}
        zip_path = renderer.render(context)
        try:
            with ZipFile(zip_path) as zf:
                data = json.loads(zf.read(zf.namelist()[0]))
            self.assertEqual(data, [{"value": "no-dict-as-string"}])
        finally:
            zip_path.unlink(missing_ok=True)
