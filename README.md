# tugaphone — dialect-aware Portuguese phonemizer

**tugaphone** converts Portuguese text to IPA across all five Lusophone dialect groups.
It combines a curated phonetic lexicon, part-of-speech tagging for homograph
disambiguation, meaning-based heterophone resolution via
[bifonia](https://github.com/TigreGotico/bifonia), and a scientifically-grounded
regional-accent layer.

```
O gato dorme.
pt-PT → ˈu gˈa·tu ˈdoɾ·mɨ ˈ···
pt-BR → ˈu gˈa·tʊ ˈdoɾ·mɪ ˈ···
pt-AO → ˈu gˈa·tʊ ˈdoɾ·me ˈ···
pt-MZ → ˈu gˈa·tu ˈdoɾ·me ˈ···
pt-TL → ˈu gˈa·tʊ ˈdoɾ·me ˈ···
```

---

## Install

```bash
pip install tugaphone
```

---

## 30-second quick start

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
print(ph.phonemize_sentence("O gato dorme.", "pt-PT"))
# ˈu gˈa·tu ˈdoɾ·mɨ ˈ···
```

`TugaPhonemizer()` loads the lexicon and POS tagger once; then call
`phonemize_sentence(text, lang)` as many times as you like. Output is a
space-separated phoneme string — one token per word — with `ˈ` marking primary
stress and `·` marking syllable boundaries.

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
# pt-PT → ʃu·ˈvew mˈũj·tu ˈõ·tẽ ˈ···
# pt-BR → ʃo·ˈvew mwˈĩ·tʊ ˈõ·tẽ ˈ···
# pt-AO → ʃo·ˈvew mˈũjn·tʊ ˈõ·tẽ ˈ···
# pt-MZ → ʃu·ˈvew mˈũj·tu ˈõ·tẽ ˈ···
# pt-TL → ʃo·ˈvew mˈuj·tʊ ˈõ·tẽ ˈ···
```

### Homograph disambiguation

Heterophonic homographs are resolved at two levels:

1. **Meaning-based** (via bifonia): *sede* thirst vs HQ, *forma* mould vs shape.
2. **POS-based**: *gosto* noun /ˈgoʃtu/ vs verb /ˈgɔʃtu/, *para* preposition vs verb.

```python
print(ph.phonemize_sentence("Eu gosto de música."))   # verb → ˈgɔʃ·tu
print(ph.phonemize_sentence("Tenho bom gosto."))      # noun → ˈgoʃ·tu
```

### Sub-regional accents

`RegionalTransforms` presets layer phonological rules on top of any dialect.
Rules are grounded in published phonology (Cintra 1971; ALEPG). Every preset
is reachable by its BCP-47 private-use code:

```python
# Porto: stressed /o/ → [uo] (rising diphthong)
print(ph.phonemize_sentence("O vinho é muito bom.", "pt-PT-x-porto"))
# ˈu bˈi·ɲu ˈɛ mˈũj·tu bˈuõ ˈ···

# Açores: stressed /u/ → [y], l-palatalisation
print(ph.phonemize_sentence("O vinho é muito bom.", "pt-PT-x-azores"))
# ˈy vˈi·ɲu ˈɛ mˈỹj·tu bˈõ ˈ···

from tugaphone import list_dialects
print(list_dialects())   # all 20 registered codes
```

Available presets: `NorthernDialect`, `PortoDialect`, `MinhoDialect`,
`BragaDialect`, `FamalicaoDialect`, `FafeDialect`, `TrasMontanoDialect`,
`CoimbraDialect`, `AlentejoDialect`, `AlgarveDialect`, `MadeiraDialect`,
`AzoresDialect` — importable from `tugaphone.regional` and passable as
`regional_dialect=`, which overrides the code-derived preset.

### Number normalization

Digits are spelled out with gender agreement and long/short scale per dialect:

```python
from tugaphone.number_utils import normalize_numbers

normalize_numbers("vou comprar 1 casa")   # 'vou comprar uma casa'
normalize_numbers("vou adotar 1 cão")    # 'vou adotar um cão'
normalize_numbers("comprei 2 casas")     # 'comprei duas casas'
```

### Syllabification and stress

Syllabification is handled by [silabificador](https://github.com/TigreGotico/silabificador),
registered as an `orthography2ipa` syllabifier plugin. Stress detection delegates to
`orthography2ipa`'s declarative `StressRules`.

### Rules-only mode

Pass an `IRREGULAR_WORDS`-emptied dialect inventory to bypass the lexicon and use
only grapheme rules — useful for testing rule coverage or synthesising unknown words.

### orthography2ipa plugin interface

`TugaphoneG2PPlugin` implements `orthography2ipa`'s `G2PPlugin` interface;
`SilabificadorSyllabifier` implements its `SyllabifierPlugin` interface and
is registered at the `orthography2ipa.syllabify` entry point.

```python
from tugaphone.plugin import TugaphoneG2PPlugin

p = TugaphoneG2PPlugin(lang="pt-BR")
print(p.transcribe("o gato dorme"))   # ˈu gˈa·tʊ ˈdoɾ·mɪ
```

### IPA is built word-by-word (no cross-word sandhi)

tugaphone builds a sentence's IPA from a **character-level cascade**: each
`CharToken.ipa` composes into a `GraphemeToken`, graphemes into a
`WordToken.ipa`, and `Sentence.ipa` is those word IPAs joined with spaces —
each word transcribed **independently**. tugaphone does *not* route generation
through `orthography2ipa`'s pronunciation lattice (`G2P.ipa_lattice`) or its
`G2P.transcribe`; it consumes only o2i's shared *primitives* (the
`PhonetokTokenizer` grapheme trie, `vowels` classification, `StressRules`, and
`LanguageSpec` loading) and applies its own dialect grapheme rules.

A consequence is that genuinely cross-word phonology is not modelled on the
generation path. Standard European Portuguese **external `/s`-sandhi** — a
word-final coda `/s/` (isolated `[ʃ]`) voicing before a vowel-initial next word
(*os amigos* → `[ˈuz ɐˈmiɡuʃ]`, Mateus & d'Andrade 2000) — is **not** applied
in the base `pt-PT` output (`os` stays `[ˈuʃ]`). The southern/insular presets'
`sibilant_voicing_sandhi` is a per-token approximation: it voices a token's own
final `[ʃ]`→`[ʒ]` when the word ends in `<s>`, with no visibility of the
following word.

`orthography2ipa` (≥1.70) now carries this cross-word phonology natively — a
declarative `sandhi_rules` set on the `pt-PT` spec (`PT_FINAL_S_PREVOCALIC_VOICE`
→ `[z]`; `pt-PT-x-algarve`/`acores` → `[ʒ]`) run through its `SandhiEngine`, and
a `SentenceRescorer` / `SentenceLattice` **sentence-context seam** for
boundary-aware rewrites. tugaphone cannot consume either today because neither
its per-word IPA nor its lattice flows through o2i's `G2P`. Adopting the seam is
a scoped follow-up (a "B6 stage-2" refactor) that routes sentence-level
generation through o2i so cross-word sandhi is modelled once, upstream, instead
of re-approximated per token. See `docs/advanced.md`.

---

## Sibling libraries

tugaphone is part of the TigreGotico Portuguese NLP stack:

| Library | Role |
|---------|------|
| [tugalex](https://github.com/TigreGotico/tugalex) | Phonetic lexicon |
| [tugatagger](https://github.com/TigreGotico/tugatagger) | POS tagger |
| [silabificador](https://github.com/TigreGotico/silabificador) | Syllabifier |
| [bifonia](https://github.com/TigreGotico/bifonia) | Heterophone sense disambiguation |
| [orthography2ipa](https://github.com/TigreGotico/orthography2ipa) | G2P plugin base + stress rules |

---

## Documentation

- [docs/quickstart.md](docs/quickstart.md) — install, first call, dialect overview
- [docs/dialects.md](docs/dialects.md) — five inventories and sub-regional accent presets
- [docs/homographs.md](docs/homographs.md) — meaning-based and POS-based disambiguation
- [docs/numbers.md](docs/numbers.md) — number normalization and gender agreement
- [docs/api.md](docs/api.md) — full class and function reference
- [docs/tokenizer.md](docs/tokenizer.md) — the Sentence → Word → Grapheme → Character model
- [docs/advanced.md](docs/advanced.md) — accents, serialization, integration

---

## License

Apache License 2.0. See [LICENSE](LICENSE).
