"""CsvRenderer: nested flattening and one file per dataset key.

Run from the repository root:  python sandbox/csv_example.py
"""

import shutil
from pathlib import Path
from zipfile import ZipFile

from flat_file_renderers import CsvRenderer

OUTPUT = Path(__file__).parent / "output" / "csv_example.zip"

dataset = {
    "Students": [
        {"name": "Alice", "contacts": [{"phone": "1111"}, {"phone": "2222"}]},
        {"name": "Bob", "contacts": [{"phone": "3333"}]},
    ],
    "Courses": [{"title": "Python"}, {"title": "SQL"}],
}

zip_path = CsvRenderer({}).render({"dataset": dataset})
shutil.move(zip_path, OUTPUT)

print(f"Generated: {OUTPUT}")
with ZipFile(OUTPUT) as archive:
    for name in archive.namelist():
        print(f"--- {name}")
        print(archive.read(name).decode("utf-8"))
