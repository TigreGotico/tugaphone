"""Example — inspect the Sentence -> Word -> Grapheme token tree.

Run::

    python examples/05_token_tree.py
"""
from tugaphone.tokenizer import Sentence
from tugaphone.dialects import EuropeanPortuguese


def main() -> None:
    sentence = Sentence("O cão comeu o pão.", dialect=EuropeanPortuguese())

    print(f"Sentence: {sentence.surface}")
    print(f"IPA:      {sentence.ipa}")
    print(f"Words:    {sentence.n_words}")
    print()

    for word in sentence.words:
        print(f"  {word.surface}")
        print(f"    syllables: {'.'.join(word.syllables)}")
        print(f"    stress:    syllable {word.stressed_syllable_idx}")
        print(f"    ipa:       {word.ipa}")
        for g in word.graphemes:
            tags = []
            if g.is_diphthong:
                tags.append("diphthong")
            if g.is_nasal:
                tags.append("nasal")
            if g.is_digraph:
                tags.append("digraph")
            label = f" [{', '.join(tags)}]" if tags else ""
            print(f"      grapheme {g.surface!r} → {g.ipa}{label}")


if __name__ == "__main__":
    main()
