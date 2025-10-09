import os
from typing import Dict, List, Tuple

import spacy
from tugaphone.espeak import EspeakPhonemizer
from tugaphone.util import normalize


class TugaPhonemizer:
    """
    TugaPhonemizer applies dialect-aware Portuguese phonemization.

    Supports:
        - pt-PT (Portugal)
        - pt-BR (Brazil)
        - pt-AO (Angola)
        - pt-MZ (Mozambique)
        - pt-TL (Timor-Leste)
    """
    _DIALECT_REGIONS = {
        "pt-PT": "lbx",
        "pt-BR": "rjx",
        "pt-AO": "lda",
        "pt-MZ": "mpx",
        "pt-TL": "dli",
    }

    def __init__(self, dictionary_path: str = None, spacy_model: str = "pt_core_news_lg"):
        self._nlp = spacy.load(spacy_model, disable=["ner", "parser"])

        self._normalize = normalize
        self._espeak = EspeakPhonemizer()

        dictionary_path = dictionary_path or os.path.join(
            os.path.dirname(__file__), "regional_dict.csv"
        )
        self.lang_map, self.word_list = self._load_lang_map(dictionary_path)

    def _load_lang_map(self, path: str) -> Tuple[Dict[str, Dict[str, Dict[str, str]]], List[str]]:
        """Load region/language phoneme mappings from a CSV file.

        Expected CSV columns:
            _, word, pos, _, phonemes, _, region
        """
        lang_map: Dict[str, Dict[str, Dict[str, str]]] = {r: {} for r in self._DIALECT_REGIONS.values()}
        words: List[str] = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f.read().splitlines()[1:]:  # skip header
                try:
                    _, word, pos, _, phonemes, _, region = line.split(",", 6)
                    phonemes = phonemes.replace("|", "").strip()
                    word = word.strip().lower()
                    region = region.strip()

                    if region not in lang_map:
                        continue

                    lang_map[region].setdefault(word, {})[pos] = phonemes
                    words.append(word)
                except ValueError:
                    continue

        return lang_map, sorted(set(words))

    def _lang_to_region(self, lang: str) -> str:
        """Convert ISO dialect code (pt-PT, pt-BR, etc.) to dataset region code."""
        try:
            return self._DIALECT_REGIONS[lang]
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {lang}") from e

    def get_phones(self, word: str, lang: str, pos: str) -> str:
        """Get phonemes for a single word using the regional dictionary or eSpeak fallback."""
        region = self._lang_to_region(lang)
        word = word.lower().strip()

        if region in self.lang_map and word in self.lang_map[region]:
            for fallback in [pos, "NOUN", "PRON", "ADP", "DET", "ADJ", "VERB", "ADV", "SCONJ"]:
                phones = self.lang_map[region][word].get(fallback)
                if phones:
                    # print(f"DEBUG - word={word}, region={region}, pos={fallback}, phonemes={phones}")
                    return phones

        # Fallback: eSpeak phonemization
        if word == "à":
            return "ˌɐ" # HACK: espeak expands and reads "à grave" when spelling single letter with accent

        espeak_lang = "pt-PT" if lang != "pt-BR" else "pt-BR"
        # print(f"DEBUG - word={word}, espeak-lang={espeak_lang}")
        return self._espeak.phonemize(word, espeak_lang)

    def phonemize_sentence(self, sentence: str, lang: str = "pt-PT") -> str:
        """Phonemize a single sentence in the specified dialect."""
        sentence = sentence.lower().strip()
        sentence_norm = normalize(sentence, "pt")
        doc = self._nlp(sentence_norm)
        phones = " ".join(
            self.get_phones(tok.text, lang, tok.pos_) if tok.pos_ != "PUNCT" else tok.text
            for tok in doc
        )
        return phones


if __name__ == "__main__":
    ph = TugaPhonemizer()

    sentences = [
        "O gato dorme.",
        "Tu falas português muito bem.",
        "O comboio chegou à estação.",
        "A menina comeu o pão todo.",
        "Vou pôr a manteiga no frigorífico.",
        "Ele está a trabalhar no escritório.",
        "Choveu muito ontem à noite.",
        "A rapariga comprou um telemóvel novo.",
        "Vamos tomar um pequeno-almoço.",
        "O carro ficou sem gasolina."
    ]

    for s in sentences:
        print(s)
        for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
            print(f"{code} → {ph.phonemize_sentence(s, code)}")
        print("######")
