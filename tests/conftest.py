import pytest
from src.infrastructure.emojis_repository import EmojisRepository


@pytest.fixture
def repository(scope="module"):
    return EmojisRepository("tests/infrastructure/data/mock_emojis_data.json")
