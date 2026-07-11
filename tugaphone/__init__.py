from typing import Optional

from tugaphone.version import __version__
from tugaphone.dialects import (DialectInventory, LEXICON,
                                EuropeanPortuguese, BrazilianPortuguese,
                                AngolanPortuguese, MozambicanPortuguese, TimoresePortuguese)
from tugalex import TugaLexicon
from tugatagger import TugaTagger
from tugaphone.regional import RegionalTransforms
from tugaphone.registry import (DialectEntry, resolve_dialect, list_dialects,
                                get_regional_transforms)
from tugaphone.registry import get_dialect_inventory as _registry_inventory
from tugaphone.tokenizer import Sentence, DialectInventory

# Disambiguates heterophonic homographs (sede = thirst vs seat, forma = mould
# vs shape, …) by meaning and marks the result with the open/closed-vowel
# diacritic the grapheme rules read directly — resolving same-part-of-speech
# pairs the tagger cannot split.
from bifonia import add_extra_diacritics as _bifonia_diacritics


class TugaPhonemizer:
    """
    TugaPhonemizer applies dialect-aware Portuguese phonemization.

    Supports the five major Lusophone dialects (pt-PT, pt-BR, pt-AO, pt-MZ,
    pt-TL), city-level inventories (pt-PT-x-lisbon, pt-BR-x-rio-janeiro,
    pt-BR-x-sao-paulo) and the regional accent presets reachable through
    BCP-47 private-use codes (pt-PT-x-porto, pt-PT-x-alentejo, …); the full
    list comes from :func:`tugaphone.list_dialects`.
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
        """Return the :class:`DialectInventory` registered for ``lang``."""
        return _registry_inventory(lang)

    def phonemize_sentence(self, sentence: str, lang: str = "pt-PT",
                           regional_dialect: Optional[RegionalTransforms] = None) -> str:
        """
        Phonemizes a sentence for the given Portuguese dialect.

        Parameters:
            sentence (str): Input sentence to phonemize.
            lang (str): BCP-47 dialect code to target. Major dialects
                ("pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"), city
                inventories ("pt-BR-x-sao-paulo", …) and regional accent
                presets ("pt-PT-x-porto", …) all resolve through the
                dialect registry; see :func:`tugaphone.list_dialects`.
            regional_dialect (RegionalTransforms): Explicit regional accent
                preset; overrides whatever preset ``lang`` resolves to.

        Returns:
            phonemized (str): Space-separated phoneme tokens for each word; punctuation tokens are preserved unchanged.
        """
        if lang.startswith("pt"):
            # Resolve heterophone meaning first; the inserted diacritics drive the
            # correct vowel quality in the grapheme rules below.
            sentence = _bifonia_diacritics(sentence)

        tagged = self.postag.tag(sentence)

        regional_dialect = regional_dialect or get_regional_transforms(lang)
        if regional_dialect:
            # 1. apply morpheme transforms
            morph = lambda tok, pos: regional_dialect.apply_morpheme(word=tok, postag=pos)
            tagged = [(morph(tok, pos), pos) for tok, pos in tagged]
            morphed_sentence = " ".join([w[0] for w in tagged])

            # 2. phonemize
            nlp = Sentence.from_postagged(surface=morphed_sentence,
                                          tags=tagged,
                                          dialect=self.get_dialect_inventory(lang))
            ipa_str = nlp.ipa

            # 3. apply IPA transforms
            ipa_transform = lambda ipa, tok, pos: regional_dialect.apply_ipa(word=tok, phonemes=ipa, postag=pos)
            morphed_ipa = [ipa_transform(ipa, word, pos) for ipa, (word, pos) in zip(ipa_str.split(), tagged)]
            return " ".join(morphed_ipa)

        nlp = Sentence.from_postagged(surface=sentence, tags=tagged, dialect=self.get_dialect_inventory(lang))
        return nlp.ipa


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
        for code in ["pt-PT", "pt-PT-x-porto", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
            print(f"{code} → {ph.phonemize_sentence(s, code)}")
        print("######")
