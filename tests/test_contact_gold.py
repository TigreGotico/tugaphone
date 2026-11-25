"""A contact row phonemized with ``contact="auto"`` is no further from its gold than it was at the baseline.

``tests/data/contact_auto_distances.json`` holds the baseline distance of each
row. ``scripts/contact_gold_distances.py`` writes it.
"""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from contact_gold_distances import LANGS, OUTPUT, contact_rows, distance  # noqa: E402

BASELINE = json.loads(Path(OUTPUT).read_text(encoding="utf-8"))
ROWS = [row for lang in LANGS for row in contact_rows(lang)]


def test_the_baseline_covers_every_contact_row():
    assert sorted(BASELINE) == sorted(row["id"] for row in ROWS)
    assert len(ROWS) >= 60


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["id"])
def test_contact_auto_is_no_worse_than_the_baseline(row):
    assert distance(row) <= BASELINE[row["id"]], row["text"]
