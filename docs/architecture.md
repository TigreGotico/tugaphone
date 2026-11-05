# Architecture

tugaphone phonemizes Portuguese by driving the shared
[orthography2ipa](https://github.com/TigreGotico/orthography2ipa) candidate
lattice and layering on top only the stages orthography2ipa leaves to the
caller. A dialect *is* an orthography2ipa lect spec, so selecting a dialect is
selecting a lect.

## The lattice core

`TugaPhonemizer().phonemize_sentence(text, lang)` resolves `lang` to an
orthography2ipa lect code and drives
`orthography2ipa.G2P(lect, normalizer=...).transcribe(text)`, with the
lexicon for that lect enabled first. Every Portuguese-family lect ships
an engine spec whose grapheme table, `allophone_rules` and cross-word
`sandhi_rules` encode that variety's phonology. The dialect phenomena are
produced by the lattice itself, not by a post-hoc string-transform pass:

- northern **betacism** (`/v/` → `[b]`, *vinho* → `[ˈbiɲu]`),
- Porto **rising diphthongs** (*bola* → `[ˈbwɔlɐ]`, *é* → `[ˈjɛ]`),
- Transmontano `<ch>` → `[tʃ]` and the apico-alveolar `[s̺]`,
- Madeiran `/l/` → `[ʎ]`,
- Azorean and Alentejan stressed `/u/` → `[y]`,
- Brazilian `/t d/` palatalization before `[i]` and coda-`/l/` vocalization,
- coda-sibilant voicing **sandhi** across word boundaries,

and the rest of each lect's inventory, allophony and stress. There is no
string-edit layer applied after transcription.

## The caller-owned layers

tugaphone contributes the concerns orthography2ipa deliberately does not own,
wired through orthography2ipa's own extension points (see
`tugaphone/lattice_core.py`). The third stage below, syllabification, comes
from orthography2ipa itself:

### 1. Normalization / verbalization

Orthographic rewrites (`tugaphone.text_normalization.normalize_orthography`:
ranges, clock times, separators, abbreviations, Roman numerals, acronyms),
gender-aware number and ordinal expansion
(`tugaphone.number_utils.normalize_numbers`) and sense-based
heterophonic-homograph marking (`bifonia.add_extra_diacritics`, e.g. *sede*
thirst `/ˈsedɨ/` vs seat `/ˈsɛdɨ/`) run in that order as the engine's
`normalizer`, the orthography2ipa `normalize` stage, before the lattice sees the
text. Numbers are verbalized before homograph marking, so their spelled-out
words are available to it. All three are orthographic, pre-lattice
transformations.

### 2. Lexicon

The `pt-PT` and `pt-BR` lects each take a residual lexicon of
[`o2i-lexicons`](https://github.com/TigreGotico/o2i-lexicons), enabled through
`orthography2ipa.use_packaged_lexicons`. A covered word folds into the same
override path as a spec `word_exceptions` entry. Each lexicon holds only the
words that the lect's rules get wrong. The `pt-PT` entries come from the
Infopédia readings of the
[portuguese-unified pronunciation lexicon](https://huggingface.co/datasets/TigreGotico/portuguese-unified-pronunciation-lexicon).
The `pt-BR` entries come from the NILC Aeiouadô training file and from
pt.wiktionary, and each one has a second source.
Every other lect runs on the orthography2ipa rules alone.
`tugaphone.registry.PACKAGED_LEXICON_LECTS` names the lects that take a
lexicon. Enabling a parent lexicon for a sub-lect such as `pt-PT-x-porto` or
`pt-BR-x-sp` would overwrite that spec's phonology with the parent's forms, so
no sub-lect takes one.

### 3. Syllabification

tugaphone does not own this stage. `orthography2ipa[portuguese]`, a tugaphone
dependency, registers a `silabificador`-backed plugin in the
`orthography2ipa.syllabify` entry-point group, and the lattice uses it for
Portuguese stress detection.

## What comes from where

| Concern | Owner |
|---------|-------|
| Base phonology (grapheme → phoneme inventory) | orthography2ipa lect spec |
| Dialect phenomena (betacism, rising diphthongs, palatalization, `/u/` fronting, …) | orthography2ipa lect spec (`allophone_rules`) |
| Cross-word sandhi (coda-sibilant voicing, …) | orthography2ipa lect spec (`sandhi_rules`) |
| Stress placement | orthography2ipa lect spec (stress rules) |
| Number / ordinal verbalization | tugaphone (`number_utils`, via the `normalize` stage) |
| Sense-based homograph marking | tugaphone (`bifonia`, via the `normalize` stage) |
| `pt-PT` and `pt-BR` residual lexicons | `o2i-lexicons`, enabled by tugaphone via `use_packaged_lexicons` |
| Syllabification | orthography2ipa (`silabificador`, through the `syllabify` plugin of `orthography2ipa[portuguese]`) |

## Selecting a dialect

The accent is selected entirely by `lang`, there is no runtime accent argument.

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
    print(code, "→", ph.phonemize_sentence("O gato dorme.", code))
# pt-PT → o ˈɡatu ˈdɔɾmɨ
# pt-BR → u ˈɡatu ˈdoɾmi
# pt-AO → ʊ ˈɡatʊ ˈdɔʁmɨ
# pt-MZ → u ˈɡatu ˈdɔrme
# pt-TL → o ˈɡatʊ ˈdɔrme
```

## The token-feature API

`tugaphone.tokenizer` and `tugaphone.dialects` remain as a token-tree
linguistic **feature** API (manner, place, voicing, vowel height, syllable
roles, CV skeletons) and as the rules-only benchmark baseline. They are **not**
the phonemization path, `phonemize_sentence` never routes through them. See
[tokenizer.md](tokenizer.md) for the feature model.

## Where next

- [dialects.md](dialects.md), the lect codes, aliases and lexicon overlay
- [api.md](api.md), the public surface
- [benchmarking.md](benchmarking.md), how accuracy is measured


---
[← Quickstart](quickstart.md) · [Home](../README.md) · [Dialects →](dialects.md)
