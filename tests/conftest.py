import pytest

from src.pymojis.application.pymojis_manager import PymojisManager
from src.pymojis.infrastructure.pymojis_repository import PymojisRepositoryImpl


@pytest.fixture
def repository(scope="module") -> PymojisRepositoryImpl:
    return PymojisRepositoryImpl("tests/infrastructure/data/mock_emojis_data.json")


@pytest.fixture
def manager(scope="module") -> PymojisManager:
    return PymojisManager()
