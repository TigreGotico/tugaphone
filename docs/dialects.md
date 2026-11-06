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
# pt-PT → o ˈɡatu ˈdɔɾmɨ
# pt-BR → u ˈɡatu ˈdoɾmi
# pt-AO → ʊ ˈɡatʊ ˈdɔʁmɨ
# pt-MZ → u ˈɡatu ˈdɔrme
# pt-TL → o ˈɡatʊ ˈdɔrme
```

## The lect codes

`tugaphone.list_dialects()` returns every reachable code. It reads them from
`orthography2ipa.available_codes()` at import time, so the set follows the
installed orthography2ipa. The lists below group the codes it returns.

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
`pt-PT-x-alfena`, `pt-PT-x-tras-os-montes`, `pt-PT-x-aveiro`, `pt-PT-x-beira`,
`pt-PT-x-coimbra`, `pt-PT-x-alentejo`, `pt-PT-x-algarve`, `pt-PT-x-madeira`,
`pt-PT-x-acores`, `pt-PT-x-sao-miguel`, `pt-PT-x-terceira`, `pt-PT-x-lisbon`.

Each spec's `allophone_rules` and `sandhi_rules` encode the variety's phonology
directly:

```python
# Porto: rising diphthongs, betacism /v/ → [b]
print(ph.phonemize_sentence("A bola é do Porto.", "pt-PT-x-porto"))
# ɐ ˈbwɔlɐ ˈjɛ du ˈpwoɾtu
print(ph.phonemize_sentence("O vinho é muito bom.", "pt-PT-x-porto"))
# o ˈbiɲu ˈjɛ ˈmujtu ˈbõ

# Trás-os-Montes: <ch> → [tʃ], betacism
print(ph.phonemize_sentence("A chave.", "pt-PT-x-tras-os-montes"))
# ɐ ˈtʃabɨ

# Madeira: intervocalic /l/ after /i/ → [ʎ]
print(ph.phonemize_sentence("A vila é bonita.", "pt-PT-x-madeira"))
# ɐ ˈviʎɐ ˈɛ buˈnitɐ
```

### Brazilian sub-regional varieties

`pt-BR-x-sp`, `pt-BR-x-rj`, `pt-BR-x-mg`, `pt-BR-x-pr`, `pt-BR-x-sul`,
`pt-BR-x-caipira`, `pt-BR-x-fluminen`, `pt-BR-x-bahia`, `pt-BR-x-recife`,
`pt-BR-x-ce`, `pt-BR-x-norte`, `pt-BR-x-cuiaba`, `pt-BR-x-floripa`.

```python
print(ph.phonemize_sentence("noite", "pt-BR"))       # ˈnojtʃɪ
print(ph.phonemize_sentence("noite", "pt-BR-x-sp"))  # ˈnojti
```

### African, Asian and other lects

`pt-CV` (Cape Verde), `pt-GW` (Guinea-Bissau), `pt-ST` (São Tomé and Príncipe),
`pt-MO` (Macau) and `pt-UY` (Uruguay).

Barranquenho, Old Portuguese and Galician-Portuguese are not tugaphone lects.
Each has its own orthography, so the modern Portuguese text stages do not apply.
`g2p_barranquenho` reads Barranquenho, and orthography2ipa keeps all three specs.

## Legacy aliases

Legacy tugaphone accent codes resolve to their orthography2ipa equivalents.
Resolution is case-insensitive, an unresolved private-use subtag falls back to
its parent tag, and any unrecognised code falls back to `pt-PT`. Both fallbacks
warn. A code that
orthography2ipa renamed also resolves, through the old key orthography2ipa
keeps as an alias.

| Alias | Resolves to |
|-------|-------------|
| `pt` | `pt-PT` |
| `pt-PT-x-lisboa` | `pt-PT-x-lisbon` |
| `pt-PT-x-azores` | `pt-PT-x-acores` |
| `pt-PT-x-north`, `pt-PT-x-norte`, `pt-PT-x-fafe` | `pt-PT-x-minho` |
| `pt-PT-x-famalicao` | `pt-PT-x-viana` |
| `pt-PT-x-transmontano`, `pt-PT-x-trasosmontes` | `pt-PT-x-tras-os-montes` |
| `pt-PT-x-central` | `pt-PT-x-coimbra` |
| `pt-BR-x-sao-paulo` | `pt-BR-x-sp` |
| `pt-BR-x-rio-janeiro`, `pt-BR-x-rio` | `pt-BR-x-rj` |
| `pt-BR-x-fluminense` | `pt-BR-x-fluminen` |

```python
from tugaphone import resolve_lect

resolve_lect("pt-PT-x-lisboa")     # 'pt-PT-x-lisbon'
resolve_lect("pt-BR-x-sao-paulo")  # 'pt-BR-x-sp'
resolve_lect("pt")                 # 'pt-PT'
```

## Lexicon vs pure lattice

Only `pt-PT` and `pt-BR` take a lexicon: the `o2i-lexicons` residual lexicon of
the lect, which holds the words that the lect's rules get wrong. For a covered
word the lexicon supplies the pronunciation, and the lattice reads every other
word.

Every other lect is **pure lattice**, its phonology comes entirely from the
orthography2ipa spec. A sub-lect does not take its parent's lexicon, because it
would overwrite the sub-lect spec's phonology with the parent's forms. See
[architecture.md](architecture.md) for the layer boundary.

## Where next

- [architecture.md](architecture.md), the pipeline and the caller-owned layers
- [homographs.md](homographs.md), meaning-based disambiguation
- [numbers.md](numbers.md), number normalization
- [api.md](api.md), full class reference


---
[← Architecture](architecture.md) · [Home](../README.md) · [Accent forcing →](accent_forcing.md)
