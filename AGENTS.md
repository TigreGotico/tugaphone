# tugaphone: agent guide

`tugaphone` is a Python package that turns Portuguese text into IPA for each Lusophone dialect. It drives the orthography2ipa lattice, and it adds spelling conversion, number reading, homograph marks and the packaged lexicons that orthography2ipa leaves to the caller.

The documentation starts at [docs/index.md](docs/index.md).

## Repository map

| Path | Holds |
|---|---|
| `tugaphone/__init__.py` | `TugaPhonemizer` and the public names |
| `tugaphone/lattice_core.py` | The orthography2ipa `Pipeline`: spelling step, `expand`, `mark`, lexicon |
| `tugaphone/registry.py` | Lect codes, legacy aliases, `PACKAGED_LEXICON_LECTS` |
| `tugaphone/content_revision.py` | `revision`, `tugaphone==<version>` and the sorted dependency pins |
| `tugaphone/number_utils.py`, `tugaphone/text_normalization.py` | The text2spoken step and the orthographic rewrites |
| `tugaphone/codeswitch.py`, `tugaphone/langdetect.py`, `tugaphone/data/` | Contact-language routing, detector models and the loanword list |
| `tugaphone/accent.py`, `tugaphone/__main__.py` | Accent forcing and the `tugaphone` command |
| `docs/`, `examples/`, `tests/` | Documentation, runnable scripts and tests |
| `scripts/`, `benchmarks/` | Benchmarks, the regression gate, `check_docs_examples.py` and the board files |

## Setup and tests

```bash
unset VIRTUAL_ENV
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python --prerelease=allow -e ".[test]"
.venv/bin/python -m pytest tests
```

Use uv, never pip. The `test` extra installs `markovonnx`, and the `langdetect` extra installs it for users. `tests/test_examples.py` runs every script in `examples/`.

## Hard rules

1. A dialect is an orthography2ipa lect spec. Dialect phonology comes from the spec, and no string-edit pass runs after transcription ([architecture.md](docs/architecture.md#the-lattice-core)).
2. Only `pt-PT` and `pt-BR` take a packaged lexicon. A sub-regional lect never takes one ([architecture.md](docs/architecture.md#2-lexicon)).
3. Never edit `docs/scoreboard.md` or `benchmarks/results.json` by hand. Run `scripts/benchmark.py`, and commit the regenerated files with a change that improves the score ([benchmarking.md](docs/benchmarking.md#regression-gate)).
4. CI never uses the network. Only a maintainer refreshes the gold fixtures with `scripts/benchmark.py --refresh-fixtures` ([benchmarking.md](docs/benchmarking.md#regression-gate)).
5. The wheel carries no sentence sets and no tests. `.github/workflows/sentence_gate.yml` checks it.
6. Every IPA sample in the docs is output of the installed orthography2ipa specs. A page example carries its output in the comment under it, and `scripts/check_docs_examples.py` compares the two.
7. The release workflow writes `tugaphone/version.py` and `CHANGELOG.md`. Do not edit either.

## Before you push

1. Run the full test suite.
2. If you changed `README.md` or `docs/`, run the example check:

```bash
.venv/bin/python scripts/check_docs_examples.py README.md docs/*.md
```

3. A page you add goes in the table of `docs/index.md`, gets an `agent-hint` comment after its H1, and ends with a footer that links the index, the previous page and the next page.
4. If you changed the phonemization path or a spec dependency, run the regression gate:

```bash
.venv/bin/python scripts/check_benchmark_regression.py
```

`dev` is the work branch and `master` is the stable branch.
