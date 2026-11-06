"""Example — sub-regional accents, selected by lect code.

A regional accent is an orthography2ipa lect spec: the phonology (northern
betacism, Porto rising diphthongs, Transmontano affrication, …) lives in the
spec, so selecting the accent is just choosing the code. There is no separate
transform layer to compose.

Run::

    python examples/03_regional_accents.py
"""
from tugaphone import TugaPhonemizer


def main() -> None:
    ph = TugaPhonemizer()

    sentence = "a gente sente o que sabe"
    accents = [
        "pt-PT",
        "pt-PT-x-porto",
        "pt-PT-x-minho",
        "pt-PT-x-braga",
        "pt-PT-x-trasosmontes",
        "pt-PT-x-alentejo",
        "pt-PT-x-madeira",
    ]

    print(sentence)
    for code in accents:
        print(f"  {code:22s} → {ph.phonemize_sentence(sentence, code)}")


if __name__ == "__main__":
    main()
