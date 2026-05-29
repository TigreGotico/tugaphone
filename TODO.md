# TODO — tugaphone

A dialect-aware Portuguese phonemizer covering pt-PT, pt-BR, pt-AO, pt-MZ, pt-TL
plus regional micro-dialects (Porto, Minho, Braga, Trás-os-Montes, …). Hybrid
approach: a curated phonetic lexicon (`tugalex`) with rule-based G2P fallback,
POS-aware homograph disambiguation (`tugatagger`), number normalization,
syllabification (`silabificador`), stress detection, and IPA output.

## Open issues

- [ ] #12 Epenthetic `[j]` insertion regex in `ipa_transforms.py` only matches stressed vowels (bug).
- [ ] #11 `palatal_affrication_ch` may over-apply the transformation to all `ʃ` phonemes (bug).
- [ ] #10 Fixed-length string slicing breaks with multi-codepoint phoneme characters.
- [ ] #9 Hardcoded `'boa'` case in `retain_ou_diphthong` does not match the function's purpose.
- [ ] #8 `RegionalDialect.as_dict` silently drops unmapped rules, causing lossy serialization.
- [ ] #20 Dependency Dashboard (Renovate meta-issue).

## Hardening (CI / packaging / hygiene)

- [ ] Realign workflows to `OpenVoiceOS/gh-automations@dev`: `release_workflow.yml` and `publish_stable.yml` reference `TigreGotico/gh-automations@master`.
- [ ] Add the missing standard workflows: `build-tests`, `coverage`, `license_check`.
- [ ] Migrate packaging to `pyproject.toml`; metadata is thin (`description` empty, no classifiers). Keep the `version.py` block untouched by humans.
- [ ] Add a `LICENSE` file (README declares Apache 2.0; metadata `license` is empty).
- [ ] Add a `.gitignore` (egg-info, `__pycache__`, build/dist) so `tugaphone.egg-info/` is never committed.
- [ ] Add a `tests/` suite with a runner. The README's per-dialect worked examples and the ~99.6% syllabification benchmark are natural seeds for regression tests.

## Code TODOs

- [ ] `tugaphone/regional.py:109` — implement morpheme rules and update the lookup map.
- [ ] `tugaphone/dialects.py:453` — map to the modern word equivalent and normalize for IPA parsing.
- [ ] `tugaphone/dialects.py:887` — handle hiatus suffixes (e.g. suffix `inha`: `Vinha` → `V.inha`).
- [ ] `tugaphone/tokenizer.py:311` — go to previous grapheme.
- [ ] `tugaphone/tokenizer.py:321` — go to next grapheme.
- [ ] `tugaphone/tokenizer.py:612` — per-dialect handling.
- [ ] `tugaphone/tokenizer.py:1184` — unresolved `return False  # TODO`.
- [ ] `tugaphone/number_utils.py:21` — document the max value (cannot handle very large numbers).
- [ ] `tugaphone/number_utils.py:52` — allow scale independent from the language code.
- [ ] `tugaphone/number_utils.py:139` — differentiate float and decimal (float also handles scientific notation).
