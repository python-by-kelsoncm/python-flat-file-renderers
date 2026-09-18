"""flat_file_renderers - render tabular/nested datasets into xlsx, csv, tsv, json, html or
parquet files, zipped.

Only the dependency-free renderers (csv, tsv, json, html) are exported here, so importing this
package never requires openpyxl or pyarrow. XlsxRenderer and ParquetRenderer are available from
their own submodules and require the matching optional extra:

    pip install flat-file-renderers[xlsx]     # from flat_file_renderers.xlsx import XlsxRenderer
    pip install flat-file-renderers[parquet]  # from flat_file_renderers.parquet import ParquetRenderer
    pip install flat-file-renderers[all]      # both
"""

from flat_file_renderers.base import BaseRenderer, ZipFileEntry
from flat_file_renderers.flat_dict_list_helper import FlatDictListHelper
from flat_file_renderers.html import HtmlRenderer
from flat_file_renderers.json import JsonRenderer
from flat_file_renderers.separated_value import CsvRenderer, FlatDelimitedRenderer, TsvRenderer
from flat_file_renderers.text import replace_crlf

__version__ = "0.3.0"

__all__ = [
    "BaseRenderer",
    "ZipFileEntry",
    "FlatDictListHelper",
    "replace_crlf",
    "CsvRenderer",
    "TsvRenderer",
    "FlatDelimitedRenderer",
    "JsonRenderer",
    "HtmlRenderer",
]
