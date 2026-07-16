# Benchmarking

tugaphone is measured against two golds, one per path. The
**phonemization pipeline** — a dialect selected by its lect code, driving the
orthography2ipa lattice — is scored sentence-level against orthography2ipa's TTS
gold. The **rules-only grapheme cascade** (the benchmark baseline, not the
pipeline) is scored word-level against the unified pronunciation gold; those
numbers live in [scoreboard.md](scoreboard.md).

## Pipeline: the TTS-gold harness

The reference for the phonemization pipeline is orthography2ipa's sentence-level
TTS gold — one gold set per Portuguese lect (`data/gold/portuguese_tts/<lect>.tsv`
in orthography2ipa), authored in the broad IPA tradition the lect specs are
written to. `scripts/tts_gold_benchmark.py` scores it end to end, reusing
orthography2ipa's own character-level PER and IPA normalization:

```bash
python scripts/tts_gold_benchmark.py            # every pt-family lect
python scripts/tts_gold_benchmark.py pt-PT pt-BR
```

The default lect set is the intersection of orthography2ipa's Portuguese TTS gold
with tugaphone's own 41 canonical dialects — the Portuguese family. orthography2ipa
also ships gold for the Astur-Leonese lects of Portugal (Mirandese `mwl`, the
`ast-PT` border varieties), which dedicated downstream phonemizers own; those are
out of tugaphone's scope and are excluded rather than scored through the pt-PT
fallback.

The mean sentence-level PER across the 41 pt-family lects is **0.034**. The
reading splits cleanly by path:

- the **pure-lattice** lects (no lexicon overlay) match the gold near-exactly —
  the lect spec and the gold share one convention; most score **0.000**;
- the **lexicon-overlay** lects (`pt-PT`, `pt-BR`, `pt-AO`, `pt-MZ`, `pt-TL` and
  their city variants) carry a small residual (`pt-PT` 0.11, `pt-BR` 0.17,
  `pt-TL` 0.31), because the gold is authored in a broader convention than the
  lect spec resolves to. The `tugalex` lexicon overlay now reproduces the lattice
  output for the words these sentences exercise, so it neither helps nor hurts the
  score; it is retained as the authority for lexical facts outside the gold. Read
  the number as agreement-with-the-spec-tradition, not absolute correctness.

## Rules-only baseline

The sections below measure the grapheme cascade in `tugaphone.tokenizer` /
`tugaphone.dialects` — the rules-only baseline, not the lattice pipeline —
against the unified pronunciation lexicon gold.

## Gold source

[TigreGotico/portuguese-unified-pronunciation-lexicon](https://huggingface.co/datasets/TigreGotico/portuguese-unified-pronunciation-lexicon)
(CC BY-SA 4.0) merges three sources into one convention-normalized
dataset: Infopédia (Porto Editora dictionary), the Portal da Língua
Portuguesa 10-region phonetic lexicon, and pt.wiktionary.org. Every row
is a word × region × source tuple with a broad phonemic (`ipa_broad`)
and a narrow phonetic (`ipa_narrow`) transcription.

The harness scores **`ipa_narrow`** — it matches tugaphone's
transcription depth (explicit [ɐ ɨ ɾ ʀ ɫ]).

One gold region is scored per registered dialect code:

| Dialect code | Gold region |
|---|---|
| pt-PT | pt-PT |
| pt-PT-x-lisbon | pt-PT-x-lisboa |
| pt-BR | pt-BR |
| pt-BR-x-sao-paulo | pt-BR-x-saopaulo |
| pt-BR-x-rio-janeiro | pt-BR-x-riodejaneiro |
| pt-AO | pt-AO |
| pt-MZ | pt-MZ-x-maputo |
| pt-TL | pt-TL-x-dili |

## Rules-only mode, and why it is non-circular

tugaphone ships a lexicon (tugalex) built from the same sources as the
gold. Scoring the normal lookup-first path would therefore measure
*lexicon coverage* — a word found in the lexicon scores perfectly by
construction — and say nothing about the grapheme rules that handle
every out-of-vocabulary word.

The harness instead empties the lexicon exception table
(`DialectInventory.IRREGULAR_WORDS = {}`) before scoring, so **every**
gold word takes the rule path. The number is then a per-word honest
measurement: the rules never saw the answer.

## Offline fixtures

CI never touches the network. `tests/data/gold/<dialect>.tsv` holds a
fixed-seed sample (seed `20260713`, up to 1000 words per region, all
pronunciation variants of each sampled word) drawn from the gold; each
fixture header records the SHA-256 of the exact dataset file it was
drawn from. Refreshing the sample is a maintainer action:

```bash
python scripts/benchmark.py --refresh-fixtures
```

## Scoring

Both sides are normalized identically — NFC, stress marks and
syllable/tie joiners removed, whitespace collapsed — then a
character-level edit distance is taken against the **closest** attested
variant of the word (a word with several valid pronunciations is not
penalised for the variants it did not choose). Reported per dialect:

- **PER** — summed edit distance / summed reference length;
- **word accuracy** — exact matches after normalization;
- the top-20 phone-confusion pairs (in `benchmarks/results.json`),
  which drive the accuracy campaign: fix the biggest confusion with a
  cited rule, re-run, repeat.

The PER routine is adapted from orthography2ipa's benchmark harness.

## Regression gate

`scripts/check_benchmark_regression.py` re-scores every dialect from
the committed fixtures and compares against the committed baseline
(`benchmarks/results.json`), failing CI when any dialect's PER worsens
by more than 0.005 absolute. Improvements never fail; commit the
regenerated baseline with the improving change so the new level becomes
the floor. The gate fails closed when fewer rows than registered
dialects are scored, so a broken fixture cannot produce a silent green.

```bash
python scripts/benchmark.py                    # rescore + rewrite reports
python scripts/check_benchmark_regression.py   # gate
```
