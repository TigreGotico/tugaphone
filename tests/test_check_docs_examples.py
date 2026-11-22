"""scripts/check_docs_examples.py must fail a page whose example is wrong."""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_docs_examples.py"

CLEAN = "```python\nprint(1 + 1)\n# 2\n```\n"

FAULTS = {
    "syntax error in a block with an output comment": (
        "```python\nprint(1 + 1\n# 3\n```\n"
    ),
    "output comment under an assignment": "```python\nx = 1 + 1\n# 3\n```\n",
    "output comment under an import": "```python\nimport math\n# 3\n```\n",
    "statement that raises": "```python\nundefined_name.call()\n```\n",
    "wrong output in a py block": "```py\nprint(1 + 1)\n# 3\n```\n",
}


def run(tmp_path: Path, page: str) -> subprocess.CompletedProcess:
    path = tmp_path / "page.md"
    path.write_text(page, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True
    )


def test_clean_page_passes(tmp_path):
    assert run(tmp_path, CLEAN).returncode == 0


def test_text_fence_is_not_executed(tmp_path):
    assert run(tmp_path, CLEAN + "\n```text\nfunc(a: int) -> str\n```\n").returncode == 0


@pytest.mark.parametrize("page", FAULTS.values(), ids=FAULTS.keys())
def test_wrong_page_fails(tmp_path, page):
    assert run(tmp_path, CLEAN + "\n" + page).returncode == 1
