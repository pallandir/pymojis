from src.domain.entities.emojis import Categories
from src.infrastructure.emojis_repository import EmojisRepository


class PymojisManager:
    def __init__(self):
        self.repository = EmojisRepository(
            data_file_path="./src/infrastructure/data/emoji_data.json"
        )

    def get_random(self, category: Categories, length=1):
        return self.repository.get_random_emojis(category, length)

    def get_all_emojis(self, exclude):
        return self.repository.get_all(exclude)

    def get_by_code(self, code: str) -> str | None:
        return self.repository.get_by_code(code)

    def get_by_name(self, name: str) -> str | None:
        return self.repository.get_by_name(name)

    def get_by_category(self, category: Categories) -> list[str]:
        return self.get_by_category(category)
