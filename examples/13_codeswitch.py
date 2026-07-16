"""Example — code-switching: embedded English/Spanish/French words nativized.

Code-switching is opt-in (``contact="auto"``); the default ``"none"`` transcribes
everything as Portuguese. With ``auto`` the Brazilian tech register's English
loans are routed through the English lattice and projected onto the Portuguese
inventory, while the Portuguese function words are untouched.

Run::

    python examples/11_codeswitch.py
"""
from tugaphone import TugaPhonemizer


def main() -> None:
    ph = TugaPhonemizer()

    sentence = "fiz o download do app"
    print(sentence)
    print(f"  none → {ph.phonemize_sentence(sentence, 'pt-BR', contact='none')}")
    print(f"  auto → {ph.phonemize_sentence(sentence, 'pt-BR', contact='auto')}")

    border = "comprei cerveza no bar"
    print(border)
    print(f"  pt-UY auto → {ph.phonemize_sentence(border, 'pt-UY', contact='auto')}")


if __name__ == "__main__":
    main()
