from typing import Optional

from tugaphone.lexicon import TugaLexicon
from tugaphone.pos import TugaTagger
from tugaphone.regional import DialectTransforms
from tugaphone.tokenizer import EuropeanPortuguese, BrazilianPortuguese, AngolanPortuguese, MozambicanPortuguese, \
    TimoresePortuguese
from tugaphone.tokenizer import Sentence, DialectInventory, LEXICON


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

    def __init__(self,
                 postag_engine="auto",
                 postag_model="pt_core_news_lg"):
        """
        Initialize the TugaPhonemizer by loading the regional lexicon and configuring the part-of-speech tagger.

        Parameters:
            postag_engine (str): Tagging engine selection passed to TugaTagger (e.g., "auto" to let the tagger choose the best available engine).
            postag_model (str): Model name or identifier used by the POS tagger (for engines that accept a model parameter).
        """
        self.postag = TugaTagger(postag_engine, postag_model)
        # lexicon is lazy loaded on first usage, do it now so first inference is faster
        _ = LEXICON.ipa

    @staticmethod
    def get_dialect_inventory(lang: str = "pt-PT") -> DialectInventory:
        if lang == "pt-BR":
            return BrazilianPortuguese()
        elif lang == "pt-AO":
            return AngolanPortuguese()
        elif lang == "pt-MZ":
            return MozambicanPortuguese()
        elif lang == "pt-TL":
            return TimoresePortuguese()
        return EuropeanPortuguese()

    def phonemize_sentence(self, sentence: str, lang: str = "pt-PT",
                           regional_dialect: Optional[DialectTransforms] = None) -> str:
        """
        Phonemizes a sentence for the given Portuguese dialect.

        Parameters:
            sentence (str): Input sentence to phonemize.
            lang (str): ISO dialect code to target (e.g., "pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL").

        Returns:
            phonemized (str): Space-separated phoneme tokens for each word; punctuation tokens are preserved unchanged.
        """
        if regional_dialect:
            tagged = self.postag.tag(sentence)

            # 1. apply morpheme transforms
            morph = lambda tok, pos: regional_dialect.apply_morpheme(word=tok, postag=pos)
            words = [morph(tok, pos) for tok, pos in tagged]
            morphed_sentence = " ".join(words)

            # 2. phonemize
            nlp = Sentence(surface=morphed_sentence, dialect=self.get_dialect_inventory(lang))
            ipa_str = nlp.ipa

            # 3. apply IPA transforms
            ipa_transform = lambda ipa, tok, pos: regional_dialect.apply_ipa(word=tok, phonemes=ipa, postag=pos)
            morphed_ipa = [ipa_transform(ipa, word, pos) for ipa, (word, pos) in zip(ipa_str.split(), tagged)]

            return " ".join(morphed_ipa)

        nlp = Sentence(surface=sentence, dialect=self.get_dialect_inventory(lang))
        return nlp.ipa


if __name__ == "__main__":
    from tugaphone.regional import PortoDialect

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
        print(f"pt-PT-x-porto → {ph.phonemize_sentence(s, regional_dialect=PortoDialect)}")
        for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
            print(f"{code} → {ph.phonemize_sentence(s, code)}")
        print("######")
