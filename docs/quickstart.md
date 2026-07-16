# Quickstart — zero to hero

`tugaphone` turns Portuguese text into IPA phonemes, and it does it per dialect.
Give it a sentence and a Lusophone dialect code, get back a phoneme string with
stress markers and syllable boundaries.

```
Choveu muito ontem.
pt-PT → ʃu·ˈvew mˈũj·tu ˈõ·tɐ̃j
pt-BR → ʃo·ˈvew mwˈĩ·tʊ ˈõ·tẽj
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
print(ph.phonemize_sentence("O gato dorme.", "pt-PT"))   # ˈu gˈa·tu ˈdoɾ·mɨ
print(ph.phonemize_sentence("O gato dorme.", "pt-BR"))   # ˈu gˈa·tʊ ˈdoɾ·mɪ
```

The return value is a space-separated phoneme string: one token per word, with
`ˈ` marking primary stress and `·` marking syllable boundaries.

## 3. Pick a dialect

Five Lusophone dialects are supported through the `lang` argument:

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

Anything that is not one of the four non-European codes falls back to European
Portuguese.

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

On top of the five dialects, `tugaphone` ships experimental sub-regional accents
as `RegionalTransforms` presets. Pass one through `regional_dialect`:

```python
from tugaphone import TugaPhonemizer
from tugaphone.regional import PortoDialect

ph = TugaPhonemizer()
print(ph.phonemize_sentence("O Porto é uma cidade bonita.", regional_dialect=PortoDialect))
```

Each rule is annotated in the source with the phenomenon it models and a source
reference, but the presets are experimental approximations — hand-tuned against
project gold, not validated field transcriptions. See
[dialects.md](dialects.md#sub-regional-accent-presets) for the full list.

## 6. orthography2ipa plugin

`TugaphoneG2PPlugin` implements the `orthography2ipa` G2P plugin interface
(`transcribe`, `transcribe_word`, `language_codes`) — useful when a framework
loads phonemizers through that interface:

```python
from tugaphone.plugin import TugaphoneG2PPlugin

p = TugaphoneG2PPlugin(lang="pt-PT")
print(p.transcribe("o gato dorme"))   # ˈu gˈa·tu ˈdoɾ·mɨ
```

`SilabificadorSyllabifier` is a `SyllabifierPlugin` you can use directly.
`orthography2ipa[portuguese]` (a tugaphone dependency) already ships its own
`silabificador`-backed syllabifier, so tugaphone does not register a competing
entry point for it.

## Where next

- [api.md](api.md) — every public class, function and keyword argument with real signatures
- [dialects.md](dialects.md) — the five inventories and sub-regional accent presets
- [homographs.md](homographs.md) — meaning-based disambiguation
- [numbers.md](numbers.md) — number normalization and gender agreement
- [advanced.md](advanced.md) — regional accents, number normalization, the token tree
- [tokenizer.md](tokenizer.md) — the `Sentence → Word → Grapheme → Character` model and its features
