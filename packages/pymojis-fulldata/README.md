# pymojis-fulldata

Full Unicode emoji dataset shipped as a companion package to
[`pymojis`](https://pypi.org/project/pymojis/).

This package only ships data — it has no Python API. Install it together
with `pymojis` to enable the full dataset:

```bash
pip install 'pymojis[full]'
```

Then use it explicitly:

```python
from pymojis import PymojisManager

manager = PymojisManager(use_full_dataset=True)
print(len(manager.get_all_emojis()))
```

Without `use_full_dataset=True`, the lightweight bundled dataset is used.

## License

MIT — see the LICENSE file. The underlying emoji metadata is generated
from the [Unicode CLDR](https://cldr.unicode.org/) sources
([`emoji-test.txt`](https://unicode.org/Public/emoji/) and the English
annotations), licensed under the Unicode License V3.
