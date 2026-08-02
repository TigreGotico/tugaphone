# Advanced

Once the basic `phonemize_sentence` loop is clear, this is what sits underneath
it.

## The lattice core and the caller-owned layers

tugaphone phonemizes by driving the shared
[orthography2ipa](https://github.com/TigreGotico/orthography2ipa) candidate
lattice. A dialect *is* an orthography2ipa lect spec:
`phonemize_sentence(text, lang)` resolves `lang` to a lect code and runs
`orthography2ipa.G2P(lect).transcribe(text)`. The spec's grapheme table,
`allophone_rules` and cross-word `sandhi_rules` produce the dialect's phonology, betacism, rising diphthongs, palatalization, `/u/` fronting, coda-sibilant
voicing sandhi and the rest, with no string-transform pass after transcription.

tugaphone adds only the stages orthography2ipa leaves to the caller, wired
through orthography2ipa's own extension points:

1. **Normalization**, number/ordinal verbalization
   (`tugaphone.number_utils.normalize_numbers`) and sense-based homograph marking
   (`bifonia.add_extra_diacritics`) run as the engine's `normalizer`, before the
   lattice sees the text.
2. **Lexicon**, the curated `tugalex` lexicon is registered per lect via
   `orthography2ipa.register_lexicon()`, so a covered word folds into the same
   override path as a spec `word_exceptions` entry, the lattice generates only
   out-of-vocabulary words.
3. **Syllabification**, supplied by orthography2ipa's own `silabificador`
   `syllabify` plugin.

For the full breakdown of what comes from where, see
[architecture.md](architecture.md).

## The lexicon-overlay boundary

The lexicon overlay is registered for **only** the eight lects whose lexical
tradition matches a `tugalex` region: `pt-PT` and `pt-PT-x-lisbon` (Lisbon),
`pt-BR` and `pt-BR-x-rj` (Rio), `pt-BR-x-sp` (São Paulo), `pt-AO` (Luanda),
`pt-MZ` (Maputo) and `pt-TL` (Dili). Every other lect is produced purely by the
lattice.

The boundary is deliberate: a `tugalex` region encodes one tradition's lexical
pronunciations, so registering the Lisbon lexicon on a Porto lect would overwrite
the Porto spec's phonology with Lisbon forms. `tugalex` entries are relaid from
its `·`-joined, nucleus-marked layout into the spec's stress-before-syllable
layout on registration, keeping a lexicon hit and a lattice-generated word in one
notation so a sentence's IPA stays internally consistent.

## Number normalization

`normalize_numbers` spells digits out before transcription and is independently
useful for any TTS front-end:

```python
from tugaphone.number_utils import normalize_numbers

normalize_numbers("vou comprar 1 casa")      # 'vou comprar uma casa'  (feminine)
normalize_numbers("vou adotar 1 cão")        # 'vou adotar um cão'      (masculine)
normalize_numbers("897654356789098", "pt-PT")  # long scale (biliões)
normalize_numbers("897654356789098", "pt-BR")  # short scale (trilhões)
```

Gender is inferred from preceding articles (`a`, `as`, `da`, `das`) and from the
shape of the following noun (`-a`, `-dade`, `-agem` endings lean feminine). Pass
`strict=False` to leave unparseable tokens in place instead of raising. Inside
the pipeline this runs as the engine's `normalize` stage, so a bare digit in the
input sentence is verbalized before the lattice transcribes it.

## Integration with sibling libraries

`tugaphone` composes the TigreGotico Portuguese NLP stack, each library is
usable on its own:

- [`orthography2ipa`](https://github.com/TigreGotico/orthography2ipa), the
  candidate lattice and the lect specs that are tugaphone's core.
- [`tugalex`](https://github.com/TigreGotico/tugalex), the phonetic lexicon
  (`LEXICON` in `tugaphone.dialects`), registered per lect as an override.
- [`silabificador`](https://github.com/TigreGotico/silabificador), the
  syllabifier, wired in as orthography2ipa's `syllabify` plugin.
- [`bifonia`](https://github.com/TigreGotico/bifonia), meaning-based
  heterophone disambiguation, called via `add_extra_diacritics` in the
  `normalize` stage.

A TTS front-end typically wires `tugaphone` as the G2P stage: pass text and a
target lect code, hand the returned IPA string to the acoustic model. It can also
be loaded through the `orthography2ipa` G2P plugin interface, see
[api.md](api.md#tugaphoneplugin).

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
- [tokenizer.md](tokenizer.md), inspect syllables, stress and graphemes directly


---
[← Tokenizer](tokenizer.md) · [Home](../README.md) · [Benchmarking →](benchmarking.md)
