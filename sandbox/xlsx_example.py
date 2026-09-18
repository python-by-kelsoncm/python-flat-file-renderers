"""XlsxRenderer: nested flattening and one sheet per dataset key.

Requires the "xlsx" extra:  pip install -e ".[xlsx]"
Run from the repository root:  python sandbox/xlsx_example.py
"""

import shutil
from pathlib import Path
from zipfile import ZipFile

from flat_file_renderers.xlsx import XlsxRenderer

OUTPUT = Path(__file__).parent / "output" / "xlsx_example.zip"

dataset = {
    "Students": [
        {"name": "Alice", "contacts": [{"phone": "1111"}, {"phone": "2222"}]},
        {"name": "Bob", "contacts": [{"phone": "3333"}]},
    ],
    "Courses": [{"title": "Python"}, {"title": "SQL"}],
}

zip_path = XlsxRenderer({}).render({"dataset": dataset})
shutil.move(zip_path, OUTPUT)

print(f"Generated: {OUTPUT}")
with ZipFile(OUTPUT) as archive:
    print(archive.namelist())
