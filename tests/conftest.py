import pytest
from src.pymojis.application.pymojis_manager import PymojisManager
from src.pymojis.infrastructure.emojis_repository import EmojisRepository


@pytest.fixture
def repository(scope="module") -> EmojisRepository:
    return EmojisRepository("tests/infrastructure/data/mock_emojis_data.json")


@pytest.fixture
def pymoji_manager(scope="module") -> PymojisManager:
    return PymojisManager()
