"""Write the edit distance of each ``contact`` gold row under ``contact="auto"``.

The distance is the Levenshtein distance between ``phonemize(text, lang,
contact="auto")`` and the row's ``expected_ipa``. It is written once per
code-switch classifier, ``detector`` and ``fallback``, because the two route
some words differently. ``tests/test_contact_gold.py`` fails a row whose
distance is larger than the value written for its classifier. The ``detector``
map needs markovonnx installed.

    python scripts/contact_gold_distances.py
"""
import csv
import json
from pathlib import Path

import tugaphone.langdetect as langdetect
from tugaphone import phonemize
from tugaphone.accent import _levenshtein

TESTS = Path(__file__).resolve().parent.parent / "tests"
LANGS = ["pt-PT", "pt-BR"]
CLASSIFIERS = ["detector", "fallback"]
OUTPUT = TESTS / "data" / "contact_auto_distances.json"


def contact_rows(lang):
    path = TESTS / "data" / "sentences" / f"{lang}.tsv"
    with open(path, encoding="utf-8", newline="") as f:
        rows = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        return [row for row in rows if row["category"] == "contact"]


def distance(row):
    return _levenshtein(phonemize(row["text"], row["lang"], contact="auto"), row["expected_ipa"])


def distances(classifier):
    """Distance of every contact row under ``classifier``."""
    get_detector = langdetect.get_detector
    get_detector.cache_clear()
    if classifier == "fallback":
        langdetect.get_detector = lambda: None
    elif get_detector() is None:
        raise SystemExit("markovonnx or bundled langdetect models unavailable")
    try:
        return {row["id"]: distance(row) for lang in LANGS for row in contact_rows(lang)}
    finally:
        langdetect.get_detector = get_detector


if __name__ == "__main__":
    baseline = {name: distances(name) for name in CLASSIFIERS}
    OUTPUT.write_text(json.dumps(baseline, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, rows in baseline.items():
        print(f"{name}: {len(rows)} rows, total distance {sum(rows.values())}")
