"""Example — spell out numbers in Portuguese with gender and scale agreement.

Run::

    python examples/04_numbers.py
"""
from tugaphone.number_utils import normalize_numbers, NumberParser


def main() -> None:
    print("Gender agreement:")
    for text in ["vou comprar 1 casa", "vou comprar 2 casas",
                 "vou adotar 1 cão", "vou adotar 2 cães", "visitei 1 cidade"]:
        print(f"  {text:22s} → {normalize_numbers(text)}")

    print("\nOrdinals (via NumberParser, with the gender marker):")
    print(f"  1 + º → {NumberParser.pronounce_number_word('1', next_word='º')}")
    print(f"  1 + ª → {NumberParser.pronounce_number_word('1', next_word='ª')}")
    print(f"  3 + º → {NumberParser.pronounce_number_word('3', next_word='º')}")

    print("\nScientific notation:")
    for text in ["1e9", "1.5e10"]:
        print(f"  {text:22s} → {normalize_numbers(text)}")

    print("\nScale differs by dialect:")
    big = "897654356789098"
    print(f"  pt-PT (long scale)  → {normalize_numbers(big, 'pt-PT')}")
    print(f"  pt-BR (short scale) → {normalize_numbers(big, 'pt-BR')}")

    print("\nSingle-token control via NumberParser:")
    print(f"  19 (pt-BR) → {NumberParser.pronounce_number_word('19', is_brazilian=True)}")
    print(f"  19 (pt-PT) → {NumberParser.pronounce_number_word('19', is_brazilian=False)}")


if __name__ == "__main__":
    main()
