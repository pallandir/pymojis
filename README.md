<a name="readme-top"></a>

<br />
<div align="center">
  <h3 align="center">Pymojis</h3>

  <p align="center">
    Python package to add emojis into your python backend
    <br />
    <br />
    <a href="https://github.com/pallandir/pymojis/issues">Report Bug</a>
    ·
    <a href="https://github.com/pallandir/pymojis/issues">Request Feature</a>
  </p>
</div>

# 🎯 Pymojis

A clean, efficient Python package for managing emojis with a focus on simplicity and extensibility. Built with domain-driven design principles for scalable emoji operations.

## ✨ Features

- 🚀 **Zero Configuration** - Works out of the box with embedded emoji data
- 🔍 **Smart Search** - Search by name, category, or code with fuzzy matching
- 🎲 **Random Selection** - Get random emojis with optional category filtering
- ✅ **Validation** - Robust emoji code and character validation
- 🏗️ **Clean Architecture** - Domain-driven design with clear separation of concerns
- 🧪 **Well Tested** - Comprehensive test suite with high coverage
- 📦 **Lightweight** - Minimal dependencies, maximum performance

## 🚀 Quick Start

### Installation

```bash
pip install pymojis
```

### Basic Usage

```python
from pymojis import PymojisManager

# Initialize (uses embedded data)
manager = PymojisManager()

# Get emoji by code
smile = manager.get("smile")
print(f"{smile.emoji} - {smile.name}")  # 😀 - Smiling Face

# Search emojis
hearts = manager.search("heart", limit=5)
for emoji in hearts:
    print(f"{emoji.emoji} {emoji.name}")

# Get random emoji
random_emoji = manager.get_random()
print(f"Random: {random_emoji.emoji}")

# Get random emoji from category
face_emoji = manager.get_random(category="faces")
print(f"Random face: {face_emoji.emoji}")

# Get all categories
categories = manager.get_categories()
print(f"Available categories: {categories}")

# Validate emoji
is_valid = manager.validate("😀")
print(f"Is valid emoji: {is_valid}")

# Get statistics
stats = manager.stats()
print(f"Total emojis: {stats['total_emojis']}")
print(f"Categories: {stats['total_categories']}")
```

## 📚 API Reference

### PymojisManager

The main class for emoji operations.

#### Methods

| Method                      | Parameters                      | Returns       | Description                                       |
| --------------------------- | ------------------------------- | ------------- | ------------------------------------------------- |
| `get(code)`                 | `code: str`                     | `Emoji`       | Get emoji by code                                 |
| `get_random(category=None)` | `category: str = None`          | `Emoji`       | Get random emoji, optionally filtered by category |
| `search(query, limit=None)` | `query: str, limit: int = None` | `List[Emoji]` | Search emojis by query with optional limit        |
| `get_categories()`          | -                               | `List[str]`   | Get all available categories                      |
| `validate(emoji_char)`      | `emoji_char: str`               | `bool`        | Validate if character is a valid emoji            |
| `stats()`                   | -                               | `dict`        | Get emoji statistics and distribution             |

### Emoji Entity

Represents an emoji with the following properties:

```python
@dataclass(frozen=True)
class Emoji:
    code: str          # Unique identifier (e.g., "smile")
    name: str          # Human-readable name (e.g., "Smiling Face")
    category: str      # Category (e.g., "faces")
    emoji: str         # Unicode character (e.g., "😀")

    @property
    def unicode_code(self) -> str:
        """Get Unicode representation (e.g., 'U+1F600')"""

    def matches_search(self, query: str) -> bool:
        """Check if emoji matches search query"""
```

## 🏗️ Advanced Usage

### Custom Data Source

```python
from emoji_manager import PymojisManager

# Use custom emoji data file
manager = PymojisManager("/path/to/custom/emoji_data.json")
```

### Error Handling

```python
from emoji_manager import PymojisManager, EmojiNotFoundError, InvalidEmojiError

manager = PymojisManager()

try:
    emoji = manager.get("invalid_code")
except EmojiNotFoundError:
    print("Emoji not found!")

try:
    results = manager.search("")
except InvalidEmojiError:
    print("Invalid search query!")
```

### Working with Categories

```python
manager = PymojisManager()

# Get all categories
categories = manager.get_categories()
print("Available categories:", categories)

# Get random emoji from specific category
for category in ["faces", "nature", "objects"]:
    emoji = manager.get_random(category=category)
    print(f"{category}: {emoji.emoji} ({emoji.name})")

# Analyze category distribution
stats = manager.stats()
for category, count in stats['category_distribution'].items():
    print(f"{category}: {count} emojis")
```

### Batch Operations

```python
manager = PymojisManager()

# Search multiple queries
queries = ["love", "happy", "fire"]
all_results = []

for query in queries:
    results = manager.search(query, limit=3)
    all_results.extend(results)
    print(f"Found {len(results)} emojis for '{query}'")

# Validate multiple emojis
emoji_chars = ["😀", "❤️", "🔥", "a", "1"]
for char in emoji_chars:
    is_valid = manager.validate(char)
    print(f"'{char}' is {'valid' if is_valid else 'invalid'}")
```

## 📁 Data Format

The emoji data is stored in JSON format with the following structure:

```json
[
  {
    "code": "smile",
    "name": "Smiling Face",
    "category": "faces",
    "emoji": "😀"
  },
  {
    "code": "heart",
    "name": "Red Heart",
    "category": "symbols",
    "emoji": "❤️"
  }
]
```

### Custom Data File

To use your own emoji data, create a JSON file following the above format and pass the path to `PymojisManager`:

```python
manager = PymojisManager("/path/to/your/emoji_data.json")
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/pallandir/pymojis.git
cd pymojis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=emoji_manager --cov-report=html

# Run with verbose output
pytest -v
```

### Code Quality

```bash
install pre-commit with `pre-commit install`
```

## 🏛️ Architecture

This package follows **Domain-Driven Design** principles:

```
emoji_manager/
├── domain/           # Business logic and entities
│   ├── entities/     # Core emoji entity
│   ├── repositories/ # Data access interfaces
│   └── services/     # Business operations
├── infrastructure/   # External concerns
│   └── data/         # Data access implementations
├── application/      # Application services
└── utils/           # Utilities and helpers
```

### Key Design Principles

- **Separation of Concerns** - Each layer has a specific responsibility
- **Dependency Inversion** - Core logic doesn't depend on infrastructure
- **Single Responsibility** - Each class has one reason to change
- **Open/Closed Principle** - Easy to extend without modifying existing code

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Emoji data sourced from [Unicode Consortium](https://unicode.org/emoji/)
- Inspired by the need for clean, maintainable emoji management in Python projects
- Built with modern Python best practices and testing methodologies

## 📊 Stats

- **🎯 Zero dependencies** for core functionality
- **⚡ High performance** with O(1) lookups for most operations
- **🧪 95%+ test coverage** ensuring reliability
- **📦 Lightweight** package size under 100KB
- **🔄 Regular updates** following Unicode emoji releases

---

Made with ❤️ for the Python community. Happy emoji coding! 🎉
