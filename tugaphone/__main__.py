"""Command-line interface for tugaphone.

    tugaphone phonemize "o gato dorme" --lect pt-BR
    tugaphone force-accent "o vinho verde" --lect pt-PT-x-porto --mode respell
    tugaphone force-accent "a tia" --lect pt-BR --mode respell --base pt-PT \
        --overlay tweaks.json
    tugaphone list

``force-accent`` is the accent-forcing entry point (see
:mod:`tugaphone.accent`): ``--mode ipa`` prints the target lect's IPA for a
phoneme-input TTS, ``--mode respell`` prints Portuguese text respelled so a
grapheme-input TTS speaking ``--base`` pronounces the target accent.
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from tugaphone.accent import AccentOverlay, force_accent
from tugaphone.lattice_core import phonemize
from tugaphone.registry import list_dialects


def _load_overlay(path: Optional[str]) -> Optional[AccentOverlay]:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return AccentOverlay.from_json(fh.read())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tugaphone", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_ph = sub.add_parser("phonemize", help="transcribe text to IPA")
    p_ph.add_argument("text")
    p_ph.add_argument("--lect", "--lang", default="pt-PT",
                      help="target lect code (default: pt-PT)")

    p_fa = sub.add_parser("force-accent",
                          help="force text/IPA into a target accent for a TTS")
    p_fa.add_argument("text")
    p_fa.add_argument("--lect", "--lang", required=True,
                      help="target accent lect code")
    p_fa.add_argument("--mode", choices=("ipa", "respell"), default="ipa",
                      help="'ipa' for phoneme-input TTS, 'respell' for "
                           "grapheme-input TTS (default: ipa)")
    p_fa.add_argument("--base", default="pt-PT",
                      help="base accent the grapheme voice speaks "
                           "(respell mode; default: pt-PT)")
    p_fa.add_argument("--overlay", default=None,
                      help="path to a JSON AccentOverlay of user tweaks")

    sub.add_parser("list", help="list the supported dialect/lect codes")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "phonemize":
        print(phonemize(args.text, args.lect))
    elif args.command == "force-accent":
        print(force_accent(args.text, args.lect, mode=args.mode,
                           base_lect=args.base,
                           overlay=_load_overlay(args.overlay)))
    elif args.command == "list":
        for code in list_dialects():
            print(code)
    return 0


if __name__ == "__main__":
    sys.exit(main())
