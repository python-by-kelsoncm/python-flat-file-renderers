from typing import Any


def _as_plain_dict(row: Any) -> Any:
    """Returns `row` as a plain dict when it looks like a model/record instance.

    Duck-typed on purpose: rather than importing Django (or any other ORM) to `isinstance`-check
    for a `Model`, any non-dict object exposing `__dict__` (Django models, dataclasses without
    `__slots__`, plain objects, etc.) is treated as a record and flattened via its `__dict__`.
    Dicts and anything without `__dict__` (namedtuples, plain values) pass through unchanged.
    """
    if not isinstance(row, dict) and hasattr(row, "__dict__"):
        return row.__dict__
    return row


class FlatDictListHelper:
    """
    Helper for renderers that deal with lists of plain dicts (or dict-like records), without
    deeply nested structures.

    Provides methods to expand lists of dicts into flat columns and to normalize keys, so that
    renderers can handle tabular data consistently and without naming collisions. Particularly
    useful for renderers like CSV/TSV, which need to turn complex data into simple tabular rows.
    """

    @staticmethod
    def extract_rows_and_columns(context: dict[str, Any]) -> tuple[list[Any], list[str]]:
        """
        Extracts the rows and columns of a dataset present in the rendering context.

        Accepts a dataset shaped as a dict (with 'rows'/'cols'), a list, or any other iterable
        (e.g. a Django QuerySet or generator) - duck-typed via `__iter__`, no ORM import needed.

        Args:
            context (dict): Context containing the 'dataset' key.

        Returns:
            tuple[list, list]: Tuple of (rows, column names - if available).

        Raises:
            ValueError: If the context has no 'dataset' key, or its type isn't supported.
        """
        if "dataset" not in context:
            raise ValueError("context must contain a 'dataset' key")

        dataset = context.get("dataset", None)

        if isinstance(dataset, dict):
            rows: list[Any] = dataset.get("rows", [])
        elif isinstance(dataset, (list, tuple)):
            rows = list(dataset)
        elif dataset is not None and not isinstance(dataset, (str, bytes)) and hasattr(dataset, "__iter__"):
            rows = list(dataset)
        else:
            raise ValueError("dataset must be a QuerySet-like iterable, dict, or list")

        cols: list[str] = dataset.get("cols", []) if isinstance(dataset, dict) else []
        return rows, cols

    @staticmethod
    def deep_flatten(row: dict, parent_key: str = "") -> dict:
        """
        Recursively expands nested dicts and lists of dicts into a flat dict, using dot notation
        for nested keys.

        Args:
            row (dict): Data row, possibly containing plain values, lists of dicts, or nested dicts.
            parent_key (str): Key prefix (used during recursion).

        Returns:
            dict: Flat dict with all keys expanded.

        Example:
            deep_flatten({"name": "Alice", "contacts": [{"phone": "1234"}, {"phone": "5678"}]})
            -> {"name": "Alice", "contacts.1.phone": "1234", "contacts.2.phone": "5678"}
        """
        items = {}
        flat = FlatDictListHelper.expand_row(row)
        for k, v in flat.items():
            new_key = f"{parent_key}.{k}" if parent_key else str(k)
            if isinstance(v, dict):
                items.update(FlatDictListHelper.deep_flatten(v, new_key))
            else:
                items[new_key] = v
        return items

    @staticmethod
    def extract_flat_columns(rows: list) -> list[str]:
        """
        Given a list of dicts (or record objects), returns the list of flat, normalized columns,
        including columns expanded from lists of dicts.

        Args:
            rows (list): List of dicts or record/model objects representing the data rows.

        Returns:
            list[str]: List of column names, including columns expanded from lists of dicts,
                with normalized keys.

        Example:
            rows = [
                {"name": "Alice", "contacts": [{"phone": "1234"}, {"phone": "5678"}]},
                {"name": "Bob", "addresses": [{"street": "Street A"}, {"street": "Street B"}]}
            ]
            # Output: ["name", "contacts.1.phone", "contacts.2.phone", "addresses.1.street", "addresses.2.street"]
        """
        list_dict_max = {}  # key: max_len
        list_dict_keys = {}  # key: set(subkeys)
        for row in rows:
            row = _as_plain_dict(row)
            for key, value in row.items():
                if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
                    list_dict_max[key] = max(list_dict_max.get(key, 0), len(value))
                    subkeys = set()
                    for item in value:
                        subkeys.update(item.keys())
                    if key not in list_dict_keys:
                        list_dict_keys[key] = set()
                    list_dict_keys[key].update(subkeys)

        cols = set()
        for row in rows:
            row = _as_plain_dict(row)
            flat = FlatDictListHelper.expand_row(row)
            for key in flat.keys():
                if key not in list_dict_max:
                    cols.add(FlatDictListHelper.normalize_key(key))
        for key, max_len in list_dict_max.items():
            for idx in range(1, max_len + 1):
                for subkey in list_dict_keys[key]:
                    cols.add(FlatDictListHelper.normalize_key(f"{key}.{idx}.{subkey}"))
        return sorted(cols)

    @staticmethod
    def expand_row(row: dict) -> dict:
        """
        Expands lists of dicts into flat columns.

        Discovers all columns, including expanded lists of dicts, and normalizes keys to avoid
        collisions. Lists of dicts are expanded into dot+index-notation columns, and keys are
        normalized by replacing '__' with '.'.

        Args:
            row (dict): Data row, holding plain values or lists of dicts.

        Returns:
            dict: Flat dict where lists of dicts have been expanded into dot+index-notation columns.

        Example:
            expand_row({"name": "Alice", "contacts": [{"phone": "1234"}, {"phone": "5678"}]})
            -> {"name": "Alice", "contacts.1.phone": "1234", "contacts.2.phone": "5678"}
        """
        flat = {}
        for key, value in row.items():
            if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
                for idx, item in enumerate(value, 1):
                    for subkey, subval in item.items():
                        flat[f"{key}.{idx}.{subkey}"] = subval
            else:
                flat[key] = value
        return flat

    @staticmethod
    def normalize_key(key: str) -> str:
        """
        Replaces '__' with '.' in keys, to avoid clashing with the list-of-dicts dot notation.

        Args:
            key (str): Key to normalize.

        Returns:
            str: Normalized key, with '__' replaced by '.'.

        Example:
            normalize_key("address__street") -> "address.street"
            normalize_key("person__contacts__1__phone") -> "person.contacts.1.phone"
        """
        return key.replace("__", ".")

    @staticmethod
    def flatten_dataset(context: dict[str, Any]) -> tuple[list[dict], list[str]]:
        """
        Returns a flat version of the context's dataset, with all rows and columns expanded and
        normalized.

        Args:
            context (dict): Context containing the 'dataset' key.

        Returns:
            tuple[list[dict], list[str]]: List of flat rows and list of column names.
        """
        flattened_rows = []
        all_keys = set()
        rows, _ = FlatDictListHelper.extract_rows_and_columns(context)
        for row in rows:
            row = _as_plain_dict(row)
            flat = FlatDictListHelper.deep_flatten(row)
            normalized_flat = {FlatDictListHelper.normalize_key(k): v for k, v in flat.items()}
            flattened_rows.append(normalized_flat)
            all_keys.update(normalized_flat.keys())

        cols = list(all_keys)
        cols.sort()
        return flattened_rows, cols
