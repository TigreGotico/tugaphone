# Dialects and regional accents

## The five dialect inventories

tugaphone ships a `DialectInventory` subclass for each of the five major
Lusophone dialect groups. Pass the corresponding IETF tag to
`phonemize_sentence`:

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
    print(code, "→", ph.phonemize_sentence("Choveu muito ontem.", code))
# pt-PT → ʃu·ˈvew mˈũj·tu ˈõ·tẽ ˈ···
# pt-BR → ʃo·ˈvew mwˈĩ·tʊ ˈõ·tẽ ˈ···
# pt-AO → ʃo·ˈvew mˈũjn·tʊ ˈõ·tẽ ˈ···
# pt-MZ → ʃu·ˈvew mˈũj·tu ˈõ·tẽ ˈ···
# pt-TL → ʃo·ˈvew mˈuj·tʊ ˈõ·tẽ ˈ···
```

Any unrecognised tag falls back to European Portuguese.

### pt-PT — European Portuguese

`EuropeanPortuguese`. The Lisbon standard is the base inventory:
- Heavy vowel reduction in unstressed position (unstressed /e/ → [ɨ])
- Post-alveolar sibilants in syllable-final position (`<s>` → [ʃ])
- Velarized lateral [ɫ] in coda position
- Uvular /ʁ/ for strong R

### pt-BR — Brazilian Portuguese

`BrazilianPortuguese`. Key differences from European:
- Fuller unstressed vowels (less reduction)
- Palatalisation of /t d/ before [i] → [tʃ dʒ]
- Coda /l/ vocalisation → [w] (creates diphthongs absent in European)
- Alveolar [s] for syllable-final position (not post-alveolar)

### pt-AO — Angolan Portuguese

`AngolanPortuguese`. Centred on Luanda:
- Less vowel reduction than European Portuguese
- Alveolar trill [r] for strong R
- Bantu-influenced prosody (substrate vowel lengthening)

### pt-MZ — Mozambican Portuguese

`MozambicanPortuguese`. Centred on Maputo:
- Bantu substrate influence from Tswa, Ronga, Chona and others
- Less vowel reduction than European
- Regional variation between north and south

### pt-TL — Timorese Portuguese

`TimoresePortuguese`. Second language for most speakers; influenced by Tetum
and other Austronesian languages. Conservative consonantism, /u/ not fronted.

---

## Sub-regional accent presets

On top of any dialect code, you can layer a `RegionalTransforms` preset via
the `regional_dialect` argument. Every preset is a composition of grounded
phonological rules cited to published sources (Cintra 1971; ALEPG 2006).

```python
from tugaphone.regional import PortoDialect, AzoresDialect

ph = TugaPhonemizer()
s = "O vinho é muito bom."

print(ph.phonemize_sentence(s, "pt-PT"))
# pt-PT standard: ˈu vˈi·ɲu ˈɛ mˈũj·tu bˈõ ˈ···

print(ph.phonemize_sentence(s, "pt-PT", regional_dialect=PortoDialect))
# Porto: ˈu bˈi·ɲu ˈɛ mˈũj·tu bˈuõ ˈ···  (betacism + rising diphthong)

print(ph.phonemize_sentence(s, "pt-PT", regional_dialect=AzoresDialect))
# Açores: ˈy vˈi·ɲu ˈɛ mˈỹj·tu bˈõ ˈ···  (stressed /u/ → [y])
```

### Preset table

All presets are importable from `tugaphone.regional`.

| Preset | Region | Signature rules |
|--------|--------|-----------------|
| `NorthernDialect` | Northern Portugal (generic) | `<ou>/<ei>` retention, betacism /v/→[b] |
| `CoimbraDialect` | Coimbra / Centro-Litoral | `<ou>/<ei>` retention, no betacism |
| `PortoDialect` | Porto / Douro Litoral | Stressed /o/→[uo] rising diphthong + northern core |
| `MinhoDialect` | Minho (conservative rural) | Vowel-centralisation resistance, open /a/, alveolar [r] |
| `BragaDialect` | Braga | Palatal epenthesis (`abelha`→`abeilha`) + Minho |
| `FamalicaoDialect` | Vila Nova de Famalicão | Conservative `-ão`→[õ] retention + Minho |
| `FafeDialect` | Fafe / inner Minho | Nasal /ẽ/→[eĩ] diphthongisation + Minho |
| `TrasMontanoDialect` | Trás-os-Montes | `<ch>` affrication, s-voicing, nasal denasalisation |
| `AlentejoDialect` | Alentejo | Intervocalic /d/ deletion, `meu`→[me], `ei`→[e] |
| `AlgarveDialect` | Algarve | `meu`→[me], coda-sibilant voicing sandhi |
| `MadeiraDialect` | Madeira | l-palatalisation, nasal diphthong → Ṽ+[n] |
| `AzoresDialect` | Açores (São Miguel) | Stressed /u/→[y], l-palatalisation, `oi`→[o] |

### Building a custom accent

Compose any rules from `RULE_MAP`:

```python
from tugaphone.regional import RegionalTransforms, RULE_MAP

my_accent = RegionalTransforms(
    ipa_rules=[RULE_MAP["betacism"], RULE_MAP["monophthongize_ei"]],
)
print(ph.phonemize_sentence("Vou beber vinho.", "pt-PT", regional_dialect=my_accent))
```

A `RegionalTransforms` round-trips through a plain dict:

```python
cfg = my_accent.as_dict
# {'morpheme_rules': [], 'ipa_rules': ['betacism', 'monophthongize_ei']}
clone = RegionalTransforms.from_dict(cfg)
```

### Rules-only mode

Instantiate a dialect inventory with an empty `IRREGULAR_WORDS` to bypass
the lexicon and rely purely on grapheme rules:

```python
from tugaphone.dialects import EuropeanPortuguese
from tugaphone.tokenizer import Sentence

inv = EuropeanPortuguese()
inv.IRREGULAR_WORDS = {}
s = Sentence("gato dorme", dialect=inv)
print(s.ipa)   # ˈɡa·tu ˈdoɾ·mɨ
```

---

## Where next

- [homographs.md](homographs.md) — meaning-based and POS-based disambiguation
- [numbers.md](numbers.md) — number normalization
- [api.md](api.md) — full class reference
- [advanced.md](advanced.md) — serialization and integration
