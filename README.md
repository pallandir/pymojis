# 🎭 Pymojis

[![PyPI version](https://badge.fury.io/py/pymojis.svg)](https://badge.fury.io/py/pymojis)
[![Python Support](https://img.shields.io/pypi/pyversions/pymojis.svg)](https://pypi.org/project/pymojis/)
[![License](https://img.shields.io/pypi/l/pymojis.svg)](https://github.com/yourusername/pymojis/blob/main/LICENSE)

A comprehensive and intuitive Python library for emoji manipulation, search, and transformation. Pymojis provides a clean API for working with emojis in your Python applications with support for categories, random selection, text transformation, and more.

## ✨ Features

- 🎲 **Random emoji generation** with category filtering
- 📂 **Category-based emoji organization**
- 🔍 **Search emojis** by name, code, or character
- 🎨 **Text transformation** - convert words to emojis automatically
- ✅ **Emoji detection** and validation in strings
- 🌐 **HTML conversion** with Unicode support
- 🚫 **Flexible exclusion filters** for complex emojis
- 🏗️ **Type-safe** with full type hints support

## 🚀 Installation

```bash
pip install pymojis
```

## 📋 Requirements

- Python 3.12+
- No external dependencies required

## 🎯 Quick Start

```python
from pymojis import PymojisManager

# Initialize the manager
manager = PymojisManager()

# Get random emojis
random_emojis = manager.get_random(length=3)
print([emoji.emoji for emoji in random_emojis])  # ['😊', '🎉', '🌟']

# Transform text with emojis
text = manager.emojifie("I'm feeling happy and sleepy")
print(text)  # "I'm feeling 😊 and 😪"

# Check if text contains emojis
has_emojis = manager.contains_emojis("Hello 👋 World!")
print(has_emojis)  # True
```

## 📚 API Reference

### Core Methods

#### `get_random(categories=None, length=1, exclude=None)`

Generate random emojis with optional filtering.

```python
# Get 5 random emojis
emojis = manager.get_random(length=5)

# Get random emojis from specific categories
from pymojis import Categories
happy_emojis = manager.get_random(
    categories=[Categories.SMILEYS_EMOTION],
    length=3
)

# Exclude complex emojis (multi-codepoint)
simple_emojis = manager.get_random(length=5, exclude="complex")
```

#### `get_all_emojis(exclude=None)`

Retrieve all available emojis with optional exclusions.

```python
# Get all emojis
all_emojis = manager.get_all_emojis()

# Get all except complex ones
simple_emojis = manager.get_all_emojis(exclude="complex")

# Exclude specific categories
filtered_emojis = manager.get_all_emojis(
    exclude=[Categories.SYMBOLS, Categories.FLAGS]
)
```

### Search Methods

#### `get_by_code(code)`

Find emoji by Unicode codepoint.

```python
emoji = manager.get_by_code("1F604")
print(emoji)  # "😄"
```

#### `get_by_name(name)`

Find emoji by its descriptive name.

```python
emoji = manager.get_by_name("smiling face with smiling eyes")
print(emoji)  # "😄"
```

#### `get_by_category(category)`

Get all emojis from a specific category.

```python
food_emojis = manager.get_by_category(Categories.FOOD_DRINK)
print(food_emojis[:3])  # ['🍎', '🍌', '🍇']
```

#### `get_by_emoji(emoji)`

Get detailed information about an emoji.

```python
emoji_info = manager.get_by_emoji("😊")
print(emoji_info.name)  # "smiling face with smiling eyes"
print(emoji_info.category)  # "Smileys & Emotion"
print(emoji_info.code)  # "1F60A"
```

### Text Processing

#### `emojifie(text)`

Transform text by replacing words with matching emojis.

```python
text = manager.emojifie("I love pizza and coffee")
print(text)  # "I ❤️ 🍕 and ☕"

text = manager.emojifie("Good morning! Have a great day")
print(text)  # "Good 🌅! Have a great day"
```

#### `contains_emojis(text)`

Check if text contains any emojis.

```python
result = manager.contains_emojis("Hello 👋 World!")
print(result)  # True

result = manager.contains_emojis("Just plain text")
print(result)  # False
```

#### `is_emoji(text)`

Check if a string is a single emoji.

```python
result = manager.is_emoji("😄")
print(result)  # True

result = manager.is_emoji("😄😊")
print(result)  # False
```

### Utility Methods

#### `to_html(emoji)`

Convert emoji to HTML Unicode representation.

```python
html = manager.to_html("😪")
print(html)  # "&#x1F62A;"

# Works with complex emojis too
html = manager.to_html("😵‍💫")
print(html)  # "&#x1F635;&#x200D;&#x1F4AB;"
```

## 🎨 Advanced Usage

### Working with Categories

```python
from pymojis import Categories

# Available categories
categories = [
    Categories.SMILEYS_EMOTION,
    Categories.PEOPLE_BODY,
    Categories.ANIMALS_NATURE,
    Categories.FOOD_DRINK,
    Categories.TRAVEL_PLACES,
    Categories.ACTIVITIES,
    Categories.OBJECTS,
    Categories.SYMBOLS,
    Categories.FLAGS
]

# Get emojis from multiple categories
party_emojis = manager.get_random(
    categories=[Categories.SMILEYS_EMOTION, Categories.ACTIVITIES],
    length=10
)
```

### Complex Emoji Filtering

```python
# Complex emojis include skin tones, gender variants, etc.
# Examples: 👨‍💻, 🤷‍♀️, 👋🏽

# Get only simple emojis
simple_only = manager.get_random(length=10, exclude="complex")

# Get all emojis except from specific categories
filtered = manager.get_all_emojis(
    exclude=[Categories.FLAGS, Categories.SYMBOLS]
)
```

### Batch Text Processing

```python
texts = [
    "I'm so happy today!",
    "Time for coffee break",
    "Working late tonight",
    "Weekend party time!"
]

emojified_texts = [manager.emojifie(text) for text in texts]
for original, emojified in zip(texts, emojified_texts):
    print(f"{original} -> {emojified}")
```

## 🏗️ Data Model

The `Emoji` class represents individual emoji objects:

```python
@dataclass
class Emoji:
    emoji: str          # The actual emoji character
    name: str           # Descriptive name
    code: str           # Unicode codepoint
    category: str       # Category classification
```

## ⚠️ Important Notes

- **Category Precedence**: When both `categories` and `exclude` parameters are provided, `categories` takes precedence
- **Complex Emojis**: Some emojis may not render properly on all platforms due to Unicode support variations
- **Performance**: The emoji dataset is loaded once during initialization for optimal performance

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Unicode Consortium for emoji standards
- Python community for excellent tooling and libraries

---

**Made with ❤️ for the Python community**
