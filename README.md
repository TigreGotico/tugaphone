# tugaphone: dialect-aware Portuguese phonemizer

**tugaphone** turns Portuguese text into IPA, and it does it per Lusophone
dialect. Give it a sentence and a dialect code, get back a phoneme string with
stress marks.

```
O gato dorme.
pt-PT → u ˈɡatu ˈdɔɾmɨ
pt-BR → u ˈɡatu ˈdoɾmi
pt-AO → ʊ ˈɡatʊ ˈdɔʁmɨ
pt-MZ → u ˈɡatu ˈdɔrme
pt-TL → o ˈɡato ˈdɔrme
```

Every IPA sample in these docs is the output of the orthography2ipa lect specs
that tugaphone resolves at run time, so a spec change in orthography2ipa can
change a sample.

Under the hood it drives the
[orthography2ipa](https://github.com/TigreGotico/orthography2ipa) candidate
lattice: a dialect **is** an orthography2ipa lect spec, and the spec's grapheme
table, allophone rules and cross-word sandhi produce that dialect's phonology
directly. tugaphone adds the stages orthography2ipa leaves to the caller: text
normalization, gender- and scale-aware number expansion, meaning-based homograph
marking and the residual lexicon of `pt-PT` and `pt-BR`, wired through
orthography2ipa's own extension points. See
[docs/architecture.md](docs/architecture.md).

---

## Install

```bash
pip install tugaphone
```

Its runtime dependencies (`orthography2ipa`, `o2i-lexicons`, `silabificador`,
`tugalex`, `bifonia`, `text2spoken`) install automatically. The `pt-PT`
and `pt-BR` lexicons ride in through [`o2i-lexicons`](https://github.com/TigreGotico/o2i-lexicons).

---

## 30-second quick start

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
print(ph.phonemize_sentence("O gato dorme.", "pt-PT"))
# u ˈɡatu ˈdɔɾmɨ
```

Construct `TugaPhonemizer()`, then call `phonemize_sentence(text, lang)` as
often as you like. The first call for a lect builds that lect's engine, so it is
slower than the calls after it. The result is a
space-separated phoneme string, one token per word, with `ˈ` marking primary
stress. `lang` selects the orthography2ipa lect spec, so it changes the
phonology, not just the spelling.

Digits need no preparation. `phonemize_sentence` spells them out with gender
agreement before it transcribes the sentence:

```python
print(ph.phonemize_sentence("comprei 2 casas", "pt-PT"))
# kõˈpɾej ˈduɐʃ ˈkazɐʃ
```

---

## Why tugaphone

Most Portuguese G2P you can reach for treats Portuguese as one or two varieties.
tugaphone's reason to exist is **dialect granularity**: one API that spans the
whole Lusophone space and, within European Portuguese, a set of sub-regional
accents.

| Tool | Portuguese coverage | Notes |
|------|--------------------|-------|
| **espeak-ng** | `pt` (European) + `pt-br` (Brazilian) | Small, fast, rule-based, about 100 languages, widely used as a TTS front-end. Two Portuguese varieties only, no African/Asian Lusophone, no sub-regional accents. |
| **phonemizer** (bootphon) | via espeak-ng | A backend wrapper, for Portuguese it delegates to espeak-ng, so the same two varieties. Needs the espeak binary. |
| Single-variety Portuguese toolkits (e.g. Brazilian-focused phonetic transcribers) | one national variety | Strong within their variety, not built to cover the full Lusophone range from one interface. |
| **tugaphone** | every Portuguese-family orthography2ipa lect: five national standards + European, Brazilian, African, Asian and other varieties | Pure Python, IPA output with stress, meaning-based homograph resolution, one API across the whole Lusophone space. |

What tugaphone buys you over the coarse options:

- **Every Portuguese-family orthography2ipa lect** reachable by BCP-47 code, the five national
  standards (`pt-PT`, `pt-BR`, `pt-AO`, `pt-MZ`, `pt-TL`) plus European and
  Brazilian sub-regional varieties and the African, Asian and other lects.
- **Meaning-based homograph resolution**, *sede* thirst vs headquarters,
  *gosto* verb vs noun, via [bifonia](https://github.com/TigreGotico/bifonia).
- **Gender- and scale-aware number expansion** (long scale for `pt-PT`, short
  scale for `pt-BR`).
- **A phonology-accurate core**, each dialect's sounds come from its
  orthography2ipa lect spec, not from a post-hoc string-edit layer.

Honest trade-offs: tugaphone is Portuguese-only and younger than espeak-ng,
which covers far more languages and years of field use. Its accuracy against the
per-lect gold is measured openly, see
[docs/benchmarking.md](docs/benchmarking.md).

---

## Features

### Dialect coverage

The five national standards, plus European, Brazilian, African, Asian and other
sub-regional lects. `list_dialects()` returns the full set:

| Code | Region |
|------|--------|
| `pt-PT` | European Portuguese, heavy vowel reduction, post-alveolar fricatives, uvular /ʁ/ |
| `pt-BR` | Brazilian Portuguese, fuller vowels, /t d/ palatalisation, l-vocalisation |
| `pt-AO` | Angolan Portuguese, moderate reduction, alveolar trill, Bantu substrate |
| `pt-MZ` | Mozambican Portuguese, similar to European with regional variation |
| `pt-TL` | Timorese Portuguese, conservative pronunciation, Tetum substrate |

```python
for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
    print(code, "→", ph.phonemize_sentence("Choveu muito ontem.", code))
# pt-PT → ʃuˈvew ˈmũj̃tu ˈõtɐ̃j̃
# pt-BR → ʃoˈvew ˈmũj̃tu ˈõtẽj̃
# pt-AO → ʃoˈvew ˈmũj̃tʊ ˈõtẽj̃
# pt-MZ → ʃoˈvew ˈmũj̃tu ˈõtẽ
# pt-TL → ʃoˈvew ˈmũj̃to ˈõtẽj̃
```

The European sub-regional lects (`pt-PT-x-porto`, `-braga`, `-tras-os-montes`,
`-madeira`, `-acores`, …), the Brazilian ones (`pt-BR-x-sp`, `-rj`, `-caipira`,
`-bahia`, …) and the rest are all reachable the same way. See
[docs/dialects.md](docs/dialects.md) for the full list and the legacy aliases.

An unknown code falls back to its parent lect, or else to `pt-PT`, with a
warning. `is_supported(code)` tells
you first whether a code names a lect:

```python
from tugaphone import is_supported

is_supported("pt-BR-x-sao-paulo")   # True, through an alias
is_supported("en-US")               # False
```

### Homograph disambiguation

Heterophonic homographs are resolved by meaning via **bifonia**: *sede* thirst
vs headquarters, *forma* mould vs shape, *gosto* noun vs verb. bifonia inserts
open/closed-vowel diacritics in the pipeline's `mark` stage, after number
expansion and before the lattice transcribes the sentence, so the same spelling
maps to different pronunciations depending on sentence context.

```python
print(ph.phonemize_sentence("Eu gosto de música."))   # verb → ˈew ˈɡɔʃtu dɨ ˈmuzikɐ
print(ph.phonemize_sentence("Tenho bom gosto."))       # noun → ˈteɲu ˈbõ ˈɡoʃtu
```

### Sub-regional accents

Sub-regional accents are lects like any other, select one by its BCP-47
private-use code. Its phonology (betacism, rising diphthongs, palatalization,
`/u/` fronting, coda-sibilant sandhi, …) is encoded in the orthography2ipa lect
spec, so no extra argument is needed:

```python
# Porto: rising diphthongs, betacism (/v/ → [b])
print(ph.phonemize_sentence("O vinho é muito bom.", "pt-PT-x-porto"))
# u ˈbiɲu ˈjɛ ˈmũj̃tu ˈbõ

# Trás-os-Montes: <ch> → [tʃ], betacism
print(ph.phonemize_sentence("A chave.", "pt-PT-x-tras-os-montes"))
# ɐ ˈtʃabɨ

from tugaphone import list_dialects
print(list_dialects())   # every registered lect code
```

Legacy tugaphone accent codes and the old orthography2ipa keys resolve as
aliases (`pt-PT-x-azores` → `pt-PT-x-acores`, `pt-BR-x-sao-paulo` →
`pt-BR-x-sp`, `pt-PT-x-trasosmontes` → `pt-PT-x-tras-os-montes`, …). See
[docs/dialects.md](docs/dialects.md).

### Forcing an accent for a TTS

Selecting a lect *describes* an accent, `force_accent` *forces* one into a
downstream voice. For a phoneme-input TTS (phoonnx-style) that is the target
IPA, for a grapheme-input TTS (a fixed pt-PT voice) it is Portuguese text
**respelled** so the base voice reads it as the target sounds, feed a pt-PT
voice `binho` to force the Northern betacism of `vinho`.

```python
from tugaphone import force_accent

# phoneme-input TTS: the target accent's IPA
force_accent("o vinho verde", "pt-PT-x-porto", mode="ipa")
# 'u ˈbiɲu ˈbjɛɾdɨ'

# grapheme-input pt-PT TTS: respelled text it will pronounce with the accent
force_accent("o vinho verde", "pt-PT-x-porto", mode="respell", base_lect="pt-PT")
# 'o binho berde'
```

The respeller is verification-gated (an edit is kept only if it moves the base
voice's own reading toward the target), so it never makes a word worse and
leaves unspellable contrasts alone. Ad-hoc per-voice tweaks live in a
JSON-serialisable `AccentOverlay`, and `examples/12_synthetic_corpus.py`
generates a parallel `(sentence, lect, ipa, respelled_text)` training corpus.
See [docs/accent_forcing.md](docs/accent_forcing.md).

### Numbers, dates and abbreviations

`phonemize_sentence` reads numbers, dates, clock times, money, measures,
Roman numerals and abbreviations with
[text2spoken](https://github.com/TigreGotico/text2spoken). `normalize_numbers`
exposes that step on its own, for a TTS front-end that needs the text:

```python
from tugaphone.number_utils import normalize_numbers

normalize_numbers("Nasceu a 25/12/2023.")
# 'Nasceu a vinte e cinco de dezembro de dois mil e vinte e três.'
normalize_numbers("A reunião é às 19h30.")
# 'A reunião é às dezanove horas e trinta minutos.'
normalize_numbers("A reunião é às 19h30.", "pt-BR")
# 'A reunião é às dezenove horas e trinta minutos.'
normalize_numbers("vou comprar 1 casa")   # 'vou comprar uma casa'
```

The European lects and the African and Asian lects read the `pt-PT` variety
("dezanove"). The Brazilian lects and `pt-UY` read the `pt-BR` variety
("dezenove"). A form with digits that text2spoken cannot read, such as "3D",
gives an `UnreadFormWarning` that names the form and the text, because the
phoneme lattice drops its digits. See [docs/numbers.md](docs/numbers.md).

tugaphone rewrites the forms that text2spoken leaves as written. Abbreviations
such as "vs.", "pág." and "n.º" expand, so "vs." reads as "versus". A title
such as "Sr." or "Dr." expands everywhere, so "o Sr. presidente" reads as "o
Senhor presidente". A letter-digit code reads as its letters and a number, so
"T2" reads as "tê dois". Acronyms are spelled with Portuguese letter names, so
"IA" reads as "i á", while lowercase words such as "ia" are left alone. The
full rule list with examples is in
[docs/text_normalization.md](docs/text_normalization.md).

### Syllabification and stress

Stress and the dialect's phonology come from the orthography2ipa lect spec.
Syllabification comes from the bundled splitter of orthography2ipa, which reads
the diphthongs and hiatus of the lect spec. Only the deprecated
`tugaphone.tokenizer` token tree syllabifies with
[silabificador](https://github.com/TigreGotico/silabificador).

### Command line

The package installs a `tugaphone` command:

```bash
tugaphone phonemize "o gato dorme" --lect pt-BR
tugaphone force-accent "o vinho verde" --lect pt-PT-x-porto --mode respell --base pt-PT
tugaphone list
```

`phonemize` defaults to `--lect pt-PT`. `force-accent` takes `--mode ipa` or
`--mode respell`, and `--overlay` reads a JSON `AccentOverlay`. See
[docs/accent_forcing.md](docs/accent_forcing.md#command-line).

### orthography2ipa pipeline

`tugaphone.pipeline(lect)` returns the orthography2ipa `Pipeline` that
tugaphone runs for a lect: the packaged lexicon, the number expansion and the
homograph marks. A program that already drives `orthography2ipa.G2P` gets
tugaphone's output from it:

```python
from orthography2ipa import G2P
import tugaphone

engine = G2P("pt-BR", pipeline=tugaphone.pipeline("pt-BR"))
print(engine.transcribe("o gato dorme"))   # u ˈɡatu ˈdoɾmi
```

The pipeline covers `contact="none"`, the default. `lect` must be a code of
`list_dialects()`; resolve a loose tag with `resolve_lect` first.

---

## Architecture: relationship to orthography2ipa

tugaphone phonemizes by driving the shared o2i candidate lattice. A dialect
**is** an o2i lect spec: `phonemize_sentence(text, lang)` resolves `lang` to a
lect code and runs `orthography2ipa.G2P(lect).transcribe(text)`. The spec's
grapheme table, `allophone_rules` and cross-word `sandhi_rules` produce the
dialect's phonology, including genuinely cross-word processes like
coda-sibilant voicing sandhi, with no string-transform pass after
transcription.

tugaphone contributes the stages o2i leaves to the caller, wired through
o2i's own extension points, and relies on o2i for syllabification:

| Concern | Owner |
|---------|-------|
| Base phonology, dialect phenomena, sandhi, stress | orthography2ipa lect spec |
| Number, date and time reading | text2spoken, called by tugaphone (`number_utils`, via `Pipeline.expand`) |
| Sense-based homograph marking | tugaphone (`bifonia`, via `Pipeline.mark`) |
| `pt-PT` and `pt-BR` residual lexicons | `o2i-lexicons`, passed by tugaphone through `Pipeline` |
| Syllabification | orthography2ipa (the bundled splitter) |

Only `pt-PT` and `pt-BR` take a lexicon. Each holds the words that the lect's rules get
wrong. Every other lect runs on the rules alone.

`tugaphone.tokenizer` and `tugaphone.dialects` are a token-tree linguistic
**feature** API (manner, place, voicing, syllable roles, CV skeletons) and the
rules-only benchmark baseline, not the phonemization path. Both modules and
`registry.get_dialect_inventory` are deprecated. They emit a
`DeprecationWarning` and go in tugaphone 2.0.0. See
[docs/architecture.md](docs/architecture.md) and
[docs/tokenizer.md](docs/tokenizer.md).

---

## Sibling libraries

tugaphone is part of the TigreGotico Portuguese NLP stack:

| Library | Role in tugaphone |
|---------|------|
| [orthography2ipa](https://github.com/TigreGotico/orthography2ipa) | The candidate lattice and the Portuguese lect specs |
| [o2i-lexicons](https://github.com/TigreGotico/o2i-lexicons) | The `pt-PT` and `pt-BR` residual lexicons |
| [bifonia](https://github.com/TigreGotico/bifonia) | Heterophone sense disambiguation, the pipeline's `mark` stage |
| [text2spoken](https://github.com/TigreGotico/text2spoken) | Numbers, dates, times, money and abbreviations for `normalize_numbers` |
| [tugalex](https://github.com/TigreGotico/tugalex) | Given-name gender for `D.` (Dom or Dona) |
| [silabificador](https://github.com/TigreGotico/silabificador) | Syllabifier of the deprecated token tree |

---

## Documentation

- [docs/quickstart.md](docs/quickstart.md), install, first call, dialect overview
- [docs/architecture.md](docs/architecture.md), the lattice core and the caller-owned layers
- [docs/dialects.md](docs/dialects.md), the lect codes, aliases and lexicon overlay
- [docs/accent_forcing.md](docs/accent_forcing.md), forcing an accent into a TTS (IPA / respelling / overlays)
- [docs/homographs.md](docs/homographs.md), meaning-based disambiguation
- [docs/codeswitch.md](docs/codeswitch.md), embedded es/fr/en detection and nativization
- [docs/numbers.md](docs/numbers.md), number normalization and gender agreement
- [docs/text_normalization.md](docs/text_normalization.md), abbreviations, acronyms, letter-digit codes and the text2spoken step
- [docs/api.md](docs/api.md), full class and function reference
- [docs/tokenizer.md](docs/tokenizer.md), the token-tree feature model
- [docs/advanced.md](docs/advanced.md), the pipeline internals and integration
- [docs/benchmarking.md](docs/benchmarking.md), the TTS-gold and rules-only benchmarks
- [docs/scoreboard.md](docs/scoreboard.md), accuracy per dialect
- [examples/](examples/), runnable scripts

---

## Development

Set up a checkout with its test extra, then run the suite:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python --prerelease=allow -e ".[test]"
.venv/bin/python -m pytest tests
```

The `test` extra installs `markovonnx`. Without it, code-switch detection uses
the orthographic fallback. `tests/test_examples.py` runs every script in
`examples/`, so a broken example fails the suite.

| Path | Content |
|------|---------|
| `tugaphone/lattice_core.py` | The phonemization pipeline on the orthography2ipa lattice |
| `tugaphone/registry.py` | Lect codes, legacy aliases, the lects that take a packaged lexicon |
| `tugaphone/text_normalization.py`, `tugaphone/number_utils.py` | The `expand` step of the engine's `Pipeline` |
| `tugaphone/codeswitch.py`, `tugaphone/langdetect.py` | Contact-language detection and nativization |
| `tugaphone/accent.py`, `tugaphone/__main__.py` | Accent forcing and the command line |
| `tugaphone/tokenizer.py`, `tugaphone/dialects.py` | The token-tree feature API and the rules-only baseline |
| `scripts/` | Benchmarks and code-switch model training |

`scripts/benchmark.py` writes `benchmarks/results.json` and
`docs/scoreboard.md`, so do not edit either by hand. A change that improves the
score commits the regenerated baseline with it, and
`scripts/check_benchmark_regression.py` is the CI gate. CI never uses the
network: only a maintainer refreshes the gold fixtures, with
`scripts/benchmark.py --refresh-fixtures`. See
[docs/benchmarking.md](docs/benchmarking.md).

---

## Acknowledgements

The abbreviation rules in `tugaphone/text_normalization.py` are ported from
[tts_eu_pt](https://github.com/logus2k/tts_eu_pt), a European-Portuguese TTS
front-end by Antonio Cruz, released under the Apache License 2.0. The rules
were reimplemented in tugaphone's own idiom rather than copied verbatim.

The English loanword lexicon in `tugaphone/data/loanwords.json` (see
[docs/codeswitch.md](docs/codeswitch.md)) is likewise ported from
[tts_eu_pt](https://github.com/logus2k/tts_eu_pt). The word list is kept as
upstream curated it, minus a handful of proper nouns and words that collide
with an existing `tugalex` Portuguese pronunciation; the `en-GB` IPA upstream
generated offline with espeak ships alongside it as reference/test-gold
material, tugaphone's own `en-US` lattice and nativization produce the
pronunciation actually spoken.

## License

Apache License 2.0. See [LICENSE](LICENSE).
