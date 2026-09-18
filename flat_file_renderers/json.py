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
    Renders data as JSON Lines (a.k.a. NDJSON): one compact JSON object per line.

    The same layout used by the OpenSearch/Elasticsearch bulk API. Consumers can read the file
    line by line instead of loading it whole, and the renderer itself writes record by record
    without materializing the dataset as a list.
    """

    _extension = "jsonl"

    def render(self, context: dict[str, any], *args, **kwargs) -> Path:
        """Renders the data as JSON Lines and writes it into a temporary zip file on disk.

        Lists and QuerySet-like iterables produce one line per record. Any other dataset (a single
        record, or a dict with a "rows" key) produces a single line.

        Returns:
            Path: Path to the compressed (zip) file containing the .jsonl file(s).
        """
        if "dataset" not in context:
            raise ValueError("context must contain a 'dataset' key")

        dataset = context.get("dataset")

        def dump_line(tmp, obj) -> None:
            json.dump(obj, tmp, ensure_ascii=False, default=str, separators=(",", ":"))
            tmp.write("\n")

        def dump_json_file(data) -> Path:
            with NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", newline="\n", suffix=".jsonl") as tmp:
                if isinstance(data, list) or (hasattr(data, "model") and hasattr(data, "__iter__")):
                    for item in data:
                        dump_line(tmp, _serialize_item(item))
                elif isinstance(data, dict):
                    dump_line(
                        tmp,
                        {
                            k: [_serialize_item(i) for i in v] if isinstance(v, list) else _serialize_item(v)
                            for k, v in data.items()
                        },
                    )
                else:
                    dump_line(tmp, _serialize_item(data))
                return Path(tmp.name)

        if isinstance(dataset, dict) and "rows" not in dataset:
            entries = []
            for table_name, table_data in dataset.items():
                slug_name = str(table_name).lower().replace(" ", "_").replace("í", "i").replace("á", "a")
                alias = f"{slug_name}.jsonl"
                tmp_path = dump_json_file(table_data)
                entries.append(ZipFileEntry(zipfilealias=alias, osfilepath=tmp_path))
            return self.write_zipfile(entries)
        else:
            tmp_path = dump_json_file(dataset)
            return self.write_zipfile([ZipFileEntry(zipfilealias=self.default_filename, osfilepath=tmp_path)])
