flat_file_renderers
====================
Render tabular/nested datasets (list, dict, QuerySet-like iterables, or record objects)
into xlsx, csv, tsv, json, html or parquet files, zipped - with zero required dependencies.

.. image:: https://img.shields.io/badge/GitHub-Repository-blue?logo=github
   :target: https://github.com/python-by-kelsoncm/python-flat-file-renderers
   :alt: GitHub Repository

.. image:: https://img.shields.io/badge/License-MIT-lemon.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

.. image:: https://img.shields.io/pypi/pyversions/flat-file-renderers.svg
   :target: https://pypi.org/project/flat-file-renderers/
   :alt: Python

.. image:: https://github.com/python-by-kelsoncm/python-flat-file-renderers/actions/workflows/qa.yml/badge.svg
   :target: https://github.com/python-by-kelsoncm/python-flat-file-renderers/actions/workflows/qa.yml
   :alt: QA

.. image:: https://codecov.io/gh/python-by-kelsoncm/python-flat-file-renderers/branch/main/graph/badge.svg
   :target: https://github.com/python-by-kelsoncm/python-flat-file-renderers
   :alt: Coverage

.. image:: https://github.com/python-by-kelsoncm/python-flat-file-renderers/actions/workflows/publish.yml/badge.svg
   :target: https://github.com/python-by-kelsoncm/python-flat-file-renderers/actions/workflows/publish.yml
   :alt: Publish

.. image:: https://github.com/python-by-kelsoncm/python-flat-file-renderers/actions/workflows/docs.yml/badge.svg
   :target: https://python-by-kelsoncm.github.io/python-flat-file-renderers/
   :alt: Docs

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit


Installation
------------

.. code-block:: bash

    pip install flat-file-renderers            # csv, tsv, json, html
    pip install flat-file-renderers[xlsx]       # + Excel
    pip install flat-file-renderers[parquet]    # + Apache Parquet
    pip install flat-file-renderers[all]        # everything

Modules
-------

* :doc:`flat_file_renderers.base <flat_file_renderers.base>` - ``BaseRenderer``, ``ZipFileEntry``
* :doc:`flat_file_renderers.flat_dict_list_helper <flat_file_renderers.flat_dict_list_helper>` - flattens nested
  dicts/lists into tabular rows and columns
* :doc:`flat_file_renderers.separated_value <flat_file_renderers.separated_value>` - ``CsvRenderer``, ``TsvRenderer``
* :doc:`flat_file_renderers.json <flat_file_renderers.json>` - ``JsonRenderer``
* :doc:`flat_file_renderers.html <flat_file_renderers.html>` - ``HtmlRenderer``
* :doc:`flat_file_renderers.xlsx <flat_file_renderers.xlsx>` - ``XlsxRenderer`` (extra: ``xlsx``)
* :doc:`flat_file_renderers.parquet <flat_file_renderers.parquet>` - ``ParquetRenderer`` (extra: ``parquet``)

Quick start
-----------

.. code-block:: python

    from flat_file_renderers import CsvRenderer

    renderer = CsvRenderer({})
    zip_path = renderer.render({"dataset": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]})
    # zip_path -> Path to a .zip containing one .csv

Nested data is flattened automatically (``contacts.1.phone``, ``contacts.2.phone``, ...), and a
``dict[str, dataset]`` renders one file per key, zipped together:

.. code-block:: python

    from flat_file_renderers.xlsx import XlsxRenderer  # extra: xlsx

    renderer = XlsxRenderer({})
    zip_path = renderer.render({"dataset": {"Students": [...], "Courses": [...]}})
    # zip_path -> Path to a .zip containing one .xlsx with two sheets

Next steps
----------

.. toctree::
   :maxdepth: 1

   flat_file_renderers
