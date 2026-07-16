# Optional base phonemization on the orthography2ipa lattice

tugaphone builds a word's IPA in layers:

1. **lexicon** (`DialectInventory.IRREGULAR_WORDS` plus the region lexicon from
   `tugalex`) — the authoritative pronunciation for every covered word;
2. **base G2P** — used only for words the lexicon does not cover
   (out-of-vocabulary);
3. **regional accent primitives** (`tugaphone.ipa_transforms`) — composed on top
   of whatever base layer 2 produces.

Layer 2 has two possible sources, selected per dialect by the
`DialectInventory.USE_O2I_LATTICE_BASE` flag:

- **the private grapheme→phoneme character cascade** (`USE_O2I_LATTICE_BASE =
  False`) — tugaphone's own Portuguese grapheme rules; this is the default for
  every shipped dialect;
- **the shared orthography2ipa pronunciation lattice**
  (`USE_O2I_LATTICE_BASE = True`) — `orthography2ipa.g2p.G2P.ipa_lattice`, so
  o2i's Portuguese phonology produces the base for OOV words.

Layers 1 and 3 are identical either way; only the OOV base changes.

## What comes from where

| Concern | Owner |
| --- | --- |
| Word pronunciations (in-lexicon) | tugaphone `IRREGULAR_WORDS` (tugalex) |
| Base IPA for OOV words | tugaphone cascade, or the o2i lattice when the dialect opts in |
| Verbalization / numbers | tugaphone `number_utils` |
| Regional accent composition | tugaphone `ipa_transforms` / `regional` |

## The segment-model boundary

`tugaphone.lattice_adapter.lattice_base_ipa` converts the flat, pre-stress
lattice into tugaphone's canonical per-word layout so the accent primitives
(which slice IPA by grapheme cluster and match stress-anchored regexes) keep
composing unchanged:

- **stress + syllabification** — the lattice's per-grapheme slots are re-grouped
  into the word's syllables (via `silabificador`, the same syllabifier tugaphone
  already uses), the primary-stress mark is placed before the stressed syllable,
  and syllables are joined with the hiatus token `·` — matching the cascade's own
  `WordToken.ipa` layout;
- **nasal glides** — the lattice emits nasalised off-glides as `w̃`/`j̃` (base +
  combining tilde); tugaphone nasalises only the nucleus and keeps the glide bare
  (`ɐ̃w`), so the tilde is stripped from glide symbols while every nucleus tilde
  is preserved.

## Why it is opt-in

The flag is `False` for every shipped dialect. The character cascade encodes
Portuguese-specific phonology — coda nasalization (`campo` → `ˈkɐ̃pu`), `<ou>`
diphthong retention, `<x>` = `[ks]`, the `ex-` prefix `[iz]` — that a
general-purpose lattice base does not reproduce out of the box. Enabling the
lattice per dialect is appropriate only where its OOV base matches or improves on
the cascade for that dialect's gold. Gaps between the two are resolved in
`orthography2ipa`'s Portuguese specs rather than re-forked into tugaphone.
