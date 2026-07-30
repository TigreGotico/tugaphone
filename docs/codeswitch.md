# Code-switch handling

Real Portuguese text is bilingual, and in the modern register trilingual. The
Brazilian tech/media register embeds **English** heavily (`download`, `app`,
`site`, `feedback`, `streaming`, product and band names), European and African
writing embeds English loans too, and on the Uruguayan border (`pt-UY`,
*portunhol*) Portuguese embeds **Spanish**, quoted French fragments turn up
throughout. tugaphone can detect that material at the word level, transcribe it
through the orthography2ipa `es-ES`/`fr-FR`/`en-US` lattice, and **nativize** the
result onto the target Portuguese lect's phoneme inventory.

## Opt-in: the `contact` parameter

Code-switching is **off by default**. Portuguese, Spanish and French share the
Romance character-shape so tightly that unattended statistical routing misroutes
some common native words (`noite`, `carne`), so the default reproduces the
engine-only output exactly and code-switching is opt-in.

| value | behaviour |
|-------|-----------|
| `"none"` (default) | disable switching, transcribe everything as Portuguese, output unchanged by this feature |
| `"auto"` | detect contact words, classify each among es/fr/en, route unclassified words to the dialect's side |
| `"es"` / `"fr"` / `"en"` | force that contact lattice for detected words |

```python
ph.phonemize_sentence("fiz o download do app", "pt-BR")                  # none: ˈfis u dõˈload du ˈapp
ph.phonemize_sentence("fiz o download do app", "pt-BR", contact="auto")  # en:   ˈfis u dawnlowd du ap
ph.phonemize_sentence("comprei cerveza", "pt-UY", contact="auto")        # es side on the border
```

The dialect's default side comes from `tugaphone.registry.default_contact`:
English for every lect except the Uruguayan border lect `pt-UY`, which defaults
to Spanish.

## Total nativization

Following arbtok's principle, *never drop a segment, always project it*, every
foreign phone maps to its nearest Portuguese phone rather than being deleted.
Because Portuguese already has `/v z ʃ ʒ ʁ/`, the palatals `/ɲ ʎ/`, the glides
`/w j/` and a full set of **nasal vowels**, the projections are far gentler than
the Basque frontend's: most contact phones are already Portuguese phones and pass
through unchanged. Only the genuinely non-Portuguese segments move.

Where the phonological-adaptation literature on Portuguese anglicisms and
borrowings documents a substitution it is followed, where it is silent the
mapping is stated as a **convention**. Stress and length marks are stripped, the
nasal tilde is kept, so a French nasal vowel projects onto a Portuguese nasal
vowel rather than being denasalised.

### English → Portuguese

| English | → Portuguese | rationale / convention |
|---------|--------------|------------------------|
| θ | t | TH-stopping, Portuguese lacks `/θ/`, adapted as a stop |
| ð | d | voiced TH-stopping |
| ɹ ɻ | ɾ | English approximant rhotic → Portuguese tap |
| ŋ | n | `/ŋ/` is not phonemic in Portuguese |
| ɫ (dark l) | l | Portuguese has a single `/l/` |
| ʍ | w | `/w/` is a native Portuguese glide, kept |
| æ ʌ | a | low/central → `/a/` |
| ɒ | ɔ | → `/ɔ/` (Portuguese has open-o) |
| ɪ | i · ʊ → u | five-/seven-vowel collapse |
| ɜ ɝ ə | ɛ · ɐ | reduced/rhotacised central vowels |
| eɪ aɪ ɔɪ | ej aj ɔj | diphthongs preserved on Portuguese vowels+glide |
| aʊ oʊ əʊ | aw ow ow | |
| v z ʃ ʒ dʒ tʃ j w | *(kept)* | already Portuguese phones, no substitution |

### Spanish/French (Romance) → Portuguese

| source | → Portuguese | rationale / convention |
|--------|--------------|------------------------|
| θ | s | Castilian interdental → seseo `/s/` |
| β ð ɣ | b d ɡ | Spanish approximants → their stops |
| ʝ / ɟʝ | ʒ / dʒ | Spanish yeísmo → Portuguese `/ʒ dʒ/` (convention) |
| x | ʁ | Spanish jota / velar fricative → Portuguese uvular |
| r ʀ | ʁ | trills → Portuguese `/ʁ/` (the tap `/ɾ/` is kept) |
| y | i | French `/y/` → `/i/` |
| ø œ | e ɛ | French rounded front vowels |
| ɑ̃ ɛ̃ ɔ̃ œ̃ | ɐ̃ ẽ õ ẽ | French nasal vowels → **Portuguese nasal vowels** |
| ʁ ʃ ʒ z v | *(kept)* | already Portuguese phones |

