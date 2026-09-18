# flat-file-renderers

[![License](https://img.shields.io/badge/License-MIT-lemon.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/pypi/pyversions/flat-file-renderers.svg)](https://pypi.org/project/flat-file-renderers/)
[![QA](https://github.com/python-by-kelsoncm/python-flat-file-renderers/actions/workflows/qa.yml/badge.svg)](https://github.com/python-by-kelsoncm/python-flat-file-renderers/actions/workflows/qa.yml)
[![Coverage](https://codecov.io/gh/python-by-kelsoncm/python-flat-file-renderers/branch/main/graph/badge.svg)](https://codecov.io/gh/python-by-kelsoncm/python-flat-file-renderers)
[![Publish](https://github.com/python-by-kelsoncm/python-flat-file-renderers/actions/workflows/publish.yml/badge.svg)](https://github.com/python-by-kelsoncm/python-flat-file-renderers/actions/workflows/publish.yml)
[![Docs](https://github.com/python-by-kelsoncm/python-flat-file-renderers/actions/workflows/docs.yml/badge.svg)](https://python-by-kelsoncm.github.io/python-flat-file-renderers/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Render tabular/nested datasets - a `list` of dicts, a `dict` of `{"rows": [...], "cols": [...]}`,
a QuerySet-like iterable, or record/model objects - into **xlsx, csv, tsv, json, html or parquet**
files, zipped. Nested lists of dicts are flattened automatically into dot+index-notation columns
(`contacts.1.phone`, `contacts.2.phone`, ...), and a `dict[str, dataset]` renders one file per key
into the same zip (one sheet per key for xlsx, one file per key for the others).

No required dependencies for csv/tsv/json/html. `xlsx` and `parquet` are optional extras.

## Installation

```bash
pip install flat-file-renderers            # csv, tsv, json, html - zero extra dependencies
pip install flat-file-renderers[xlsx]       # + openpyxl, for XlsxRenderer
pip install flat-file-renderers[parquet]    # + pyarrow, for ParquetRenderer
pip install flat-file-renderers[all]        # everything
```

## Quick start

```python
from flat_file_renderers import CsvRenderer

renderer = CsvRenderer({})
zip_path = renderer.render({"dataset": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]})
# zip_path -> Path to a .zip containing one .csv
```

```python
from flat_file_renderers.xlsx import XlsxRenderer  # requires the "xlsx" extra

renderer = XlsxRenderer({})
zip_path = renderer.render({"dataset": {"Students": [{"name": "Alice"}], "Courses": [{"title": "Python"}]}})
# zip_path -> Path to a .zip containing one .xlsx with two sheets
```

Every renderer shares the same interface (`BaseRenderer.render(context) -> Path`, where
`context["dataset"]` holds the data), so switching output formats is a one-line change:

```python
from flat_file_renderers import CsvRenderer, TsvRenderer, JsonRenderer, HtmlRenderer
from flat_file_renderers.xlsx import XlsxRenderer
from flat_file_renderers.parquet import ParquetRenderer

for Renderer in (CsvRenderer, TsvRenderer, JsonRenderer, HtmlRenderer, XlsxRenderer, ParquetRenderer):
    zip_path = Renderer({}).render({"dataset": rows})
```

Runnable examples for every renderer live in [`sandbox/`](sandbox/).

## Modules

* `flat_file_renderers.base` - `BaseRenderer`, `ZipFileEntry`
* `flat_file_renderers.flat_dict_list_helper` - `FlatDictListHelper`, the flattening engine shared
  by every renderer
* `flat_file_renderers.separated_value` - `CsvRenderer`, `TsvRenderer`
* `flat_file_renderers.json` - `JsonRenderer`
* `flat_file_renderers.html` - `HtmlRenderer`
* `flat_file_renderers.xlsx` - `XlsxRenderer` (extra: `xlsx`)
* `flat_file_renderers.parquet` - `ParquetRenderer` (extra: `parquet`)

See the [documentation](https://python-by-kelsoncm.github.io/python-flat-file-renderers/) for
details and more examples.

## Security

Please report vulnerabilities according to [SECURITY.md](SECURITY.md).

## Author

Kelson da Costa Medeiros <kelsoncm@gmail.com>
