"""
NOTE: dialect modeling is a work in progress. Use at your own risk.
"""
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Dict

from tugaphone.ipa_transforms import (labial_fricative_stop_merger, reduce_vowel_centralization, retain_ou_diphthong,
                                      retain_ei_diphthong, conservative_o_nasal_retention, palatal_affrication_ch,
                                      rhotic_realization, open_vowel_preference, epenthetic_j_before_palatal,
                                      nasal_glide_palatalization, nasal_vowel_raising, nasal_diphthongization_e,
                                      final_nasal_denasalization, rising_diphthong_o,
                                      initial_z_devoicing, intervocalic_s_voicing)

# typing helpers
IPATransform = Callable[[str, str, str], str]
MorphemeTransform = Callable[[str, str], str]

# --- Function Mapping for Serialization/Deserialization ---
# This map ensures that the string name in a config file can be correctly mapped
# to the Python function object, and vice versa.
RULE_MAP: Dict[str, IPATransform] = {
    "reduce_vowel_centralization": reduce_vowel_centralization,
    "open_vowel_preference": open_vowel_preference,
    "retain_ou_diphthong": retain_ou_diphthong,
    "retain_ei_diphthong": retain_ei_diphthong,
    "conservative_o_nasal_retention": conservative_o_nasal_retention,
    "labial_fricative_stop_merger": labial_fricative_stop_merger,
    "palatal_affrication_ch": palatal_affrication_ch,
    "rhotic_realization": rhotic_realization,
    "epenthetic_j_before_palatal": epenthetic_j_before_palatal,
    "nasal_diphthongization_e": nasal_diphthongization_e,
    "rising_diphthong_o": rising_diphthong_o,
}
# Inverse map for serialization (function object -> string name)
INVERSE_RULE_MAP: Dict[IPATransform, str] = {v: k for k, v in RULE_MAP.items()}


# -----------------------------------------------------------


@dataclass
class RegionalTransforms:
    morpheme_rules: List[MorphemeTransform] = field(default_factory=list)  # transform word before g2p
    ipa_rules: List[IPATransform] = field(default_factory=list)  # transform ipa after g2p
    base_region: Optional[str] = None  # for the bundled lexicon

    def apply_ipa(self, word: str, phonemes: str, postag: str = "NOUN") -> str:
        """
        Apply the configured IPA transformation rules to a phoneme string for a given word and part of speech.

        Parameters:
            word (str): The orthographic word used by rule functions when contextual information is required.
            phonemes (str): The input phoneme string to transform.
            postag (str): The part-of-speech tag influencing rule behaviour (default: "NOUN").

        Returns:
            str: The phoneme string after all IPA rules have been applied.
        """
        for rule in self.ipa_rules:
            phonemes = rule(word, phonemes, postag)
        return phonemes

    def apply_morpheme(self, word: str, postag: str = "NOUN") -> str:
        """
        Apply morpheme transformation rules to a word in sequence.

        Parameters:
            word (str): Input word to transform.
            postag (str): Part-of-speech tag used by morpheme rules to guide transformations (defaults to "NOUN").

        Returns:
            str: Transformed word after applying all morpheme rules.
        """
        for rule in self.morpheme_rules:
            word = rule(word, postag)
        return word

    @staticmethod
    def from_dict(data: Dict[str, str | List[str]]) -> 'RegionalTransforms':
        """
        Create a DialectTransforms instance from a dictionary configuration.

        Parameters:
            data (Dict[str, str | List[str]]): Mapping that may contain:
                - 'ipa_rules': list of IPA rule names to apply in order.
                - 'morpheme_rules': list of morpheme rule names (currently not implemented and ignored).
                - 'base_region': optional base lexicon identifier.

        Returns:
            RegionalTransforms: A new instance with `ipa_rules` set to the functions named in
            `data['ipa_rules']`, `morpheme_rules` left empty (pending implementation), and
            `base_region` set from the input (or None).

        Raises:
            ValueError: If any name listed in 'ipa_rules' is not a recognized IPA rule.
        """
        ipa_str_rules: List[str] = data.get('ipa_rules', [])
        morpheme_str_rules: List[str] = data.get('morpheme_rules', [])
        base_region: Optional[str] = data.get('base_region')

        # Use the lookup map for cleaner function assignment
        ipa_rules: List[IPATransform] = []
        for rule_name in ipa_str_rules:
            if rule_name not in RULE_MAP:
                raise ValueError(f"Unknown ipa transform rule: {rule_name}")
            ipa_rules.append(RULE_MAP[rule_name])

        morpheme_rules: List[MorphemeTransform] = []
        for rule_name in morpheme_str_rules:
            # TODO - implement morpheme rules and update lookup map
            print(f"Warning: Morpheme rule '{rule_name}' is not yet implemented.")

        return RegionalTransforms(
            ipa_rules=ipa_rules,
            morpheme_rules=morpheme_rules,
            base_region=base_region
        )

    @property
    def as_dict(self) -> Dict[str, str | List[str]]:
        """
        Serialize the RegionalDialect to a plain dictionary representation.

        Returns:
            dict: A dictionary with keys:
                - "base_region": the dialect's base region (defaults to "lbx" if not set).
                - "morpheme_rules": list of morpheme rule names for rules that have a known string mapping.
                - "ipa_rules": list of IPA rule names for rules that have a known string mapping.
        """
        return {
            "base_region": self.base_region or "lbx",  # Default to Lisbon
            "morpheme_rules": [INVERSE_RULE_MAP[rule] for rule in self.morpheme_rules if rule in INVERSE_RULE_MAP],
            "ipa_rules": [INVERSE_RULE_MAP[rule] for rule in self.ipa_rules if rule in INVERSE_RULE_MAP]
        }


