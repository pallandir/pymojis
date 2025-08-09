import pytest

from src.pymojis.application.pymojis_manager import PymojisManager
from src.pymojis.infrastructure.pymojis_repository import PymojisRepositoryImpl


@pytest.fixture
def repository(scope="module") -> PymojisRepositoryImpl:
    repo = PymojisRepositoryImpl()
    repo.load_emojis()
    return repo


@pytest.fixture
def manager(scope="module") -> PymojisManager:
    return PymojisManager()
