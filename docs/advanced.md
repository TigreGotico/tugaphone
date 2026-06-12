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
| `CoimbraDialect` | Diphthong retention only (neutral baseline). |
| `MinhoDialect` | Vowel-centralization resistance, open vowels, alveolar rhotic. |
| `BragaDialect` | Palatal epenthesis (`abelha` → `abeilha`) on top of northern rules. |
| `FamalicaoDialect` | Conservative `o`-nasal retention (`Famalicão` → `Famalicoum`). |
| `TrasMontanoDialect` | `ch` affrication, s-voicing, final nasal denasalization. |
| `PortoDialect` | Rising `o` diphthong (`Porto` → `Puorto`). |
| `FafeDialect` | Nasal diphthongization of `e` (`gente` → `geinte`). |

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

`tugaphone` composes three TigreGotico Portuguese NLP libraries; each is usable
on its own:

- [`tugalex`](https://github.com/TigreGotico/tugalex) — the phonetic lexicon
  (`LEXICON` in `tugaphone.dialects`). `LEXICON.get_ipa_map(region=...)` returns
  the per-region exception table.
- [`tugatagger`](https://github.com/TigreGotico/tugatagger) — the POS tagger
  behind `postag_engine`.
- [`silabificador`](https://github.com/TigreGotico/silabificador) — the
  syllabifier behind `WordToken.syllables`.

A TTS front-end typically wires `tugaphone` as the G2P stage: normalize text,
phonemize per target dialect, hand the IPA string to the acoustic model.

## Where next

- [api.md](api.md) — full signatures
- [tokenizer.md](tokenizer.md) — inspect syllables, stress and graphemes directly
- [quickstart.md](quickstart.md) — the basics
