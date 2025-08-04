import logging
from dataclasses import dataclass
from typing import Any

from ..exceptions import DatasetNotFoundError
from .file_loader import FileLoader


@dataclass
class DatasetConfig:
    module: str
    filename: str
    dataset_type: str


class EmojiDataLoader:
    # Default dataset configurations in order of preference
    DEFAULT_DATASETS = [
        DatasetConfig("pymojis.infrastructure.data", "emoji_data.json", "light"),
        DatasetConfig("pymojis_fulldata.data", "full_emoji_data.json", "full"),
    ]

    def __init__(
        self,
        file_loader: FileLoader,
        dataset_configs: list[DatasetConfig] | None = None,
    ):
        self.file_loader = file_loader
        self.dataset_configs = dataset_configs or self.DEFAULT_DATASETS
        self.logger = logging.getLogger(__name__)

    def load_from_path(self, path: str) -> dict[str, Any]:
        """
        Load emoji data from custom file path.

        Args:
            path: File path to emoji data

        Returns:
            Raw emoji data dictionary
        """
        return self.file_loader.load_json_file(path)

    def load_from_default_sources(self) -> dict[str, Any]:
        """
        Load emoji data from default sources with fallback.

        Returns:
            Raw emoji data dictionary

        Raises:
            DatasetNotFoundError: If no dataset can be loaded
        """
        last_error = None

        for config in self.dataset_configs:
            try:
                data = self.file_loader.load_json_from_package(
                    config.module, config.filename
                )
                self.logger.info(f"Loaded {config.dataset_type} emoji dataset")
                return data

            except Exception as e:
                self.logger.debug(f"Failed to load {config.dataset_type} dataset: {e}")
                last_error = e
                continue

        raise DatasetNotFoundError(
            f"No emoji dataset could be loaded. Last error: {last_error}"
        )
