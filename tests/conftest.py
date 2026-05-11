import pytest

from pymojis import PymojisManager
from pymojis.infrastructure.pymojis_repository import PymojisRepositoryImpl


@pytest.fixture
def repository() -> PymojisRepositoryImpl:
    repo = PymojisRepositoryImpl()
    repo.load_emojis()
    return repo


@pytest.fixture
def manager() -> PymojisManager:
    return PymojisManager()
