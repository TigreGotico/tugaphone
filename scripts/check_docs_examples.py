#!/usr/bin/env python3
"""Run the python blocks of a Markdown page and compare each result with its comment.

A comment run directly under a ``print(...)`` call or a bare expression states
the output: the printed text, or the ``repr`` of the value. A trailing comment
on the same line does the same. Blocks of one page share a namespace.

    python scripts/check_docs_examples.py README.md docs/quickstart.md
"""

from __future__ import annotations

import ast
import contextlib
import io
import re
import sys

BLOCK = re.compile(r"^```python\n(.*?)^```", re.S | re.M)


def stated(lines: list[str], stmt: ast.stmt) -> str | None:
    """The output a statement's comments claim, or None when it claims none."""
    tail = lines[stmt.end_lineno - 1]
    if stmt.end_lineno == stmt.lineno and "  # " in tail:
        return tail.split("  # ", 1)[1].strip()
    out = []
    for line in lines[stmt.end_lineno:]:
        text = line.strip()
        if not text.startswith("#"):
            break
        out.append(text[1:].removeprefix(" "))
    return "\n".join(out) if out else None


def check(path: str) -> tuple[int, int]:
    checked = failed = 0
    scope: dict = {"__name__": "__docs__"}
    with open(path, encoding="utf-8") as fh:
        page = fh.read()
    for block in BLOCK.findall(page):
        lines = block.splitlines()
        try:
            body = ast.parse(block).body
        except SyntaxError:
            continue
        for stmt in body:
            source = ast.Module([stmt], [])
            outputs = isinstance(stmt, (ast.Expr, ast.For))
            claim = stated(lines, stmt) if outputs else None
            buf = io.StringIO()
            shows_value = (
                claim is not None
                and isinstance(stmt, ast.Expr)
                and not (
                    isinstance(stmt.value, ast.Call)
                    and getattr(stmt.value.func, "id", "") == "print"
                )
            )
            try:
                with contextlib.redirect_stdout(buf):
                    if shows_value:
                        expr = ast.Expression(stmt.value)
                        print(repr(eval(compile(expr, path, "eval"), scope)))
                    else:
                        exec(compile(source, path, "exec"), scope)
            except Exception as err:
                if claim is None:
                    continue
                buf = io.StringIO(f"{type(err).__name__}: {err}")
            if claim is None:
                continue
            checked += 1
            got = buf.getvalue().rstrip("\n")
            if got != claim:
                failed += 1
                print(f"{path}:{stmt.lineno}: stated {claim!r}, got {got!r}")
    return checked, failed


def main() -> int:
    total = failed = 0
    for path in sys.argv[1:]:
        n, bad = check(path)
        print(f"{path}: {n} outputs checked, {bad} differ")
        total += n
        failed += bad
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