## The statistical detector (used by `auto`/`es`/`fr`/`en`)

The orthographic heuristic below can only flag a word that carries a non-native
letter (`k w y ñ`, a French accent) or a known function word, it misses the
loans and internationalisms spelled with Portuguese-legal letters (`site`,
`feedback`, `general`) and cannot tell Spanish embedding from French. tugaphone
therefore ships a small statistical detector: four **character-level Markov
models**, one each for Portuguese, Spanish, French and English, trained on
Wikipedia and stored gzip-compressed under `tugaphone/data/langdetect/` (about
35 to 43 KB each, about 158 KB for all four). A word is scored under all four models and
the lowest-perplexity model wins. The detector is scored by
[`markovonnx`](https://github.com/TigreGotico/markovonnx), it is an optional
dependency (`pip install tugaphone[langdetect]`). Without it, the code falls back
to the orthographic heuristic, the routing behind `contact="auto"`/`"es"`/`"fr"`/`"en"`
is unchanged, so there is no API break.

The Spanish, French and English models are the same shape and Wikipedia pipeline
as the ones the Basque frontend (euskaphone) ships, so the family could share one
`markovonnx` model set, tugaphone retrains its own for a self-contained bundle
with Portuguese as the fourth in-language model. `scripts/train_langdetect.py`
reproduces them.

### Threshold policy: in-language default (null beats wrong)

Portuguese is the surrounding language, so it is the default. A word is routed
**out** of Portuguese only when a foreign model beats the Portuguese model by at
least a fixed margin (`DEFAULT_MARGIN = 0.5` nats-per-character of
log-perplexity). This margin is set well above the Basque frontend's `0.25`
because the Romance overlap is far tighter than Basque-vs-Romance, a small
margin misroutes common native words. Below the margin the word stays `pt`. Two
extra guards keep the default honest:

* a **guard list of high-frequency Portuguese grammar words** (`de`, `que`, `com`,
  `não`, `olá`, …) is always kept Portuguese. Encyclopedic training text
  underrepresents conversational grammar, and these shared-Romance function words
  are exactly the ones a Spanish or French model also fits.
* an empty or all-punctuation token is Portuguese by default.

A `default_side` tie-break routes a genuinely ambiguous embed (two foreign models
within a margin of each other) to the dialect's expected contact language.

```python
from tugaphone.langdetect import get_detector
d = get_detector()                 # None if markovonnx/models unavailable
d.detect("download")               # ('en', {...})  -> routed and nativized
d.detect("que")                    # ('pt', {})     -> native grammar word, kept
d.detect("radio")                  # ('pt', {...})  -> inside the margin band
d.is_contact("ayuntamiento")       # True
```

### How the models measure up

The models are character n-gram chains of **order 2** (evaluated against order 3, order 2 both classifies better on this word-level task and is smaller). Training
text is one Wikipedia shard per language (~3 M characters each), normalized to
NFC, lower-cased and stripped to alphabetic words wrapped with word-boundary
sentinels.

On a held-out set of 800 words per language (Wikipedia articles disjoint from
training, each word absent from that language's training vocabulary), the
Portuguese-vs-contact routing decision compares as follows
(`scripts/eval_langdetect.py`):

| detector | precision | recall | F1 | accuracy |
|----------|-----------|--------|----|----------|
| char-Markov (order 2, margin 0.4) | 0.907 | 0.590 | 0.715 | 0.647 |
| char-Markov (order 2, margin 0.5, **default**) | 0.915 | 0.517 | 0.661 | 0.602 |
| char-Markov (order 2, margin 0.6) | 0.916 | 0.452 | 0.605 | 0.558 |
| orthographic heuristic | 0.960 | 0.247 | 0.393 | 0.427 |

The Markov detector roughly **doubles** the heuristic's recall and F1 (0.52 vs
0.25 recall, 0.66 vs 0.39 F1 at the default margin), it catches the
Portuguese-legal-letter loans the heuristic is blind to, at a modest precision
cost (0.92 vs 0.96). This held-out set is deliberately harsh: the Spanish/French/
Portuguese Romance overlap caps achievable recall, since many contact words
genuinely share Portuguese's character statistics. Where a contact word does slip
through as Portuguese, **total nativization** would have projected it onto the
same inventory anyway, so the failure is contained.


---
[← Homographs](homographs.md) · [Home](../README.md) · [Numbers →](numbers.md)
