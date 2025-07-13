from src.domain.entities.emojis import Categories, Emoji
from src.infrastructure.emojis_repository import EmojisRepository


class PymojisManager:
    def __init__(self):
        self.repository = EmojisRepository(
            data_file_path="./src/infrastructure/data/emoji_data.json"
        )

    def get_random(self, category: Categories, length: int = 1) -> list[Emoji]:
        """
        Retrieve a list of random emojis.

        This method returns a list of random emojis from the dataset. You can optionally filter by specific categories and specify the number of emojis to retrieve. By default, it returns one emoji selected from all available categories.

        Args:
            categories (Optional[List[str]]): A list of category names to filter emojis by. Defaults to all categories.
            length (Optional[int]): The number of random emojis to return. Defaults to 1. Maximum is the total number of emojis available in the dataset.

        Returns:
            List[Emoji]: A list of randomly selected emoji objects.

        Example:
            >>> manager = PymojisManager()
            >>> manager.get_random(length=3)
            [Emoji(emoji='😊', name='smiling face with smiling eyes', code='1F604',category='Smiley & Emotions'), ...]
        """
        return self.repository.get_random_emojis(category, length)

    def get_all_emojis(self, exclude):
        return self.repository.get_all(exclude)

    def get_by_code(self, code: str) -> str | None:
        return self.repository.get_by_code(code)

    def get_by_name(self, name: str) -> str | None:
        return self.repository.get_by_name(name)

    def get_by_category(self, category: Categories) -> list[str]:
        return self.get_by_category(category)
