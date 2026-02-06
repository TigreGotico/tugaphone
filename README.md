# TugaPhone — Dialect-aware Portuguese Phonemizer

**TugaPhone** is a Python library that phonemizes arbitrary Portuguese text across major Lusophone dialects (pt-PT, pt-BR, pt-AO, pt-MZ, pt-TL). It uses a curated phonetic lexicon plus a rule-based fallback to deliver plausible phoneme transcriptions while preserving dialectal variation.

```
Choveu muito ontem à noite.
pt-PT-x-porto → ˈʃɔ·vew mˈũj·tu õ·ˈtẽ ˈa nˈuoj·tɨ 
pt-PT → ˈʃɔ·vew mˈũj·tu õ·ˈtẽ ˈa nˈoj·tɨ 
pt-BR → ˈʃɔ·vew mwˈĩ·tʊ õ·ˈtẽ ˈa nˈoj·tʃɪ 
pt-AO → ˈʃɔ·vew mˈũjn·tʊ õ·ˈtẽ ˈa nˈoj·tɨ 
pt-MZ → ˈʃɔ·vew mˈũj·tu õ·ˈtẽ ˈa nˈɔj·tɨ 
pt-TL → ˈʃɔ·vew mˈuj·tʊ õ·ˈtẽ ˈa nˈojtʰ 
```

---

## 🚀 Features

