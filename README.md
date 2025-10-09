# TugaPhone — Dialect-aware Portuguese Phonemizer

**TugaPhone** is a Python library that phonemizes arbitrary Portuguese text across major Lusophone dialects (pt-PT, pt-BR, pt-AO, pt-MZ, pt-TL). It uses a curated phonetic lexicon plus eSpeak fallback to deliver plausible phoneme transcriptions while preserving dialectal variation.

```
O comboio chegou à estação.
pt-PT → u kõbˈɔju ʃɨɡˈow ˌɐ iʃtɐsˈɐ̃w .
pt-BR → u kõbˈojʊ ʃɨɡˈow ˌɐ iʃtasˈɐ̃w .
pt-AO → u kõmbˈɔjʊ ʃɨɡˈow ˌɐ ɨʃtɐsˈɐ̃w .
pt-MZ → u kõbˈɔju ʃɨɡˈow ˌɐ eʃtɐsˈãw .
pt-TL → u kõmbˈɔjʊ ʃɨɡˈow ˌɐ ʃtəsˈə̃w .
```

---

## 🚀 Features

* Converts from ISO dialect codes like `pt-PT`, `pt-BR`, `pt-AO`, `pt-MZ`, `pt-TL` to internal region codes.
* Uses a **phonetic dictionary** ([Portuguese Phonetic Lexicon](](https://huggingface.co/datasets/TigreGotico/portuguese_phonetic_lexicon))) for known words.
* Takes postag into account when looking up words (via spacy)
* Falls back to **eSpeak** for unseen words.

---

## 📦 Installation

```bash
pip install tugaphone
# or if developing:
pip install -e .
```

Ensure you also have `pt_core_news_lg` model for SpaCy:

```bash
python -m spacy download pt_core_news_lg
```

the `espeak` binary needs to be available, installing it will depend on your distro
```bash
sudo apt-get install espeak-ng
```

---

## 🧰 Usage

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer()

sentences = [
    "O gato dorme.",
    "Tu falas português muito bem.",
    "O comboio chegou à estação.",
    "A menina comeu o pão todo.",
    "Vou pôr a manteiga no frigorífico."
]

for s in sentences:
    print(f"Sentence: {s}")
    for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
        phones = ph.phonemize_sentence(s, code)
        print(f"  {code} → {phones}")
    print("-----")

```

---

## 🔧 Implementation Notes

* The mapping from dialect code → region is deterministic. `pt-BR → rjx` (Rio de Janeiro) is chosen as the canonical Brazilian accent.
* If a word is in the dictionary for the relevant region, it’s used (with part-of-speech fallback).
* Otherwise, `eSpeak` is invoked with the dialect code (either `pt-PT` or `pt-BR`).
* The library normalizes input text (numbers, dates, time...) before tokenization.
* SpaCy is used only for POS tags (no parsing or NER).

---

## ⚠️ Limitations & Future Work

* Many words (especially names, foreign words, neologisms) will not be in the dictionary; they rely solely on eSpeak fallback.
* The phonetic dictionary is region-specific; for some dialects (pt-AO, pt-MZ, pt-TL), coverage may be sparser.
* Lexical variation (e.g. “trem” vs “comboio”) is **not** handled automatically; text is assumed orthographically consistent.
* Prosody, stress, intonation, and variation beyond segment-level phonemes are not modeled.
