import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

from openpyxl import Workbook

from flat_file_renderers.base import BaseRenderer, ZipFileEntry
from flat_file_renderers.flat_dict_list_helper import FlatDictListHelper
from flat_file_renderers.text import replace_crlf

logger = logging.getLogger(__name__)


class XlsxRenderer(BaseRenderer):
    """
    Renders data as XLSX (Excel). Requires the ``xlsx`` extra (openpyxl):
    ``pip install flat-file-renderers[xlsx]``.
    """

    _extension = "xlsx"

    def render(self, context: dict[str, any], *args, **kwargs) -> Path:
        """Renders the data as XLSX and writes it into a temporary zip file on disk.

        Returns:
            Path: Path to the compressed (zip) file containing the .xlsx file.
        """
        dataset = context.get("dataset")
        wb = Workbook()

        if isinstance(dataset, dict) and "rows" not in dataset:
            first = True
            for sheet_name, sheet_data in dataset.items():
                if first:
                    ws = wb.active
                    ws.title = str(sheet_name)[:31]
                    first = False
                else:
                    ws = wb.create_sheet(title=str(sheet_name)[:31])

                rows, cols = FlatDictListHelper.flatten_dataset({"dataset": sheet_data})
                ws.append(cols)

                # `rows` always comes from FlatDictListHelper.flatten_dataset(), which always
                # produces dicts - so every row here is a dict.
                for row in rows:
                    ws.append(
                        [replace_crlf(str(row.get(col, "") or "")) if row.get(col) is not None else "" for col in cols]
                    )
        else:
            ws = wb.active
            rows, cols = FlatDictListHelper.flatten_dataset(context)
            ws.append(cols)

            for row in rows:
                ws.append(
                    [replace_crlf(str(row.get(col, "") or "")) if row.get(col) is not None else "" for col in cols]
                )

        with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            wb.save(tmp.name)
            tmp_path = Path(tmp.name)

        return self.write_zipfile([ZipFileEntry(zipfilealias=self.default_filename, osfilepath=tmp_path)])
