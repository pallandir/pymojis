from src.infrastructure.emojis_repository import EmojisRepository
from src.domain.entities.emojis import Emoji


def test_emoji_repository_get_all(repository):
    repository = EmojisRepository(
        data_file_path="tests/infrastructure/data/mock_emojis_data.json"
    )
    result = repository.get_all(None)
    assert isinstance(result[0], Emoji)


def test_emoji_repositiry_get_by_code():
    pass
