"""Example — serialize a regional accent to a dict and rebuild it.

Run::

    python examples/06_serialize_accent.py
"""
from tugaphone.regional import PortoDialect, RegionalTransforms


def main() -> None:
    cfg = PortoDialect.as_dict
    print("Serialized PortoDialect:")
    print(f"  ipa_rules:      {cfg['ipa_rules']}")
    print(f"  morpheme_rules: {cfg['morpheme_rules']}")

    clone = RegionalTransforms.from_dict(cfg)
    print(f"\nRebuilt accent has {len(clone.ipa_rules)} IPA rules.")
    print(f"First rule: {clone.ipa_rules[0].__name__}")

    print("\nApplying the rebuilt rules to a phoneme string:")
    sample = "pˈoɾ·tu"
    print(f"  {sample} → {clone.apply_ipa(word='porto', phonemes=sample)}")

    try:
        RegionalTransforms.from_dict({"ipa_rules": ["does_not_exist"]})
    except ValueError as e:
        print(f"\nUnknown rule names raise: {e}")


if __name__ == "__main__":
    main()
