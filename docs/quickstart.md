# Quickstart: zero to hero

`tugaphone` turns Portuguese text into IPA phonemes, and it does it per dialect.
Give it a sentence and a Lusophone dialect code, get back a phoneme string with
stress markers.

```
O gato dorme.
pt-PT → ˈo ˈgatu ˈdɔɾmɨ
pt-BR → ˈu ˈgatʊ ˈdoɾmi
```

## 1. Install

```bash
pip install tugaphone            # from PyPI
pip install -e .                 # from a source checkout
```

Runtime dependencies (`unicode-rbnf`, `silabificador`, `tugalex`,
`bifonia`, `orthography2ipa`) install automatically. The phonetic lexicon ships through
[`tugalex`](https://github.com/TigreGotico/tugalex), which wraps the HuggingFace
dataset `TigreGotico/portuguese_phonetic_lexicon`. It is lazy-loaded on first use
and warmed during `TugaPhonemizer()` construction.

## 2. The one thing to understand

`TugaPhonemizer` is the entry point. You construct it once (it loads the
lexicon), then call `phonemize_sentence(text, lang)` as many times as you like.
The `lang` argument is an IETF dialect tag and it changes the phonology, not just
the spelling:

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()
print(ph.phonemize_sentence("O gato dorme.", "pt-PT"))   # ˈo ˈgatu ˈdɔɾmɨ
print(ph.phonemize_sentence("O gato dorme.", "pt-BR"))   # ˈu ˈgatʊ ˈdoɾmi
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
`list_dialects()` returns all 41.

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
```

Digits in your text are best spelled out first, with gender agreement, using the
`normalize_numbers` helper:

```python
from tugaphone.number_utils import normalize_numbers

text = normalize_numbers("comprei 2 casas")   # 'comprei duas casas'
print(ph.phonemize_sentence(text, "pt-PT"))
```

## 5. Sub-regional accents

Sub-regional accents are lects like any other, select them by their BCP-47
code. The accent's phonology is encoded in the orthography2ipa lect spec, so no
extra argument is needed:

```python
ph = TugaPhonemizer()
print(ph.phonemize_sentence("O vinho é muito bom.", "pt-PT-x-porto"))
# ˈwo ˈbiɲu ˈjɛ ˈmujtu ˈbõ   (betacism: vinho → binho, rising diphthongs)
```

See [dialects.md](dialects.md) for the full list of European and Brazilian
sub-regional codes and the legacy aliases.

## 6. orthography2ipa plugin

`TugaphoneG2PPlugin` implements the `orthography2ipa` G2P plugin interface
(`transcribe`, `transcribe_word`, `language_codes`), useful when a framework
loads phonemizers through that interface:

```python
from tugaphone.plugin import TugaphoneG2PPlugin

p = TugaphoneG2PPlugin(lang="pt-PT")
print(p.transcribe("o gato dorme"))   # ˈo ˈgatu ˈdɔɾmɨ
```

`SilabificadorSyllabifier` is a `SyllabifierPlugin` you can use directly.
`orthography2ipa[portuguese]` (a tugaphone dependency) already ships its own
`silabificador`-backed syllabifier, so tugaphone does not register a competing
entry point for it.

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
