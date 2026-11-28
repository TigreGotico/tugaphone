# Homograph disambiguation
<!-- agent-hint
covers: how bifonia marks the sense of a heterophonic homograph before transcription
source: tugaphone/lattice_core.py, bifonia.add_extra_diacritics
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py docs/homographs.md
see: architecture.md, codeswitch.md
-->

Portuguese has heterophonic homographs (same spelling, different pronunciation)
where the vowel quality shifts depending on which sense is active:

- *sede* as thirst /ˈsedɨ/ vs as headquarters /ˈsɛdɨ/,
- *forma* as mould /ˈfoɾmɐ/ vs as shape /ˈfɔɾmɐ/,
- *gosto* as "I like" /ˈɡɔʃtu/ vs as "taste" /ˈɡoʃtu/.

## Meaning-based: bifonia

[bifonia](https://github.com/TigreGotico/bifonia) is a required dependency, so
`TugaPhonemizer.phonemize_sentence` always calls
`bifonia.add_extra_diacritics` on Portuguese input, in the pipeline's `mark`
step, before the lattice transcribes it. bifonia
performs context-sensitive sense disambiguation and inserts the open/closed
vowel diacritic directly into the orthography, so the lattice produces the
correct vowel quality without any special casing.

bifonia receives the lect code. Every `pt-BR` and `pt-UY` lect takes the
Brazilian marks: Brazilian Portuguese keeps the stressed vowel closed in every
sense of *soma*, *aceno*, *abono*, *domo*, *empeno* and *desempeno*. Every other
lect takes the European marks. bifonia's `data/lect_overrides.csv` holds these
rows with their sources.

bifonia also marks a short list of words that need no context, from its
`data/context_free_marks.csv`: a mark that an older spelling norm wrote and that
the lect says, such as *pêra* for `pt-PT` and *assembléia* for `pt-BR`. Each
row names the `pt-PT` and `pt-BR` lects that take its mark, and every other lect
takes none.

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()

# sede thirst (closed /e/)
print(ph.phonemize_sentence("Tenho muita sede."))
# ˈteɲu ˈmũj̃tɐ ˈsedɨ

# sede headquarters (open /ɛ/)
print(ph.phonemize_sentence("A sede da empresa fica em Lisboa."))
# ɐ ˈsɛdɨ dɐ ẽˈpɾezɐ ˈfikɐ ɐ̃j̃ liʒˈboɐ

# gosto verb (open /ɔ/)
print(ph.phonemize_sentence("Eu gosto de música."))
# ˈew ˈɡɔʃtu dɨ ˈmuzikɐ

# gosto noun (closed /o/)
print(ph.phonemize_sentence("Tenho bom gosto."))
# ˈteɲu ˈbõ ˈɡoʃtu
```

---

## Where next

- [dialects.md](dialects.md), the lect codes and sub-regional accents
- [api.md](api.md), `TugaPhonemizer`
- [advanced.md](advanced.md), the pipeline internals

---
[← Accent forcing](accent_forcing.md) · [Home](index.md) · [Code-switch →](codeswitch.md)
