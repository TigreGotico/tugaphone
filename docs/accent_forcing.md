# Forcing an accent

`tugaphone.phonemize(text, lect)` *describes* an accent: it produces the IPA a
speaker of `lect` would say. Accent **forcing** is the inverse job, bending a
downstream text-to-speech voice into a target accent on purpose, for two uses:

1. **Tuning a TTS voice**, make a voice speak with an accent it does not
   natively have.
2. **Synthetic training data**, manipulate input so a TTS *learns* a target
   accent from text a base speaker already reads.

How you force an accent depends on what the TTS eats.

| Your TTS takes… | Force the accent with… | `force_accent` mode |
|---|---|---|
| **IPA / phonemes** (phoonnx-style) | the target lect's IPA, the lattice already produces it | `mode="ipa"` |
| **graphemes / text** (a fixed pt-PT or pt-BR voice) | Portuguese text **respelled** so the base voice reads it as the target sounds | `mode="respell"` |

Everything lives in `tugaphone.accent` and is re-exported from the package
top level.

---

## Zero to hero

### 1. Phoneme-input TTS: `mode="ipa"`

The voice already takes IPA, so forcing the accent is just transcribing with the
target lect. This is a thin wrapper over `phonemize`.

```python
from tugaphone import force_accent

force_accent("o vinho verde", "pt-PT-x-porto", mode="ipa")
# 'o ˈbiɲu ˈbjɛɾd'   ← Northern betacism, [v]→[b], from the lect spec
```

Feed the returned string straight to a phoneme-input voice.

### 2. Grapheme-input TTS: `mode="respell"`

A fixed pt-PT voice reads *text* and always applies *its own* accent. To make it
pronounce a different accent you must respell the input in conventions that
voice reads as the target sounds, feed it `binho` to force the Northern
betacism of `vinho`.

```python
force_accent("o vinho verde", "pt-PT-x-porto", mode="respell", base_lect="pt-PT")
# 'o binho berde'    ← a pt-PT voice now says [ˈbiɲu ˈbɛɾd]
```

`base_lect` is the accent your grapheme voice actually speaks. Respelling only
rewrites the graphemes whose pronunciation **differs** from that base, words the
base voice already says correctly are left untouched, so the output stays
readable Portuguese, not a phonetic soup.

```python
force_accent("a tia no Brasil", "pt-BR", mode="respell", base_lect="pt-PT")
# 'a tchia no Brasiu'   ← [t]→[tʃ] palatalisation, coda [ɫ]→[w] vocalisation
```

### 3. User tweaks: `AccentOverlay`

The rule table ships the *systematic* phonology. For per-voice, ad-hoc quirks, "this particular voice mispronounces the uvular R", use an overlay: an ordered
stack of your own regex/word substitutions applied **after** the lattice. This is
explicitly *user space*, not shipped dialect phonology, and it serialises to JSON
so a voice tweak is shareable.

```python
from tugaphone import AccentOverlay, Transform, force_accent

overlay = AccentOverlay(
    name="my-voice-tweaks",
    transforms=[
        # stage="ipa" edits the phonemic output of mode="ipa"
        Transform(kind="regex", pattern="ʀ", replacement="ɾ", stage="ipa"),
        # stage="text" edits the respelled text of mode="respell"
        Transform(kind="word", pattern="binho", replacement="vinho", stage="text"),
    ],
)

force_accent("o carro", "pt-PT", mode="ipa", overlay=overlay)   # 'o ˈkaɾu'

open("voice.json", "w").write(overlay.to_json())      # share it
overlay = AccentOverlay.from_json(open("voice.json").read())
```

`Transform` fields: `kind` (`"regex"` or whole-`"word"`), `pattern`,
`replacement`, `stage` (`"ipa"` or `"text"`), `ignore_case`. Transforms run in
list order, only those whose `stage` matches the mode fire.

### 4. Synthetic training corpus

`examples/12_synthetic_corpus.py` emits a parallel corpus, `(sentence, lect,
ipa, respelled_text)`, over the sentence-level Portuguese TTS gold across all 41
pt-family lects. Point a phoneme-input voice at the `ipa` column, or a fixed
pt-PT grapheme voice at the `respelled_text` column, to teach it the target
accent.

```bash
python examples/12_synthetic_corpus.py                 # quick demo to stdout
python examples/12_synthetic_corpus.py --full out.tsv  # full corpus
```

---

## Command line

```bash
tugaphone force-accent "o vinho verde" --lect pt-PT-x-porto --mode ipa
tugaphone force-accent "o vinho verde" --lect pt-PT-x-porto --mode respell --base pt-PT
tugaphone force-accent "a tia"         --lect pt-BR --mode respell --overlay voice.json
tugaphone phonemize    "o gato dorme"  --lect pt-BR
tugaphone list
```

## Plugin

`TugaphoneG2PPlugin.force_accent(text, lect, mode=…, base_lect=…, overlay=…)`
exposes the same call, `base_lect` defaults to the plugin's own `lang`, i.e. the
accent the grapheme voice it drives speaks.

---

## How respelling works, and its ceiling

The respeller is **verification-gated**, which is what makes it trustworthy. For
each word it:

1. transcribes the word with the **target** lect (the sound we want), 2. hill-climbs orthographic edits from a rule table
   (`DEFAULT_RESPELL_RULES`, betacism, dental palatalisation, coda-`l`
   vocalisation, diphthong monophthongisation), 3. keeps an edit **only if** re-transcribing the candidate with the **base** lect
   moves it measurably closer to the target IPA.

Two consequences follow directly:

- **A respelling can never make a word worse.** The base voice's own reading is
  the gate, so an accepted edit is guaranteed to help. Stress marks are kept
  inside the distance metric, so an edit that shifts stress is rejected, the
  respeller is stress-preserving without special-casing.
- **Unrespellable contrasts are left alone.** Some accent differences simply
  cannot be spelled in Portuguese orthography, European `[ɨ]` reduction versus a
  fuller `[ə]`, fine nasal-vowel quality, coda-sibilant voicing. No orthographic
  edit improves them, so the word is returned unchanged rather than mangled. This
  is the **ceiling**: respelling closes the *spellable* part of the accent gap
  and no more.

Measured honestly on the gold (`scripts/roundtrip_eval.py`), respelling closes a
large share of the gap for accents whose phenomena are orthographic, Northern
betacism (Alfena, Braga, Porto, Viana) and Brazilian palatalisation / `l`-vowel
(Minas, Bahia, Brasília), and correctly does *nothing* where the contrast is
unspellable (São Paulo coda sibilants, Mozambican vowels), where the honest gain
is `0`. The evaluation measures the respeller against the lattice's own target
transcription, holding the lattice fixed on both sides.

```bash
python scripts/roundtrip_eval.py                     # per-lect base/respell/gain
python scripts/roundtrip_eval.py pt-BR pt-PT-x-porto
```

One caveat the numbers carry: words are respelled independently, so
cross-word sandhi is not modelled during respelling, which can leave a
negligible sentence-level residue on a few lects.


---
[← Dialects](dialects.md) · [Home](../README.md) · [Homographs →](homographs.md)
