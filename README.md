# tugaphone: dialect-aware Portuguese phonemizer

**tugaphone** turns Portuguese text into IPA, and it does it per Lusophone
dialect. Give it a sentence and a dialect code, get back a phoneme string with
stress marks.

```
O gato dorme.
pt-PT → ˈo ˈgatu ˈdɔɾmɨ
pt-BR → ˈu ˈgatʊ ˈdoɾmi
pt-AO → ˈʊ ˈgatʊ ˈdɔʁmɨ
pt-MZ → ˈu ˈgatu ˈdɔrme
pt-TL → ˈo ˈgatʊ ˈdɔrme
```

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

Its runtime dependencies (`orthography2ipa`, `silabificador`, `tugalex`,
`bifonia`, `unicode-rbnf`) install automatically. The phonetic lexicon rides in
through [`tugalex`](https://github.com/TigreGotico/tugalex).

---

## 30-second quick start

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
print(ph.phonemize_sentence("O gato dorme.", "pt-PT"))
# ˈo ˈgatu ˈdɔɾmɨ
```

Construct `TugaPhonemizer()` once, then call `phonemize_sentence(text, lang)` as
often as you like. The result is a space-separated phoneme string, one token per
word, with `ˈ` marking primary stress. `lang` selects the orthography2ipa lect
spec, so it changes the phonology, not just the spelling.

Digits are best spelled out first, with gender agreement:

```python
from tugaphone.number_utils import normalize_numbers

text = normalize_numbers("comprei 2 casas")   # 'comprei duas casas'
print(ph.phonemize_sentence(text, "pt-PT"))
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
| **tugaphone** | 41 lects: five national standards + European, Brazilian, African, Asian and other varieties | Pure Python, IPA output with stress, meaning-based homograph resolution, one API across the whole Lusophone space. |

What tugaphone buys you over the coarse options:

- **41 Portuguese-family lects** reachable by BCP-47 code, the five national
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
sub-regional lects, 41 codes in all, from `list_dialects()`:

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

The European sub-regional lects (`pt-PT-x-porto`, `-braga`, `-trasosmontes`,
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
print(ph.phonemize_sentence("Eu gosto de música."))   # verb → ˈew ˈɡɔʃtu ˈdɨ ˈmuzikɐ
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
# ˈwo ˈbiɲu ˈjɛ ˈmujtu ˈbõ

# Trás-os-Montes: <ch> → [tʃ], betacism
print(ph.phonemize_sentence("A chave.", "pt-PT-x-trasosmontes"))
# ˈɐ ˈtʃabɨ

from tugaphone import list_dialects
print(list_dialects())   # all 41 registered lect codes
```

Legacy tugaphone accent codes resolve as aliases (`pt-PT-x-azores` →
`pt-PT-x-acores`, `pt-BR-x-sao-paulo` → `pt-BR-x-sp`, …). See
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
# 'o ˈbiɲu ˈbjɛɾd'

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

Digits are spelled out with gender agreement and long/short scale per dialect:

```python
from tugaphone.number_utils import normalize_numbers

normalize_numbers("vou comprar 1 casa")   # 'vou comprar uma casa'
normalize_numbers("vou adotar 1 cão")     # 'vou adotar um cão'
normalize_numbers("comprei 2 casas")      # 'comprei duas casas'
```

### Text normalization

Written text contains conventions that a phonemizer cannot read as they are: digit ranges, clock times, thousands separators, abbreviations, Roman numerals and acronyms. The `tugaphone.text_normalization` module rewrites each of them into words before the number rules run.

A dash between two numbers is a range. "1139-1185" reads as "1139 a 1185". A colon between digits is a clock time. "16:00" reads as "16 horas", "9:05" as "9 e 5" and "24:00" as "24 horas".

European number separators are kept. The dot in "92.073" groups thousands and is dropped. The comma in "10,4" is a decimal mark and reads as "10 vírgula 4".

Abbreviations expand in two ways. Common ones such as "vs.", "pág." and "Av." always expand, so "vs." reads as "versus". Honorifics such as "Sr." and "Dr." expand only before a capitalised name, so "Sr. Silva" reads as "Senhor Silva" and a lone "Sr." at the end of a sentence stays as it is.

A Roman numeral after a name becomes an ordinal: "Afonso I" reads as "Afonso Primeiro". Acronyms are spelled with Portuguese letter names, so "IA" reads as "i á", while lowercase words such as "ia" are left alone.

The numbers themselves are then spelled out by `normalize_numbers` in standard European Portuguese, for example "vinte e cinco". The full rule list with examples is in [docs/text_normalization.md](docs/text_normalization.md).

### Syllabification and stress

Stress and the dialect's phonology come from the orthography2ipa lect spec, syllabification is supplied by
[silabificador](https://github.com/TigreGotico/silabificador), wired in as
orthography2ipa's `syllabify` plugin.

### orthography2ipa plugin interface

`TugaphoneG2PPlugin` implements the `orthography2ipa` G2P plugin interface
(`transcribe`, `transcribe_word`, `language_codes`), so a framework that loads
phonemizers through that interface can drive tugaphone:

```python
from tugaphone.plugin import TugaphoneG2PPlugin

p = TugaphoneG2PPlugin(lang="pt-BR")
print(p.transcribe("o gato dorme"))   # u ˈɡatʊ ˈdoɾmi
```

---

## Architecture: relationship to orthography2ipa

tugaphone phonemizes by driving the shared o2i candidate lattice. A dialect
**is** an o2i lect spec: `phonemize_sentence(text, lang)` resolves `lang` to a
lect code and runs `orthography2ipa.G2P(lect).transcribe(text)`. The spec's
grapheme table, `allophone_rules` and cross-word `sandhi_rules` produce the
dialect's phonology, including genuinely cross-word processes like
coda-sibilant voicing sandhi, with no string-transform pass after
transcription.

tugaphone contributes only the stages o2i leaves to the caller, wired through
o2i's own extension points:

| Concern | Owner |
|---------|-------|
| Base phonology, dialect phenomena, sandhi, stress | orthography2ipa lect spec |
| Number / ordinal verbalization | tugaphone (`number_utils`, via the `normalize` stage) |
| Sense-based homograph marking | tugaphone (`bifonia`, via the `normalize` stage) |
| Curated pronunciation lexicon | tugaphone (`tugalex`, via `register_lexicon`) |
| Syllabification | tugaphone (`silabificador`, via the `syllabify` plugin) |

The lexicon overlay applies only to the lects whose lexical tradition matches a
`tugalex` region (`pt-PT`/`pt-PT-x-lisbon`, `pt-BR`/`pt-BR-x-rj`, `pt-BR-x-sp`,
`pt-AO`, `pt-MZ`, `pt-TL`), every other lect is pure lattice.

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
- [docs/dialects.md](docs/dialects.md), the 41 lect codes, aliases and lexicon overlay
- [docs/accent_forcing.md](docs/accent_forcing.md), forcing an accent into a TTS (IPA / respelling / overlays)
- [docs/homographs.md](docs/homographs.md), meaning-based disambiguation
- [docs/codeswitch.md](docs/codeswitch.md), embedded es/fr/en detection and nativization
- [docs/numbers.md](docs/numbers.md), number normalization and gender agreement
- [docs/text_normalization.md](docs/text_normalization.md), ranges, clock times, separators, abbreviations, regnal numerals, acronyms
- [docs/api.md](docs/api.md), full class and function reference
- [docs/tokenizer.md](docs/tokenizer.md), the token-tree feature model
- [docs/advanced.md](docs/advanced.md), the pipeline internals and integration
- [docs/benchmarking.md](docs/benchmarking.md), the TTS-gold and rules-only benchmarks
- [docs/scoreboard.md](docs/scoreboard.md), accuracy per dialect
- [examples/](examples/), runnable scripts

---

## Acknowledgements

The clock-time, number-separator, abbreviation, and regnal-numeral reading
rules in `tugaphone/text_normalization.py` are ported from
[tts_eu_pt](https://github.com/logus2k/tts_eu_pt), a European-Portuguese TTS
front-end by Antonio Cruz, released under the Apache License 2.0. The rules
were reimplemented in tugaphone's own idiom rather than copied verbatim.

## License

Apache License 2.0. See [LICENSE](LICENSE).
