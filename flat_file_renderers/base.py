import logging
from abc import abstractmethod
from datetime import datetime
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile

logger = logging.getLogger(__name__)


class ZipFileEntry:
    def __init__(self, zipfilealias: str, osfilepath: Path):
        self.zipfilealias = zipfilealias
        self.osfilepath = osfilepath


class BaseRenderer:
    """
    Base class for dataset renderers.

    Defines the interface and basic structure for concrete renderers (CSV, Excel, Parquet, etc).
    Subclasses must implement the abstract `render` method to provide the file-generation logic.

    Attributes:
        context (dict): Context dict used to render the file. May hold input data, a validated
            form, the requesting user, etc.

    Example:
        class CsvRenderer(BaseRenderer):
            def render(self, *args, **kwargs) -> BytesIO:
                ...

        renderer = CsvRenderer({'columns': ["Name", "Age"], 'rows': [{"Name": "Alice", "Age": "30"}]})
        csv_file = renderer.render()
        with open("data.csv", "wb") as f:
            f.write(csv_file.getvalue())
    """

    def __init__(self, context: dict[str, any]):
        """
        Initializes the base renderer with the given context.

        Args:
            context (dict): Context dict holding whatever the renderer needs to produce the file.
        """
        self.context = context

    @property
    def default_filename(self) -> str:
        """
        Builds a default filename from the current date/time and the renderer's extension.

        Returns:
            str: Suggested filename.
        """
        return f"dataset_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.{self.extension}"

    def write_zipfile(self, entries: list["ZipFileEntry"]) -> Path:
        """
        Compresses one or more files into a temporary ZIP file.

        Args:
            entries (list[ZipFileEntry]): Entries to compress.

        Returns:
            Path: Path to the generated ZIP file.

        Examples:
        ```python
        zip_path = renderer.write_zipfile([ZipFileEntry("data.csv", Path("/path/to/data.csv"))])

        with open(zip_path, "rb") as f:
            zip_content = f.read()

        from zipfile import ZipFile
        with ZipFile(zip_path, 'r') as zipf:
            print(zipf.namelist())
        # ['data.csv']
        ```
        """
        with NamedTemporaryFile(delete=False, suffix=".zip") as zipfilehandler:
            logger.info(
                "Creating temporary zip file to compress: %s",
                [entry.zipfilealias for entry in entries],
            )
            with ZipFile(zipfilehandler, mode="w", compression=ZIP_DEFLATED) as archive:
                for entry in entries:
                    logger.info("Adding file %s to zip as %s", entry.osfilepath, entry.zipfilealias)
                    archive.write(entry.osfilepath, arcname=entry.zipfilealias)
            logger.info("Zip file created successfully: %s", zipfilehandler.name)
            return Path(zipfilehandler.name)

    @property
    def extension(self) -> str:
        """
        Returns the default file extension produced by this renderer.

        Returns:
            str: File extension (e.g. 'csv', 'xlsx').
        """
        return getattr(self, "_extension", "dat")

    @abstractmethod
    def render(self, *args, **kwargs) -> BytesIO:
        """
        Abstract method that renders the data and produces the file.

        Subclasses must implement this to provide the format-specific generation logic.

        Returns:
            BytesIO: In-memory generated file.
        """
        ...
