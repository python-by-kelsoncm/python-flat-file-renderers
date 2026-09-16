import logging
from csv import DictWriter
from pathlib import Path
from tempfile import NamedTemporaryFile

from flat_file_renderers.base import BaseRenderer, ZipFileEntry
from flat_file_renderers.flat_dict_list_helper import FlatDictListHelper
from flat_file_renderers.text import replace_crlf

logger = logging.getLogger(__name__)


class FlatDelimitedRenderer(BaseRenderer):
    """
    Renders data as delimiter-separated values (CSV or TSV).

    This base class exports tabular data into delimiter-separated files, such as CSV (comma)
    or TSV (tab).

    The context must contain the 'dataset' key, which can be:
        - A QuerySet-like iterable: columns are inferred from the record fields.
        - A dict: must contain 'rows' (list of dicts) and 'cols' (list of column names).
        - A list: list of dicts, columns inferred from the first item's keys.

    Usage examples:
        renderer = CsvRenderer({'dataset': {'cols': ["Name", "Age"], 'rows': [{"Name": "Alice", "Age": "30"}]}})
        csv_file = renderer.render({'dataset': ...})
        with open("data.csv", "wb") as f:
            f.write(csv_file.read_bytes())

        renderer = CsvRenderer({})
        csv_file = renderer.render({'dataset': [{"Name": "Alice", "Age": "30"}, {"Name": "Bob", "Age": "25"}]})
    """

    @property
    def delimiter(self):
        """
        Returns the delimiter used to separate values.

        Returns:
            str: Delimiter (comma by default).
        """
        return getattr(self, "_delimiter", ",")

    def render(self, context: dict[str, any], *args, **kwargs) -> Path:
        """
        Renders the data as delimiter-separated values and writes it into a temporary zip file
        on disk.

        Args:
            context (dict): Dict holding the data to render. Must contain the 'dataset' key.
            *args: Extra positional arguments.
            **kwargs: Extra keyword arguments.

        Returns:
            Path: Path to the compressed (zip) file containing the delimited file(s).
        """
        dataset = context.get("dataset")
        entries = []

        if isinstance(dataset, dict) and "rows" not in dataset:
            for table_name, table_data in dataset.items():
                slug_name = str(table_name).lower().replace(" ", "_").replace("í", "i").replace("á", "a")
                alias = f"{slug_name}.{self.extension}"
                tmp = NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", newline="")
                self.__write_dsv({"dataset": table_data}, tmp)
                tmp.close()
                entries.append(ZipFileEntry(zipfilealias=alias, osfilepath=Path(tmp.name)))
            return self.write_zipfile(entries)
        else:
            with NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", newline="") as csvfile:
                logger.info("Rendering file %s with delimiter '%s'", self.default_filename, self.delimiter)
                self.__write_dsv(context, csvfile)
                logger.info("File %s rendered successfully.", self.default_filename)
                csvfile_path = Path(csvfile.name)
            # write_zipfile needs to read the file from disk: calling it while still inside the
            # "with" block would zip the file before its write buffer was flushed/closed,
            # producing an empty csv/tsv inside the zip.
            return self.write_zipfile([ZipFileEntry(zipfilealias=self.default_filename, osfilepath=csvfile_path)])

    def __write_dsv(self, context: dict[str, any], csvfile: NamedTemporaryFile):
        rows, cols = FlatDictListHelper.flatten_dataset(context)
        writer = DictWriter(csvfile, fieldnames=cols, delimiter=self.delimiter)
        writer.writeheader()
        line_num = 1
        for row in rows:
            if line_num % 500 == 1 and line_num > 1:
                logger.info("Progress: %d rows written to %s", line_num - 1, self.default_filename)
            writer.writerow({col: replace_crlf(row.get(col) or "") for col in cols})
            line_num += 1


class CsvRenderer(FlatDelimitedRenderer):
    """
    Renders data as CSV (Comma-Separated Values).

    Uses comma as delimiter and '.csv' extension.
    """

    _delimiter = ","
    _extension = "csv"


class TsvRenderer(FlatDelimitedRenderer):
    """
    Renders data as TSV (Tab-Separated Values).

    Uses tab as delimiter and '.tsv' extension.
    """

    _delimiter = "\t"
    _extension = "tsv"