- **Multi-dialect support**: European Portuguese (pt-PT), Brazilian Portuguese (pt-BR), Angolan (pt-AO), Mozambican (pt-MZ), and Timorese (pt-TL)
- **Regional accent modeling**: Additional micro-dialects like Porto, Minho, Braga, Trás-os-Montes, and more
- **Hybrid approach**: Combines a curated phonetic lexicon ([Portuguese Phonetic Lexicon](https://huggingface.co/datasets/TigreGotico/portuguese_phonetic_lexicon)) with rule-based G2P fallback
- **Context-aware**: Takes part-of-speech tags into account for homograph disambiguation
- **Number normalization**: Automatically converts digits to their Portuguese spoken forms with proper gender agreement
- **Syllabification**: Rule-based syllable boundary detection (~99.6% accuracy on benchmark)
- **Stress detection**: Automatic stress placement following Portuguese phonological rules
- **IPA output**: Full International Phonetic Alphabet transcription with stress markers and syllable boundaries

---

## 📦 Installation

```bash
pip install tugaphone
```

---

## 🧰 Usage

### Basic Phonemization

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

### Regional Dialects

```python
from tugaphone import TugaPhonemizer
from tugaphone.regional import PortoDialect, MinhoDialect, BragaDialect

ph = TugaPhonemizer()

sentence = "O Porto é uma cidade bonita."

# Standard European Portuguese
print(f"pt-PT: {ph.phonemize_sentence(sentence, 'pt-PT')}")

# Porto accent (rising diphthongs, rhotic realization)
print(f"Porto: {ph.phonemize_sentence(sentence, regional_dialect=PortoDialect)}")

# Minho accent (vowel resistance, open vowels)
print(f"Minho: {ph.phonemize_sentence(sentence, regional_dialect=MinhoDialect)}")
```

### Number Normalization

```python
from tugaphone.number_utils import normalize_numbers

# Automatic gender agreement
print(normalize_numbers("vou comprar 1 casa"))    # uma casa
print(normalize_numbers("vou comprar 2 casas"))   # duas casas
print(normalize_numbers("vou adotar 1 cão"))      # um cão
print(normalize_numbers("vou adotar 2 cães"))     # dois cães

# Ordinals
print(normalize_numbers("1º lugar"))              # primeiro lugar
print(normalize_numbers("1ª vez"))                # primeira vez

# Large numbers with scale differences
print(normalize_numbers("897654356789098", "pt-PT"))  # long-scale (biliões)
print(normalize_numbers("897654356789098", "pt-BR"))  # short-scale (trilhões)
```

### Syllabification

```python
from tugaphone.syl import syllabify

words = ["casa", "Brasil", "extraordinário", "português"]

for word in words:
    syllables = syllabify(word)
    print(f"{word} → {'.'.join(syllables)}")

# Output:
# casa → ca.sa
# Brasil → bra.sil
# extraordinário → ex.tra.or.di.ná.rio
# português → por.tu.guês
```

### Advanced: Tokenization and Features

```python
from tugaphone.tokenizer import Sentence
from tugaphone.dialects import EuropeanPortuguese

sentence = Sentence("O cão comeu o pão.", dialect=EuropeanPortuguese())

print(f"IPA: {sentence.ipa}")

# Access word-level details
for word in sentence.words:
    print(f"\nWord: {word.surface}")
    print(f"  Syllables: {'.'.join(word.syllables)}")
    print(f"  Stress: syllable {word.stressed_syllable_idx}")
    print(f"  IPA: {word.ipa}")
    
    # Access grapheme-level details
    for grapheme in word.graphemes:
        if grapheme.is_diphthong:
            print(f"  Diphthong: {grapheme.surface} → {grapheme.ipa}")
```

---

## 📖 Documentation

### Supported Dialects

| Dialect Code | Region | Characteristics |
|-------------|--------|-----------------|
| `pt-PT` | European Portuguese (Lisbon) | Heavy vowel reduction, fricative palatalization, uvular /r/ |
| `pt-BR` | Brazilian Portuguese (Rio) | Less vowel reduction, t/d palatalization, l-vocalization |
| `pt-AO` | Angolan Portuguese (Luanda) | Moderate vowel reduction, alveolar trill /r/, Bantu substrate |
| `pt-MZ` | Mozambican Portuguese (Maputo) | Similar to European with regional variation, Bantu influence |
| `pt-TL` | Timorese Portuguese (Dili) | Conservative pronunciation, Tetum substrate influence |

### Regional Accents (Experimental)

TugaPhone includes experimental support for sub-regional Portuguese accents:

- **PortoDialect**: Rising diphthongs (o → uo), rhotic realization
- **MinhoDialect**: Reduced vowel centralization, open vowel preference
- **BragaDialect**: Palatal epenthesis (abelha → abeilha)
- **TrasMontanoDialect**: Palatal affrication, s-voicing, final nasal denasalization
- **FafeDialect**: Nasal diphthongization (gente → geinte)

**Note**: These are based on documented phonological features but should be considered approximate. Real-world variation is more complex.

### Part-of-Speech Tagging

TugaPhone uses POS tags to disambiguate homographs:

```python
from tugaphone import TugaPhonemizer

ph = TugaPhonemizer(postag_engine="spacy")  # or "brill", "auto"

# "para" has different pronunciations as preposition vs. verb
print(ph.phonemize_sentence("Vou para casa."))      # preposition
print(ph.phonemize_sentence("Ele para o carro."))   # verb
```

Supported engines:
- `spacy`: Requires `spacy` and Portuguese model (most accurate)
- `brill`: Requires `brill-postaggers` (lighter, faster)
- `lexicon`: Uses built-in lexicon lookup (limited coverage)
- `auto`: Falls back through available engines
- `dummy`: Simple rule-based fallback (no dependencies)

---

## 🏗️ Architecture

TugaPhone uses a hierarchical tokenization model:

```
Sentence → Words → Graphemes → Characters
```

Each level applies context-sensitive phonological rules:

1. **Character level**: Vowel quality, consonant allophones
2. **Grapheme level**: Digraphs (ch, nh), diphthongs (ai, ou)
3. **Word level**: Stress assignment, syllabification
4. **Sentence level**: Prosodic boundaries (future: liaison, phrasal stress)

The phonemization process:

1. Normalize text (numbers → words)
2. POS tagging (for homograph disambiguation)
3. Lexicon lookup (for known words)
4. Rule-based G2P fallback (for unknown words)
5. Dialect-specific transformations (regional accents)

---

## ⚠️ Limitations & Future Work

### Current Limitations

- **Lexicon coverage**: Many words (especially names, foreign words, neologisms) rely solely on rule-based fallback
- **Sparse coverage**: African and Timorese dialects have less lexicon data than European/Brazilian
- **Lexical variation**: Dialect-specific vocabulary (e.g., "trem" vs "comboio") is not handled; text is assumed orthographically consistent
- **Regional accents**: Sub-regional dialects are experimental and approximate
- **Prosody**: Sentence-level features (liaison, phrasal stress, intonation) are simplified
- **Homograph disambiguation**: Limited to POS-based rules; doesn't handle semantic context

---

## 🤝 Contributing

Contributions are welcome! Areas where help is especially needed:

- **Lexicon expansion**: Especially for pt-AO, pt-MZ, pt-TL
- **Regional accent validation**: Native speaker verification of dialectal features
- **Test cases**: Edge cases, challenging words, dialectal examples
- **Documentation**: Usage examples, linguistic explanations

---

## 📄 License

This project is licensed under the Apache License 2.0. See LICENSE for details.
