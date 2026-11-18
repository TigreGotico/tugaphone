# API Reference

Every public symbol, with the signatures and return shapes as they exist in the
source.

## `tugaphone.TugaPhonemizer`

The phonemizer entry class. It drives the orthography2ipa lattice, see
[architecture.md](architecture.md).

```python
TugaPhonemizer()
```

### `phonemize_sentence`

```python
phonemize_sentence(sentence: str,
                   lang: str = "pt-PT",
                   contact: str = "none",
                   regional_dialect=None) -> str
```

Transcribes `sentence` to IPA for the target dialect through the orthography2ipa
lattice. Returns a space-separated phoneme string, one token per word, with `ˈ`
marking primary stress.

`lang` is any code from `list_dialects()` (or a legacy alias): the five national
standards (`pt-PT`, `pt-BR`, `pt-AO`, `pt-MZ`, `pt-TL`), the European and
Brazilian sub-regional varieties (`pt-PT-x-porto`, `pt-BR-x-sp`, …), and the
African, Asian and other lects. Resolution is case-insensitive with alias
support, an unresolved code falls back to `pt-PT`. See
[dialects.md](dialects.md#the-lect-codes).

`contact` sets the code-switch policy: `"none"` (the default) transcribes
every word as Portuguese, `"auto"` detects Spanish, French and English words,
and `"es"`, `"fr"` or `"en"` forces one contact lattice. Any other value raises
`ValueError`. See [codeswitch.md](codeswitch.md).

`regional_dialect` is **deprecated and ignored**. The accent is selected
entirely by `lang`, it is encoded in the orthography2ipa lect spec, not applied
as a post-hoc transform. Passing it emits a `DeprecationWarning`.

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
ph.phonemize_sentence("O gato dorme.", "pt-BR")        # 'u ˈɡatu ˈdoɾmi'
ph.phonemize_sentence("O vinho é bom.", "pt-PT-x-porto")  # 'u ˈbiɲu ˈjɛ ˈbõ'
```

### `force_accent` (staticmethod)

```python
TugaPhonemizer.force_accent(text: str, lect: str, mode: str = "ipa",
                            base_lect: str = "pt-PT",
                            overlay: AccentOverlay | None = None) -> str
```

The same call as [`tugaphone.force_accent`](#force_accent), without the `rules`
argument.

### `is_supported` (staticmethod)

```python
TugaPhonemizer.is_supported(lang: str) -> bool
```

Whether `lang` names a tugaphone lect, itself or through an alias
(`"pt"`, `"pt_BR"`, `"pt-PT-x-azores"`). The same function is
`tugaphone.is_supported` and `tugaphone.registry.is_supported`.

A tag that `resolve_lect` answers only by its fallback returns `False`:
another language (`"en-US"`, `"es-ES"`), a lect written in another
orthography (`"pt-PT-x-medieval"`, Barranquenho `"ext-PT-x-barranco"`) and
an unknown sub-tag (`"pt-PT-x-unknown"`). `resolve_lect` still answers these
tags with a fallback lect and a warning.

```python
from tugaphone import is_supported

is_supported("pt-BR-x-sao-paulo")  # True
is_supported("en-US")              # False
```

## `tugaphone.phonemize`

```python
phonemize(text: str, lang: str = "pt-PT", contact: str = "none") -> str
```

The function behind `TugaPhonemizer.phonemize_sentence`, with the same `lang`
and `contact` arguments and the same return value. It takes no
`regional_dialect` argument.

```python
import tugaphone

tugaphone.phonemize("O gato dorme.", "pt-BR")   # 'u ˈɡatu ˈdoɾmi'
```

## `tugaphone.accent`

Accent forcing for downstream TTS. All symbols are re-exported from the package
root. See [accent_forcing.md](accent_forcing.md) for the guide.

### `force_accent`

```python
force_accent(text: str, lect: str, mode: str = "ipa",
             base_lect: str = "pt-PT",
             overlay: AccentOverlay | None = None,
             rules: tuple[RespellRule, ...] = DEFAULT_RESPELL_RULES) -> str
```

Force `text` into the `lect` accent. `mode="ipa"` returns the target lect's IPA
(phoneme-input TTS), `mode="respell"` returns Portuguese text respelled so a
grapheme-input TTS speaking `base_lect` pronounces the target accent. An optional
`overlay` of user tweaks is applied last. `rules` is the respelling rule table.
Any other `mode` raises `ValueError`.

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

## `tugaphone.pipeline`

```python
pipeline(lect: str) -> orthography2ipa.Pipeline
```

Returns the orthography2ipa `Pipeline` that tugaphone runs for `lect`: the
lect's packaged lexicon (`pt-PT` and `pt-BR`, an empty dict for every other
lect), the text and number expansion as `expand`, and bifonia's homograph marks
as `mark`. `G2P(lect, pipeline=pipeline(lect)).transcribe(text)` gives the same
output as `phonemize(text, lect)`, and `phonemize` builds its engine from this
function.

The function covers `contact="none"` only. With `contact="auto"`, `phonemize`
sends contact words through the `es-ES`, `fr-FR` or `en-US` lattice, and one
`Pipeline` cannot express that.

`lect` must be a code of `list_dialects()`. Any other code raises `ValueError`.
tugaphone and orthography2ipa resolve a loose tag differently: `resolve_lect("br")`
gives `pt-PT`, and orthography2ipa resolves `br` to Breton. Resolve the tag with
`resolve_lect` and pass the result to both. Each call returns a new `Pipeline`,
because the lexicon is a mutable dict.

```python
from orthography2ipa import G2P
import tugaphone

lect = tugaphone.resolve_lect("pt_pt")
engine = G2P(lect, pipeline=tugaphone.pipeline(lect))
engine.transcribe("Tenho 3 gatos.")   # same as tugaphone.phonemize("Tenho 3 gatos.", lect)
```

## `tugaphone.revision`

```python
revision(lang: str = "pt-PT") -> str
```

Returns a string that changes when the output of `phonemize(text, lang)` can
change, for some text. A voice records the revision of the lect it was trained
on. At load time, an equal revision tells that the running tugaphone gives the
same output, even when the version differs.

The revision covers `contact="none"`, the default and the path that scriptconv
uses. Another `contact` value also reads the `en-US`, `es-ES` and `fr-FR` specs
of orthography2ipa and the optional markovonnx detector. The
revision covers neither, so it can stay equal while that output changes.

The value is `tp1:` and a SHA-256 in hex. The hash covers:

- `unicodedata.unidata_version` of the running Python. The Unicode database
  decides how the text stages normalise and classify characters.
- `orthography2ipa.spec_revision(lect)`, and `lexicon_revision(lect, patches=True)`
  for `pt-PT` and `pt-BR`, the lects that take a packaged lexicon.
- Each other distribution that a probe call of `phonemize` for the lect imports,
  in a fresh process. The distribution counts whole: the code tokens of each of
  its Python modules, also the modules that the probe does not load, and the
  bytes of each of its data files.

A comment, a docstring, a blank line, the width of an indent, and a `version.py`
or `_version.py` at the top of a package do not count. A version string does not
count, with one exception. A distribution that ships a compiled module, such as
`numpy`, counts by its name and version, because its files differ by platform.

A distribution whose files cannot be read from the file system, such as a
package imported from a zip, raises `RevisionError`. A hash of no files would
stay equal across every edit of that distribution.

The probe also raises `RevisionError` when its process fails, prints no
result, prints a result that is not JSON, or runs longer than 120 s.
`tugaphone.RevisionError` is a subclass of `RuntimeError`.

`lang` resolves as `phonemize` resolves it, with the same warning for a code that
is not a lect. So `revision("pt")` equals `revision("pt-PT")`. The first call for
a lect in a process runs the probe and reads the files, which takes some seconds.
Later calls return the kept value.

```python
import tugaphone

tugaphone.revision("pt-PT")   # 'tp1:' and 64 hex digits
tugaphone.revision("pt-BR")   # another value: the specs differ
```

## `tugaphone.registry`

The dialect registry behind code resolution. `list_dialects` and `resolve_lect`
are re-exported from the package root.

| Symbol | Role |
|--------|------|
| `resolve_lect(lang="pt-PT")` | Resolve any BCP-47 code (case-insensitive, alias-aware) to the orthography2ipa lect code that answers for it, unresolved codes fall back to the parent tag, then `pt-PT`. |
| `list_dialects()` | Sorted list of every reachable lect code (the Portuguese-family orthography2ipa specs). |
| `is_supported(lang)` | Whether `lang` names a lect, itself or through an alias. See [`is_supported`](#is_supported-staticmethod). |
| `default_contact(lect)` | The contact language that `contact="auto"` gives an unclassified word: `"es"` for `pt-UY`, `"en"` for every other lect. |
| `PACKAGED_LEXICON_LECTS` | The lects that take a packaged orthography2ipa lexicon: `pt-PT` and `pt-BR`. |
| `lexicon_region(lect)` | **Deprecated**, returns `None`: no lect takes a `tugalex` region map. Emits a `DeprecationWarning` that names the removal release. |
| `normalize_dialect_code(lang)` | BCP-47 case normalization (`PT-pt-X-PORTO` → `pt-PT-x-porto`). |
| `resolve_dialect(lang)` | **Deprecated** alias for `resolve_lect`, emits a `DeprecationWarning`. |
| `get_dialect_inventory(lang="pt-PT")` | **Deprecated**, returns the `tugaphone.dialects` inventory of the nearest national standard. Emits a `DeprecationWarning` and goes in tugaphone 2.0.0. |

```python
from tugaphone import resolve_lect, list_dialects

resolve_lect("pt-PT-x-lisboa")   # 'pt-PT-x-lisbon'  (alias)
"pt-BR-x-sp" in list_dialects()  # True
```

## `tugaphone.lattice_core.normalize_spelling`

```python
normalize_spelling(text: str, lect: str) -> str
```

The spelling step, the first part of the `expand` step of the pipeline. It
rewrites the old spellings of `text` in the AO1990 norm of `lect` with
desacordo_ortografico: `ao1990-br` for the Brazilian lects and `pt-UY`,
`ao1990-pt` for every other lect. Pass a code of `list_dialects()`: a loose tag
such as `"pt"` raises `ValueError`, so resolve it with `resolve_lect` first. Text
that is already in the AO1990 spelling stays as written. See
[text_normalization.md](text_normalization.md#old-spellings) for the changes
it makes to modern text.

```python
from tugaphone.lattice_core import normalize_spelling
normalize_spelling("A acção da pharmacia foi rápida.", "pt-PT")   # 'A ação da farmácia foi rápida.'
normalize_spelling("Tive uma ideia.", "pt-BR")                    # 'Tive uma idéia.'
```

## `tugaphone.number_utils`

### `normalize_numbers`

```python
normalize_numbers(text: str, lang: str = "pt-PT", strict: bool = True,
                  scale: str | None = None) -> str
```

Reads the numbers, dates, clock times, money, measures and abbreviations of
`text` with text2spoken, in the variety of `lang`, and reads the forms that
text2spoken leaves as written with the
[fallback rewrites](text_normalization.md#fallback-rewrites). The rest of the
text stays as written. `pt-PT` uses the long scale (biliões) and `pt-BR` the
short scale (trilhões); `scale="long"` or `scale="short"` overrides the scale.
A form that is still unread stays as written, and a form with digits gives an
`UnreadFormWarning`. With `strict=True`, the default, an error in text2spoken
raises; with `strict=False`, `text` comes back as written. See
[numbers.md](numbers.md).

```python
from tugaphone.number_utils import normalize_numbers
normalize_numbers("vou comprar 1 casa")                  # 'vou comprar uma casa'
normalize_numbers("Nasceu a 25/12/2023.")                # 'Nasceu a vinte e cinco de dezembro de dois mil e vinte e três.'
normalize_numbers("A reunião é às 19h30.", "pt-BR")      # 'A reunião é às dezenove horas e trinta minutos.'
```

### `text2spoken_tag`

```python
text2spoken_tag(lang: str) -> str
```

The text2spoken variety that a lect reads: `"pt-PT"` for the lects of the
`ao1990-pt` spelling norm and `"pt-BR"` for the lects of `ao1990-br`.

```python
from tugaphone.number_utils import text2spoken_tag
text2spoken_tag("pt-AO")   # 'pt-PT'
text2spoken_tag("pt-UY")   # 'pt-BR'
```

### `NumberParser`

**Deprecated.** The token helper of tugaphone 1.7. Its readings come from
text2spoken. Importing it emits a `DeprecationWarning` that names the removal
release, tugaphone 2.0.0. Use `normalize_numbers` instead.

| Method | Returns |
|--------|---------|
| `pronounce_number_word(word, prev_word=None, next_word=None, gender=None, as_ordinal=None, is_brazilian=False, scale=None)` | Spelled-out form of one numeric token. |
| `to_int(word)` / `is_int(word)` | Integer value (ordinal markers stripped) / membership test. |
| `to_float(word)` / `is_float(word)` | Float value / membership test. |
| `is_decimal(word)` | `True` for a non-scientific decimal like `"10,4"`. |
| `is_scientific_notation(word)` | `True` for forms like `"1.5e10"`. |
| `pronounce_scientific(word, is_brazilian=False, scale=None)` | Spoken form of scientific notation. |
| `is_ordinal(word, next_word=None)` | Detects `º`/`ª` markers, attached or separate. |
| `get_number_gender(word, prev_word=None, next_word=None)` | `"feminine"` or `"masculine"`. |

```python
from tugaphone.number_utils import NumberParser
NumberParser.pronounce_number_word("19", is_brazilian=True)                    # 'dezenove'
NumberParser.pronounce_number_word("19", is_brazilian=False)                   # 'dezanove'
NumberParser.pronounce_number_word("1", as_ordinal=True, gender="masculine")   # 'primeiro'
NumberParser.get_number_gender("1", next_word="casa")                          # 'feminine'
```

## `tugaphone.text_normalization`

### `normalize_text`

```python
normalize_text(text: str, lang: str = "pt-PT") -> str
```

The words a speaker of `lang` says for `text`: the `expand` step of the
pipeline after the spelling step. It expands abbreviations, acronyms and
letter-digit codes, then reads the numbers as `normalize_numbers` does, then
reads the Roman numerals that text2spoken leaves. See
[text_normalization.md](text_normalization.md).

```python
from tugaphone.text_normalization import normalize_text
normalize_text("O Sr. presidente pagou 20%.")   # 'O Senhor presidente pagou vinte por cento.'
```

### The rewrites

`normalize_orthography(text, lang="pt-PT")` runs the rewrites of tugaphone 1.7
and leaves the digits for `normalize_numbers`. Each rewrite is public:
`separate_unit_symbols`, `split_number_ranges`, `expand_clock_times`,
`normalize_number_separators`, `expand_abbreviations`,
`expand_regnal_numerals(text, lang)`, `expand_acronyms` and
`expand_letter_digit_codes(text, lang)`. See
[text_normalization.md](text_normalization.md) for each one.

## `tugaphone.tokenizer` and `tugaphone.dialects`

**Deprecated.** Both modules and `tugaphone.registry.get_dialect_inventory`
emit a `DeprecationWarning` and go in tugaphone 2.0.0. The phonemization path
does not use them.

These modules are the token-tree **feature** API and the rules-only benchmark
baseline. They are not the phonemization path, `phonemize_sentence` runs on the
orthography2ipa lattice and never routes through them. Use them to inspect
manner, place, voicing, vowel height, syllable roles and CV skeletons. See
[tokenizer.md](tokenizer.md) for the full model, the public surface is:

| Symbol | Role |
|--------|------|
| `Sentence(surface, words=[], dialect=EuropeanPortuguese())` | Top-level container, `.ipa`, `.words`, `.n_words`, `.features`. |
| `WordToken` | `.surface`, `.syllables`, `.n_syllables`, `.graphemes`, `.stressed_syllable_idx`, `.ipa`, `.features`, phonological summaries `.stress_pattern`, `.syllable_structure_pattern`, `.phoneme_count`, `.vowel_sequence`, `.consonant_sequence`, `.has_diphthongs`, `.has_nasal_sounds`, `.has_palatal_sounds`, `.has_consonant_clusters`, `.is_homograph`, `.is_irregular`. |
| `GraphemeToken` | `.surface`, `.ipa`, `.is_diphthong`, `.is_nasal`, `.is_digraph`, `.features`, syllable features `.syllable_position`, `.phonological_weight`, `.has_complex_onset`, `.is_palatal`, `.triggers_palatalization`, `.is_vowel_grapheme`/`.is_consonant_grapheme`. |
| `CharToken` | character-level predicates (`.is_vowel`, `.is_consonant`, `.ipa`, ...), articulatory features `.manner_of_articulation`, `.place_of_articulation`, `.voicing`, `.vowel_height`/`.vowel_backness`/`.vowel_roundedness`, syllable role `.is_nucleus`/`.is_onset`/`.is_coda`. |

`tugaphone.dialects` supplies the `DialectInventory` subclasses those tokens
read (`EuropeanPortuguese`, `BrazilianPortuguese`, `AngolanPortuguese`,
`MozambicanPortuguese`, `TimoresePortuguese`, and city inventories) plus the
module-level `LEXICON` (`TugaLexicon()`) instance.

## Where next

- [architecture.md](architecture.md), the lattice core and caller-owned layers
- [dialects.md](dialects.md), the lect codes and aliases
- [homographs.md](homographs.md), meaning-based disambiguation
- [numbers.md](numbers.md), number normalization and gender agreement
- [tokenizer.md](tokenizer.md), the token tree and feature extraction


---
[← Text normalization](text_normalization.md) · [Home](../README.md) · [Tokenizer →](tokenizer.md)
