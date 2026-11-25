"""Example — rules-only G2P (lexicon lookup disabled).

An inventory takes no lexicon unless the caller passes IRREGULAR_WORDS, and
clearing the table makes sure that every word takes the grapheme rules.
This is useful for testing rule coverage or transcribing words that are
intentionally not in a lexicon (neologisms, invented words).

Run::

    python examples/08_rules_only.py
"""
from tugaphone.dialects import EuropeanPortuguese, BrazilianPortuguese
from tugaphone.tokenizer import Sentence


def main() -> None:
    # Clear IRREGULAR_WORDS after instantiation
    inv_pt = EuropeanPortuguese()
    inv_pt.IRREGULAR_WORDS = {}

    inv_br = BrazilianPortuguese()
    inv_br.IRREGULAR_WORDS = {}

    words = [
        "gato",
        "fonologia",
        "supercalifragilístico",
        "neologismo",
    ]

    print("Rules-only transcription (no lexicon lookup):")
    for word in words:
        ipa_pt = Sentence(word, dialect=inv_pt).ipa
        ipa_br = Sentence(word, dialect=inv_br).ipa
        print(f"  {word:25s}  pt-PT → {ipa_pt:<30s}  pt-BR → {ipa_br}")


if __name__ == "__main__":
    main()
