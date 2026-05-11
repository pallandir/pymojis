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

MIT — see the LICENSE file. The underlying emoji metadata is derived from
the [emoji-test data](https://unicode.org/Public/emoji/) maintained by the
Unicode Consortium and the work of Chalda Pnuzig (ISC License, see
`third_party/`).
