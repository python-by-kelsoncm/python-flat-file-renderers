"""ParquetRenderer: nested flattening and one file per dataset key.

Requires the "parquet" extra:  pip install -e ".[parquet]"
Run from the repository root:  python sandbox/parquet_example.py
"""

import shutil
from pathlib import Path
from zipfile import ZipFile

from flat_file_renderers.parquet import ParquetRenderer

OUTPUT = Path(__file__).parent / "output" / "parquet_example.zip"

dataset = {
    "Students": [
        {"name": "Alice", "contacts": [{"phone": "1111"}, {"phone": "2222"}]},
        {"name": "Bob", "contacts": [{"phone": "3333"}]},
    ],
    "Courses": [{"title": "Python"}, {"title": "SQL"}],
}

zip_path = ParquetRenderer({}).render({"dataset": dataset})
shutil.move(zip_path, OUTPUT)

print(f"Generated: {OUTPUT}")
with ZipFile(OUTPUT) as archive:
    print(archive.namelist())
