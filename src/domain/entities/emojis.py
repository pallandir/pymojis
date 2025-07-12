from enum import StrEnum


class Categories(StrEnum):
    SMILEYS_EMOTION = "Smileys & Emotion"
    PEOPLE_BODY = "People & Body"
    ANIMALS_NATURE = "Animals & Nature"
    FOOD_DRINK = "Food & Drink"
    ACTIVITIES = "Activities"
    TRAVEL_PLACES = "Travel & Places"
    OBJECTS = "Objects"
    SYMBOLS = "Symbols"
    FLAGS = "Flags"
    COMPONENT = "Component"


class Emoji:
    def __init__(self, category: str, code: list[str], name: str, emoji: str) -> None:
        self.category = category
        self.code = code
        self.name = name
        self.emoji = emoji
