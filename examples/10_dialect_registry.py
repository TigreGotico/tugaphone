"""Example — the dialect registry: every dialect reachable by language code.

Major dialects, city inventories and regional accent presets all resolve from
BCP-47 codes; regional accents use private-use subtags (``pt-PT-x-porto``).

Run::

    python examples/10_dialect_registry.py
"""
from tugaphone import TugaPhonemizer, list_dialects, resolve_dialect


def main() -> None:
    print("Registered dialect codes:")
    for code in list_dialects():
        entry = resolve_dialect(code)
        kind = "preset" if entry.transforms else "inventory"
        print(f"  {code:24s} {kind:9s} {entry.region}")

    ph = TugaPhonemizer()
    sentence = "O vinho é muito bom."

    print(f"\n{sentence}")
    for code in ["pt-PT", "pt-PT-x-porto", "pt-PT-x-alentejo",
                 "pt-PT-x-azores", "pt-BR", "pt-BR-x-sao-paulo"]:
        print(f"  {code:20s} → {ph.phonemize_sentence(sentence, code)}")

    # Aliases and unknown subtags resolve sanely.
    print("\nResolution:")
    for code in ["pt", "PT-BR", "pt-PT-x-lisboa", "pt-PT-x-unknown"]:
        print(f"  {code:18s} → {resolve_dialect(code).code}")


if __name__ == "__main__":
    main()
