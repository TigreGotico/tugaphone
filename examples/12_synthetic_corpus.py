"""Example — generating a parallel accent corpus for TTS training.

The synthetic-data use case the old accent transforms served: purposefully
manipulate input so a downstream TTS learns to pronounce a target accent. For
each ``(sentence, lect)`` this emits a row with both representations a TTS
trainer might want:

    sentence          the original Portuguese text
    lect              the target accent's lect code
    ipa               target-accent IPA          (phoneme-input TTS target)
    respelled_text    text forced toward the accent for a pt-PT base voice
                      (grapheme-input TTS input)

Point a phoneme-input voice at the ``ipa`` column, or a fixed pt-PT
grapheme-input voice at the ``respelled_text`` column, to teach it the target
accent from text your base speaker already reads.

By default this runs over a small built-in sentence set and a handful of lects
so it stays fast. Pass ``--full`` to iterate orthography2ipa's entire
sentence-level Portuguese TTS gold over every pt-family lect that has gold,
writing a real parallel corpus TSV.

Run::

    python examples/12_synthetic_corpus.py                 # quick demo to stdout
    python examples/12_synthetic_corpus.py --full out.tsv  # full corpus to TSV
"""
from __future__ import annotations

import csv
import sys
from typing import Iterable, List, Tuple

from tugaphone import force_accent, list_dialects

# A tiny built-in set for the quick demo — chosen to exercise betacism,
# palatalisation, coda-l vocalisation and monophthongisation.
DEMO_SENTENCES = [
    "o vinho verde da minha terra",
    "a tia dele vendeu o carro",
    "o sal e o pastel no Brasil",
    "hoje o peixe estava caro",
]
DEMO_LECTS = ["pt-PT-x-porto", "pt-BR", "pt-BR-x-caipira", "pt-AO"]

FIELDS = ["sentence", "lect", "ipa", "respelled_text"]


def _row(sentence: str, lect: str, base_lect: str = "pt-PT") -> dict:
    return {
        "sentence": sentence,
        "lect": lect,
        "ipa": force_accent(sentence, lect, mode="ipa"),
        "respelled_text": force_accent(sentence, lect, mode="respell",
                                       base_lect=base_lect),
    }


def _iter_demo() -> Iterable[dict]:
    for sentence in DEMO_SENTENCES:
        for lect in DEMO_LECTS:
            yield _row(sentence, lect)


def _load_full() -> List[Tuple[str, str]]:
    """(sentence, lect) pairs over the full pt-family sentence gold."""
    import importlib.util
    import os
    from importlib import import_module
    from pathlib import Path

    # orthography2ipa's scripts/benchmark.py, from $O2I_ROOT or from above an
    # editable install. A scripts/ directory counts only next to the
    # orthography2ipa package, never tugaphone's own scripts/benchmark.py.
    o2i_file = Path(import_module("orthography2ipa").__file__).resolve()
    roots = [Path(os.environ["O2I_ROOT"])] if os.environ.get("O2I_ROOT") else []
    roots += o2i_file.parents
    for root in roots:
        cand = root / "scripts" / "benchmark.py"
        if cand.exists() and (root / "orthography2ipa" / "__init__.py").exists():
            spec = importlib.util.spec_from_file_location("_o2i_bench", cand)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            break
    else:
        raise RuntimeError(
            "orthography2ipa's scripts/benchmark.py is not in its wheel: set "
            "O2I_ROOT to an orthography2ipa checkout, or install orthography2ipa editable")

    lects = sorted(set(module._PORTUGUESE_TTS_LANGS) & set(list_dialects()))
    pairs: List[Tuple[str, str]] = []
    for lect in lects:
        for sentence, _gold in module.load_portuguese_tts(lect, 10 ** 6):
            pairs.append((sentence, lect))
    return pairs


def main(argv: List[str]) -> int:
    if argv and argv[0] == "--full":
        out_path = argv[1] if len(argv) > 1 else "accent_corpus.tsv"
        pairs = _load_full()
        with open(out_path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t")
            writer.writeheader()
            for sentence, lect in pairs:
                writer.writerow(_row(sentence, lect))
        print(f"wrote {len(pairs)} rows over "
              f"{len({l for _, l in pairs})} lects → {out_path}")
        return 0

    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS, delimiter="\t")
    writer.writeheader()
    for row in _iter_demo():
        writer.writerow(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
