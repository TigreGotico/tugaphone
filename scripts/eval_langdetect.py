#!/usr/bin/env python3
"""Evaluate the code-switch language detector against the orthographic baseline.

The task is the binary routing decision the code-switch stage actually makes:
*is this word Portuguese, or contact-language material to route out?* Held-out
words are drawn from Wikipedia articles disjoint from training, each word absent
from its language's training vocabulary, so neither detector has seen them.
Portuguese words are the negative class (should stay ``pt``); Spanish, French and
English words are the positive class (should route out).

Two detectors are scored:

* ``markov`` — :class:`tugaphone.langdetect.MarkovLangDetector` at a sweep of
  margins;
* ``heuristic`` — the orthographic :func:`tugaphone.codeswitch.is_contact_word`.

Run::

    python scripts/eval_langdetect.py --per-lang 800
"""
from __future__ import annotations

import argparse
import unicodedata
from pathlib import Path

TRAIN = Path(__file__).resolve().parent
WIKI_SNAPSHOT = "20231101"
LANGS = ["pt", "es", "fr", "en"]


def _norm_words(text: str):
    text = unicodedata.normalize("NFC", text).lower()
    out, cur = [], []
    for ch in text:
        if ch.isalpha():
            cur.append(ch)
        elif cur:
            out.append("".join(cur)); cur = []
    if cur:
        out.append("".join(cur))
    return out


def training_vocab(lang: str, chars: int):
    """The set of words the model saw in training (first ``chars`` characters)."""
    from datasets import load_dataset
    ds = load_dataset("wikimedia/wikipedia", f"{WIKI_SNAPSHOT}.{lang}",
                      split="train", streaming=True)
    seen, total = set(), 0
    for row in ds:
        for w in _norm_words(row["text"]):
            seen.add(w); total += len(w)
        if total >= chars:
            break
    return seen


def heldout_words(lang: str, train_words: set, n: int, skip_chars: int):
    """``n`` held-out words for ``lang``: unseen in training, length >= 3."""
    from datasets import load_dataset
    ds = load_dataset("wikimedia/wikipedia", f"{WIKI_SNAPSHOT}.{lang}",
                      split="train", streaming=True)
    out, skipped = [], 0
    for row in ds:
        words = _norm_words(row["text"])
        if skipped < skip_chars:
            skipped += sum(len(w) for w in words)
            continue
        for w in words:
            if len(w) >= 3 and w not in train_words and w not in out:
                out.append(w)
                if len(out) >= n:
                    return out
    return out


def prf(tp, fp, fn, tn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    acc = (tp + tn) / (tp + fp + fn + tn)
    return p, r, f, acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-lang", type=int, default=800)
    ap.add_argument("--train-chars", type=int, default=3_000_000)
    args = ap.parse_args()

    from tugaphone.langdetect import get_detector
    from tugaphone.codeswitch import is_contact_word

    det = get_detector()
    assert det is not None, "detector unavailable (need markovonnx + models)"

    # Build held-out sets.
    words = {}  # lang -> [word]
    for lang in LANGS:
        tv = training_vocab(lang, args.train_chars)
        words[lang] = heldout_words(lang, tv, args.per_lang, args.train_chars)
        print(f"[{lang}] held-out {len(words[lang])} words")

    pos = [(w, True) for lg in ("es", "fr", "en") for w in words[lg]]
    neg = [(w, False) for w in words["pt"]]
    dataset = pos + neg

    def score(predict):
        tp = fp = fn = tn = 0
        for w, is_contact in dataset:
            pred = predict(w)
            if is_contact and pred: tp += 1
            elif is_contact and not pred: fn += 1
            elif not is_contact and pred: fp += 1
            else: tn += 1
        return prf(tp, fp, fn, tn)

    print(f"\n{'detector':38} {'prec':>6} {'rec':>6} {'F1':>6} {'acc':>6}")
    for margin in (0.4, 0.5, 0.6):
        p, r, f, a = score(lambda w: det.is_contact(w, margin=margin))
        print(f"char-Markov (order 2, margin {margin:<4})        "
              f"{p:6.3f} {r:6.3f} {f:6.3f} {a:6.3f}")
    p, r, f, a = score(is_contact_word)
    print(f"orthographic heuristic                 {p:6.3f} {r:6.3f} {f:6.3f} {a:6.3f}")


if __name__ == "__main__":
    main()
