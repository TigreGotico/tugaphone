"""Example — phonemize a Portuguese sentence to IPA.

Run::

    python examples/01_basic.py
"""
from tugaphone import TugaPhonemizer


def main() -> None:
    ph = TugaPhonemizer()

    sentences = [
        "O gato dorme.",
        "Tu falas português muito bem.",
        "A menina comeu o pão todo.",
        "Vou pôr a manteiga no frigorífico.",
    ]

    for s in sentences:
        print(f"{s}")
        print(f"  pt-PT → {ph.phonemize_sentence(s, 'pt-PT')}")


if __name__ == "__main__":
    main()
