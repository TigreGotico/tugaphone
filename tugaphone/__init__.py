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

        """
        Initialize the TugaPhonemizer by loading the regional lexicon and configuring the part-of-speech tagger.

        Parameters:
            dictionary_path (str): Path to a CSV lexicon file; if omitted, defaults to the bundled "regional_dict.csv" located next to this module.
            postag_engine (str): Tagging engine selection passed to TugaTagger (e.g., "auto" to let the tagger choose the best available engine).
            postag_model (str): Model name or identifier used by the POS tagger (for engines that accept a model parameter).
        """
        self.dictionary_path = dictionary_path or os.path.join(
            os.path.dirname(__file__), "regional_dict.csv"
        )
        self.lexicon = TugaLexicon(self.dictionary_path)
        self.postag = TugaTagger(postag_engine, postag_model)

    def _lang_to_region(self, lang: str) -> str:
        """
        Map an ISO Portuguese dialect code to the internal region code used by the lexicon.

        Parameters:
            lang (str): ISO dialect code (e.g., "pt-PT", "pt-BR").

        Returns:
            str: The corresponding internal region code.

        Raises:
            ValueError: If `lang` is not a supported dialect.
        """
        try:
            return self._DIALECT_REGIONS[lang]
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {lang}") from e

    def _get_phones(self, word: str, lang: str, pos: str,
                    region: Optional[str] = None) -> str:
        """
        Retrieve the phonemic transcription for a single word in a specified Portuguese dialect.

        Attempts to find a lexicon entry for the lowercased word using the given part-of-speech tag and a predefined sequence of POS fallbacks; if no lexicon entry is found, produces a dialect-appropriate IPA transcription via the tokenizer (European Portuguese for non-pt-BR dialects, Brazilian Portuguese for pt-BR).

        Parameters:
            word (str): The word to phonemize.
            lang (str): ISO dialect code (e.g., "pt-PT", "pt-BR") used to determine the default region when `region` is not provided.
            pos (str): The part-of-speech tag to prefer when looking up lexicon entries.
            region (Optional[str]): Optional explicit region code to use for lexicon lookup; when omitted, the region is derived from `lang`.

        Returns:
            str: A phoneme string from the regional lexicon when available, otherwise an IPA transcription produced by the tokenizer.
        """
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
        """
        Phonemizes a sentence for the given Portuguese dialect.

        Parameters:
            sentence (str): Input sentence to phonemize.
            lang (str): ISO dialect code to target (e.g., "pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL").

        Returns:
            phonemized (str): Space-separated phoneme tokens for each word; punctuation tokens are preserved unchanged.
        """
        phonemized = [self._get_phones(word=tok, lang=lang, pos=pos)
                      if pos != "PUNCT" else tok
                      for tok, pos in self.postag.tag(sentence)]

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
