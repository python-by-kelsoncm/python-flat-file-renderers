# Sandbox

Runnable examples of every renderer, useful as a playground while developing and as copy/paste
material for the community. Each script is self-contained.

## Setup

From the repository root:

```bash
pip install -e ".[all]"
```

The csv, tsv, json and html examples need no extras. `xlsx_example.py` needs the `xlsx` extra and
`parquet_example.py` needs the `parquet` extra.

## Running

```bash
python sandbox/csv_example.py
python sandbox/tsv_example.py
python sandbox/json_example.py
python sandbox/html_example.py
python sandbox/xlsx_example.py
python sandbox/parquet_example.py
```

Each script renders a dataset with a nested list (flattened into `contacts.1.phone`,
`contacts.2.phone`, ... by the tabular renderers; `JsonRenderer` keeps the nesting) and two keys
(`Students`, `Courses`), then moves the generated zip to
`sandbox/output/<renderer>_example.zip`. The contents of `sandbox/output/` are ignored by git.
