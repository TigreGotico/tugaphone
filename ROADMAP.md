# Roadmap — tugaphone

A dialect-aware Portuguese phonemizer that transcribes arbitrary text to IPA
across the major Lusophone dialects (pt-PT, pt-BR, pt-AO, pt-MZ, pt-TL) and
several pt-PT micro-dialects. It is a hybrid system: a curated phonetic lexicon
(`tugalex`) backed by rule-based G2P, with POS-aware homograph disambiguation
(`tugatagger`), number normalization, syllabification (`silabificador`), and
automatic stress placement. It is the flagship of the org's Lusophone phonetics
stack and the most likely first-class `phoonnx` pt backend.

## Phase 0 — Hardening

- Realign `release_workflow.yml` / `publish_stable.yml` to
  `OpenVoiceOS/gh-automations@dev` and add `build-tests`, `coverage`,
  `license_check`.
- Migrate to `pyproject.toml` (classifiers, real `description`), add the Apache-2.0
  `LICENSE` the README declares, add a `.gitignore` so `tugaphone.egg-info/` stays
  out of git.
- Stand up a `tests/` suite seeded from the per-dialect README examples and the
  syllabification benchmark; wire it into `build-tests`/`coverage`.

## Phase 1 — Correctness & coverage

- Fix the five open correctness bugs (#8–#12): lossy `RegionalDialect.as_dict`
  serialization, the `retain_ou_diphthong` `boa` special-case, multi-codepoint
  phoneme slicing, `palatal_affrication_ch` over-application, and the
  stressed-only epenthetic `[j]` regex.
- Work the tokenizer/dialect/number TODOs: hiatus suffixes, modern-equivalent word
  mapping, per-dialect tokenization branches, grapheme cursor movement, and the
  number-normalizer scale/float/decimal limits.
- Add regression coverage per dialect so rule changes are scored, not eyeballed.

## Phase 2 — Integration

- Make tugaphone the first-class pt phonemizer backend in `phoonnx`: the
  `PhonemeType.tugaphone` slot and `phoonnx/phonemizers/pt.py` already exist —
  ensure `TugaPhonemizer` is wired through `BasePhonemizer`, emits `Alphabet.IPA`
  with stress/syllable markers compatible with the voice configs, and that the
  dialect/region langcodes (`pt-PT-x-porto`, etc.) map onto phoonnx voice
  selection.
- Align the IPA inventory and tokenization with `orthography2ipa`: reconcile (or
  contribute) pt / pt-region `LanguageSpec` grapheme→IPA and allophone maps so
  tugaphone output validates against its tokenizer and can be compared via the
  distance metrics, and so the regional layer shares one ancestry model.
- Coordinate the pt-PT regional accents with `sotaque_forcado` to avoid two
  divergent accent inventories; keep `silabificador` and `tugatagger`/`tugalex` as
  shared dependencies rather than re-implementing their logic.

## Phase 3 — Datasets & publishing

- Maintain and version the Portuguese Phonetic Lexicon dataset that backs the
  lexicon and benchmark; publish per-dialect gold IPA evaluation slices.
- Continue PyPI releases through the standard publish workflow once Phase 0 lands.
