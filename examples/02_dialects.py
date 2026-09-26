"""Example — the same sentence across the five Lusophone dialects.

Run::

    python examples/02_dialects.py
"""
from tugaphone import TugaPhonemizer


def main() -> None:
    ph = TugaPhonemizer()

    sentence = "O comboio chegou à estação."
    print(sentence)
    for code in ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]:
        print(f"  {code} → {ph.phonemize_sentence(sentence, code)}")


if __name__ == "__main__":
    main()
