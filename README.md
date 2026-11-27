# tugaphone: dialect-aware Portuguese phonemizer
<!-- agent-hint
covers: what tugaphone does, how to install it, a first call and where the documentation starts
source: tugaphone/__init__.py, tugaphone/lattice_core.py, tugaphone/__main__.py, pyproject.toml
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py README.md
see: docs/index.md, docs/quickstart.md, AGENTS.md
-->

**tugaphone** turns Portuguese text into IPA, and it does it per Lusophone
dialect. Give it a sentence and a dialect code, get back a phoneme string with
stress marks. It drives the
[orthography2ipa](https://github.com/TigreGotico/orthography2ipa) candidate
lattice and adds old-spelling conversion, text normalization, number expansion
and homograph marking.

Try it in your browser: [TigreGotico/tugaphone on Hugging Face](https://huggingface.co/spaces/TigreGotico/tugaphone).

## Install

```bash
uv pip install --prerelease=allow tugaphone
```

## Quickstart

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
for code in ["pt-PT", "pt-BR", "pt-AO"]:
    print(code, "→", ph.phonemize_sentence("O gato dorme.", code))
# pt-PT → u ˈɡatu ˈdɔɾmɨ
# pt-BR → u ˈɡatu ˈdoɾmi
# pt-AO → ʊ ˈɡatʊ ˈdɔʁmɨ
```

## Documentation

[docs/index.md](docs/index.md) lists every page in reading order.

| Page | Content |
|------|---------|
| [Quickstart](docs/quickstart.md) | Install, first call, dialect overview |
| [Comparison](docs/comparison.md) | How tugaphone compares with espeak-ng and other tools |
| [Architecture](docs/architecture.md) | The lattice core and the caller-owned layers |
| [Dialects](docs/dialects.md) | The lect codes, aliases and lexicon overlay |
| [Accent forcing](docs/accent_forcing.md) | Forcing an accent into a TTS, and the command line |
| [Homographs](docs/homographs.md) | Meaning-based disambiguation |
| [Code-switch](docs/codeswitch.md) | Embedded es/fr/en detection and nativization |
| [Numbers](docs/numbers.md) | Number normalization and gender agreement |
| [Text normalization](docs/text_normalization.md) | Old spellings, abbreviations, acronyms and codes |
| [API](docs/api.md) | Full class and function reference |
| [Advanced](docs/advanced.md) | Pipeline internals and sibling libraries |
| [Development](docs/development.md) | Checkout, tests and code layout |
| [Benchmarking](docs/benchmarking.md) | Accuracy benchmarks and the regression gate |

## License

Apache License 2.0. See [LICENSE](LICENSE).
