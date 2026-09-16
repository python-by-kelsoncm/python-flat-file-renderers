import logging
from html import escape
from pathlib import Path
from tempfile import NamedTemporaryFile

from flat_file_renderers.base import BaseRenderer, ZipFileEntry
from flat_file_renderers.flat_dict_list_helper import FlatDictListHelper
from flat_file_renderers.text import replace_crlf

logger = logging.getLogger(__name__)


class HtmlRenderer(BaseRenderer):
    """
    Renders data as HTML (an HTML table).
    """

    _extension = "html"

    def render(self, context: dict[str, any], *args, **kwargs) -> Path:
        """Renders the data as HTML and writes it into a temporary zip file on disk.

        Returns:
            Path: Path to the compressed (zip) file containing the .html file(s).
        """
        if "dataset" not in context:
            raise ValueError("context must contain a 'dataset' key")

        dataset = context.get("dataset")

        def dump_html_file(title: str, sub_dataset: any) -> Path:
            html_parts = [
                "<!DOCTYPE html>",
                "<html lang='en'>",
                "<head>",
                "  <meta charset='utf-8'>",
                f"  <title>{escape(str(title or 'Report'))}</title>",
                "  <style>",
                "    body { font-family: Arial, sans-serif; margin: 20px; color: #333; }",
                "    h2 { color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 5px; }",
                "    table { border-collapse: collapse; width: 100%; margin-bottom: 30px; font-size: 14px; }",
                "    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
                "    th { background-color: #f2f2f2; font-weight: bold; }",
                "    tr:nth-child(even) { background-color: #f9f9f9; }",
                "  </style>",
                "</head>",
                "<body>",
            ]
            if title:
                html_parts.append(f"<h2>{escape(str(title))}</h2>")

            rows, cols = FlatDictListHelper.flatten_dataset({"dataset": sub_dataset})
            html_parts.append("<table>")
            html_parts.append("  <thead><tr>")
            for col in cols:
                html_parts.append(f"    <th>{escape(str(col))}</th>")
            html_parts.append("  </tr></thead>")
            html_parts.append("  <tbody>")
            for row in rows:
                # `rows` always comes from FlatDictListHelper.flatten_dataset(), which always
                # produces dicts - so every row here is a dict.
                html_parts.append("    <tr>")
                for col in cols:
                    val = row.get(col, "")
                    val_str = replace_crlf(str(val)) if val is not None else ""
                    html_parts.append(f"      <td>{escape(val_str)}</td>")
                html_parts.append("    </tr>")
            html_parts.append("  </tbody>")
            html_parts.append("</table>")
            html_parts.append("</body>")
            html_parts.append("</html>")

            content = "\n".join(html_parts)
            with NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".html") as tmp:
                tmp.write(content)
                return Path(tmp.name)

        if isinstance(dataset, dict) and "rows" not in dataset:
            entries = []
            for table_name, table_data in dataset.items():
                slug_name = str(table_name).lower().replace(" ", "_").replace("í", "i").replace("á", "a")
                alias = f"{slug_name}.html"
                tmp_path = dump_html_file(table_name, table_data)
                entries.append(ZipFileEntry(zipfilealias=alias, osfilepath=tmp_path))
            return self.write_zipfile(entries)
        else:
            tmp_path = dump_html_file("Report", dataset)
            return self.write_zipfile([ZipFileEntry(zipfilealias=self.default_filename, osfilepath=tmp_path)])
