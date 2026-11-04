# Homograph disambiguation

Portuguese has heterophonic homographs (same spelling, different pronunciation)
where the vowel quality shifts depending on which sense is active:

- *sede* as thirst /ˈsedɨ/ vs as headquarters /ˈsɛdɨ/,
- *forma* as mould /ˈfoɾmɐ/ vs as shape /ˈfɔɾmɐ/,
- *gosto* as "I like" /ˈɡɔʃtu/ vs as "taste" /ˈɡoʃtu/.

## Meaning-based: bifonia

[bifonia](https://github.com/TigreGotico/bifonia) is a required dependency, so
`TugaPhonemizer.phonemize_sentence` always calls
`bifonia.add_extra_diacritics` on Portuguese input, in the engine's `normalize`
stage, before the lattice transcribes it. bifonia
performs context-sensitive sense disambiguation and inserts the open/closed
vowel diacritic directly into the orthography, so the lattice produces the
correct vowel quality without any special casing.

bifonia receives the lect code. Every `pt-BR` lect takes the Brazilian marks:
Brazilian Portuguese keeps the stressed vowel closed in every sense of *soma*,
*aceno*, *abono*, *domo*, *empeno* and *desempeno*. Every other lect takes the
European marks.

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()

# sede thirst (closed /e/)
print(ph.phonemize_sentence("Tenho muita sede."))
# ˈtɛɲu ˈmujtɐ ˈsedɨ

# sede headquarters (open /ɛ/)
print(ph.phonemize_sentence("A sede da empresa fica em Lisboa."))
# ɐ ˈsɛdɨ dɐ ẽˈpɾezɐ ˈfikɐ ẽj liʒˈboɐ

# gosto verb (open /ɔ/)
print(ph.phonemize_sentence("Eu gosto de música."))
# ˈew ˈɡɔʃtu dɨ ˈmuzikɐ

# gosto noun (closed /o/)
print(ph.phonemize_sentence("Tenho bom gosto."))
# ˈtɛɲu ˈbõ ˈɡoʃtu
```

---

## Where next

- [dialects.md](dialects.md), the lect codes and sub-regional accents
- [api.md](api.md), `TugaPhonemizer`
- [advanced.md](advanced.md), the pipeline internals


---
[← Accent forcing](accent_forcing.md) · [Home](../README.md) · [Code-switch →](codeswitch.md)
