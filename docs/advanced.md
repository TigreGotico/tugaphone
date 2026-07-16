# Advanced recipes

Once the basic `phonemize_sentence` loop is clear, these are the knobs worth
knowing.

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
- [`silabificador`](https://github.com/TigreGotico/silabificador) — the
  syllabifier behind `WordToken.syllables`.
- [`bifonia`](https://github.com/TigreGotico/bifonia) — meaning-based
  heterophone disambiguation; called via `add_extra_diacritics` before G2P.
- [`orthography2ipa`](https://github.com/TigreGotico/orthography2ipa) — the
  `G2PPlugin` base interface and declarative stress rules tugaphone exposes.

A TTS front-end typically wires `tugaphone` as the G2P stage: normalize text,
phonemize per target dialect, hand the IPA string to the acoustic model.

## Cross-word phonology

`Sentence.ipa` joins each `WordToken.ipa` with spaces and transcribes every word
**independently** — a character-level cascade (`CharToken` → `GraphemeToken` →
`WordToken` → `Sentence`) that never crosses a word boundary. tugaphone consumes
`orthography2ipa`'s shared *primitives* (grapheme trie, vowel classification,
stress rules, `LanguageSpec`) but does not route IPA generation through o2i's
`G2P.transcribe` or its pronunciation lattice.

Because generation runs word-by-word, cross-word processes are not modelled on
that path:

- Standard European Portuguese **external `/s`-sandhi** (coda `/s` `[ʃ]` → `[z]`
  before a vowel-initial next word: *os amigos* → `[ˈuz ɐˈmiɡuʃ]`) is not
  applied in base `pt-PT`; `os` stays `[ˈuʃ]`.
- The southern/insular `sibilant_voicing_sandhi` IPA transform is a per-token
  approximation: it voices a token's own final `[ʃ]` → `[ʒ]` whenever the word
  ends in `<s>`, with no visibility of the following word — so it fires even
  utterance-finally, where a true cross-word rule would not.

For the optional o2i-lattice base path (which changes only the base IPA of
out-of-vocabulary words, not cross-word phonology) see
[lattice-base-migration.md](lattice-base-migration.md).

## Where next

- [api.md](api.md) — full signatures
- [dialects.md](dialects.md) — the five inventories and sub-regional accent presets
- [homographs.md](homographs.md) — meaning-based disambiguation
- [numbers.md](numbers.md) — number normalization and gender agreement
- [tokenizer.md](tokenizer.md) — inspect syllables, stress and graphemes directly
- [quickstart.md](quickstart.md) — the basics
