# tugaphone: dialect-aware Portuguese phonemizer

**tugaphone** turns Portuguese text into IPA, and it does it per Lusophone
dialect. Give it a sentence and a dialect code, get back a phoneme string with
stress marks.

```
O gato dorme.
pt-PT → o ˈɡatu ˈdɔɾmɨ
pt-BR → u ˈɡatu ˈdoɾmi
pt-AO → ʊ ˈɡatʊ ˈdɔʁmɨ
pt-MZ → u ˈɡatu ˈdɔrme
pt-TL → o ˈɡatʊ ˈdɔrme
```

Every IPA sample in these docs is the output of the orthography2ipa lect specs
that tugaphone resolves at run time, so a spec change in orthography2ipa can
change a sample.

Under the hood it drives the
[orthography2ipa](https://github.com/TigreGotico/orthography2ipa) candidate
lattice: a dialect **is** an orthography2ipa lect spec, and the spec's grapheme
table, allophone rules and cross-word sandhi produce that dialect's phonology
directly. tugaphone adds the stages orthography2ipa leaves to the caller: a
phonetic lexicon, meaning-based homograph resolution, and gender- and scale-aware
number expansion, wired through orthography2ipa's own extension points. See
[docs/architecture.md](docs/architecture.md).

---

## Install

```bash
pip install tugaphone
```

Its runtime dependencies (`orthography2ipa`, `o2i-lexicons`, `silabificador`,
`tugalex`, `bifonia`, `ovos-number-parser`) install automatically. The `pt-PT`
lexicon rides in through [`o2i-lexicons`](https://github.com/TigreGotico/o2i-lexicons).

---

## 30-second quick start

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
print(ph.phonemize_sentence("O gato dorme.", "pt-PT"))
# o ˈɡatu ˈdɔɾmɨ
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
# pt-PT → ʃuˈvew ˈmũjtu ˈõtɐ̃j
# pt-BR → ʃoˈvew ˈmwĩtʊ ˈõtẽj
# pt-AO → ʃoˈvew ˈmũjntʊ ˈõntẽj
# pt-MZ → ʃoˈvew ˈmũjtu ˈõtẽj
# pt-TL → ʃoˈvew ˈmujtʊ ˈõntɐ̃j
```

The European sub-regional lects (`pt-PT-x-porto`, `-braga`, `-tras-os-montes`,
`-madeira`, `-acores`, …), the Brazilian ones (`pt-BR-x-sp`, `-rj`, `-caipira`,
`-bahia`, …) and the rest are all reachable the same way. See
[docs/dialects.md](docs/dialects.md) for the full list and the legacy aliases.

### Homograph disambiguation

Heterophonic homographs are resolved by meaning via **bifonia**: *sede* thirst
vs headquarters, *forma* mould vs shape, *gosto* noun vs verb. bifonia inserts
open/closed-vowel diacritics during the pipeline's normalization stage, before
the lattice transcribes the sentence, so the same spelling maps to different
pronunciations depending on sentence context.

```python
print(ph.phonemize_sentence("Eu gosto de música."))   # verb → ˈew ˈɡɔʃtu dɨ ˈmuzikɐ
print(ph.phonemize_sentence("Tenho bom gosto."))       # noun → ˈtɛɲu ˈbõ ˈɡoʃtu
```

### Sub-regional accents

Sub-regional accents are lects like any other, select one by its BCP-47
private-use code. Its phonology (betacism, rising diphthongs, palatalization,
`/u/` fronting, coda-sibilant sandhi, …) is encoded in the orthography2ipa lect
spec, so no extra argument is needed:

```python
# Porto: rising diphthongs, betacism (/v/ → [b])
print(ph.phonemize_sentence("O vinho é muito bom.", "pt-PT-x-porto"))
# o ˈbiɲu ˈjɛ ˈmujtu ˈbõ

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
# 'o ˈbiɲu ˈbjɛɾdɨ'

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

### Number normalization

`phonemize_sentence` spells digits out itself. `normalize_numbers` exposes
that step on its own, for a TTS front-end that needs the text. It applies
gender agreement and the long or short scale of the dialect:

```python
from tugaphone.number_utils import normalize_numbers

normalize_numbers("vou comprar 1 casa")   # 'vou comprar uma casa'
normalize_numbers("vou adotar 1 cão")     # 'vou adotar um cão'
normalize_numbers("comprei 2 casas")      # 'comprei duas casas'
normalize_numbers("aprovou 1 lei")        # 'aprovou uma lei'
normalize_numbers("passou 1 dia")         # 'passou um dia'
```

### Text normalization

Written text contains conventions that a phonemizer cannot read as they are: digit ranges, clock times, thousands separators, abbreviations, Roman numerals and acronyms. The `tugaphone.text_normalization` module rewrites each of them into words before the number rules run.

A dash between two numbers is a range. "1139-1185" reads as "1139 a 1185". A colon between digits is a clock time. "16:00" reads as "16 horas", "9:05" as "9 e 5" and "24:00" as "24 horas".

European number separators are kept. The dot in "92.073" groups thousands and is dropped. The comma in "10,4" is a decimal mark and reads as "10 vírgula 4".

Abbreviations expand in two ways. Common ones such as "vs.", "pág." and "Av." always expand, so "vs." reads as "versus". Honorifics such as "Sr." and "Dr." expand only before a capitalised name, so "Sr. Silva" reads as "Senhor Silva" and a lone "Sr." at the end of a sentence stays as it is.

A Roman numeral after a name or a century reads as an ordinal up to ten and as a cardinal above ten: "Afonso I" reads as "Afonso Primeiro" and "o século XIX" as "o século dezanove". The ordinal takes the gender of the name, so "D. Maria II" reads as "Dona Maria Segunda". A capital in a fixed expression such as "raio X" or "vitamina C" stays a letter. A letter-digit code reads as its letters and a number, so "T2" reads as "tê dois". Acronyms are spelled with Portuguese letter names, so "IA" reads as "i á", while lowercase words such as "ia" are left alone.

The numbers themselves are then spelled out by `normalize_numbers` in standard European Portuguese, for example "vinte e cinco". The full rule list with examples is in [docs/text_normalization.md](docs/text_normalization.md).

### Syllabification and stress

Stress and the dialect's phonology come from the orthography2ipa lect spec.
Syllabification comes from
[silabificador](https://github.com/TigreGotico/silabificador), through the
`syllabify` plugin that `orthography2ipa[portuguese]` registers.

### Engine object

`TugaphoneG2PPlugin` wraps the phonemizer in an engine object with
`transcribe`, `transcribe_word` and `language_codes`. `transcribe_word` accepts
an `orthography2ipa.WordContext`, so a framework that drives several G2P
engines through these three members can drive tugaphone too:

```python
from tugaphone.plugin import TugaphoneG2PPlugin

p = TugaphoneG2PPlugin(lang="pt-BR")
print(p.transcribe("o gato dorme"))   # u ˈɡatu ˈdoɾmi
```

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
| Number / ordinal verbalization | tugaphone (`number_utils`, via the `normalize` stage) |
| Sense-based homograph marking | tugaphone (`bifonia`, via the `normalize` stage) |
| `pt-PT` and `pt-BR` residual lexicons | `o2i-lexicons`, enabled by tugaphone via `use_packaged_lexicons` |
| Syllabification | orthography2ipa (`silabificador`, through the `syllabify` plugin of `orthography2ipa[portuguese]`) |

Only `pt-PT` and `pt-BR` take a lexicon. Each holds the words that the lect's rules get
wrong. Every other lect runs on the rules alone.

`tugaphone.tokenizer` and `tugaphone.dialects` remain as a token-tree
linguistic **feature** API (manner, place, voicing, syllable roles, CV
skeletons) and the rules-only benchmark baseline, not the phonemization path.
See [docs/architecture.md](docs/architecture.md) and
[docs/tokenizer.md](docs/tokenizer.md).

---

## Sibling libraries

tugaphone is part of the TigreGotico Portuguese NLP stack:

| Library | Role |
|---------|------|
| [tugalex](https://github.com/TigreGotico/tugalex) | Phonetic lexicon |
| [silabificador](https://github.com/TigreGotico/silabificador) | Syllabifier |
| [bifonia](https://github.com/TigreGotico/bifonia) | Heterophone sense disambiguation |
| [orthography2ipa](https://github.com/TigreGotico/orthography2ipa) | The candidate lattice and the Portuguese lect specs |

---

## Documentation

- [docs/quickstart.md](docs/quickstart.md), install, first call, dialect overview
- [docs/architecture.md](docs/architecture.md), the lattice core and the caller-owned layers
- [docs/dialects.md](docs/dialects.md), the lect codes, aliases and lexicon overlay
- [docs/accent_forcing.md](docs/accent_forcing.md), forcing an accent into a TTS (IPA / respelling / overlays)
- [docs/homographs.md](docs/homographs.md), meaning-based disambiguation
- [docs/codeswitch.md](docs/codeswitch.md), embedded es/fr/en detection and nativization
- [docs/numbers.md](docs/numbers.md), number normalization and gender agreement
- [docs/text_normalization.md](docs/text_normalization.md), ranges, clock times, separators, abbreviations, Roman numerals, acronyms, letter-digit codes
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
| `tugaphone/text_normalization.py`, `tugaphone/number_utils.py` | The `normalize` stage |
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

The clock-time, number-separator, abbreviation, and regnal-numeral reading
rules in `tugaphone/text_normalization.py` are ported from
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
