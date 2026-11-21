"""Example — read numbers, dates and times in Portuguese with text2spoken.

Run::

    python examples/04_numbers.py
"""
from tugaphone.number_utils import normalize_numbers, text2spoken_tag


def main() -> None:
    print("Gender agreement:")
    for text in ["vou comprar 1 casa", "vou comprar 2 casas",
                 "vou adotar 1 cão", "vou adotar 2 cães", "visitei 1 cidade"]:
        print(f"  {text:22s} → {normalize_numbers(text)}")

    print("\nOrdinals, dates, times and money:")
    for text in ["A 1.ª vez e o 2.º lugar.", "Nasceu a 25/12/2023.",
                 "A reunião é às 19h30.", "Pagou 2,50 € ontem."]:
        print(f"  {text:26s} → {normalize_numbers(text)}")

    print("\nScale differs by variety:")
    big = "897654356789098"
    print(f"  pt-PT (long scale)  → {normalize_numbers(big, 'pt-PT')}")
    print(f"  pt-BR (short scale) → {normalize_numbers(big, 'pt-BR')}")

    print("\nThe variety of each lect:")
    for lect in ["pt-PT", "pt-PT-x-porto", "pt-AO", "pt-BR", "pt-BR-x-sp", "pt-UY"]:
        print(f"  {lect:15s} {text2spoken_tag(lect)}  → {normalize_numbers('tem 19 anos', lect)}")


if __name__ == "__main__":
    main()
