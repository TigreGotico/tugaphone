# Homograph disambiguation

Portuguese has heterophonic homographs (same spelling, different pronunciation)
where the vowel quality shifts depending on which sense is active:

- *sede* as thirst /ˈsedɨ/ vs as headquarters /ˈsɛdɨ/, - *forma* as mould /ˈfoɾmɐ/ vs as shape /ˈfɔɾmɐ/, - *gosto* as "I like" /ˈgɔʃtu/ vs as "taste" /ˈgoʃtu/.

## Meaning-based: bifonia

[bifonia](https://github.com/TigreGotico/bifonia) is a required dependency, so
`TugaPhonemizer.phonemize_sentence` always calls
`bifonia.add_extra_diacritics` on Portuguese input before G2P. bifonia
performs context-sensitive sense disambiguation and inserts the open/closed
vowel diacritic directly into the orthography, so the grapheme rules that
follow produce the correct vowel quality without any special casing.

bifonia receives the lect code. Every `pt-BR` lect takes the Brazilian marks:
Brazilian Portuguese keeps the stressed vowel closed in every sense of *soma*,
*aceno*, *abono*, *domo*, *empeno* and *desempeno*. Every other lect takes the
European marks.

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()

# sede thirst (closed /e/)
print(ph.phonemize_sentence("Tenho muita sede."))
# ˈte·ɲu ˈmũj·tɐ ˈse·dɨ

# sede headquarters (open /ɛ/)
print(ph.phonemize_sentence("A sede da empresa fica em Lisboa."))
# ɐ ˈsɛ·dɨ ˈdɐ ẽ·pɾˈe·zɐ ˈfi·kɐ ẽj liʒ·bˈo·ɐ

# gosto verb (open /ɔ/)
print(ph.phonemize_sentence("Eu gosto de música."))
# ˈew ˈɡɔʃ·tu dɨ mˈu·zi·kɐ

# gosto noun (closed /o/)
print(ph.phonemize_sentence("Tenho bom gosto."))
# ˈte·ɲu bˈõ ˈɡoʃ·tu
```

---

## Where next

- [dialects.md](dialects.md), the five inventories and sub-regional accents
- [api.md](api.md), `TugaPhonemizer`
- [advanced.md](advanced.md), regional accents, numbers


---
[← Accent forcing](accent_forcing.md) · [Home](../README.md) · [Code-switch →](codeswitch.md)