# --- Standard Dialect Presets ---
NEUTRAL_RULES = [  # undoes the "lisbon" particularities present in base G2P
    retain_ou_diphthong,  # Diphthong retention
    retain_ei_diphthong  # Diphthong retention
]

COMMON_NORTHERN_RULES = [
    *NEUTRAL_RULES,
    nasal_vowel_raising,
    reduce_vowel_centralization,  # Vowel centralization resistance
    open_vowel_preference,  # Open /ɐ/ realization
    labial_fricative_stop_merger,  # V/B merger tendency
    rhotic_realization  # Alveolar rhotic
]

LisbonDialect = RegionalTransforms(
    base_region="lbx"  # Base G2P output, no additional transformations
)

CoimbraDialect = RegionalTransforms(
    ipa_rules=NEUTRAL_RULES,
    base_region="lbx"
)

MinhoDialect = RegionalTransforms(
    ipa_rules=COMMON_NORTHERN_RULES,
    base_region="lbx"
)

BragaDialect = RegionalTransforms(
    ipa_rules=[
        nasal_glide_palatalization,  # 'mãe' [mˈɐ̃j] → [mˈɐ̃jɲ]
        epenthetic_j_before_palatal,  # "bolacha" -> "bolaicha"  / "abelha" -> "abeilha"
        *COMMON_NORTHERN_RULES
    ],
    base_region="lbx"
)

FamalicaoDialect = RegionalTransforms(
    ipa_rules=[
        conservative_o_nasal_retention,  # "Famalicão" -> "Famalicoum"
        *COMMON_NORTHERN_RULES
    ],
    base_region="lbx"
)

TrasMontanoDialect = RegionalTransforms(
    ipa_rules=[
        palatal_affrication_ch,  # <ch> affrication  "tchouriço", "tchuva", "tchaves"
        initial_z_devoicing,  # 'zero' [ˈzeɾu] → [ˈseɾu]
        intervocalic_s_voicing,  # 'moço' [ˈmosu] → [ˈmozu]
        final_nasal_denasalization,  # 'viagem' -> 'viage' / [viˈaʒẽ] → [viˈaʒe]
        *COMMON_NORTHERN_RULES
    ],
    base_region="lbx"
)

PortoDialect = RegionalTransforms(
    ipa_rules=[
        rising_diphthong_o,  # Puorto
        *COMMON_NORTHERN_RULES
    ],
    base_region="lbx"
)

FafeDialect = RegionalTransforms(
    ipa_rules=[
        nasal_diphthongization_e, # "a geinte só sabe verdadeirameinte o que seinte quando esta doeinte"
        *COMMON_NORTHERN_RULES
    ],
    base_region="lbx"
)

RioJaneiroDialect = RegionalTransforms(
    base_region="rjx"  # Base G2P output, no additional transformations
)

SaoPauloDialect = RegionalTransforms(
    base_region="spx"  # Base G2P output, no additional transformations
)

if __name__ == "__main__":
    from tugaphone import TugaPhonemizer

    pho = TugaPhonemizer()

    sentences = [
        # --- Diphthongs (rule_m_d1 + rule_m_d2) ---
        "boa roupa touro pouco ouro",  # ou → ow
        "manteiga beira peixe feito reino meio",  # ei → ej

        # --- Consonant features ---
        "chave chão chaleira peixe",  # ch → tʃ (palatal affrication)
        "rosa carro ferro vermelho rei",  # ʁ → r (alveolar trill)
        "velho abelha bolacha banha ranho",  # epenthetic [j] before palatals
        "chouriço feijão mochila bicho",  # affricate retention + epenthesis mix

        # --- Vowel openness and resistance to centralization ---
        "verdade verde verdadeira boi vaca bacalhau",  # v→b, open vowels, diphthongs
        "pão irmão cagão bolhão cão",  # nasal vowels (õ)
        "mesa pequeno bonito saber verdade",  # ɨ→e (reduced centralization)
        "sinal animal final jornal canal",  # ɐ→a before nasal/lateral

        # --- Miscellaneous regional cues ---
        "minho vinho caminho",  # nasal + palatal interplay
        "abelha coelho velha telha",  # epenthetic [j] + palatal l
        "bolacha castanha lenha montanha",  # palatal nasal epenthesis

        "foda-se bolo do Porto",
        "a gente só sabe verdadeiramente o que sente quando está doente",
        "amanhã de manhã a minha mãe"
    ]

    for s in sentences:
        phonemes = pho.phonemize_sentence(s, "pt-PT", regional_dialect=FafeDialect)
        print(f"'{s:30s}' -> {phonemes}")

    # Demonstrate serialization
    print("\n--- Serialization Demo ---")
    porto_config = PortoDialect.as_dict
    print(f"Porto Config (Serialized):\n{porto_config}")

    # Demonstrate deserialization
    recreated_porto = RegionalTransforms.from_dict(porto_config)
    print(f"\nRecreated Porto has {len(recreated_porto.ipa_rules)} IPA rules.")
    # Show that the specific Porto rule (rising_diphthong_o) is present
    print(f"First rule is: {recreated_porto.ipa_rules[0].__name__}")
