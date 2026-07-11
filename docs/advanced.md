# Advanced recipes

Once the basic `phonemize_sentence` loop is clear, these are the knobs worth
knowing.

## POS engines and homographs

Portuguese homographs change pronunciation by part of speech. `tugaphone` tags
the sentence first and feeds the tags into transcription, so the engine you pick
affects accuracy:

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer(postag_engine="spacy")    # most accurate, needs pt_core_news_lg
ph.phonemize_sentence("Vou para casa.")        # 'para' as preposition
ph.phonemize_sentence("Ele para o carro.")     # 'para' as verb
```

Engine options, from heaviest to lightest:

| Engine | Needs | Notes |
|--------|-------|-------|
| `spacy` | `spacy` + `pt_core_news_lg` | Most accurate. |
| `brill` | `brill-postaggers` | Lighter, faster; installed via `tugatagger[brill]`. |
| `lexicon` | nothing extra | Built-in lookup, limited coverage. |
| `dummy` | nothing | Rule-based fallback, no dependencies. |
| `auto` | — | Falls through whatever is installed. Default. |

If you only need deterministic output with no optional dependencies, construct
with `postag_engine="dummy"`.

## Regional accents

On top of the five dialect codes, `tugaphone.regional` ships sub-regional accent
presets as `RegionalTransforms`. Pass one through `regional_dialect`; it is
applied on top of the `lang` dialect:

```python
from tugaphone import TugaPhonemizer
from tugaphone.regional import (PortoDialect, MinhoDialect, BragaDialect,
                                TrasMontanoDialect, FafeDialect)

ph = TugaPhonemizer()
sentence = "a gente sente o que sabe"
for name, accent in [("porto", PortoDialect), ("minho", MinhoDialect),
                     ("braga", BragaDialect), ("trasmontano", TrasMontanoDialect),
                     ("fafe", FafeDialect)]:
    print(name, "→", ph.phonemize_sentence(sentence, "pt-PT", regional_dialect=accent))
```

| Preset | Signature features |
|--------|--------------------|
| `NorthernDialect` | `<ou>/<ei>` retention + betacism /v/→[b] (core northern). |
| `CoimbraDialect` | Diphthong retention only (neutral baseline, no betacism). |
| `PortoDialect` | Rising `o` diphthong (stressed /o/→[uo]) + northern core. |
| `MinhoDialect` | Vowel-centralization resistance, open vowels, alveolar rhotic. |
| `BragaDialect` | Palatal epenthesis (`abelha` → `abeilha`) on top of Minho rules. |
| `FamalicaoDialect` | Conservative `o`-nasal retention + Minho rules. |
| `FafeDialect` | Nasal diphthongization of `e` (`gente` → `geinte`) + Minho rules. |
| `TrasMontanoDialect` | `ch` affrication, s-voicing, final nasal denasalization. |
| `AlentejoDialect` | Intervocalic /d/ deletion, `meu`→[me], `ei`→[e]. |
| `AlgarveDialect` | `meu`→[me], coda-sibilant voicing sandhi. |
| `MadeiraDialect` | l-palatalisation, nasal diphthong → Ṽ+[n]. |
| `AzoresDialect` | Stressed /u/→[y], l-palatalisation, `oi`→[o]. |

These are explicitly experimental — real variation is messier than any rule set.

### Serializing an accent

`RegionalTransforms` round-trips through a plain dict, so an accent config can
live in JSON or YAML:

```python
from tugaphone.regional import PortoDialect, RegionalTransforms

cfg = PortoDialect.as_dict
# {'morpheme_rules': [], 'ipa_rules': ['rising_diphthong_o', ...]}

