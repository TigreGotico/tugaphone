"""Example — homograph disambiguation (meaning-based).

Run::

    python examples/07_homographs.py
"""
from tugaphone import TugaPhonemizer


def main() -> None:
    ph = TugaPhonemizer()

    meaning_pairs = [
        ("sede (thirst)", "Tenho muita sede."),
        ("sede (HQ)",     "A empresa tem sede em Lisboa."),
        ("forma (mould)", "Untou a forma com manteiga."),
        ("forma (shape)", "Resolveu o problema desta forma."),
        ("gosto (verb)",  "Eu gosto de música."),
        ("gosto (noun)",  "Tenho bom gosto."),
    ]

    print("=== Meaning-based homographs ===")
    for label, sentence in meaning_pairs:
        print(f"  {label:20s} → {ph.phonemize_sentence(sentence)}")


if __name__ == "__main__":
    main()
