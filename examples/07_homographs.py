"""Example — homograph disambiguation (meaning-based and POS-based).

Run::

    python examples/07_homographs.py
"""
from tugaphone import TugaPhonemizer


def main() -> None:
    ph = TugaPhonemizer()

    # Meaning-based homographs (bifonia resolves sense before G2P)
    meaning_pairs = [
        ("sede (thirst)", "Tenho muita sede."),
        ("sede (HQ)",     "A empresa tem sede em Lisboa."),
    ]

    print("=== Meaning-based homographs ===")
    for label, sentence in meaning_pairs:
        print(f"  {label:20s} → {ph.phonemize_sentence(sentence)}")

    print()

    # POS-based homographs (open /ɔ/ for verb, closed /o/ for noun)
    pos_pairs = [
        ("gosto (verb)",  "Eu gosto de música."),
        ("gosto (noun)",  "Tenho bom gosto."),
        ("choro (verb)",  "Eu choro de alegria."),
        ("choro (noun)",  "O choro é livre."),
        ("porto (verb)",  "Eu porto a mochila."),
        ("porto (noun)",  "O porto é belo."),
    ]

    print("=== POS-based homographs ===")
    for label, sentence in pos_pairs:
        print(f"  {label:20s} → {ph.phonemize_sentence(sentence)}")


if __name__ == "__main__":
    main()
