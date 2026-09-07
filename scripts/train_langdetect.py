#!/usr/bin/env python3
"""Train the char-Markov code-switch language detector bundled with tugaphone.

Four character-level Markov models (Portuguese, Spanish, French, English) are
trained on Wikipedia text and written gzip-compressed to
``tugaphone/data/langdetect/<lang>.json.gz`` — the artifacts
:mod:`tugaphone.langdetect` loads.

Design choices (see ``docs/codeswitch.md``):

* **Order 2.** Character bigram context. Evaluated against order 3; order 2 both
  classifies better on this word-level task and produces far smaller models.
* **Word-level, boundary-wrapped.** Text is normalized to NFC, lower-cased and
  stripped to alphabetic words; each word is wrapped with start/end sentinels so
  word-initial and word-final character statistics are modelled.
* **~3 M characters per language** is ample for character n-grams.

The Spanish, French and English models are the same shape and pipeline as the
ones euskaphone ships for the Basque frontend — Wikipedia character n-grams under
the identical (Apache-2.0) licensing — so the family could share one
``markovonnx`` model set. tugaphone retrains its own from scratch here to keep
the bundle self-contained: the four models are produced by one command, at one
``markovonnx`` version, with Portuguese as the fourth in-language model rather
than Basque.

Requires ``markovonnx`` and ``datasets``. Wikipedia is streamed, so no large
local dump is needed::

    python scripts/train_langdetect.py
    python scripts/train_langdetect.py --chars 3000000 --order 2
"""
from __future__ import annotations

import argparse
import gzip
import shutil
import tempfile
import unicodedata
from pathlib import Path

#: ``pt`` is the in-language default; the other three are the contact lattices.
LANGS = ["pt", "es", "fr", "en"]
BOS, EOS = "\x02", "\x03"
OUT_DIR = Path(__file__).resolve().parent.parent / "tugaphone" / "data" / "langdetect"
WIKI_SNAPSHOT = "20231101"


def normalize_words(text: str):
    text = unicodedata.normalize("NFC", text).lower()
    out, cur = [], []
    for ch in text:
        if ch.isalpha():
            cur.append(ch)
        elif cur:
            out.append("".join(cur))
            cur = []
    if cur:
        out.append("".join(cur))
    return out


def wrap(word: str):
    return [BOS] + list(word) + [EOS]


def stream_words(lang: str, max_chars: int):
    from datasets import load_dataset

    ds = load_dataset(
        "wikimedia/wikipedia", f"{WIKI_SNAPSHOT}.{lang}",
        split="train", streaming=True,
    )
    total = 0
    for row in ds:
        for w in normalize_words(row["text"]):
            yield w
            total += len(w)
        if total >= max_chars:
            return


def train_lang(lang: str, max_chars: int, order: int, out_dir: Path):
    from markovonnx import MarkovChain, Vocabulary

    seqs = [wrap(w) for w in stream_words(lang, max_chars)]
    vocab = Vocabulary()
    vocab.build_from_sequences(seqs)
    mc = MarkovChain(order=order, vocab=vocab, smoothing=1e-5,
                     backoff=True, kneser_ney=True)
    mc.fit(seqs)

    out_dir.mkdir(parents=True, exist_ok=True)
    gz_path = out_dir / f"{lang}.json.gz"
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name
    mc.save(tmp_path)
    with open(tmp_path, "rb") as src, gzip.open(gz_path, "wb") as dst:
        shutil.copyfileobj(src, dst)
    Path(tmp_path).unlink()
    kb = gz_path.stat().st_size / 1024
    print(f"  [{lang}] {len(seqs)} words, vocab={vocab.size}, {gz_path.name} {kb:.0f} KB")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chars", type=int, default=3_000_000,
                    help="Training characters per language (default 3M).")
    ap.add_argument("--order", type=int, default=2, help="N-gram order (default 2).")
    ap.add_argument("--out", type=Path, default=OUT_DIR, help="Output directory.")
    ap.add_argument("--langs", nargs="+", default=LANGS)
    args = ap.parse_args()

    print(f"Training char-Markov detectors (order={args.order}, "
          f"{args.chars} chars/lang) -> {args.out}")
    for lang in args.langs:
        train_lang(lang, args.chars, args.order, args.out)
    print("Done.")


if __name__ == "__main__":
    main()
