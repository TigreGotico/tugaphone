# API Reference

Every public symbol, with the signatures and return shapes as they exist in the
source.

## `tugaphone.TugaPhonemizer`

The phonemizer entry class.

```python
TugaPhonemizer(postag_engine="auto", postag_model="pt_core_news_lg")
```

| Argument | Meaning |
|----------|---------|
| `postag_engine` | POS tagging backend passed to `TugaTagger`: `"auto"`, `"spacy"`, `"brill"`, `"lexicon"`, `"dummy"`. |
| `postag_model` | Model identifier for engines that take one (e.g. the spaCy model name). |

Construction builds the `TugaTagger` and warms the lexicon so the first
transcription is fast.

### `phonemize_sentence`

```python
phonemize_sentence(sentence: str,
                   lang: str = "pt-PT",
                   regional_dialect: Optional[RegionalTransforms] = None) -> str
```

Transcribes `sentence` to IPA for the target dialect. Returns a space-separated
phoneme string — one token per word, with `ˈ` for primary stress and `·` for
syllable boundaries; punctuation tokens are preserved.

`lang` is one of `pt-PT`, `pt-BR`, `pt-AO`, `pt-MZ`, `pt-TL`; any other value
falls back to European Portuguese.

When `regional_dialect` is given, the word is first run through the preset's
morpheme rules, transcribed, then run through its IPA rules. See
[`RegionalTransforms`](#tugaphoneregionalregionaltransforms).

```python
ph = TugaPhonemizer()
ph.phonemize_sentence("O gato dorme.", "pt-BR")   # 'ˈu gˈa·tʊ ˈdɔh·me'
```

### `get_dialect_inventory` (staticmethod)

```python
TugaPhonemizer.get_dialect_inventory(lang: str = "pt-PT") -> DialectInventory
```

Maps a dialect code to its `DialectInventory` instance (`EuropeanPortuguese`,
`BrazilianPortuguese`, `AngolanPortuguese`, `MozambicanPortuguese`,
`TimoresePortuguese`).

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
NumberParser.pronounce_number_word("19", is_brazilian=True)   # 'dezenove'
NumberParser.pronounce_number_word("19", is_brazilian=False)  # 'dezanove'
NumberParser.pronounce_number_word("1", next_word="º")        # 'primeiro' (ordinal)
NumberParser.get_number_gender("1", next_word="casa")         # 'feminine'
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
| `apply_morpheme(word, postag="NOUN")` | Runs every morpheme rule in order, returns the rewritten word. |
| `apply_ipa(word, phonemes, postag="NOUN")` | Runs every IPA rule in order, returns the rewritten phoneme string. |
| `as_dict` (property) | Serializes the rule lists to rule-name strings. |
| `from_dict(data)` (staticmethod) | Rebuilds an instance from `{"ipa_rules": [...], "morpheme_rules": [...]}`; raises `ValueError` on an unknown IPA rule name. |

```python
from tugaphone.regional import PortoDialect, RegionalTransforms

cfg = PortoDialect.as_dict
clone = RegionalTransforms.from_dict(cfg)
[r.__name__ for r in clone.ipa_rules]   # ['rising_diphthong_o', ...]
```

### Preset accents

Importable from `tugaphone.regional`: `CoimbraDialect`, `MinhoDialect`,
`BragaDialect`, `FamalicaoDialect`, `TrasMontanoDialect`, `PortoDialect`,
`FafeDialect`. Each is a ready-built `RegionalTransforms`. Pass any of them to
`phonemize_sentence(..., regional_dialect=...)`.

Only the IPA rules listed in `RULE_MAP` round-trip through `as_dict`/`from_dict`;
accents built from other rule functions serialize a subset.

## `tugaphone.dialects`

| Symbol | Role |
|--------|------|
| `DialectInventory` | Base class: phoneme maps, character sets, stress/punctuation tokens. `dialect_code` attribute carries the tag. |
| `EuropeanPortuguese`, `BrazilianPortuguese`, `AngolanPortuguese`, `MozambicanPortuguese`, `TimoresePortuguese` | The five dialect inventories. |
| `LisbonPortuguese`, `RioJaneiroPortuguese`, `SaoPauloPortuguese` | City-specific inventories layered on the base dialects. |
| `LEXICON` | Module-level `TugaLexicon()` instance; `LEXICON.get_ipa_map(region=...)` returns the per-region exception map. |

You rarely instantiate these directly — `TugaPhonemizer` does it for you — but
they are the `dialect` argument the tokenizer accepts.

## `tugaphone.tokenizer`

The hierarchical model. See [tokenizer.md](tokenizer.md) for the full walkthrough;
the public surface is:

| Symbol | Role |
|--------|------|
| `Sentence(surface, words=[], dialect=EuropeanPortuguese())` | Top-level container; `.ipa`, `.words`, `.n_words`, `.features`. |
| `Sentence.from_postagged(surface, tags, dialect=None)` | Build from `(token, pos)` pairs (the path `TugaPhonemizer` uses). |
| `WordToken` | `.surface`, `.syllables`, `.graphemes`, `.stressed_syllable_idx`, `.ipa`, `.features`. |
| `GraphemeToken` | `.surface`, `.ipa`, `.is_diphthong`, `.is_nasal`, `.is_digraph`, `.features`, and more predicates. |
| `CharToken` | character-level predicates (`.is_vowel`, `.is_consonant`, `.ipa`, ...). |

## Where next

- [quickstart.md](quickstart.md) — install and first call
- [advanced.md](advanced.md) — recipes for accents, POS engines, numbers
- [tokenizer.md](tokenizer.md) — the token tree and feature extraction
