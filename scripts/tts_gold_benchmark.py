"""Score tugaphone against the orthography2ipa Portuguese sentence-level TTS gold.

The reference is orthography2ipa's ``data/gold/portuguese_tts/<lect>.tsv`` — one
sentence-level gold set per Portuguese lect, in the broad IPA tradition the lect
specs are written to. This measures the phonemization pipeline end to end (a
dialect is selected by its lect code) with the same character-level PER and IPA
normalization orthography2ipa's own benchmark uses.

    python scripts/tts_gold_benchmark.py            # every pt-family lect
    python scripts/tts_gold_benchmark.py pt-PT pt-BR

The default lect set is the intersection of orthography2ipa's Portuguese TTS
gold with tugaphone's own canonical dialects
(:func:`tugaphone.registry.list_dialects`): the Portuguese family. orthography2ipa
also ships gold for the Astur-Leonese lects of Portugal (Mirandese ``mwl``, the
``ast-PT`` border varieties); those are out of tugaphone's scope — dedicated
downstream phonemizers own them — so scoring them here through the pt-PT fallback
would be meaningless, and they are excluded. Pass explicit lect codes to override.

Read the number as agreement-with-the-spec-tradition, not absolute correctness:
the gold is authored to the lect specs' broad convention. The ``tugalex`` lexicon
overlay (registered for the lects in :data:`tugaphone.registry._LEXICON_REGION`)
is retained as the authority for lexical facts the rules would otherwise get
wrong; where the lattice already reproduces the lexicon form it has no effect on
the score.
"""
from __future__ import annotations

import importlib.util
import sys
from importlib import import_module
from pathlib import Path

from tugaphone import TugaPhonemizer


def _load_o2i_benchmark():
    """Load orthography2ipa's benchmark module (PER/normalize/gold loader).

    Imported by file path, not by name, so it never collides with tugaphone's
    own ``scripts/benchmark.py`` on ``sys.path``.
    """
    o2i_file = Path(import_module("orthography2ipa").__file__).resolve()
    for parent in o2i_file.parents:
        cand = parent / "scripts" / "benchmark.py"
        if cand.exists():
            spec = importlib.util.spec_from_file_location("_o2i_benchmark", cand)
            module = importlib.util.module_from_spec(spec)
            sys.modules["_o2i_benchmark"] = module
            spec.loader.exec_module(module)
            return module
    raise RuntimeError("orthography2ipa benchmark script not found")


O2I = _load_o2i_benchmark()


def _per(pairs, phonemize, *, strip_stress=True, broad=False):
    pers = []
    for sentence, gold in pairs:
        try:
            hyp = O2I.normalize(phonemize(sentence), strip_stress, broad)
        except Exception:
            continue
        if not hyp:
            continue
        ref = O2I.normalize(gold, strip_stress, broad)
        pers.append(O2I.levenshtein(hyp, ref) / max(len(ref), 1))
    return (sum(pers) / len(pers)) if pers else float("nan")


def _default_lects():
    """The pt-family gold sets: orthography2ipa TTS gold ∩ tugaphone dialects.

    Keeps orthography2ipa's non-pt Portuguese-territory lects (Mirandese, the
    ``ast-PT`` varieties), which dedicated downstream phonemizers own, out of
    tugaphone's score rather than measuring them through the pt-PT fallback.
    """
    from tugaphone.registry import list_dialects

    return sorted(set(O2I._PORTUGUESE_TTS_LANGS) & set(list_dialects()))


def main(argv):
    lects = argv or _default_lects()
    pho = TugaPhonemizer()
    print(f"{'lect':<24}{'PER':>10}{'n':>6}")
    scores = []
    for lect in lects:
        pairs = O2I.load_portuguese_tts(lect, 10 ** 6)
        if not pairs:
            continue
        per = _per(pairs, lambda s, L=lect: pho.phonemize_sentence(s, L))
        if per == per:
            scores.append(per)
        print(f"{lect:<24}{per:>10.4f}{len(pairs):>6}")
    if scores:
        print("-" * 40)
        print(f"{'MEAN':<24}{sum(scores) / len(scores):>10.4f}")


if __name__ == "__main__":
    main(sys.argv[1:])
