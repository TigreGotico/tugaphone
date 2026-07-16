# tugaphone — dialect-aware Portuguese phonemizer

**tugaphone** turns Portuguese text into IPA, and it does it per Lusophone
dialect. Give it a sentence and a dialect code, get back a phoneme string with
stress marks and syllable boundaries.

```
O gato dorme.
pt-PT → ˈu gˈa·tu ˈdoɾ·mɨ
pt-BR → ˈu gˈa·tʊ ˈdoɾ·mɪ
pt-AO → ˈu gˈa·tʊ ˈdoɾ·me
pt-MZ → ˈu gˈa·tu ˈdoɾ·me
pt-TL → ˈu gˈa·tʊ ˈdoɾ·me
```

Under the hood it is the Portuguese text-to-speech front-end built on
[orthography2ipa](https://github.com/TigreGotico/orthography2ipa): it adds a
phonetic lexicon, meaning-based homograph resolution, gender- and scale-aware
number expansion, and a sub-regional accent layer on top of o2i's shared
grapheme-to-phoneme machinery.

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
# ˈu gˈa·tu ˈdoɾ·mɨ
```

Construct `TugaPhonemizer()` once — it loads the lexicon — then call
`phonemize_sentence(text, lang)` as often as you like. The result is a
space-separated phoneme string, one token per word, with `ˈ` marking primary
stress and `·` marking syllable boundaries. `lang` changes the phonology, not
just the spelling.

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
| **espeak-ng** | `pt` (European) + `pt-br` (Brazilian) | Tiny, fast, rule-based, ~100 languages, battle-tested as a TTS front-end. Two Portuguese varieties only; no African/Asian Lusophone, no sub-regional accents. |
| **phonemizer** (bootphon) | via espeak-ng | A backend wrapper; for Portuguese it delegates to espeak-ng, so the same two varieties. Needs the espeak binary. |
| Single-variety Portuguese toolkits (e.g. Brazilian-focused phonetic transcribers) | one national variety | Strong within their variety; not built to cover the full Lusophone range from one interface. |
| **tugaphone** | five national standards + city + sub-regional accents | Pure Python, IPA output with stress and syllable structure, meaning-based homograph resolution, an inspectable token tree. |

What tugaphone buys you over the coarse options:

- **Five national standards** — `pt-PT`, `pt-BR`, `pt-AO`, `pt-MZ`, `pt-TL` —
  plus city inventories and a dozen European sub-regional accent presets.
- **Meaning-based homograph resolution** — *sede* thirst vs headquarters,
  *gosto* verb vs noun — via [bifonia](https://github.com/TigreGotico/bifonia).
- **Gender- and scale-aware number expansion** (long scale for `pt-PT`, short
  scale for `pt-BR`).
- **An inspectable token tree** — syllables, stress, graphemes and phonological
  features, not just the final string.

Honest trade-offs: tugaphone is Portuguese-only and younger than espeak-ng,
which covers far more languages and years of field use. Its sub-regional accent
presets are **experimental approximations** (see below), not validated field
transcriptions. Out-of-vocabulary words go through grapheme rules whose accuracy
is measured openly per dialect — see [docs/scoreboard.md](docs/scoreboard.md).

---

## Features

### Five dialect inventories

| Code | Region |
|------|--------|
| `pt-PT` | European Portuguese — heavy vowel reduction, post-alveolar fricatives, uvular /ʁ/ |
| `pt-BR` | Brazilian Portuguese — fuller vowels, /t d/ palatalisation, l-vocalisation |
| `pt-AO` | Angolan Portuguese — moderate reduction, alveolar trill, Bantu substrate |
| `pt-MZ` | Mozambican Portuguese — similar to European with regional variation |
| `pt-TL` | Timorese Portuguese — conservative pronunciation, Tetum substrate |

```python
for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
    print(code, "→", ph.phonemize_sentence("Choveu muito ontem.", code))
# pt-PT → ʃu·ˈvew mˈũj·tu ˈõ·tɐ̃j
# pt-BR → ʃo·ˈvew mwˈĩ·tʊ ˈõ·tẽj
# pt-AO → ʃo·ˈvew mˈũjn·tʊ ˈõn·tẽj
# pt-MZ → ʃu·ˈvew mˈũj·tu ˈõ·tẽj
# pt-TL → ʃo·ˈvew mˈuj·tʊ ˈõn·tɐ̃j
```

### Homograph disambiguation

Heterophonic homographs are resolved by meaning via **bifonia**: *sede* thirst
vs headquarters, *forma* mould vs shape, *gosto* noun vs verb. bifonia inserts
open/closed-vowel diacritics that the grapheme rules read directly, so the same
spelling maps to different pronunciations depending on sentence context.

```python
print(ph.phonemize_sentence("Eu gosto de música."))   # verb → ˈew ˈɡɔʃ·tu dɨ mˈu·zi·kɐ
print(ph.phonemize_sentence("Tenho bom gosto."))       # noun → ˈte·ɲu ˈbõ ˈɡoʃ·tu
```

### Sub-regional accents

`RegionalTransforms` presets layer phonological rules on top of any dialect.
Every preset is reachable by its BCP-47 private-use code:

```python
# Porto: betacism (/v/ → [b]) among its northern features
print(ph.phonemize_sentence("O vinho é muito bom.", "pt-PT-x-porto"))
# ˈu bˈi·ɲu ˈɛ mˈũj·tu ˈbõ

# Açores: stressed /u/ → [y], l-palatalisation
print(ph.phonemize_sentence("O vinho é muito bom.", "pt-PT-x-azores"))
# ˈy vˈi·ɲu ˈɛ mˈỹj·tu ˈbõ

from tugaphone import list_dialects
print(list_dialects())   # all 20 registered codes
```

Each preset is a composition of transform rules; each rule is annotated in the
source with the phonological phenomenon it models, the dialect zone it is
attested in, and a source reference (Cintra 1971 and others). Treat them as
**experimental approximations** — several rules rest on internal field notes
rather than published sources, and the presets are hand-tuned against the
project's gold slices, not independently validated. Real regional variation is
messier than any rule set. See [docs/dialects.md](docs/dialects.md).

### Number normalization

Digits are spelled out with gender agreement and long/short scale per dialect:

```python
from tugaphone.number_utils import normalize_numbers

normalize_numbers("vou comprar 1 casa")   # 'vou comprar uma casa'
normalize_numbers("vou adotar 1 cão")     # 'vou adotar um cão'
normalize_numbers("comprei 2 casas")      # 'comprei duas casas'
```

### Syllabification and stress

Syllabification comes from [silabificador](https://github.com/TigreGotico/silabificador);
stress detection delegates to `orthography2ipa`'s declarative `StressRules`.

### Rules-only mode

Empty a dialect inventory's `IRREGULAR_WORDS` to bypass the lexicon and use only
grapheme rules — useful for testing rule coverage or transcribing words that are
intentionally out of vocabulary.

### orthography2ipa plugin interface

`TugaphoneG2PPlugin` implements the `orthography2ipa` G2P plugin interface
(`transcribe`, `transcribe_word`, `language_codes`), so a framework that loads
phonemizers through that interface can drive tugaphone:

```python
from tugaphone.plugin import TugaphoneG2PPlugin

p = TugaphoneG2PPlugin(lang="pt-BR")
print(p.transcribe("o gato dorme"))   # ˈu gˈa·tʊ ˈdoɾ·mɪ
```

---

## Architecture: relationship to orthography2ipa

tugaphone is the Portuguese front-end **over** o2i, not a fork of it. It builds a
sentence's IPA from a **character-level cascade**: each `CharToken.ipa` composes
into a `GraphemeToken`, graphemes into a `WordToken.ipa`, and `Sentence.ipa` is
those word IPAs joined with spaces — each word transcribed **independently**.

From o2i it consumes only the shared *primitives*: the `PhonetokTokenizer`
grapheme trie, vowel classification, `StressRules`, and `LanguageSpec` loading.
It supplies the Portuguese-specific data on top: the grapheme→IPA inventories,
the lexicon, the homograph pass, number expansion, and the regional accent
rules.

Because generation runs word-by-word, genuinely cross-word phonology is not
modelled on that path. Standard European Portuguese external `/s`-sandhi — a
word-final coda `/s` ([ʃ]) voicing before a vowel-initial next word (*os amigos*
→ [ˈuz ɐˈmiɡuʃ]) — is not applied in base `pt-PT`; `os` stays [ˈuʃ]. The
southern/insular presets' `sibilant_voicing_sandhi` is a per-token
approximation: it voices a token's own final [ʃ]→[ʒ] when the word ends in
`<s>`, with no visibility of the following word.

For the full token model see [docs/tokenizer.md](docs/tokenizer.md); for the
optional o2i-lattice base path see
[docs/lattice-base-migration.md](docs/lattice-base-migration.md).

---

## Sibling libraries

tugaphone is part of the TigreGotico Portuguese NLP stack:

| Library | Role |
|---------|------|
| [tugalex](https://github.com/TigreGotico/tugalex) | Phonetic lexicon |
| [silabificador](https://github.com/TigreGotico/silabificador) | Syllabifier |
| [bifonia](https://github.com/TigreGotico/bifonia) | Heterophone sense disambiguation |
| [orthography2ipa](https://github.com/TigreGotico/orthography2ipa) | Shared G2P primitives + stress rules |

---

## Documentation

- [docs/quickstart.md](docs/quickstart.md) — install, first call, dialect overview
- [docs/dialects.md](docs/dialects.md) — five inventories and sub-regional accent presets
- [docs/homographs.md](docs/homographs.md) — meaning-based disambiguation
- [docs/numbers.md](docs/numbers.md) — number normalization and gender agreement
- [docs/api.md](docs/api.md) — full class and function reference
- [docs/tokenizer.md](docs/tokenizer.md) — the Sentence → Word → Grapheme → Character model
- [docs/advanced.md](docs/advanced.md) — accents, serialization, integration
- [docs/benchmarking.md](docs/benchmarking.md) — the gold benchmark: rules-only PER per dialect
- [docs/scoreboard.md](docs/scoreboard.md) — accuracy per dialect
- [examples/](examples/) — ten runnable scripts

---

## License

Apache License 2.0. See [LICENSE](LICENSE).
