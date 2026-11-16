"""Example — forcing an accent for a downstream TTS.

Two downstream uses, two modes of :func:`tugaphone.force_accent`:

* **phoneme-input TTS** (phoonnx-style): the voice takes IPA, so forcing the
  accent is just transcribing with the target lect — ``mode="ipa"``.
* **grapheme-input TTS** (a fixed pt-PT voice you cannot re-point): the voice
  reads text, so you must respell the input in conventions the base voice reads
  as the target sounds — ``mode="respell"``. Feed a pt-PT voice ``binho`` to
  force the Northern betacism of ``vinho``.

Plus the user-space escape hatch: an :class:`~tugaphone.AccentOverlay` of ad-hoc
tweaks, serialisable to JSON so a voice tweak is shareable.

Run::

    python examples/11_force_accent.py
"""
from tugaphone import AccentOverlay, Transform, force_accent, phonemize


def main() -> None:
    sentence = "o vinho verde e a tia dele no Brasil"

    print("mode='ipa'  (feed the target IPA to a phoneme-input TTS)")
    for lect in ["pt-PT-x-porto", "pt-BR", "pt-AO"]:
        print(f"  {lect:16s} → {force_accent(sentence, lect, mode='ipa')}")

    print("\nmode='respell'  (feed respelled TEXT to a pt-PT grapheme-input TTS)")
    for lect in ["pt-PT-x-porto", "pt-BR"]:
        respelled = force_accent(sentence, lect, mode="respell", base_lect="pt-PT")
        print(f"  {lect:16s} → {respelled!r}")
        # what the pt-PT voice now says vs the target accent it is chasing:
        print(f"      base voice says : {phonemize(respelled, 'pt-PT')}")
        print(f"      target accent   : {phonemize(sentence, lect)}")

    print("\nuser-space overlay (ad-hoc tweaks, JSON-serialisable)")
    overlay = AccentOverlay(
        name="my-voice-tweaks",
        transforms=[
            # this voice mispronounces the uvular R; nudge it to a tap
            Transform(kind="regex", pattern="ʀ", replacement="ɾ", stage="ipa"),
        ],
    )
    tweaked = force_accent("o carro", "pt-PT", mode="ipa", overlay=overlay)
    print(f"  with overlay → {tweaked}")
    print("  overlay JSON (shareable):")
    print(overlay.to_json())


if __name__ == "__main__":
    main()
