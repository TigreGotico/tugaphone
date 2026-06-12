"""Example — experimental sub-regional accents on top of pt-PT.

Run::

    python examples/03_regional_accents.py
"""
from tugaphone import TugaPhonemizer
from tugaphone.regional import (PortoDialect, MinhoDialect, BragaDialect,
                                TrasMontanoDialect, FafeDialect)


def main() -> None:
    ph = TugaPhonemizer()

    sentence = "a gente sente o que sabe"
    accents = {
        "pt-PT (base)": None,
        "porto": PortoDialect,
        "minho": MinhoDialect,
        "braga": BragaDialect,
        "trasmontano": TrasMontanoDialect,
        "fafe": FafeDialect,
    }

    print(sentence)
    for name, accent in accents.items():
        ipa = ph.phonemize_sentence(sentence, "pt-PT", regional_dialect=accent)
        print(f"  {name:14s} → {ipa}")


if __name__ == "__main__":
    main()
