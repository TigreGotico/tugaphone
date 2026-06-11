# The token tree

`phonemize_sentence` returns a string, but the transcription is built from a
four-level model you can inspect directly:

```
Sentence → Word → Grapheme → Character
```

Each level carries phonological features and its own IPA. This is the layer to
reach for when you want syllables, stress positions, diphthong detection, or a
feature dict for machine learning — not just the final phoneme string.

## Building a Sentence

The simplest path constructs a `Sentence` with a dialect inventory:

```python
from tugaphone.tokenizer import Sentence
from tugaphone.dialects import EuropeanPortuguese

s = Sentence("O cão comeu o pão.", dialect=EuropeanPortuguese())
print(s.ipa)        # 'ˈu kˈɐ̃w ˈkɔ·mew ˈu pˈɐ̃w'
print(s.n_words)    # 4
print(repr(s))      # Sentence('O cão comeu o pão.' → [...])
```

`TugaPhonemizer` itself uses `Sentence.from_postagged(surface, tags, dialect)`,
where `tags` is a list of `(token, pos)` pairs. Use that form when you already
have POS tags and want them respected during transcription.

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
comeu co.meu  stress@ 0 → ˈkɔ·mew
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

## Feature extraction

Every level has a `.features` dict. `Sentence.features` flattens the whole tree
into a single namespaced dict suitable for a feature vector:

```python
feats = s.features
# {'n_words': 4, 'n_whitespaces': 3,
#  'word_0_n_syllables': 1, 'word_0_stressed_syllable_idx': 0, 'word_0_pos': ...}
```

Long sentences produce large dictionaries — for ML pipelines, project the keys
you need rather than materializing the whole thing per sample.

## Where next

- [api.md](api.md) — the class table and signatures
- [advanced.md](advanced.md) — accents, POS engines, numbers
- [quickstart.md](quickstart.md) — the basics
