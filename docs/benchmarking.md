# Benchmarking
<!-- agent-hint
covers: how tugaphone measures accuracy and which scripts run each benchmark
source: scripts/tts_gold_benchmark.py, scripts/pt_br_gold_benchmark.py, scripts/benchmark.py, scripts/check_benchmark_regression.py
generated: no
verify: for s in tts_gold_benchmark pt_br_gold_benchmark benchmark check_benchmark_regression; do test -f scripts/$s.py || exit 1; done; grep -oE -- '--[a-z][a-z-]+' docs/benchmarking.md | sort -u | while read f; do grep -q -- "$f" scripts/*.py || { echo "unknown flag $f"; exit 1; }; done
see: scoreboard.md, architecture.md
-->

tugaphone is measured against two golds, one per path. The
**phonemization pipeline**, a dialect selected by its lect code, driving the
orthography2ipa lattice, is scored sentence-level against orthography2ipa's TTS
gold. The same pipeline with its packaged lexicon emptied, **rules-only**, is
scored word-level against the unified pronunciation gold. Those numbers are in
[scoreboard.md](scoreboard.md).

## Pipeline: the TTS-gold harness

The reference for the phonemization pipeline is orthography2ipa's sentence-level
TTS gold, one gold set per Portuguese lect (`data/gold/portuguese_tts/<lect>.tsv`
in orthography2ipa), authored in the broad IPA tradition the lect specs are
written to. `scripts/tts_gold_benchmark.py` scores it end to end, reusing
orthography2ipa's own character-level PER and IPA normalization:

The PER and normalization code is in orthography2ipa's source tree, not in its
wheel. Install orthography2ipa editable, or set `O2I_ROOT` to an orthography2ipa
checkout:

```bash
export O2I_ROOT=~/src/orthography2ipa
python scripts/tts_gold_benchmark.py            # every pt-family lect
python scripts/tts_gold_benchmark.py pt-PT pt-BR
```

The default lect set is the intersection of orthography2ipa's Portuguese TTS gold
with tugaphone's canonical dialects (`list_dialects()`), the Portuguese family.
A lect with no gold set is not scored. orthography2ipa
also ships gold for the Astur-Leonese lects of Portugal (Mirandese `mwl`, the
`ast-PT` border varieties), which dedicated downstream phonemizers own, those are
out of tugaphone's scope and are excluded rather than scored through the pt-PT
fallback.

The script prints one PER per lect and the mean. The scores split by path:

- The European, African and Asian lects match the gold almost exactly,
  because the lect spec and the gold share one convention. `pt-PT` takes its
  `o2i-lexicons` residual lexicon.
- `pt-BR` takes its `o2i-lexicons` residual lexicon, and every other lect runs
  on the rules alone.
- The Brazilian sub-regional lects carry a residual.

Read the number as agreement with the spec tradition, not as absolute
correctness.

## Pipeline: the Brazilian word sources

`scripts/pt_br_gold_benchmark.py` scores the pipeline word by word against four
Brazilian Portuguese sources. No source is a gold for every feature, so each
row prints the tier of its source, and each source scores only what it can show.

| Source | Tier | What it scores |
| --- | --- | --- |
| NILC Aeiouadô training file (São Paulo) | human-revised by one research team, not independently verified | PER, stress position, stressed e/o quality |
| Michaelis | broad notation, editor-made, method unstated, some stress marks misplaced and some readings of another word | Stress position and stressed e/o quality, never allophones |
| Aeiouadô published lexicon | machine-generated | A comparison row on a fixed sample, never a gold target |
| ALiB per-informant forms | expert-human, narrow | Only the coda /S/ of six words, by city, against the regional spec |

The script reads the source files from paths on the command line, because the
sources do not ship with tugaphone. Each source is optional:

```bash
O2I_ROOT=/path/to/orthography2ipa python scripts/pt_br_gold_benchmark.py \
    --nilc unitex_sample_transcribed.txt --aeiouado aeiouado-ipa-01.csv \
    --michaelis entries.jsonl --alib-capitals alib-capitals-coda-s.tsv \
    --alib-bahia alib-bahia-coda-s.tsv --lects pt-BR pt-BR-x-sp
```

This script folds the notation of a source into the spec's symbols: [ɪ ʊ ə] and the
fricative rhotics. It folds nothing else, so a `pt-BR-x-sp` row pays for the tap
and the dropped infinitive ⟨r⟩ that the spec writes and the NILC file does not.

The stress measure aligns the two readings sound by sound, and the stress agrees
when a cheapest alignment pairs the two stressed vowels. So notation does not
count as a stress miss: a glide against a hiatus after the stress (vácuo), the
epenthetic [i] (pacto) and a dropped infinitive ⟨r⟩ leave the comparison equal,
and saída [saˈidɐ] against [ˈsajdɐ] stays a miss. The script prints the words in,
the words compared and the misses for each row. `--stress-misses` writes each
miss to a file, because a miss may be a defect of the source. Some Michaelis
entries place the stress mark on the wrong vowel or print the reading of another
word, so a Michaelis miss is a lead to read, not a rules error by itself.

The `pt-BR` lexicon takes its readings from the NILC file, and its build uses
Michaelis as one second source, so a lexicon word would score a source against
itself. The script leaves the words of the lect's lexicon out of each row, so
every row measures the rules.

An ALiB row gives the share of the city's forms with a palatal coda, and the
share with the class that the spec gives. A city with no regional spec scores
against `pt-BR`.

## Rules-only baseline

The sections below measure the phonemization pipeline with its packaged lexicon
emptied against the unified pronunciation lexicon gold. A benchmark code that
is not a tugaphone lect goes through `resolve_lect` (`pt-BR-x-sao-paulo` is
`pt-BR-x-sp`, `pt-BR-x-rio-janeiro` is `pt-BR-x-rj`).

## Gold source

[TigreGotico/portuguese-unified-pronunciation-lexicon](https://huggingface.co/datasets/TigreGotico/portuguese-unified-pronunciation-lexicon)
(CC BY-SA 4.0) merges three sources into one convention-normalized
dataset: Infopédia (Porto Editora dictionary), the Portal da Língua
Portuguesa 10-region phonetic lexicon, and pt.wiktionary.org. Every row
is a word × region × source tuple with a broad phonemic (`ipa_broad`)
and a narrow phonetic (`ipa_narrow`) transcription.

The harness scores **`ipa_narrow`**, it matches tugaphone's
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

A lexicon built from the same sources as the gold would make a
lookup-first score measure *lexicon coverage*: a word found in the
lexicon scores perfectly by construction, and the score says nothing
about the grapheme rules that handle every out-of-vocabulary word.

The harness empties the lexicon of a copy of the lect's
`tugaphone.lattice_core.pipeline`, so **every** gold word takes the
orthography2ipa rule path. The shipped pipeline keeps its lexicon. The number is then a per-word honest
measurement: the rules never saw the answer.

## Offline fixtures

CI never touches the network. `tests/data/gold/<dialect>.tsv` holds a
fixed-seed sample (seed `20260713`, up to 1000 words per region, all
pronunciation variants of each sampled word) drawn from the gold, each
fixture header records the SHA-256 of the exact dataset file it was
drawn from. Refreshing the sample is a maintainer action:

```bash
python scripts/benchmark.py --refresh-fixtures
```

## Scoring

Both sides go through one segment rule, the rule of the shared phonemizer PER
board. The text is NFD. The ligatures ⟨ʧ ʤ ʦ ʣ⟩ become the tied forms. Stress
marks, syllable dots, joiners and spaces are removed. A segment is one base
symbol with its combining marks and modifier letters ⟨ʰ ʲ ʷ ˠ ˤ ː ˑ⟩, and a tie
bar joins the next base symbol into the same segment, so [t͡ʃ] is one segment.

Before the segment rule, a notation fold maps a symbol to the one that a source
calls the same phone. Phone PER uses only these folds:

| written | scored as | source |
|---|---|---|
| ⟨ə⟩ | ⟨ɨ⟩ in the Infopédia rows of pt-PT | Cruz-Ferreira (1999), *Handbook of the IPA* p. 127: the vowel "is often represented as /ə/" |
| ⟨r⟩ | ⟨ɾ⟩ in the Infopédia rows of pt-PT | Infopédia's own readings: caro ˈkaru against carro ˈkaʀu, and ⟨r⟩ in a tap position in 28,162 of 28,183 words (`portuguese-unified-pronunciation-lexicon@23898e1`, `ipa_narrow`) |
| ⟨ã⟩ | ⟨ɐ̃⟩ | Cruz-Ferreira (1999: 127) and Barbosa & Albano (2004), JIPA 34(2) p. 229 write the low nasal vowel ⟨ɐ̃⟩ |
| ⟨tʃ dʒ⟩ | ⟨t͡ʃ d͡ʒ⟩ | the same affricate without its tie bar |
| ⟨ⁿ ( ) '⟩ | removed | markup for optional segments and ASCII stress |

Phoneme PER adds the merge of the phones of one rhotic phoneme:

| written | scored as | source |
|---|---|---|
| ⟨χ ʀ⟩ | ⟨ʁ⟩ | Pereira (2020), *R-forte do português europeu*: the trill [ʀ] and the uvular and velar fricatives are variants of one /ʀ/ |
| ⟨ɹ⟩ | ⟨ɾ⟩ | Barbosa & Albano (2004: 228): the pt-BR /R/ "is extremely variable" |

| ⟨ɪ ʊ⟩ | ⟨i u⟩ in the Wiktionary and Michaelis rows of pt-BR | the rows' own usage: Wiktionary writes final unstressed ⟨-e⟩ as [i] 258 times and [ɪ] 44 times, and ⟨-o⟩ as [u] 606 times and [ʊ] 139 times; Michaelis writes [ɪ ʊ] in 0 of 20,580 rows (`portuguese-unified-pronunciation-lexicon@23898e1`, `ipa_narrow`) |

A fold applies by the source of the gold row, which the third column of each
fixture names. A row that several sources attest takes the folds of all of
them. A fold needs evidence that its source writes the two symbols for one
sound. Barbosa & Albano (2004: 229) plot [ʊ ɪ] apart from [u i], so no source
without such evidence folds them. No fold maps pt-BR ⟨ə⟩ to [ɐ] or [w̃ j̃] to
[w j]. The pt-AO, pt-MZ and pt-TL gold writes the trill as ⟨r⟩ beside the tap
⟨ɾ⟩, so its ⟨r⟩ does not fold.
Barbosa & Albano (2004: 229) plot [ʊ ɪ] apart from [u i], and no source found
calls the other pairs one phone. Each word scores against its **closest**
attested variant, so a word with several valid pronunciations is not penalised
for the variants it did not choose. Reported per dialect:

- **PER** (`per`): phone PER, the summed segment edits divided by the summed
  gold segments. The pt frontend gate uses this number, because a voice learns
  phones, not phonemes.
- **phoneme PER** (`per_phoneme`): the same sum with the rhotic merge.
- **PER, variants accepted** (`per_accepted`, European dialects only): the
  same PER, with two cited variants of the sound scored as one reading. First, [iʃ], [ɨʃ] and [ʃ] scored as one reading of a word-initial
  ⟨es⟩ + consonant on both sides. This is a variant of the sound, not of the
  notation, so the plain PER keeps it as an error. Vázquez Diéguez (2015,
  *Anuario de Estudios Filológicos* 38) gives "esc- [(i)ʃk]" and "est- [(i)ʃt]"
  on p. 250 and "Na sequência <es- + consoante> pode desaparecer" on p. 265.
  Teyssier (1989: 28), quoted in Vázquez Diéguez (2015: 244), writes estar [(i)ʃ'tar]. A stressed ⟨e⟩ (este), a
  double ⟨ss⟩ (essência) and initial ⟨ex⟩ stay outside the step.
  Second, an [i u] before a vowel scores as the glide [j w] on both sides.
  Mateus & Andrade (1998, *D.E.L.T.A.* 14(1), §1.3) give the glide in casual
  speech, "in casual speech glides may be followed by any vowel", and the vowel
  in careful speech; §1.5 gives passear pas[i]ar / pas[j]ar. The step cannot see
  stress, so a stressed hiatus such as [diɐ] also scores as [djɐ] on both sides.
  The source names /i u/ only, so an [ɨ] before a vowel (afeável [ɐfɨˈavɛɫ]
  against [ɐˈfjavɛɫ]) stays an edit.
- **word accuracy**: exact matches after normalization.
- **stress accuracy** (`stress_acc`, with its word count `n_stress`): the share
  of stress-eligible gold words whose primary stress lands on the gold's
  syllable. See [Stress accuracy](#stress-accuracy).
- the top-20 phone-confusion pairs (in `benchmarks/results.json`), which drive
  the accuracy campaign: fix the biggest confusion with a cited rule, re-run,
  repeat.

The PER routine is adapted from orthography2ipa's benchmark harness.

## Stress accuracy

PER strips the stress marks, so a transcription with every segment right and
the stress on the wrong syllable scores a perfect PER. Stress accuracy measures
that one choice. orthography2ipa's board reports the same column with the same
definition, so the two numbers compare.

A gold word is eligible when it is one word, its transcription carries exactly
one primary stress mark `ˈ` (an ASCII apostrophe in the gold counts as `ˈ`), and
it has two syllables or more. `n_stress` counts the eligible words. Below 20
eligible words `stress_acc` is null. A word with several gold variants scores a
hit when the hypothesis matches any eligible variant.

The hypothesis misses when it has no primary mark, more than one, or its mark
on another syllable. To find the syllable, the harness aligns the two
stress-stripped segment strings with the edit-distance alignment PER uses. A
segment is a character with its diacritics, and a tie bar joins the two
characters it links (`t͡ʃ`, `e͡ɪ`) into one segment.
When several alignments have the same minimum cost, the harness takes the one
that pairs the fewest nuclei with non-nuclei. The hit condition is that the gold's stressed nucleus aligns with the hypothesis's
stressed nucleus. A nucleus is a vowel that is not marked non-syllabic (`◌̯`)
and is not a glide letter (`j w ɥ ɰ`). A syllabic consonant (`◌̩`) is also a
nucleus. The stressed nucleus is the first nucleus after the primary mark.
Secondary marks `ˌ` are ignored.

The alignment keeps the two failure modes apart. `saída` with gold `sɐˈidɐ`
and hypothesis `ˈsajdɐ` is a miss: the hiatus became a diphthong and the stress
moved to `a`. Counting nuclei from the end of the word would call it a hit.
`texto` with gold `ˈtɐjʃtu` and hypothesis `ˈtɐʃtu` is a hit: the lost glide is
a segment error, and PER already counts it.

## Regression gate

`scripts/check_benchmark_regression.py` re-scores every dialect from
the committed fixtures and compares against the committed baseline
(`benchmarks/results.json`), failing CI when any dialect's PER rises or
its stress accuracy falls by more than 0.005 absolute. A dialect whose
baseline has a stress accuracy and whose rescored row has none also fails.
Improvements never fail, commit the
regenerated baseline with the improving change so the improved level becomes
the floor. The gate fails closed when fewer rows than registered
dialects are scored, so a broken fixture cannot produce a silent green.

```bash
python scripts/benchmark.py                    # rescore + rewrite reports
python scripts/check_benchmark_regression.py   # gate
```

---
[← Development](development.md) · [Home](index.md) · [Scoreboard →](scoreboard.md)
