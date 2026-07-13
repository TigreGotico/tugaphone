from typing import Optional

from tugaphone.version import __version__
from tugaphone.dialects import (DialectInventory, LEXICON,
                                EuropeanPortuguese, BrazilianPortuguese,
                                AngolanPortuguese, MozambicanPortuguese, TimoresePortuguese)
from tugaphone.regional import RegionalTransforms
from tugaphone.registry import (DialectEntry, resolve_dialect, list_dialects,
                                get_regional_transforms)
from tugaphone.registry import get_dialect_inventory as _registry_inventory
from tugaphone.tokenizer import Sentence, DialectInventory

# Disambiguates heterophonic homographs (sede = thirst vs seat, forma = mould
# vs shape, …) by meaning and marks the result with the open/closed-vowel
# diacritic the grapheme rules read directly.
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

    def __init__(self):
        """
        Initialize the TugaPhonemizer by loading the regional lexicon.
        """
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
            phonemized (str): Space-separated phoneme tokens for each word.
        """
        if lang.startswith("pt"):
            # Resolve heterophone meaning first; the inserted diacritics drive the
            # correct vowel quality in the grapheme rules below.
            sentence = _bifonia_diacritics(sentence)

        dialect = self.get_dialect_inventory(lang)
        regional_dialect = regional_dialect or get_regional_transforms(lang)

        if regional_dialect:
            # 1. apply morpheme transforms to each surface word
            base = Sentence(sentence, dialect=dialect)
            morphed_surfaces = [regional_dialect.apply_morpheme(w.surface) for w in base.words]
            morphed_sentence = " ".join(morphed_surfaces)

            # 2. phonemize the respelled sentence
            nlp = Sentence(morphed_sentence, dialect=dialect)
            ipa_tokens = nlp.ipa.split()

            # 3. apply IPA transforms per word
            final_ipa = [
                regional_dialect.apply_ipa(word=surface, phonemes=ipa)
                for surface, ipa in zip(morphed_surfaces, ipa_tokens)
            ]
            return " ".join(final_ipa)

        nlp = Sentence(sentence, dialect=dialect)
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
