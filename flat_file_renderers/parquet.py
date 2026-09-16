import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

import pyarrow as pa
import pyarrow.parquet as pq

from flat_file_renderers.base import BaseRenderer, ZipFileEntry
from flat_file_renderers.flat_dict_list_helper import FlatDictListHelper

logger = logging.getLogger(__name__)


class ParquetRenderer(BaseRenderer):
    """
    Renders data as Apache Parquet (.parquet). Requires the ``parquet`` extra (pyarrow):
    ``pip install flat-file-renderers[parquet]``.
    """

    _extension = "parquet"

    def render(self, context: dict[str, any], *args, **kwargs) -> Path:
        """Renders the data as Apache Parquet and writes it into a temporary zip file on disk.

        Returns:
            Path: Path to the compressed (zip) file containing the .parquet file(s).
        """
        if "dataset" not in context:
            raise ValueError("context must contain a 'dataset' key")

        dataset = context.get("dataset")

        def dump_parquet_file(sub_dataset: any) -> Path:
            rows, cols = FlatDictListHelper.flatten_dataset({"dataset": sub_dataset})

            # `rows` always comes from FlatDictListHelper.flatten_dataset(), which always
            # produces dicts - so every row here is a dict.
            cleaned_rows = []
            for row in rows:
                cleaned_row = {}
                for col in cols:
                    val = row.get(col)
                    if isinstance(val, (list, dict)):
                        cleaned_row[col] = str(val)
                    else:
                        cleaned_row[col] = val
                cleaned_rows.append(cleaned_row)

            # `pa.Table.from_batches([])` requires an explicit (possibly empty) schema - without
            # one it raises "Must pass schema, or at least one RecordBatch".
            table = (
                pa.Table.from_pylist(cleaned_rows) if cleaned_rows else pa.Table.from_batches([], schema=pa.schema([]))
            )
            with NamedTemporaryFile(delete=False, suffix=".parquet") as tmp:
                pq.write_table(table, tmp.name)
                return Path(tmp.name)

        if isinstance(dataset, dict) and "rows" not in dataset:
            entries = []
            for table_name, table_data in dataset.items():
                slug_name = str(table_name).lower().replace(" ", "_").replace("í", "i").replace("á", "a")
                alias = f"{slug_name}.parquet"
                tmp_path = dump_parquet_file(table_data)
                entries.append(ZipFileEntry(zipfilealias=alias, osfilepath=tmp_path))
            return self.write_zipfile(entries)
        else:
            tmp_path = dump_parquet_file(dataset)
            return self.write_zipfile([ZipFileEntry(zipfilealias=self.default_filename, osfilepath=tmp_path)])
