# Homograph disambiguation

Portuguese has two overlapping classes of heterophonic homographs (same spelling,
different pronunciation):

1. **Meaning-based** — the vowel quality shifts depending on which sense is active.
   Example: *sede* as thirst /ˈsedɨ/ vs as headquarters /ˈsɛdɨ/.
2. **POS-based** — the vowel quality shifts between noun and verb conjugation.
   Example: *gosto* noun /ˈgoʃtu/ vs verb /ˈgɔʃtu/.

tugaphone handles both in a single pipeline.

---

## Meaning-based: bifonia

When [bifonia](https://github.com/TigreGotico/bifonia) is installed (it is a
required dependency), `TugaPhonemizer.phonemize_sentence` calls
`bifonia.add_extra_diacritics` on the input text before tagging. bifonia
performs context-sensitive sense disambiguation and inserts the open/closed
vowel diacritic directly into the orthography, so the grapheme rules that
follow produce the correct vowel quality without any special casing.

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()

# sede thirst (closed /e/)
print(ph.phonemize_sentence("Tenho muita sede."))
# ˈte·ɲu ˈmũj·tɐ ˈse·dɨ ˈ···

# sede headquarters (open /ɛ/)
print(ph.phonemize_sentence("A sede da empresa fica em Lisboa."))
# ˈɐ ˈsɛ·dɨ ˈdɐ ẽ·pɾˈe·zɐ ˈfi·kɐ ˈẽ liʒ·bˈo·ɐ ˈ···
```

If bifonia is not importable, the pipeline continues without it and falls back
to the POS-based table.

---

## POS-based: HOMOGRAPHS table

The `DialectInventory` dataclass carries a `HOMOGRAPHS` dict mapping each
ambiguous word to a `{POS_tag: IPA}` mapping. After POS tagging, each token is
looked up in this table; if the tag matches an entry, that IPA is used
directly.

| Word | Noun IPA | Verb IPA | Disambiguation |
|------|----------|----------|----------------|
| gosto | ˈgoʃtu | ˈgɔʃtu | noun "taste" vs verb "I like" |
| choro | ˈʃoɾu | ˈʃɔɾu | noun "crying" vs verb "I cry" |
| coro | ˈkoɾu | ˈkɔɾu | noun "choir" vs verb "I blush" |
| jogo | ˈʒoɡu | ˈʒɔɡu | noun "game" vs verb "I play" |
| olho | ˈoʎu | ˈɔʎu | noun "eye" vs verb "I watch" |
| peso | ˈpezu | ˈpɛzu | noun "weight" vs verb "I weigh" |
| porto | ˈpoɾtu | ˈpɔɾtu | noun "port" vs verb "I carry" |
| sede | ˈsɛdɨ | ˈsedɨ | headquarters (NOUN key) vs thirst (VERB key) — two noun senses sharing the noun/verb slots |
| colher | kuˈʎɛɾ | kuˈʎeɾ | noun "spoon" vs verb "to pick" |

The full table is defined in `DialectInventory.HOMOGRAPHS` in
`tugaphone/dialects.py`.

### Example

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()

print(ph.phonemize_sentence("Eu gosto de música."))   # verb → ˈgɔʃ·tu
# ˈew ˈɡɔʃ·tu ˈdɨ mˈu·zi·kɐ ˈ···

print(ph.phonemize_sentence("Tenho bom gosto."))       # noun → ˈgoʃ·tu
# ˈte·ɲu bˈõ ˈɡoʃ·tu ˈ···
```

---

## POS tagger engines

The accuracy of POS-based disambiguation depends on the tagger. Pass
`postag_engine` to `TugaPhonemizer.__init__`:

| Engine | Dependency | Notes |
|--------|-----------|-------|
| `auto` | — | Falls through whatever is installed. Default. |
| `spacy` | `spacy` + `pt_core_news_lg` | Most accurate. |
| `brill` | `brill-postaggers` (via `tugatagger[brill]`) | Lighter; installed by default. |
| `lexicon` | none | Built-in lookup, limited coverage. |
| `dummy` | none | Rule-based fallback; no optional dependencies. |

```python
ph_lite = TugaPhonemizer(postag_engine="brill")
ph_dummy = TugaPhonemizer(postag_engine="dummy")
```

---

## Where next

- [dialects.md](dialects.md) — the five inventories and sub-regional accents
- [api.md](api.md) — `TugaPhonemizer`, `DialectInventory.HOMOGRAPHS`
- [advanced.md](advanced.md) — POS engines, regional accents
