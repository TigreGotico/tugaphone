# Base phonemization on the orthography2ipa lattice (B6 stage-2)

tugaphone builds a word's IPA in layers:

1. **lexicon** (`DialectInventory.IRREGULAR_WORDS`, the region lexicon from
   `tugalex`) — the authoritative pronunciation for every covered word;
2. **base G2P** — used only for words the lexicon does not cover (OOV);
3. **regional accent primitives** (`tugaphone.ipa_transforms`) — composed on
   top of whatever base is produced (`TugaPhonemizer.phonemize_sentence`).

B6 stage-2 replaces layer 2's private grapheme→phoneme **character cascade**
with the shared orthography2ipa pronunciation **lattice**
(`orthography2ipa.g2p.G2P.ipa_lattice` — the object the beam reads), so the
research-backed o2i Portuguese phonology becomes tugaphone's base for OOV words.
Layers 1 and 3 are unchanged.

## What comes from where

| Concern | Owner after B6 stage-2 |
| --- | --- |
| Word pronunciations (in-lexicon) | tugaphone `IRREGULAR_WORDS` (tugalex) |
| **Base IPA for OOV words** | **o2i lattice** (when the dialect opts in) |
| Verbalization / numbers | tugaphone `number_utils` |
| Regional accent composition | tugaphone `ipa_transforms` / `regional` |

## The segment-model boundary

`tugaphone.lattice_adapter.lattice_base_ipa` converts the flat, pre-stress
lattice into tugaphone's canonical per-word layout so the accent primitives
(which slice IPA by grapheme cluster and match stress-anchored regexes) keep
composing unchanged:

* **stress + syllabification** — the lattice's per-grapheme slots are
  re-grouped into the word's syllables (via `silabificador`, the same
  syllabifier tugaphone already uses), the primary-stress mark is placed before
  the stressed syllable, and syllables are joined with the hiatus token `·`
  — matching the cascade's own `WordToken.ipa` layout;
* **nasal glides** — the lattice emits nasalised off-glides as `w̃`/`j̃`
  (base + combining tilde U+0303); tugaphone nasalises only the nucleus and
  keeps the glide bare (`ɐ̃w`), so the tilde is stripped from glide symbols
  while every nucleus tilde is preserved. This is exactly the atomic-vs-
  decomposed hazard that bit the barranquenho work; it is handled explicitly
  rather than left to silently corrupt the primitives' string operations.

## Why it is opt-in and off for every shipped dialect

`DialectInventory.USE_O2I_LATTICE_BASE` gates the routing per dialect and is
`False` everywhere. The mechanism is complete and exercised by the test suite,
but the current o2i pt specs (1.71.x) still have **base gaps** that would
regress the research-backed cascade gold if the lattice were made the default.
Each is an **o2i gap to fix upstream**, not something to re-fork privately into
tugaphone.

| o2i gap (pt specs, 1.71.x) | Example (o2i greedy → correct) | Blocks |
| --- | --- | --- |
| Coda nasalization not modelled | `campo` → `ˈkampu` (→ `ˈkɐ̃pu`); `santo` → `ˈsantu` (→ `ˈsɐ̃tu`); `sim` → `ˈsim` (→ `ˈsĩ`) | all pt dialects |
| `<ou>` over-monophthongised | `chegou` → `ʃɨˈɡo` (→ `ʃɨˈɡow`) | pt-PT + EP regional presets |
| pt-BR/AO final unstressed `/a/` over-reduced to `[ɐ]` | `casa` (pt-BR) → `ˈkazɐ` (→ `ˈkaza`) | pt-BR, pt-AO |
| `<x>` = `[ks]` context not modelled | `táxi` → `ˈtaʃi` (→ `ˈtaksi`) | all (OOV `<x>` words) |
| `ex-` prefix `[iz]` not modelled | `exemplo` → `eˈʃɛmplu` (→ `izˈẽplu`) | all (OOV `ex-` words) |
| nasal-diphthong stress placed on the off-glide | `cão` → `kɐ̃ˈw̃` (stress on glide) | cosmetic; adapter re-places stress per syllable |

The last row is neutralised by the adapter (it re-marks stress per syllable),
so it does not block adoption; the others are genuine phoneme-level regressions.

## Flip plan (per dialect, as o2i gaps close)

1. **Prerequisite for every pt dialect:** o2i models coda nasalization
   (`am/an/em/.../um` → nasal vowel) in the pt specs. This is the single
   largest blocker — it affects a large fraction of the vocabulary.
2. **pt-PT (+ EP regional presets):** additionally requires the `<ou>` retention
   fix. Then set `USE_O2I_LATTICE_BASE = True` on `EuropeanPortuguese`, re-run
   the suite, and adjudicate every divergence in
   `tests/test_lattice_adapter.py::TestCascadeVsLatticeCharacterization`:
   adopt o2i's value where it is the better-cited form (updating the expected
   value with a source note), and file any remaining tuga-better case as a new
   o2i gap. The regional accent gold is lexicon-covered, so it is unaffected by
   the OOV base swap and needs no migration.
3. **pt-BR / pt-AO:** additionally require the final unstressed `/a/` fix, then
   flip `BrazilianPortuguese` / `AngolanPortuguese` and adjudicate the
   `rules_only` characterization cases the same way.
4. **pt-MZ / pt-TL:** flip after nasalization lands and their
   characterization cases are adjudicated.

The generic `<x>`/`ex-` gaps affect only OOV words containing those patterns and
can be closed independently; they do not block the per-dialect flip because
such words are overwhelmingly lexicon-covered in practice.
