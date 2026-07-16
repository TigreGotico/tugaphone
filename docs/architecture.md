# Architecture

tugaphone phonemizes Portuguese by driving the shared
[orthography2ipa](https://github.com/TigreGotico/orthography2ipa) candidate
lattice and layering on top only the stages orthography2ipa leaves to the
caller. A dialect *is* an orthography2ipa lect spec, so selecting a dialect is
selecting a lect.

## The lattice core

`TugaPhonemizer().phonemize_sentence(text, lang)` resolves `lang` to an
orthography2ipa lect code and drives
`orthography2ipa.G2P(lect).transcribe(text)`. Every Portuguese-family lect ships
an engine spec whose grapheme table, `allophone_rules` and cross-word
`sandhi_rules` encode that variety's phonology. The dialect phenomena are
produced by the lattice itself, not by a post-hoc string-transform pass:

- northern **betacism** (`/v/` → `[b]`, *vinho* → `[ˈbiɲu]`),
- Porto **rising diphthongs** (`[ˈwo]`, `[ˈje]`),
- Transmontano `<ch>` → `[tʃ]` and the apico-alveolar `[s̺]`,
- Madeiran `/l/` → `[ʎ]`,
- Azorean and Alentejan stressed `/u/` → `[y]`,
- Brazilian `/t d/` palatalization before `[i]` and coda-`/l/` vocalization,
- coda-sibilant voicing **sandhi** across word boundaries,

and the rest of each lect's inventory, allophony and stress. There is no
string-edit layer applied after transcription.

## The three caller-owned layers

tugaphone contributes only the concerns orthography2ipa deliberately does not
own, wired through orthography2ipa's own extension points (see
`tugaphone/lattice_core.py`):

### 1. Normalization / verbalization

Gender-aware number and ordinal expansion
(`tugaphone.number_utils.normalize_numbers`) and sense-based
heterophonic-homograph marking (`bifonia.add_extra_diacritics`, e.g. *sede*
thirst `/ˈsedɨ/` vs seat `/ˈsɛdɨ/`) run as the engine's `normalizer` — the
orthography2ipa `normalize` stage, before the lattice sees the text. Numbers are
verbalized first so their spelled-out words are available to homograph marking;
both are orthographic, pre-lattice transformations.

### 2. Lexicon

The curated `tugalex` pronunciation lexicon is registered per lect via
`orthography2ipa.register_lexicon()`, so a covered word folds into the same
override path as a spec `word_exceptions` entry. The lattice generates only the
out-of-vocabulary words.

The lexicon overlay applies to **only the lects whose lexical tradition matches
a `tugalex` region**:

| Lect | tugalex region |
|------|----------------|
| `pt-PT`, `pt-PT-x-lisbon` | Lisbon |
| `pt-BR`, `pt-BR-x-rj` | Rio |
| `pt-BR-x-sp` | São Paulo |
| `pt-AO` | Luanda |
| `pt-MZ` | Maputo |
| `pt-TL` | Dili |

Every other lect is pure lattice. Registering the Lisbon lexicon on, say, a
Porto lect would overwrite the Porto spec's phonology with Lisbon forms, so the
overlay is deliberately withheld from lects with no matching tradition. `tugalex`
entries are relaid from its `·`-joined, nucleus-marked layout into
orthography2ipa's stress-before-syllable layout on registration, so a lexicon
hit and a lattice-generated word share one notation and a sentence's IPA stays
internally consistent.

### 3. Syllabification

Supplied by orthography2ipa's own `silabificador` `syllabify` plugin, a neutral
stage, so stress lands on the same syllable the lattice would choose.

## What comes from where

| Concern | Owner |
|---------|-------|
| Base phonology (grapheme → phoneme inventory) | orthography2ipa lect spec |
| Dialect phenomena (betacism, rising diphthongs, palatalization, `/u/` fronting, …) | orthography2ipa lect spec (`allophone_rules`) |
| Cross-word sandhi (coda-sibilant voicing, …) | orthography2ipa lect spec (`sandhi_rules`) |
| Stress placement | orthography2ipa lect spec (stress rules) |
| Number / ordinal verbalization | tugaphone (`number_utils`, via the `normalize` stage) |
| Sense-based homograph marking | tugaphone (`bifonia`, via the `normalize` stage) |
| Curated pronunciation lexicon | tugaphone (`tugalex`, via `register_lexicon`) |
| Syllabification | tugaphone (`silabificador`, via the `syllabify` plugin) |

## Selecting a dialect

The accent is selected entirely by `lang`; there is no runtime accent argument.

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
    print(code, "→", ph.phonemize_sentence("O gato dorme.", code))
# pt-PT → ˈo ˈgatu ˈdɔɾmɨ
# pt-BR → ˈu ˈgatʊ ˈdoɾmi
# pt-AO → ˈʊ ˈgatʊ ˈdɔʁmɨ
# pt-MZ → ˈu ˈgatu ˈdɔrme
# pt-TL → ˈo ˈgatʊ ˈdɔrme
```

## The token-feature API

`tugaphone.tokenizer` and `tugaphone.dialects` remain as a token-tree
linguistic **feature** API (manner, place, voicing, vowel height, syllable
roles, CV skeletons) and as the rules-only benchmark baseline. They are **not**
the phonemization path — `phonemize_sentence` never routes through them. See
[tokenizer.md](tokenizer.md) for the feature model.

## Where next

- [dialects.md](dialects.md) — the lect codes, aliases and lexicon overlay
- [api.md](api.md) — the public surface
- [benchmarking.md](benchmarking.md) — how accuracy is measured
