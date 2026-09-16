import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

from flat_file_renderers.base import BaseRenderer, ZipFileEntry

logger = logging.getLogger(__name__)


def _serialize_item(item):
    """Duck-typed record -> plain dict/value conversion.

    Recognizes Django-style models (an object exposing `_meta.concrete_fields`) without
    importing Django, so the encoder works the same whether or not Django is installed. Any
    other non-dict object exposing `__dict__` (dataclasses, plain objects) is serialized via
    its instance attributes. Everything else (dicts, plain values) passes through unchanged -
    including values `json.dump`'s `default=str` fallback will stringify on its own
    (date/datetime/Decimal/UUID/etc. all have a sensible `__str__`).
    """
    meta = getattr(item, "_meta", None)
    concrete_fields = getattr(meta, "concrete_fields", None)
    if concrete_fields is not None:
        return {field.name: getattr(item, field.name) for field in concrete_fields}
    if not isinstance(item, dict) and hasattr(item, "__dict__"):
        return dict(vars(item))
    return item


class JsonRenderer(BaseRenderer):
    """
    Renders data as JSON.
    """

    _extension = "json"

    def render(self, context: dict[str, any], *args, **kwargs) -> Path:
        """Renders the data as JSON and writes it into a temporary zip file on disk.

        Returns:
            Path: Path to the compressed (zip) file containing the .json file(s).
        """
        if "dataset" not in context:
            raise ValueError("context must contain a 'dataset' key")

        dataset = context.get("dataset")

        def dump_json_file(data) -> Path:
            if isinstance(data, list):
                serial_data = [_serialize_item(item) for item in data]
            elif hasattr(data, "model") and hasattr(data, "__iter__"):
                serial_data = [_serialize_item(item) for item in data]
            elif isinstance(data, dict):
                serial_data = {
                    k: [_serialize_item(i) for i in v] if isinstance(v, list) else _serialize_item(v)
                    for k, v in data.items()
                }
            else:
                serial_data = _serialize_item(data)

            with NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".json") as tmp:
                json.dump(serial_data, tmp, ensure_ascii=False, default=str, indent=2)
                return Path(tmp.name)

        if isinstance(dataset, dict) and "rows" not in dataset:
            entries = []
            for table_name, table_data in dataset.items():
                slug_name = str(table_name).lower().replace(" ", "_").replace("í", "i").replace("á", "a")
                alias = f"{slug_name}.json"
                tmp_path = dump_json_file(table_data)
                entries.append(ZipFileEntry(zipfilealias=alias, osfilepath=tmp_path))
            return self.write_zipfile(entries)
        else:
            tmp_path = dump_json_file(dataset)
            return self.write_zipfile([ZipFileEntry(zipfilealias=self.default_filename, osfilepath=tmp_path)])
