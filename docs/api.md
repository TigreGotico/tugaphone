# API Reference

Every public symbol, with the signatures and return shapes as they exist in the
source.

## `tugaphone.TugaPhonemizer`

The phonemizer entry class.

```python
TugaPhonemizer()
```

Construction warms the lexicon so the first transcription is fast.

### `phonemize_sentence`

```python
phonemize_sentence(sentence: str,
                   lang: str = "pt-PT",
                   regional_dialect: Optional[RegionalTransforms] = None) -> str
```

Transcribes `sentence` to IPA for the target dialect. Returns a space-separated
phoneme string — one token per word, with `ˈ` for primary stress and `·` for
syllable boundaries.

`lang` is any code from `list_dialects()` — the five majors (`pt-PT`, `pt-BR`,
`pt-AO`, `pt-MZ`, `pt-TL`), the city inventories (`pt-BR-x-sao-paulo`, …) and
the regional accent presets (`pt-PT-x-porto`, …). Resolution is
case-insensitive with alias support; unknown codes fall back to European
Portuguese. See [dialects.md](dialects.md#dialect-codes).

When `regional_dialect` is given, the word is first run through the preset's
morpheme rules, transcribed, then run through its IPA rules; an explicit
preset overrides whatever `lang` resolves to. See
[`RegionalTransforms`](#tugaphoneregionalregionaltransforms).

```python
ph = TugaPhonemizer()
ph.phonemize_sentence("O gato dorme.", "pt-BR")   # 'ˈu gˈa·tʊ ˈdoɾ·mɪ'
```

### `get_dialect_inventory` (staticmethod)

```python
TugaPhonemizer.get_dialect_inventory(lang: str = "pt-PT") -> DialectInventory
```

Maps a dialect code to a fresh `DialectInventory` instance through the
dialect registry (`EuropeanPortuguese`, `BrazilianPortuguese`,
`AngolanPortuguese`, `MozambicanPortuguese`, `TimoresePortuguese`, plus the
city inventories `LisbonPortuguese`, `RioJaneiroPortuguese`,
`SaoPauloPortuguese`).

## `tugaphone.registry`

The dialect registry behind code resolution. The first three are re-exported
from the package root.

| Symbol | Role |
|--------|------|
| `resolve_dialect(lang)` | Resolve any BCP-47 code (case-insensitive, alias-aware) to its `DialectEntry`; unknown codes fall back to the parent tag, then `pt-PT`. |
| `list_dialects()` | Sorted list of all canonical dialect codes. |
| `DialectEntry` | Frozen record: `code`, `inventory` (class), `transforms` (preset or `None`), `region`, `aliases`. |
| `get_regional_transforms(lang)` | The `RegionalTransforms` preset for a code, or `None`. |
| `normalize_dialect_code(lang)` | BCP-47 case normalization (`PT-pt-X-PORTO` → `pt-PT-x-porto`). |

```python
from tugaphone import resolve_dialect, list_dialects

resolve_dialect("pt-PT-x-porto").region   # 'Porto / Douro Litoral'
len(list_dialects())                      # 20
```

## `tugaphone.number_utils`

### `normalize_numbers`

```python
normalize_numbers(text: str, lang: str = "pt-PT", strict: bool = True) -> str
```

Replaces numeric tokens in a sentence with their Portuguese written form,
inferring gender and ordinality from the surrounding words. `pt-PT` uses the
long scale (biliões), `pt-BR` the short scale (trilhões). With `strict=False`,
tokens that fail to format are left untouched instead of raising.

```python
from tugaphone.number_utils import normalize_numbers
normalize_numbers("vou comprar 1 casa")    # 'vou comprar uma casa'
normalize_numbers("vou adotar 2 cães")     # 'vou adotar dois cães'
normalize_numbers("1.5e10")                # 'um vírgula cinco vezes dez elevado a dez'
```

### `NumberParser`

A classmethod-based helper underneath `normalize_numbers`. Useful when you need
finer control or want to interrogate a single token.

| Method | Returns |
|--------|---------|
| `pronounce_number_word(word, prev_word=None, next_word=None, gender=None, as_ordinal=None, is_brazilian=False)` | Spelled-out form of one numeric token. |
| `to_int(word)` / `is_int(word)` | Integer value (ordinal markers stripped) / membership test. |
| `to_float(word)` / `is_float(word)` | Float value / membership test. |
| `is_scientific_notation(word)` | `True` for forms like `"1.5e10"`. |
| `pronounce_scientific(word, is_brazilian=False)` | Spoken form of scientific notation. |
| `is_ordinal(word, next_word=None)` | Detects `º`/`ª` markers, attached or separate. |
| `get_number_gender(word, prev_word=None, next_word=None)` | `"feminine"` or `"masculine"`. |

```python
from tugaphone.number_utils import NumberParser
NumberParser.pronounce_number_word("19", is_brazilian=True)                    # 'dezenove'
NumberParser.pronounce_number_word("19", is_brazilian=False)                   # 'dezanove'
NumberParser.pronounce_number_word("1", as_ordinal=True, gender="masculine")   # 'primeiro'
NumberParser.pronounce_number_word("1", as_ordinal=True, gender="feminine")    # 'primeira'
NumberParser.get_number_gender("1", next_word="casa")                          # 'feminine'
```

## `tugaphone.regional.RegionalTransforms`

A serializable dataclass holding the rules for a sub-regional accent.

```python
@dataclass
class RegionalTransforms:
    morpheme_rules: List[MorphemeTransform] = []   # applied to the word before G2P
    ipa_rules:      List[IPATransform]      = []    # applied to the IPA after G2P
```

| Member | Behaviour |
|--------|-----------|
| `apply_morpheme(word)` | Runs every morpheme rule in order, returns the rewritten word. |
| `apply_ipa(word, phonemes)` | Runs every IPA rule in order, returns the rewritten phoneme string. |
| `as_dict` (property) | Serializes the rule lists to rule-name strings. |
| `from_dict(data)` (staticmethod) | Rebuilds an instance from `{"ipa_rules": [...], "morpheme_rules": [...]}`; raises `ValueError` on an unknown IPA rule name. |

```python
from tugaphone.regional import PortoDialect, RegionalTransforms

cfg = PortoDialect.as_dict
clone = RegionalTransforms.from_dict(cfg)
[r.__name__ for r in clone.ipa_rules]   # ['rising_diphthong_o', ...]
```

### Preset accents

Importable from `tugaphone.regional`: `NorthernDialect`, `CoimbraDialect`,
`MinhoDialect`, `BragaDialect`, `FamalicaoDialect`, `TrasMontanoDialect`,
`PortoDialect`, `FafeDialect`, `AlentejoDialect`, `AlgarveDialect`,
`MadeiraDialect`, `AzoresDialect`. Each is a ready-built `RegionalTransforms`,
reachable by its dialect code (see the
[preset table](dialects.md#preset-table)) or passed explicitly to
`phonemize_sentence(..., regional_dialect=...)`.

Only the IPA rules listed in `RULE_MAP` round-trip through `as_dict`/`from_dict`;
accents built from other rule functions serialize a subset.

## `tugaphone.dialects`

| Symbol | Role |
|--------|------|
| `DialectInventory` | Base class: phoneme maps, character sets, stress/punctuation tokens. `dialect_code` attribute carries the tag. |
| `EuropeanPortuguese`, `BrazilianPortuguese`, `AngolanPortuguese`, `MozambicanPortuguese`, `TimoresePortuguese` | The five dialect inventories. |
| `LisbonPortuguese`, `RioJaneiroPortuguese`, `SaoPauloPortuguese` | City-level inventories backed by their own lexicon region maps. |
| `LEXICON` | Module-level `TugaLexicon()` instance; lazy-loaded on first use and warmed by `TugaPhonemizer.__init__`. |

You rarely instantiate these directly — `TugaPhonemizer` does it for you — but
they are the `dialect` argument the tokenizer accepts.

## `tugaphone.tokenizer`

The hierarchical model. See [tokenizer.md](tokenizer.md) for the full walkthrough;
the public surface is:

| Symbol | Role |
|--------|------|
| `Sentence(surface, words=[], dialect=EuropeanPortuguese())` | Top-level container; `.ipa`, `.words`, `.n_words`, `.features`. |
| `Sentence.from_postagged(surface, tags, dialect=None)` | Build from `(token, pos)` pairs (the path `TugaPhonemizer` uses). |
| `WordToken` | `.surface`, `.syllables`, `.graphemes`, `.stressed_syllable_idx`, `.ipa`, `.features`; phonological summaries `.stress_pattern`, `.syllable_structure_pattern`, `.phoneme_count`, `.vowel_sequence`, `.consonant_sequence`, `.has_diphthongs`, `.has_nasal_sounds`, `.has_palatal_sounds`, `.has_consonant_clusters`, `.is_homograph`, `.is_irregular`. |
| `GraphemeToken` | `.surface`, `.ipa`, `.is_diphthong`, `.is_nasal`, `.is_digraph`, `.features`; syllable features `.syllable_position`, `.phonological_weight`, `.has_complex_onset`, `.is_palatal`, `.triggers_palatalization`, `.is_vowel_grapheme`/`.is_consonant_grapheme`. |
| `CharToken` | character-level predicates (`.is_vowel`, `.is_consonant`, `.ipa`, ...); articulatory features `.manner_of_articulation`, `.place_of_articulation`, `.voicing`, `.vowel_height`/`.vowel_backness`/`.vowel_roundedness`, syllable role `.is_nucleus`/`.is_onset`/`.is_coda`. See [tokenizer.md](tokenizer.md#phonological-features). |

## `tugaphone.plugin`

Two classes that implement the `orthography2ipa` plugin interfaces.

### `TugaphoneG2PPlugin`

```python
TugaphoneG2PPlugin(lang: str = "pt-PT")
```

Implements `orthography2ipa.g2p_plugin.G2PPlugin`. The underlying
`TugaPhonemizer` loads lazily on first call.

| Member | Description |
|--------|-------------|
| `language_codes` | `list_dialects()` — every registered code, majors and regional accents alike. |
| `transcribe(text)` | Phonemize a full sentence. |
| `transcribe_word(word, context=None)` | Phonemize a single word; `context.lang` overrides `self.lang`. |

```python
from tugaphone.plugin import TugaphoneG2PPlugin

p = TugaphoneG2PPlugin(lang="pt-PT")
p.transcribe("o gato dorme")   # 'ˈu gˈa·tu ˈdoɾ·mɨ'
```

### `SilabificadorSyllabifier`

Implements `orthography2ipa.syllabifier_plugin.SyllabifierPlugin` and is
registered at the `orthography2ipa.syllabify` entry point so
`orthography2ipa`'s stress detection syllabifies Portuguese with
`silabificador` automatically.

```python
from tugaphone.plugin import SilabificadorSyllabifier

s = SilabificadorSyllabifier()
s.syllabify("fonologia")   # ['fo', 'no', 'lo', 'gi', 'a']
```

## Where next

- [quickstart.md](quickstart.md) — install and first call
- [dialects.md](dialects.md) — the five inventories and sub-regional accent presets
- [homographs.md](homographs.md) — meaning-based disambiguation
- [numbers.md](numbers.md) — number normalization and gender agreement
- [advanced.md](advanced.md) — recipes for accents and numbers
- [tokenizer.md](tokenizer.md) — the token tree and feature extraction
