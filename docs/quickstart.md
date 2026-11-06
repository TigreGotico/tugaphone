# Quickstart: zero to hero

`tugaphone` turns Portuguese text into IPA phonemes, and it does it per dialect.
Give it a sentence and a Lusophone dialect code, get back a phoneme string with
stress markers.

```
O gato dorme.
pt-PT → o ˈɡatu ˈdɔɾmɨ
pt-BR → u ˈɡatu ˈdoɾmi
```

## 1. Install

```bash
pip install tugaphone            # from PyPI
pip install -e .                 # from a source checkout
```

Runtime dependencies (`ovos-number-parser`, `silabificador`, `tugalex`,
`bifonia`, `orthography2ipa`, `o2i-lexicons`) install automatically. The `pt-PT`
and `pt-BR` lexicons ship inside [`o2i-lexicons`](https://github.com/TigreGotico/o2i-lexicons),
so a phonemization call needs no network. See
[advanced.md](advanced.md#the-lexicon-boundary).

## 2. The one thing to understand

`TugaPhonemizer` is the entry point. Construct it, then call
`phonemize_sentence(text, lang)` as many times as you like. The constructor does
no work: the first call for a lect builds that lect's engine, and the calls
after it reuse the engine. The `lang` argument is an IETF dialect tag and it
changes the phonology, not just the spelling:

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
print(ph.phonemize_sentence("O gato dorme.", "pt-PT"))   # o ˈɡatu ˈdɔɾmɨ
print(ph.phonemize_sentence("O gato dorme.", "pt-BR"))   # u ˈɡatu ˈdoɾmi
```

The return value is a space-separated phoneme string: one token per word, with
`ˈ` marking primary stress. Selecting `lang` selects an
[orthography2ipa](https://github.com/TigreGotico/orthography2ipa) lect spec whose
grapheme table, allophone rules and cross-word sandhi produce that dialect's
phonology, so `lang` changes the sounds, not just the spelling. See
[architecture.md](architecture.md).

## 3. Pick a dialect

Every Portuguese-family lect is reachable by its BCP-47 code, the five national
standards plus the European, Brazilian, African, Asian and other varieties.
`list_dialects()` returns them all.

```python
ph = TugaPhonemizer()
for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
    print(code, "→", ph.phonemize_sentence("A menina comeu o pão todo.", code))
```

| Code | Region |
|------|--------|
| `pt-PT` | European Portuguese (Lisbon) |
| `pt-BR` | Brazilian Portuguese (Rio) |
| `pt-AO` | Angolan Portuguese (Luanda) |
| `pt-MZ` | Mozambican Portuguese (Maputo) |
| `pt-TL` | Timorese Portuguese (Dili) |

Sub-regional varieties use private-use subtags (`pt-PT-x-porto`,
`pt-BR-x-sp`, …). An unrecognised code falls back to European Portuguese. The
full list and the legacy aliases are in [dialects.md](dialects.md).

## 4. First real call

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
sentence = "Vou pôr a manteiga no frigorífico."
print(ph.phonemize_sentence(sentence, "pt-PT"))
# ˈvo ˈpoɾ ɐ mɐ̃ˈtɐjɡɐ nu fɾiɡuˈɾifiku
```

Digits need no preparation. `phonemize_sentence` spells them out with gender
agreement before it transcribes the sentence. The `normalize_numbers` helper
exposes that step on its own:

```python
from tugaphone.number_utils import normalize_numbers

print(ph.phonemize_sentence("comprei 2 casas", "pt-PT"))   # kõˈpɾej ˈduɐʃ ˈkazɐʃ
normalize_numbers("comprei 2 casas")                       # 'comprei duas casas'
```

## 5. Sub-regional accents

Sub-regional accents are lects like any other, select them by their BCP-47
code. The accent's phonology is encoded in the orthography2ipa lect spec, so no
extra argument is needed:

```python
ph = TugaPhonemizer()
print(ph.phonemize_sentence("O vinho é muito bom.", "pt-PT-x-porto"))
# o ˈbiɲu ˈjɛ ˈmujtu ˈbõ   (betacism: vinho → binho, rising diphthong: é → jɛ)
```

See [dialects.md](dialects.md) for the full list of European and Brazilian
sub-regional codes and the legacy aliases.

## 6. Engine object

`TugaphoneG2PPlugin` wraps the phonemizer in an engine object with
`transcribe`, `transcribe_word` and `language_codes`, for a framework that
drives several G2P engines through these members:

```python
from tugaphone.plugin import TugaphoneG2PPlugin

p = TugaphoneG2PPlugin(lang="pt-PT")
print(p.transcribe("o gato dorme"))   # o ˈɡatu ˈdɔɾmɨ
```

`SilabificadorSyllabifier` is a `SyllabifierPlugin` you can use directly. The
phonemization path does not use it, and tugaphone does not register it as an
entry point.

## Where next

- [architecture.md](architecture.md), the lattice core and the caller-owned layers
- [api.md](api.md), every public class, function and keyword argument with real signatures
- [dialects.md](dialects.md), the lect codes, aliases and lexicon overlay
- [homographs.md](homographs.md), meaning-based disambiguation
- [numbers.md](numbers.md), number normalization and gender agreement
- [advanced.md](advanced.md), the pipeline internals and integration
- [tokenizer.md](tokenizer.md), the `Sentence → Word → Grapheme → Character` feature model


---
[Home](../README.md) · [Architecture →](architecture.md)
