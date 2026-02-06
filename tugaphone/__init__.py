import os
from typing import Optional

from tugaphone.lexicon import TugaLexicon
from tugaphone.pos import TugaTagger
from tugaphone.tokenizer import Sentence as Tokenizer, EuropeanPortuguese, BrazilianPortuguese


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

    def __init__(self, dictionary_path: str = None,
                 postag_engine="auto",
                 postag_model="pt_core_news_lg"):

        self.dictionary_path = dictionary_path or os.path.join(
            os.path.dirname(__file__), "regional_dict.csv"
        )
        self.lexicon = TugaLexicon(self.dictionary_path)
        self.postag = TugaTagger(postag_engine, postag_model)

    def _lang_to_region(self, lang: str) -> str:
        """Convert ISO dialect code (pt-PT, pt-BR, etc.) to dataset region code."""
        try:
            return self._DIALECT_REGIONS[lang]
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {lang}") from e

    def _get_phones(self, word: str, lang: str, pos: str,
                    region: Optional[str] = None) -> str:
        """Get phonemes for a single word using the regional dictionary or eSpeak fallback."""
        region = region or self._lang_to_region(lang)
        word = word.lower().strip()

        for fallback in [pos, "NOUN", "PRON", "ADP", "DET", "ADJ", "VERB", "ADV", "SCONJ"]:
            gold_pho = self.lexicon.get_phonemes(word, fallback, region)
            if gold_pho:
                # print(f"DEBUG - word={word}, region={region}, pos={fallback}, phonemes={phones}")
                return gold_pho

        # Fallback
        dialect = EuropeanPortuguese() if lang != "pt-BR" else BrazilianPortuguese()
        return Tokenizer(surface=word, dialect=dialect).ipa

    def phonemize_sentence(self, sentence: str, lang: str = "pt-PT") -> str:
        """Phonemize a single sentence in the specified dialect."""
        sentence_norm = sentence.lower().strip()
        phonemized = [self._get_phones(word=tok, lang=lang, pos=pos)
                      if pos != "PUNCT" else tok
                      for tok, pos in self.postag.tag(sentence_norm)]

        return " ".join(phonemized)


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
