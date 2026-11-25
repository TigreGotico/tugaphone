# Comparison with other tools
<!-- agent-hint
covers: how tugaphone compares with espeak-ng and other Portuguese G2P tools, and where its limits are
source: tugaphone/registry.py, tugaphone/lattice_core.py
generated: no
verify: .venv/bin/python scripts/check_docs_examples.py docs/comparison.md
see: dialects.md, benchmarking.md
-->

Most Portuguese G2P tools treat Portuguese as one or two varieties. The reason
for tugaphone to exist is dialect granularity: one API that spans the whole
Lusophone space and, within European Portuguese, a set of sub-regional accents.

| Tool | Portuguese coverage | Notes |
|------|--------------------|-------|
| **espeak-ng** | `pt` (European) + `pt-br` (Brazilian) | Small, fast, rule-based, about 100 languages, widely used as a TTS front-end. Two Portuguese varieties only, no African/Asian Lusophone, no sub-regional accents. |
| **phonemizer** (bootphon) | via espeak-ng | A backend wrapper, for Portuguese it delegates to espeak-ng, so the same two varieties. Needs the espeak binary. |
| Single-variety Portuguese toolkits (e.g. Brazilian-focused phonetic transcribers) | one national variety | Strong within their variety, not built to cover the full Lusophone range from one interface. |
| **tugaphone** | every Portuguese-family orthography2ipa lect: five national standards + European, Brazilian, African, Asian and other varieties | Pure Python, IPA output with stress, meaning-based homograph resolution, one API across the whole Lusophone space. |

## What tugaphone adds

- **Every Portuguese-family orthography2ipa lect** reachable by BCP-47 code, the five national
  standards (`pt-PT`, `pt-BR`, `pt-AO`, `pt-MZ`, `pt-TL`) plus European and
  Brazilian sub-regional varieties and the African, Asian and other lects. See
  [dialects.md](dialects.md).
- **Meaning-based homograph resolution**, *sede* thirst vs headquarters,
  *gosto* verb vs noun, via [bifonia](https://github.com/TigreGotico/bifonia).
  See [homographs.md](homographs.md).
- **Gender- and scale-aware number expansion** (long scale for `pt-PT`, short
  scale for `pt-BR`). See [numbers.md](numbers.md).
- **A phonology-accurate core**, each dialect's sounds come from its
  orthography2ipa lect spec, not from a post-hoc string-edit layer. See
  [architecture.md](architecture.md).

## Trade-offs

tugaphone is Portuguese-only and younger than espeak-ng, which covers far more
languages and has years of field use. Its accuracy against the per-lect gold is
measured openly, see [benchmarking.md](benchmarking.md).

---
[← Quickstart](quickstart.md) · [Index](index.md) · [Architecture →](architecture.md)