clone = RegionalTransforms.from_dict(cfg)
[r.__name__ for r in clone.ipa_rules]
```

`from_dict` raises `ValueError` on an unknown IPA rule name. Only rules listed in
`tugaphone.regional.RULE_MAP` survive the round-trip; accents that use other rule
functions serialize a subset of their behaviour.

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
`strict=False` to leave unparseable tokens in place instead of raising.

## Integration with sibling libraries

`tugaphone` composes the TigreGotico Portuguese NLP stack; each library is
usable on its own:

- [`tugalex`](https://github.com/TigreGotico/tugalex) — the phonetic lexicon
  (`LEXICON` in `tugaphone.dialects`).
- [`tugatagger`](https://github.com/TigreGotico/tugatagger) — the POS tagger
  behind `postag_engine`.
- [`silabificador`](https://github.com/TigreGotico/silabificador) — the
  syllabifier behind `WordToken.syllables`, registered as an `orthography2ipa`
  syllabifier plugin.
- [`bifonia`](https://github.com/TigreGotico/bifonia) — meaning-based
  heterophone disambiguation; called via `add_extra_diacritics` before G2P.
- [`orthography2ipa`](https://github.com/TigreGotico/orthography2ipa) — the
  `G2PPlugin` base interface and declarative stress rules tugaphone exposes.

A TTS front-end typically wires `tugaphone` as the G2P stage: normalize text,
phonemize per target dialect, hand the IPA string to the acoustic model.

## Cross-word phonology and the sentence-context seam

`Sentence.ipa` joins each `WordToken.ipa` with spaces and transcribes every word
**independently** — a character-level cascade (`CharToken` → `GraphemeToken` →
`WordToken` → `Sentence`) that never crosses a word boundary. tugaphone consumes
`orthography2ipa`'s shared *primitives* (grapheme trie, vowel classification,
stress rules, `LanguageSpec`) but does **not** route IPA generation through
o2i's `G2P.transcribe` or its pronunciation lattice (`G2P.ipa_lattice`).

Because of that, cross-word processes are unmodelled on the generation path:

- Standard EP **external `/s`-sandhi** (coda `/s/` `[ʃ]` → `[z]` before a
  vowel-initial next word: *os amigos* → `[ˈuz ɐˈmiɡuʃ]`, Mateus & d'Andrade
  2000) is **not** applied in base `pt-PT`; `os` stays `[ˈuʃ]`.
- The southern/insular `sibilant_voicing_sandhi` IPA transform is a per-token
  approximation: it voices a token's own final `[ʃ]` → `[ʒ]` whenever the word
  ends in `<s>`, with no visibility of the following word — so it fires even
  utterance-finally, where a true cross-word rule would not.

`orthography2ipa` (≥1.70) now provides both a declarative `sandhi_rules` set on
the Portuguese specs (`PT_FINAL_S_PREVOCALIC_VOICE` → `[z]`;
`pt-PT-x-algarve` / `pt-PT-x-acores` → `[ʒ]`, run through its `SandhiEngine`) and
a **sentence-context seam** (`orthography2ipa.sentence`: `G2P.sentence_lattice`,
`SentenceRescorer`, `SentenceRescoreContext`) that exposes each word's phrase /
utterance position and its neighbours' edge lattice slots for boundary-aware,
bidirectional rewrites. tugaphone cannot consume either today: the seam operates
over o2i's `SentenceLattice`, and tugaphone's per-word IPA is not produced by
o2i's `G2P`.

### B6 stage-2 — adopting the seam (follow-up)

Routing generation through o2i's lattice is a **breaking** change to tugaphone's
segment model and is deliberately out of scope for the o2i-1.70 re-pin. A
concrete path:

1. **Post-pass with `SandhiEngine` (smaller, string-level).** `Sentence.ipa`
   already materialises `word_ipas = [word.ipa for word in self.words]`. Feed
   that list to o2i's `SandhiEngine(spec.sandhi_rules).apply(word_ipas)` for the
   resolved `LanguageSpec`. This buys `PT_FINAL_S_PREVOCALIC_VOICE` and the
   algarve/açores `[ʒ]` variants cross-word-correctly. **Hazards to gate first:**
   (a) o2i's `sandhi_rules` regexes are written against o2i's IPA conventions —
   verify tugaphone's word IPA (syllable `·` separators, combining vs
   precomposed nasal tildes, leading stress marks) matches the `left_context` /
   `right_context` classes on a gold set before enabling; (b) **double
   application** with the existing per-token `sibilant_voicing_sandhi` on the
   southern/insular presets (o2i's açores spec re-declares the rule) — one path
   must own the voicing, not both; (c) it is a behaviour change (base `pt-PT`
   gains `[z]`) and needs the gold IPA test set migrated, not just parity.

2. **Full seam consumption (larger, lattice-level).** To use `SentenceRescorer`
   / `SentenceLattice` — and the phrase/utterance-position and edge-slot
   visibility they carry — tugaphone must expose its per-word transcription as
   o2i `SegmentSlot` lattices (or generate through o2i's `G2P` directly). This is
   the segment-model refactor and carries the **atomic-vs-decomposed grapheme
   hazard** barranquenho hit: tugaphone's `GraphemeToken` groups multi-char
   graphemes (`nh`, `lh`, `ch`, nasal digraphs) whose IPA must map onto o2i's
   per-grapheme slots without splitting a nasal vowel from its tilde or an
   affricate from its parts. Sequence it after (1) proves the sandhi rules are
   correct on the string path.

## Where next

- [api.md](api.md) — full signatures
- [dialects.md](dialects.md) — the five inventories and sub-regional accent presets
- [homographs.md](homographs.md) — meaning-based and POS-based disambiguation
- [numbers.md](numbers.md) — number normalization and gender agreement
- [tokenizer.md](tokenizer.md) — inspect syllables, stress and graphemes directly
- [quickstart.md](quickstart.md) — the basics
