# Advanced
<!-- agent-hint
covers: the lexicon boundary, number scales and integration with the sibling libraries
source: tugaphone/lattice_core.py, tugaphone/number_utils.py, pyproject.toml
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py docs/advanced.md
see: architecture.md, api.md
-->

Once the basic `phonemize_sentence` loop is clear, this is what sits underneath
it.

## The lattice core and the caller-owned layers

tugaphone phonemizes by driving the shared
[orthography2ipa](https://github.com/TigreGotico/orthography2ipa) candidate
lattice. A dialect *is* an orthography2ipa lect spec:
`phonemize_sentence(text, lang)` resolves `lang` to a lect code and runs
`orthography2ipa.G2P(lect, pipeline=Pipeline(lexicon=..., expand=..., mark=...)).transcribe(text)`. The spec's grapheme table,
`allophone_rules` and cross-word `sandhi_rules` produce the dialect's phonology, betacism, rising diphthongs, palatalization, `/u/` fronting, coda-sibilant
voicing sandhi and the rest, with no string-transform pass after transcription.

tugaphone adds the stages orthography2ipa leaves to the caller, wired through
orthography2ipa's own extension points, and takes syllabification from
orthography2ipa:

1. **Normalization**, orthographic rewrites
   (`tugaphone.text_normalization.normalize_orthography`), the reading of
   numbers, dates and times by text2spoken
   (`tugaphone.number_utils.normalize_numbers`) and sense-based
   homograph marking (`bifonia.add_extra_diacritics`) run before the lattice
   sees the text. The rewrites and the numbers are the pipeline's `expand`, and
   the homograph marks are its `mark`.
2. **Lexicon**, for `pt-PT` and `pt-BR` only, the engine takes the residual
   lexicon of `o2i-lexicons`, its exceptions and its patches, through its
   `orthography2ipa.Pipeline`, so a covered
   word folds into the same override path as a spec `word_exceptions` entry.
   Every other lect runs on the rules alone.
3. **Syllabification**, supplied by the bundled splitter of orthography2ipa,
   which reads the diphthongs and hiatus of the lect spec.

For the full breakdown of what comes from where, see
[architecture.md](architecture.md).

## The lexicon boundary

The `pt-PT` and `pt-BR` lects each take the residual lexicon of
[`o2i-lexicons`](https://github.com/TigreGotico/o2i-lexicons), passed to the
engine as `Pipeline(lexicon=packaged_lexicon(lect, patches=True))`. The
exceptions are the words whose reading the spelling cannot give, and the patches
are the words that a rule could reach and does not reach yet. A covered word folds
into the same override path as a spec `word_exceptions` entry. Each lexicon holds
only the words that the lect's rules get wrong. The `pt-PT` entries come from the
Infopédia readings of the
[portuguese-unified pronunciation lexicon](https://huggingface.co/datasets/TigreGotico/portuguese-unified-pronunciation-lexicon),
and the `pt-BR` entries from the NILC Aeiouadô training file and pt.wiktionary.
Every other lect runs on the orthography2ipa rules alone.

The boundary is deliberate. Each lexicon is in the norm of its lect, so enabling
it for a sub-lect such as `pt-PT-x-porto` or `pt-BR-x-sp` would overwrite that
spec's phonology with the parent's forms. The entries are in the spec's
notation, with the stress mark before the stressed syllable, so a lexicon hit
and a rules reading share one notation.

## Number normalization

`normalize_numbers` reads numbers, dates, clock times, money and measures with
[text2spoken](https://github.com/TigreGotico/text2spoken), in the `pt-PT` or
`pt-BR` variety of the lect:

```python
from tugaphone.number_utils import normalize_numbers

normalize_numbers("vou comprar 1 casa")        # 'vou comprar uma casa'
normalize_numbers("vou adotar 1 cão")          # 'vou adotar um cão'
normalize_numbers("897654356789098", "pt-PT")
# 'oitocentos e noventa e sete biliões seiscentos e cinquenta e quatro mil trezentos e cinquenta e seis milhões setecentos e oitenta e nove mil e noventa e oito'
normalize_numbers("897654356789098", "pt-BR")
# 'oitocentos e noventa e sete trilhões seiscentos e cinquenta e quatro bilhões trezentos e cinquenta e seis milhões setecentos e oitenta e nove mil e noventa e oito'
```

`pt-PT` reads the long scale (biliões). `pt-BR` reads the short scale (trilhões).

text2spoken owns the reading rules, gender agreement included.
[numbers.md](numbers.md) shows which lect reads which variety. Inside the
pipeline this runs in the engine's `expand` step, so a bare digit in the
input sentence is read before the lattice transcribes it.

## Integration with sibling libraries

`tugaphone` composes the TigreGotico Portuguese NLP stack, each library is
usable on its own:

- [`orthography2ipa`](https://github.com/TigreGotico/orthography2ipa), the
  candidate lattice and the lect specs that are tugaphone's core.
- [`o2i-lexicons`](https://github.com/TigreGotico/o2i-lexicons), the `pt-PT` and
  `pt-BR` residual lexicons.
- [`text2spoken`](https://github.com/TigreGotico/text2spoken), numbers, dates,
  times, money and abbreviations for `normalize_numbers`.
- [`desacordo_ortografico`](https://github.com/TigreGotico/desacordo_ortografico),
  old spellings to AO1990, the spelling step of `expand`.
- [`tugalex`](https://github.com/TigreGotico/tugalex), the noun and given-name
  genders, and the gender of a given name for `D.` (Dom or Dona).
- [`silabificador`](https://github.com/TigreGotico/silabificador), the
  syllabifier of the `tugaphone.tokenizer` token tree. The phonemization path
  does not use it.
- [`bifonia`](https://github.com/TigreGotico/bifonia), meaning-based
  heterophone disambiguation, called via `add_extra_diacritics` in the
  pipeline's `mark` step.

A TTS front-end typically wires `tugaphone` as the G2P stage: pass text and a
target lect code, hand the returned IPA string to the acoustic model.

## The token-feature API

`tugaphone.tokenizer` and `tugaphone.dialects` expose a token tree (manner,
place, voicing, vowel height, syllable roles, CV skeletons) and back the
rules-only benchmark baseline. This is a feature-inspection surface, **not** the
phonemization path, `phonemize_sentence` runs on the lattice and never routes
through it. See [tokenizer.md](tokenizer.md).

## Where next

- [architecture.md](architecture.md), the pipeline in full
- [api.md](api.md), full signatures
- [dialects.md](dialects.md), the lect codes, aliases and lexicon overlay
- [homographs.md](homographs.md), meaning-based disambiguation
- [numbers.md](numbers.md), number normalization and gender agreement
- [text_normalization.md](text_normalization.md), the orthographic rewrites that run ahead of number normalization
- [tokenizer.md](tokenizer.md), inspect syllables, stress and graphemes directly

---
[← Tokenizer](tokenizer.md) · [Index](index.md) · [Development →](development.md)
