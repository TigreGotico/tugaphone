# Dialects

A tugaphone dialect *is* an orthography2ipa lect spec. The dialect set is the
Portuguese-family lects orthography2ipa ships, each reachable by its BCP-47
code. Select one through the `lang` argument to `phonemize_sentence`, `lang`
changes the phonology, not just the spelling.

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
    print(code, "→", ph.phonemize_sentence("O gato dorme.", code))
# pt-PT → ˈo ˈgatu ˈdɔɾmɨ
# pt-BR → ˈu ˈgatʊ ˈdoɾmi
# pt-AO → ˈʊ ˈgatʊ ˈdɔʁmɨ
# pt-MZ → ˈu ˈgatu ˈdɔrme
# pt-TL → ˈo ˈgatʊ ˈdɔrme
```

## The lect codes

`tugaphone.list_dialects()` returns every reachable code, 41 in all, derived
from `orthography2ipa.available_codes()`.

### National standards

| Code | Variety |
|------|---------|
| `pt-PT` | European Portuguese |
| `pt-BR` | Brazilian Portuguese |
| `pt-AO` | Angolan Portuguese |
| `pt-MZ` | Mozambican Portuguese |
| `pt-TL` | Timorese Portuguese |

### European sub-regional varieties

`pt-PT-x-porto`, `pt-PT-x-braga`, `pt-PT-x-minho`, `pt-PT-x-viana`,
`pt-PT-x-alfena`, `pt-PT-x-trasosmontes`, `pt-PT-x-aveiro`, `pt-PT-x-beira`,
`pt-PT-x-coimbra`, `pt-PT-x-alentejo`, `pt-PT-x-algarve`, `pt-PT-x-madeira`,
`pt-PT-x-acores`, `pt-PT-x-sao-miguel`, `pt-PT-x-terceira`, `pt-PT-x-lisbon`,
`pt-PT-x-medieval`.

Each spec's `allophone_rules` and `sandhi_rules` encode the variety's phonology
directly:

```python
# Porto: rising diphthongs, betacism /v/ → [b]
print(ph.phonemize_sentence("O vinho é muito bom.", "pt-PT-x-porto"))
# ˈwo ˈbiɲu ˈjɛ ˈmujtu ˈbõ

# Trás-os-Montes: <ch> → [tʃ], betacism
print(ph.phonemize_sentence("A chave.", "pt-PT-x-trasosmontes"))
# ˈɐ ˈtʃabɨ

# Madeira: /l/ palatalization → [ʎ]
print(ph.phonemize_sentence("O vinho é bom.", "pt-PT-x-madeira"))
# ˈo ˈviɲu ˈɛ ˈbõ
```

### Brazilian sub-regional varieties

`pt-BR-x-sp`, `pt-BR-x-rj`, `pt-BR-x-mg`, `pt-BR-x-pr`, `pt-BR-x-sul`,
`pt-BR-x-caipira`, `pt-BR-x-fluminense`, `pt-BR-x-bahia`, `pt-BR-x-recife`,
`pt-BR-x-ce`, `pt-BR-x-norte`, `pt-BR-x-brasilia`.

```python
print(ph.phonemize_sentence("noite", "pt-BR"))       # ˈnojtʃɪ
print(ph.phonemize_sentence("noite", "pt-BR-x-sp"))  # ˈnojti
```

### African, Asian and other lects

`pt-CV` (Cape Verde), `pt-GW` (Guinea-Bissau), `pt-ST` (São Tomé and Príncipe),
`pt-MO` (Macau), `pt-UY` (Uruguay), `ext-PT-x-barrancos` (Barranquenho), and
`roa-x-galaicopt` (Galician-Portuguese).

## Legacy aliases

Legacy tugaphone accent codes resolve to their orthography2ipa equivalents.
Resolution is case-insensitive, an unresolved private-use subtag falls back to
its parent tag, and any unrecognised code falls back to `pt-PT`.

| Alias | Resolves to |
|-------|-------------|
| `pt` | `pt-PT` |
| `pt-PT-x-lisboa` | `pt-PT-x-lisbon` |
| `pt-PT-x-azores` | `pt-PT-x-acores` |
| `pt-PT-x-north`, `pt-PT-x-norte`, `pt-PT-x-fafe` | `pt-PT-x-minho` |
| `pt-PT-x-famalicao` | `pt-PT-x-viana` |
| `pt-PT-x-transmontano`, `pt-PT-x-tras-os-montes` | `pt-PT-x-trasosmontes` |
| `pt-PT-x-central` | `pt-PT-x-coimbra` |
| `pt-BR-x-sao-paulo` | `pt-BR-x-sp` |
| `pt-BR-x-rio-janeiro`, `pt-BR-x-rio` | `pt-BR-x-rj` |

```python
from tugaphone import resolve_lect

resolve_lect("pt-PT-x-lisboa")     # 'pt-PT-x-lisbon'
resolve_lect("pt-BR-x-sao-paulo")  # 'pt-BR-x-sp'
resolve_lect("pt")                 # 'pt-PT'
```

## Lexicon overlay vs pure lattice

Eight lects carry the curated `tugalex` lexicon overlay, because their lexical
tradition matches a `tugalex` region: `pt-PT` and `pt-PT-x-lisbon` (Lisbon),
`pt-BR` and `pt-BR-x-rj` (Rio), `pt-BR-x-sp` (São Paulo), `pt-AO` (Luanda),
`pt-MZ` (Maputo) and `pt-TL` (Dili). For a covered word the lexicon supplies the
pronunciation and the lattice fills in only the out-of-vocabulary words.

Every other lect is **pure lattice**, its phonology comes entirely from the
orthography2ipa spec. The overlay is withheld deliberately: registering the
Lisbon lexicon on a Porto lect would overwrite the Porto spec's phonology with
Lisbon forms. See [architecture.md](architecture.md) for the layer boundary.

## Where next

- [architecture.md](architecture.md), the pipeline and the caller-owned layers
- [homographs.md](homographs.md), meaning-based disambiguation
- [numbers.md](numbers.md), number normalization
- [api.md](api.md), full class reference


---
[← Architecture](architecture.md) · [Home](../README.md) · [Accent forcing →](accent_forcing.md)
