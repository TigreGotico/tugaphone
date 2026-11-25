"""Write the edit distance of each ``contact`` gold row under ``contact="auto"``.

The distance is the Levenshtein distance between ``phonemize(text, lang,
contact="auto")`` and the row's ``expected_ipa``. ``tests/test_contact_gold.py``
fails a row whose distance is larger than the value written here.

    python scripts/contact_gold_distances.py
"""
import csv
import json
from pathlib import Path

from tugaphone import phonemize
from tugaphone.accent import _levenshtein

TESTS = Path(__file__).resolve().parent.parent / "tests"
LANGS = ["pt-PT", "pt-BR"]
OUTPUT = TESTS / "data" / "contact_auto_distances.json"


def contact_rows(lang):
    path = TESTS / "data" / "sentences" / f"{lang}.tsv"
    with open(path, encoding="utf-8", newline="") as f:
        rows = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        return [row for row in rows if row["category"] == "contact"]


def distance(row):
    return _levenshtein(phonemize(row["text"], row["lang"], contact="auto"), row["expected_ipa"])


if __name__ == "__main__":
    distances = {row["id"]: distance(row) for lang in LANGS for row in contact_rows(lang)}
    OUTPUT.write_text(json.dumps(distances, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(distances)} rows, total distance {sum(distances.values())}")
