from typing import Literal

from pymojis.domain.entities.emojis import Categories, Emoji
from pymojis.infrastructure.pymojis_repository import PymojisRepositoryImpl


class PymojisManager:
    def __init__(self):
        self.repository = PymojisRepositoryImpl()

    def get_random(
        self,
        categories: list[Categories] | None = None,
        length: int = 1,
        exclude: Literal["complex"] | list[Categories] | None = None,
    ) -> list[Emoji]:
        """
        Retrieve a list of random emojis.

        This method returns a list of random emojis from the dataset. You can optionally filter by specific categories and specify the number of emojis to retrieve. By default, it returns one emoji selected from all available categories.

        Args:
            categories (Optional[List[str]]): A list of category names to filter emojis by. Defaults to all categories.
            length (Optional[int]): The number of random emojis to return. Defaults to 1. Maximum is the total number of emojis available in the dataset.
            exclude (Optional[Literal["complex"] | list[Categories]]):
                - If set to "complex", all complex emojis will be excluded.
                - If a list of categories is provided, emojis from those categories will be excluded.
                Defaults to None (no exclusions).
        ⚠️ The categories parameter takes precedence on exclude. If you ask for a specific category and also exclude it, get_random will still generate emojis from this category.


        Returns:
            List[Emoji]: A list of randomly selected emoji objects.

        Example:
            >>> manager = PymojisManager()
            >>> manager.get_random(length=3)
            [Emoji(emoji='😊', name='smiling face with smiling eyes', code='1F604',category='Smiley & Emotions'), ...]
        """
        return self.repository.get_random_emojis(categories, length, exclude)

    def get_all_emojis(
        self, exclude: Literal["complex"] | list[Categories] | None = None
    ) -> list[Emoji]:
        """
        Retrieve all available emojis.

        Returns a list of all emojis in the dataset. You can optionally exclude emojis based on category or complexity. Complex emojis are composed of multiple Unicode code points (e.g., skin tone modifiers, gender variants) and may not be supported on all platforms.

        Args:
            exclude (Optional[Literal["complex"] | list[Categories]]):
                - If set to "complex", all complex emojis will be excluded.
                - If a list of categories is provided, emojis from those categories will be excluded.
                Defaults to None (no exclusions).

        Returns:
            list[Emoji]: A list of emoji objects.

        Example:
            >>> manager = PymojisManager()
            >>> manager.get_all_emojis()
            [Emoji(emoji='😊', name='smiling face with smiling eyes', code='1F604', category='Smileys & Emotion'), ...]
        """
        return self.repository.get_all(exclude)

    def get_by_code(self, code: str) -> str | None:
        """
        Retrieve an emoji by its Unicode codepoint.

        This method returns the emoji character that corresponds to the given codepoint.

        Args:
            code (str): The Unicode codepoint of the emoji (e.g., "1F604").

        Returns:
            str: The emoji character associated with the given codepoint.

        Example:
            >>> manager = PymojisManager()
            >>> manager.get_by_code("1F604")
            '😄'
        """
        return self.repository.get_by_code(code)

    def get_by_name(self, name: str) -> str | None:
        """
        Retrieve an emoji by its name.

        This method returns the emoji character that corresponds to the given name.

        Args:
            name (str): The name of the emoji (e.g., "smiling face with smiling eyes").

        Returns:
            str: The emoji character associated with the given name.

        Example:
            >>> manager = PymojisManager()
            >>> manager.get_by_name("smiling face with smiling eyes")
            '😄'
        """
        return self.repository.get_by_name(name)

    def get_by_category(self, category: Categories) -> list[str]:
        """
        Retrieve all emojis by category.

        This method returns all emojis from a given category.

        Args:
            name (str): The name of the emoji (e.g., "Smileys & Emotions").

        Returns:
            list[str]: The emojis associated with a given category.

        Example:
            >>> manager = PymojisManager()
            >>> manager.get_by_category("Smileys & Emotion")
            ['😄'....]
        """
        return self.repository.get_by_category(category)

    def get_by_emoji(self, emoji: str) -> Emoji | None:
        """
        Retrieve an Emoji object by its Unicode character.

        Looks up and returns the details of the specified emoji based on its visual representation.

        Args:
            emoji (str): The Unicode emoji character to search for.

        Returns:
            Emoji | None: The corresponding Emoji object if found, otherwise None.

        Example:
            >>> manager = PymojisManager()
            >>> manager.get_by_emoji("😊")
            Emoji(emoji='😊', name='smiling face with smiling eyes', code='1F604', category='Smileys & Emotion')
        """
        return self.repository.get_by_emoji(emoji)

    def contains_emojis(self, text: str) -> bool:
        """
        Determine is a string contains any emoji.

        This method returns True if a string contains an emoji, False otherwise.

        Args:
            text (str): The text to validate.

        Returns:
            Boolean: True if contains any emoji, False otherwise.

        Example:
            >>> manager = PymojisManager()
            >>> manager.contains_emojis("This string contains emojis: 😄")
            True
        """
        return self.repository.contains_emojis(text)

    def is_emoji(self, text: str) -> bool:
        """
        Determine is a string is an emoji.

        This method returns True if a string is an emoji, False otherwise.

        Args:
            text (str): The text to validate.

        Returns:
            Boolean: True if it's an emoji, False otherwise.

        Example:
            >>> manager = PymojisManager()
            >>> manager.is_emoji("😄")
            True
        """
        return self.repository.is_emoji(text)
