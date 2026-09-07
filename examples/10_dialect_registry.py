"""Example — the dialect registry: every lect reachable by language code.

A dialect is an orthography2ipa lect spec. The national standards, the European
and Brazilian sub-regional varieties and the African/Asian lects all resolve
from their BCP-47 codes; sub-regional varieties use private-use subtags
(``pt-PT-x-porto``). Legacy tugaphone accent codes resolve to their
orthography2ipa equivalents.

Run::

    python examples/10_dialect_registry.py
"""
from tugaphone import TugaPhonemizer, list_dialects, resolve_lect


def main() -> None:
    codes = list_dialects()
    print(f"{len(codes)} registered lect codes:")
    for code in codes:
        print(f"  {code}")

    ph = TugaPhonemizer()
    sentence = "O vinho é muito bom."

    print(f"\n{sentence}")
    for code in ["pt-PT", "pt-PT-x-porto", "pt-PT-x-alentejo",
                 "pt-PT-x-acores", "pt-BR", "pt-BR-x-sp"]:
        print(f"  {code:20s} → {ph.phonemize_sentence(sentence, code)}")

    # Aliases and unknown subtags resolve to a lect code.
    print("\nResolution:")
    for code in ["pt", "PT-BR", "pt-PT-x-lisboa", "pt-BR-x-sao-paulo",
                 "pt-PT-x-unknown"]:
        print(f"  {code:20s} → {resolve_lect(code)}")


if __name__ == "__main__":
    main()
