# The token tree

`phonemize_sentence` returns a string, but the transcription is built from a
four-level model you can inspect directly:

```
Sentence → Word → Grapheme → Character
```

Each level carries phonological features and its own IPA. This is the layer to
reach for when you want syllables, stress positions, diphthong detection, or a
feature dict for machine learning — not just the final phoneme string.

## Built on the orthography2ipa shared substrate

The token tree is not a self-contained tokenizer. Two responsibilities are
delegated to the shared [`orthography2ipa`](https://github.com/TigreGotico/orthography2ipa)
library so tugaphone rides its substrate instead of forking it:

- **Grapheme segmentation.** Splitting a syllable into graphemes (digraphs like
  `ch`/`nh`, diphthongs like `ão`/`ei`, trigraphs like `que`) is done by
  `orthography2ipa.phonetok.PhonetokTokenizer`'s maximal-munch trie, driven by
  the dialect's own `GRAPHEME_INVENTORY`. tugaphone supplies the Portuguese
  grapheme data; the segmentation algorithm is shared.
- **Vowel classification.** `CharToken.is_vowel` and the c/g front-vowel
  softening rules delegate to `orthography2ipa.vowels`
  (`is_orthographic_vowel`, `is_front_vowel`) — the single owner of
  vowel-letter membership — rather than maintaining tugaphone's own vowel and
  front-vowel character sets.

`orthography2ipa.vowels.is_orthographic_vowel` recognises the full precomposed
nasal-vowel set, including the archaic `ẽ`/`ĩ`/`ũ`, so `CharToken.is_vowel`
delegates to it with no local fallback.

## Building a Sentence

The simplest path constructs a `Sentence` with a dialect inventory:

```python
from tugaphone.tokenizer import Sentence
from tugaphone.dialects import EuropeanPortuguese

s = Sentence("O cão comeu o pão.", dialect=EuropeanPortuguese())
print(s.ipa)        # 'ˈu kˈɐ̃w ku·ˈmew ˈu pˈɐ̃w'
print(s.n_words)    # 5
print(repr(s))      # Sentence('O cão comeu o pão.' → [...])
```

## Word level

Each `WordToken` exposes its syllable structure, stress and per-word IPA:

```python
for word in s.words:
    print(word.surface,
          ".".join(word.syllables),
          "stress@", word.stressed_syllable_idx,
          "→", word.ipa)
```

```
o    o        stress@ 0 → ˈu
cão  cão      stress@ 0 → kˈɐ̃w
comeu co.meu  stress@ 1 → ku·ˈmew
```

`syllables` comes from the `silabificador` library; `stressed_syllable_idx` is
the index of the stressed syllable; `n_syllables` counts them.

## Grapheme level

A `GraphemeToken` groups characters into orthographic units (digraphs like `ch`
and `nh`, diphthongs like `ão` and `ei`) and knows how each maps to IPA:

```python
word = s.words[1]   # cão
for g in word.graphemes:
    print(repr(g.surface), "→", g.ipa,
          "diphthong" if g.is_diphthong else "",
          "nasal" if g.is_nasal else "")
```

```
'c'  → k
'ão' → ɐ̃w  diphthong nasal
```

Useful grapheme predicates: `is_diphthong`, `is_triphthong`,
`is_falling_diphthong`, `is_rising_diphthong`, `is_nasal_diphthong`,
`is_oral_diphthong`, `is_nasal`, `is_digraph`, `is_trigraph`,
`has_primary_stress`.

## Character level

The deepest level, `CharToken`, carries the phonetic primitives: `is_vowel`,
`is_consonant`, `is_semivowel`, `is_nasal_vowel`, `is_open_vowel`,
`is_intervocalic`, and its own `.ipa`. These drive the allophone rules the higher
levels assemble.

## Phonological features

Beyond the orthographic predicates, every level exposes articulatory and
syllable-structure features.

> **Orthographic heuristics.** Consonant classifications describe the typical
> realization of a letter's *default* phoneme. Letters whose value is
> context-dependent (`c` → [k]/[s], `g` → [ɡ]/[ʒ], `s` → [s]/[z]/[ʃ],
> `x` → [ʃ]/[ks]/[z]) carry the default reading — check the character's
> `.ipa` for the realized phone. Vowel features, by contrast, classify the
> *realized* phone, so dialect-specific reduction is honoured.

### Character

| Property | Values | Example (`vinho`) |
|----------|--------|-------------------|
| `manner_of_articulation` | plosive, fricative, nasal, lateral, rhotic | `v` → fricative |
| `place_of_articulation` | bilabial, labiodental, alveolar, postalveolar, velar | `v` → labiodental |
| `voicing` | voiced, voiceless (intervocalic `s` → voiced) | `v` → voiced |
| `vowel_height` | high, mid-high, mid-low, low | `i` → high |
| `vowel_backness` | front, central, back | `i` → front |
| `vowel_roundedness` | rounded, unrounded | `i` → unrounded |
| `is_nucleus` / `is_onset` / `is_coda` | syllable role | `i` → nucleus |
| `idx_in_syllable` | position within the syllable | |
| `is_sonorant`, `is_obstruent`, `is_liquid`, `is_sibilant`, `is_rhotic`, `is_plosive`, `is_fricative`, `is_nasal_consonant`, `is_front_vowel`, `is_back_vowel`, `is_rounded_vowel` | booleans | |

Vowel features read the character's realized IPA, so European Portuguese
unstressed `e` (→ [ɨ]) classifies as high/central while the same letter in
Brazilian Portuguese (→ [e]) classifies as mid-high/front.

### Grapheme

| Property | Meaning | Example (`vinho`) |
|----------|---------|-------------------|
| `syllable_position` | nucleus, onset or coda | `nh` → onset |
| `phonological_weight` | phones contributed (silent → 0, diphthong → 2) | `nh` → 1 |
| `has_complex_onset` / `is_onset_cluster` | branching onset (`pr`, `tr`, …) | |
| `is_palatal` | digraph realized as [ɲ]/[ʎ] | `nh` → True |
| `triggers_palatalization` | high front vowel ([i]) | |
| `is_vowel_grapheme` / `is_consonant_grapheme` | letter composition | |

### Word

```python
w = Sentence("vinho", dialect=EuropeanPortuguese()).words[0]
w.ipa                          # 'vˈi·ɲu'
w.stress_pattern               # 'paroxytone'
w.syllable_structure_pattern   # 'CV.CCV'
w.phoneme_count                # 4
w.vowel_sequence               # 'i.o'
w.consonant_sequence           # 'v.n.h'
w.has_palatal_sounds           # True
```

Also: `has_diphthongs`, `has_nasal_sounds`, `has_consonant_clusters`,
`is_homograph` (POS-dependent IPA, e.g. *gosto*) and `is_irregular` (IPA comes
from the lexicon rather than the rules).

## Feature extraction

Every level has a `.features` dict. `Sentence.features` flattens the whole tree
into a single namespaced dict suitable for a feature vector:

```python
feats = s.features
# {'n_words': 5, 'n_whitespaces': 4,
#  'word_0_n_syllables': 1, 'word_0_stressed_syllable_idx': 0, ...}
```

Long sentences produce large dictionaries — for ML pipelines, project the keys
you need rather than materializing the whole thing per sample.

## Where next

- [api.md](api.md) — the class table and signatures
- [advanced.md](advanced.md) — accents, numbers
- [quickstart.md](quickstart.md) — the basics
