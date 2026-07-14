"""Example — orthography2ipa G2P plugin and syllabifier plugin.

TugaphoneG2PPlugin implements the orthography2ipa G2PPlugin interface.
SilabificadorSyllabifier implements the SyllabifierPlugin interface and is
registered at the ``orthography2ipa.syllabify`` entry point.

Run::

    python examples/09_plugin.py
"""
from tugaphone.plugin import TugaphoneG2PPlugin, SilabificadorSyllabifier


def main() -> None:
    # --- G2P plugin ---
    print("=== TugaphoneG2PPlugin ===")
    for lang in ["pt-PT", "pt-BR", "pt-AO"]:
        p = TugaphoneG2PPlugin(lang=lang)
        ipa = p.transcribe("o gato dorme")
        print(f"  {lang}: {ipa}")

    print(f"\n  language_codes: {TugaphoneG2PPlugin().language_codes}")

    # --- Syllabifier plugin ---
    print("\n=== SilabificadorSyllabifier ===")
    syl = SilabificadorSyllabifier()
    words = ["fonologia", "comboio", "supercalifragilístico", "português"]
    for word in words:
        syllables = syl.syllabify(word)
        print(f"  {word:30s} → {'.'.join(syllables)}")


if __name__ == "__main__":
    main()
