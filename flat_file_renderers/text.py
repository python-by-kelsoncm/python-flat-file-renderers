def replace_crlf(val: str) -> str:
    """Replaces embedded newline/carriage-return characters with a visible ``\\n``/``\\r`` marker.

    Useful before writing a value into a single tabular cell (CSV/TSV/XLSX/HTML), where a raw
    embedded line break would otherwise corrupt the row layout.
    """
    return val.replace("\n", r"\\n").replace("\r", r"\\r") if isinstance(val, str) else val
