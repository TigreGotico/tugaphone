# API Reference

Every public symbol, with the signatures and return shapes as they exist in the
source.

## `tugaphone.TugaPhonemizer`

The phonemizer entry class. It drives the orthography2ipa lattice; see
[architecture.md](architecture.md).

```python
TugaPhonemizer()
```

### `phonemize_sentence`

```python
phonemize_sentence(sentence: str,
                   lang: str = "pt-PT",
                   regional_dialect=None) -> str
```

Transcribes `sentence` to IPA for the target dialect through the orthography2ipa
lattice. Returns a space-separated phoneme string — one token per word, with `ˈ`
marking primary stress.

`lang` is any code from `list_dialects()` (or a legacy alias): the five national
standards (`pt-PT`, `pt-BR`, `pt-AO`, `pt-MZ`, `pt-TL`), the European and
Brazilian sub-regional varieties (`pt-PT-x-porto`, `pt-BR-x-sp`, …), and the
African, Asian and other lects. Resolution is case-insensitive with alias
support; an unresolved code falls back to `pt-PT`. See
[dialects.md](dialects.md#the-lect-codes).

`regional_dialect` is **deprecated and ignored**. The accent is selected
entirely by `lang` — it is encoded in the orthography2ipa lect spec, not applied
as a post-hoc transform. Passing it emits a `DeprecationWarning`.

```python
ph = TugaPhonemizer()
ph.phonemize_sentence("O gato dorme.", "pt-BR")        # 'ˈu ˈgatʊ ˈdoɾmi'
ph.phonemize_sentence("O vinho é bom.", "pt-PT-x-porto")  # 'ˈwo ˈbiɲu ˈjɛ ˈbõ'
```

### `is_supported` (staticmethod)

```python
TugaPhonemizer.is_supported(lang: str) -> bool
```

Whether `lang` resolves to a known Portuguese lect.

## `tugaphone.accent`

Accent forcing for downstream TTS. All symbols are re-exported from the package
root. See [accent_forcing.md](accent_forcing.md) for the guide.

### `force_accent`

```python
force_accent(text: str, lect: str, mode: str = "ipa",
             base_lect: str = "pt-PT",
             overlay: AccentOverlay | None = None) -> str
```

Force `text` into the `lect` accent. `mode="ipa"` returns the target lect's IPA
(phoneme-input TTS); `mode="respell"` returns Portuguese text respelled so a
grapheme-input TTS speaking `base_lect` pronounces the target accent. An optional
`overlay` of user tweaks is applied last.

### `respell` / `respell_word`

```python
respell(text: str, target_lect: str, base_lect: str = "pt-PT", rules=…) -> str
respell_word(word: str, target_lect: str, base_lect: str = "pt-PT", rules=…) -> str
```

The respeller behind `mode="respell"`. Verification-gated: an orthographic edit
is kept only if re-transcribing it with `base_lect` moves it closer to the target
IPA, so respelling never worsens a word and leaves unspellable contrasts
unchanged. `rules` defaults to `DEFAULT_RESPELL_RULES` (a tuple of `RespellRule`).

### `AccentOverlay` / `Transform`

User-space ad-hoc tweak layer applied after the lattice. An `AccentOverlay` is an
ordered list of `Transform`s (`kind` `"regex"`/`"word"`, `pattern`,
`replacement`, `stage` `"ipa"`/`"text"`, `ignore_case`). JSON-serialisable via
`to_json` / `from_json` (and `to_dict` / `from_dict`) so a voice tweak is
shareable.

## `tugaphone.registry`

The dialect registry behind code resolution. `list_dialects` and `resolve_lect`
are re-exported from the package root.

| Symbol | Role |
|--------|------|
| `resolve_lect(lang="pt-PT")` | Resolve any BCP-47 code (case-insensitive, alias-aware) to the orthography2ipa lect code that answers for it; unresolved codes fall back to the parent tag, then `pt-PT`. |
| `list_dialects()` | Sorted list of every reachable lect code (the Portuguese-family orthography2ipa specs). |
| `lexicon_region(lect)` | The `tugalex` region whose lexicon overlays `lect`, or `None` for a pure-lattice lect. |
| `normalize_dialect_code(lang)` | BCP-47 case normalization (`PT-pt-X-PORTO` → `pt-PT-x-porto`). |
| `resolve_dialect(lang)` | **Deprecated** alias for `resolve_lect`; emits a `DeprecationWarning`. |

```python
from tugaphone import resolve_lect, list_dialects

resolve_lect("pt-PT-x-lisboa")   # 'pt-PT-x-lisbon'  (alias)
len(list_dialects())             # 41
```

## `tugaphone.number_utils`

### `normalize_numbers`

```python
normalize_numbers(text: str, lang: str = "pt-PT", strict: bool = True) -> str
```

Replaces numeric tokens in a sentence with their Portuguese written form,
inferring gender and ordinality from the surrounding words. `pt-PT` uses the
long scale (biliões), `pt-BR` the short scale (trilhões). With `strict=False`,
tokens that fail to format are left untouched instead of raising. This runs
inside the engine's `normalize` stage before the lattice sees the text.

```python
from tugaphone.number_utils import normalize_numbers
normalize_numbers("vou comprar 1 casa")    # 'vou comprar uma casa'
normalize_numbers("vou adotar 1 cão")      # 'vou adotar um cão'
normalize_numbers("comprei 2 casas")       # 'comprei duas casas'
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
NumberParser.get_number_gender("1", next_word="casa")                          # 'feminine'
```

## `tugaphone.tokenizer` and `tugaphone.dialects`

These modules are the token-tree **feature** API and the rules-only benchmark
baseline. They are not the phonemization path — `phonemize_sentence` runs on the
orthography2ipa lattice and never routes through them. Use them to inspect
manner, place, voicing, vowel height, syllable roles and CV skeletons. See
[tokenizer.md](tokenizer.md) for the full model; the public surface is:

| Symbol | Role |
|--------|------|
| `Sentence(surface, words=[], dialect=EuropeanPortuguese())` | Top-level container; `.ipa`, `.words`, `.n_words`, `.features`. |
| `Sentence.from_postagged(surface, tags, dialect=None)` | Build from `(token, pos)` pairs. |
| `WordToken` | `.surface`, `.syllables`, `.graphemes`, `.stressed_syllable_idx`, `.ipa`, `.features`; phonological summaries `.stress_pattern`, `.syllable_structure_pattern`, `.phoneme_count`, `.vowel_sequence`, `.consonant_sequence`, `.has_diphthongs`, `.has_nasal_sounds`, `.has_palatal_sounds`, `.has_consonant_clusters`, `.is_homograph`, `.is_irregular`. |
| `GraphemeToken` | `.surface`, `.ipa`, `.is_diphthong`, `.is_nasal`, `.is_digraph`, `.features`; syllable features `.syllable_position`, `.phonological_weight`, `.has_complex_onset`, `.is_palatal`, `.triggers_palatalization`, `.is_vowel_grapheme`/`.is_consonant_grapheme`. |
| `CharToken` | character-level predicates (`.is_vowel`, `.is_consonant`, `.ipa`, ...); articulatory features `.manner_of_articulation`, `.place_of_articulation`, `.voicing`, `.vowel_height`/`.vowel_backness`/`.vowel_roundedness`, syllable role `.is_nucleus`/`.is_onset`/`.is_coda`. |

`tugaphone.dialects` supplies the `DialectInventory` subclasses those tokens
read (`EuropeanPortuguese`, `BrazilianPortuguese`, `AngolanPortuguese`,
`MozambicanPortuguese`, `TimoresePortuguese`, and city inventories) plus the
module-level `LEXICON` (`TugaLexicon()`) instance.

## `tugaphone.plugin`

Two classes that implement the `orthography2ipa` plugin interfaces.

### `TugaphoneG2PPlugin`

```python
TugaphoneG2PPlugin(lang: str = "pt-PT")
```

Implements `orthography2ipa.g2p_plugin.G2PPlugin`.

| Member | Description |
|--------|-------------|
| `language_codes` | `list_dialects()` — every reachable lect code. |
| `transcribe(text)` | Phonemize a full sentence. |
| `transcribe_word(word, context=None)` | Phonemize a single word; `context.lang` overrides `self.lang`. |

```python
from tugaphone.plugin import TugaphoneG2PPlugin

p = TugaphoneG2PPlugin(lang="pt-BR")
p.transcribe("o gato dorme")   # 'ˈu ˈgatʊ ˈdoɾmi'
```

### `SilabificadorSyllabifier`

Implements `orthography2ipa.syllabifier_plugin.SyllabifierPlugin`, wrapping
`silabificador`. `orthography2ipa[portuguese]` (a tugaphone dependency) already
ships its own `silabificador`-backed syllabifier, so tugaphone does not register
a competing entry point for it.

```python
from tugaphone.plugin import SilabificadorSyllabifier

s = SilabificadorSyllabifier()
s.syllabify("fonologia")   # ['fo', 'no', 'lo', 'gi', 'a']
```

## Where next

- [architecture.md](architecture.md) — the lattice core and caller-owned layers
- [dialects.md](dialects.md) — the lect codes and aliases
- [homographs.md](homographs.md) — meaning-based disambiguation
- [numbers.md](numbers.md) — number normalization and gender agreement
- [tokenizer.md](tokenizer.md) — the token tree and feature extraction
