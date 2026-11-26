# Development
<!-- agent-hint
covers: how to set up a checkout, run the tests and which file owns which stage
source: pyproject.toml, tests/test_examples.py, scripts/
generated: no
verify: test -f tests/test_examples.py && test -f tugaphone/lattice_core.py
see: benchmarking.md, AGENTS.md
-->

Set up a checkout with its test extra, then run the suite:

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python --prerelease=allow -e ".[test]"
.venv/bin/python -m pytest tests
```

The `test` extra installs `markovonnx`. Without it, code-switch detection uses
the orthographic fallback. `tests/test_examples.py` runs every script in
`examples/`, so a broken example fails the suite.

## Where the code lives

| Path | Content |
|------|---------|
| `tugaphone/lattice_core.py` | The phonemization pipeline on the orthography2ipa lattice |
| `tugaphone/registry.py` | Lect codes, legacy aliases, the lects that take a packaged lexicon |
| `tugaphone/text_normalization.py`, `tugaphone/number_utils.py` | The `expand` step of the engine's `Pipeline` |
| `tugaphone/codeswitch.py`, `tugaphone/langdetect.py` | Contact-language detection and nativization |
| `tugaphone/accent.py`, `tugaphone/__main__.py` | Accent forcing and the command line |
| `scripts/` | Benchmarks and code-switch model training |

## Generated files

`scripts/benchmark.py` writes `benchmarks/results.json` and
`docs/scoreboard.md`, so do not edit either by hand. A change that improves the
score commits the regenerated baseline with it, and
`scripts/check_benchmark_regression.py` is the CI gate. CI never uses the
network: only a maintainer refreshes the gold fixtures, with
`scripts/benchmark.py --refresh-fixtures`. See [benchmarking.md](benchmarking.md).

---
[← Advanced](advanced.md) · [Home](index.md) · [Benchmarking →](benchmarking.md)
