"""Regional-accent composition layer for European Portuguese.

A regional accent is modelled as an ordered composition of grounded transform
rules: optional pre-G2P *morpheme* rules (archaic/dialectal spellings fed to
the grapheme-to-phoneme cascade) followed by post-G2P *IPA* rules
(:mod:`tugaphone.ipa_transforms`). Every rule carries its phonemic grounding;
presets below cite the features they compose.

Classification follows Cintra, L. F. Lindley (1971), *Nova proposta de
classificação dos dialectos galego-portugueses*; insular varieties follow the
Atlas Linguístico-Etnográfico de Portugal e da Galiza (Saramago 2006).
"""
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Dict, Tuple

from tugaphone.ipa_transforms import (
    betacism,
    reduce_vowel_centralization,
    retain_ou_diphthong,
    retain_ei_diphthong,
    monophthongize_ei,
    conservative_o_nasal_retention,
    palatal_affrication_ch,
    rhotic_realization,
    open_vowel_preference,
    epenthetic_j_before_palatal,
    nasal_glide_palatalization,
    nasal_vowel_raising,
    nasal_diphthongization_e,
    final_nasal_denasalization,
    rising_diphthong_o,
    rising_diphthong_e,
    initial_z_devoicing,
    intervocalic_s_voicing,
    intervocalic_d_deletion,
    simplify_nasal_diphthong_em,
    simplify_meu_class,
    sibilant_voicing_sandhi,
    lateral_palatalization,
    nasal_diphthong_to_nasal_plus_n,
    fronted_stressed_u,
    monophthongize_oi,
)
from tugaphone.morpheme_transforms import (
    spell_v_as_b,
    archaic_ch_to_x,
    MorphemeTransform,
)

# typing helpers
IPATransform = Callable[[str, str, str], str]


# ---------------------------------------------------------------------------
# Grounded-rule registry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GroundedRule:
    """A transform paired with its phonemic grounding.

    Attributes:
        name: registry key, identical to the wrapped function's ``__name__``,
            used for lossless serialization.
        func: the transform callable.
        phenomenon: one-line statement of the sound change.
        distribution: the dialect zone(s) where the change is attested.
        source: bibliographic / field-note citation (published > field notes >
            whitepaper), per the precedence order in the module docstrings.
    """

    name: str
    func: Callable
    phenomenon: str
    distribution: str
    source: str


def _ipa(func: IPATransform, phenomenon: str, distribution: str, source: str) -> GroundedRule:
    return GroundedRule(func.__name__, func, phenomenon, distribution, source)


def _morph(func: "MorphemeTransform", phenomenon: str, distribution: str, source: str) -> GroundedRule:
    return GroundedRule(func.__name__, func, phenomenon, distribution, source)


# IPA (post-G2P) rules, each grounded.
_IPA_REGISTRY: Tuple[GroundedRule, ...] = (
    _ipa(retain_ou_diphthong, "<ou> kept as [ow]", "North + conservative standard", "Cintra 1971; wp5 DB2/N2"),
    _ipa(retain_ei_diphthong, "<ei> kept as [ej]", "North + conservative standard", "Cintra 1971; wp5 DB1"),
    _ipa(monophthongize_ei, "[ej]→[e]", "Ribatejo, Alentejo, Algarve, Beira-Baixa", "Cintra 1971; wp5 RA1"),
    _ipa(betacism, "/v/ merged into [b]", "All northern + Galician", "Cintra 1971; wp4 N1; wp5 N1/DB4"),
    _ipa(reduce_vowel_centralization, "unstressed [ɨ]→[e]", "North (Minhoto), weak", "Cintra 1971; wp5 G3a"),
    _ipa(open_vowel_preference, "final /ɐ/→[a] / __[mnɲl]", "North, variable", "Cintra 1971; DIALECT_PATTERNS"),
    _ipa(conservative_o_nasal_retention, "-ão → [õ]", "Trás-os-Montes / Alto-Minho", "Cintra 1971; wp5 TM3"),
    _ipa(nasal_vowel_raising, "/ɐ̃/→[ã]", "North", "Cintra 1971; DIALECT_PATTERNS"),
    _ipa(palatal_affrication_ch, "<ch> /ʃ/→[tʃ]", "Transmontano / Alto-Minhoto", "Cintra 1971; wp4 N3; wp5 TM2"),
    _ipa(rhotic_realization, "onset /ʁ/→[r]", "Rural/conservative north + interior", "Cintra 1971; DIALECT_PATTERNS"),
    _ipa(epenthetic_j_before_palatal, "V→Vj / __[ʎɲʃ]", "Minho / northwest", "Cintra 1971; DIALECT_PATTERNS"),
    _ipa(rising_diphthong_o, "stressed close /o/→[wo]", "Porto / Baixo-Minho / Douro-Litoral", "Cintra 1971:684; wp5 PT2"),
    _ipa(rising_diphthong_e, "stressed close /e/→[je]", "Porto / Baixo-Minho / Douro-Litoral", "Cintra 1971:684"),
    _ipa(intervocalic_s_voicing, "apico-alveolar ⟨s,ss⟩ [s̺]/[z̺] (PLACE)", "Transmontano / Alto-Minhoto", "Cintra 1971:93; Álvarez Pérez 2014"),
    _ipa(initial_z_devoicing, "#/z/→[s] (GALICIAN trait 6)", "Galician / contact fringe", "Cintra 1971:451-457"),
    _ipa(final_nasal_denasalization, "-agem /ʒẽ/→[ʒe]", "Transmontano", "Cintra 1971; DIALECT_PATTERNS"),
    _ipa(nasal_diphthongization_e, "/ẽ/→[eĩ] / _C", "Fafe / inner Minho", "DIALECT_PATTERNS"),
    _ipa(nasal_glide_palatalization, "Ṽj̃→Ṽɲ / _#", "Braga / northwest", "DIALECT_PATTERNS"),
    _ipa(intervocalic_d_deletion, "intervocalic /d ð/→∅", "Alentejo, Algarve, Beira-Baixa", "Cintra 1971; DIALECT_PATTERNS"),
    _ipa(simplify_nasal_diphthong_em, "-em [ɐ̃j̃]→[ẽ]", "Alentejo / central-south", "Cintra 1971; DIALECT_PATTERNS"),
    _ipa(simplify_meu_class, "meu [ew]→[e]", "Alentejo, Algarve", "Cintra 1971; DIALECT_PATTERNS"),
    _ipa(sibilant_voicing_sandhi, "coda [ʃ]→[ʒ] / _ #V (external sandhi)", "South / insular sandhi", "Mateus & d'Andrade 2000; PWL"),
    _ipa(lateral_palatalization, "/l/→[ʎ] / i_V", "Madeira, Açores", "Segura 2013; o2i MAD_L_PALATALISATION"),
    _ipa(nasal_diphthong_to_nasal_plus_n, "Ṽj̃ʃ→Ṽns / _#", "Madeira, Açores", "ALEPG; o2i madeira/acores"),
    _ipa(fronted_stressed_u, "stressed /u/→[y] (not /_coda liq/sib)", "Açores (São Miguel), Alto-Alentejo, Beira-Baixa", "Cintra 1971:726; o2i ACO_U_*; wp5 BB1"),
    _ipa(monophthongize_oi, "[oj]→[o]", "Açores", "DIALECT_PATTERNS"),
)

# Morpheme (pre-G2P) rules, each grounded.
_MORPHEME_REGISTRY: Tuple[GroundedRule, ...] = (
    _morph(spell_v_as_b, "respell <v>→<b> before G2P (betacism input)", "All northern + Galician", "Cintra 1971; wp4 N1"),
    _morph(archaic_ch_to_x, "respell <ch>→<x> (apico-palatal source)", "Transmontano, archaic", "Cintra 1971; wp4 §3"),
)

# --- Serialization maps ---------------------------------------------------
# Name -> function and function -> name, derived from the grounded registry so
# the two never drift. A config file's string rule names map to the function
# objects the presets reference, and back, losslessly.
RULE_MAP: Dict[str, IPATransform] = {r.name: r.func for r in _IPA_REGISTRY}
MORPHEME_RULE_MAP: Dict[str, "MorphemeTransform"] = {r.name: r.func for r in _MORPHEME_REGISTRY}
INVERSE_RULE_MAP: Dict[IPATransform, str] = {v: k for k, v in RULE_MAP.items()}
INVERSE_MORPHEME_RULE_MAP: Dict["MorphemeTransform", str] = {v: k for k, v in MORPHEME_RULE_MAP.items()}

# name -> grounding, for documentation/introspection.
RULE_GROUNDING: Dict[str, GroundedRule] = {
    **{r.name: r for r in _IPA_REGISTRY},
    **{r.name: r for r in _MORPHEME_REGISTRY},
}


# ---------------------------------------------------------------------------


@dataclass
class RegionalTransforms:
    """An ordered composition of morpheme and IPA transform rules.

    ``morpheme_rules`` run on the surface word before G2P; ``ipa_rules`` run on
    the phoneme string after G2P. Both lists hold transform callables and
    round-trip losslessly through :meth:`as_dict` / :meth:`from_dict`.
    """

    morpheme_rules: List["MorphemeTransform"] = field(default_factory=list)
    ipa_rules: List[IPATransform] = field(default_factory=list)

    def apply_ipa(self, word: str, phonemes: str, postag: str = "NOUN") -> str:
        """Apply the configured IPA rules to ``phonemes`` in order."""
        for rule in self.ipa_rules:
            phonemes = rule(word, phonemes, postag)
        return phonemes

    def apply_morpheme(self, word: str, postag: str = "NOUN") -> str:
        """Apply the configured morpheme rules to ``word`` in order."""
        for rule in self.morpheme_rules:
            word = rule(word, postag)
        return word

    @staticmethod
    def from_dict(data: Dict[str, str | List[str]]) -> 'RegionalTransforms':
        """Build a :class:`RegionalTransforms` from a serialized config.

        Parameters:
            data: mapping that may contain ``'ipa_rules'`` and
                ``'morpheme_rules'`` (lists of registered rule names applied in
                order).

        Raises:
            ValueError: if any listed name is not a registered rule.
        """
        ipa_str_rules: List[str] = data.get('ipa_rules', [])
        morpheme_str_rules: List[str] = data.get('morpheme_rules', [])

        ipa_rules: List[IPATransform] = []
        for rule_name in ipa_str_rules:
            if rule_name not in RULE_MAP:
                raise ValueError(f"Unknown ipa transform rule: {rule_name}")
            ipa_rules.append(RULE_MAP[rule_name])

        morpheme_rules: List["MorphemeTransform"] = []
        for rule_name in morpheme_str_rules:
            if rule_name not in MORPHEME_RULE_MAP:
                raise ValueError(f"Unknown morpheme transform rule: {rule_name}")
            morpheme_rules.append(MORPHEME_RULE_MAP[rule_name])

        return RegionalTransforms(
            ipa_rules=ipa_rules,
            morpheme_rules=morpheme_rules
        )

    @staticmethod
    def _ipa_rule_name(rule: IPATransform) -> str:
        try:
            return INVERSE_RULE_MAP[rule]
        except KeyError:
            name = getattr(rule, "__name__", repr(rule))
            raise ValueError(
                f"Cannot serialize ipa rule {name!r}: it is not registered in "
                f"RULE_MAP, so as_dict/from_dict would not round-trip."
            )

    @staticmethod
    def _morpheme_rule_name(rule: "MorphemeTransform") -> str:
        try:
            return INVERSE_MORPHEME_RULE_MAP[rule]
        except KeyError:
            name = getattr(rule, "__name__", repr(rule))
            raise ValueError(
                f"Cannot serialize morpheme rule {name!r}: it is not registered "
                f"in MORPHEME_RULE_MAP, so as_dict/from_dict would not round-trip."
            )

    @property
    def as_dict(self) -> Dict[str, str | List[str]]:
        """Serialize to a name-only dict that round-trips through :meth:`from_dict`.

        Every configured rule is emitted; an unmapped rule raises rather than
        being silently dropped.
        """
        return {
            "morpheme_rules": [self._morpheme_rule_name(rule) for rule in self.morpheme_rules],
            "ipa_rules": [self._ipa_rule_name(rule) for rule in self.ipa_rules]
        }


# ===========================================================================
# Standard dialect presets
# ===========================================================================
# A preset is a composition of grounded rules. The de-biasing "retain" rules
# undo Lisbon-specific reductions present in the base G2P; the remaining rules
# add the positive features of the target accent. Rule order matters:
# betacism runs early so later rules see [b]; nasal/glide rules run before
# diphthong simplification so the nasal tilde is still attached.

# The conservative standard the north shares: no Lisbon monophthongisation.
_NEUTRAL = [
    retain_ou_diphthong,
    retain_ei_diphthong,
]

# Categorical features common to ALL northern varieties (Cintra's defining
# isoglosses): de-biasing + betacism. Deliberately minimal — features that the
# gold northern transcriptions do NOT show categorically (centralisation
# resistance, alveolar rhotic) are added only by the maximal Minhoto reading.
_NORTHERN_CORE = [
    *_NEUTRAL,
    betacism,
]


NorthernDialect = RegionalTransforms(
    morpheme_rules=[],
    ipa_rules=list(_NORTHERN_CORE),
)
"""Categorical northern EP: <ou>/<ei> retention + betacism /v/→[b].

Features: retain_ou_diphthong, retain_ei_diphthong, betacism.
The single set of features attested across the whole northern third in the
project gold; finer varieties below add their own.
Source: Cintra (1971), the betacism and diphthong-retention isoglosses.
"""

# Porto is the urban northern reference: northern core, plus its hallmark
# rising diphthongisation of stressed mid /o/. The urban Porto/Braga gold keeps
# the uvular [ʁ] and does not de-centralise, so those are not included.
PortoDialect = RegionalTransforms(
    ipa_rules=[
        rising_diphthong_o,
        rising_diphthong_e,
        *_NORTHERN_CORE,
    ]
)
"""Porto / Baixo-Minho / Douro-Litoral: northern core + tonic-close-vowel
diphthongisation ([e]→[je], [o]→[wo]).

Features: rising_diphthong_o, rising_diphthong_e, retain_ou_diphthong,
retain_ei_diphthong, betacism.
Cintra's (1971:684) single defining Porto marker is the diphthongisation of
BOTH close tonic vowels ("[e] em [je], [o] em [wo]"), so both halves compose.
Source: Cintra (1971:684); whitepaper5 PT2.
"""

# Maximal Minhoto reading: the northern core plus the conservative/rural
# vocalism and consonantism (centralisation resistance, open /a/, alveolar
# trill, raised nasals) that the field notes attribute to Minho speech.
MinhoDialect = RegionalTransforms(
    ipa_rules=[
        *_NORTHERN_CORE,
        reduce_vowel_centralization,
        open_vowel_preference,
        nasal_vowel_raising,
        rhotic_realization,
    ]
)
"""Minho (maximal conservative reading): northern core + open vowels + alveolar [r].

Features: betacism, retain_ou/ei, reduce_vowel_centralization,
open_vowel_preference, nasal_vowel_raising, rhotic_realization.
Source: Cintra (1971); DIALECT_PATTERNS field notes.
"""

BragaDialect = RegionalTransforms(
    ipa_rules=[
        nasal_glide_palatalization,
        epenthetic_j_before_palatal,
        *MinhoDialect.ipa_rules,
    ]
)
"""Braga: Minho features + nasal-glide → [ɲ] reinforcement + palatal epenthesis.

Features: nasal_glide_palatalization, epenthetic_j_before_palatal + Minho set.
Source: Cintra (1971); DIALECT_PATTERNS.
"""

FamalicaoDialect = RegionalTransforms(
    ipa_rules=[
        conservative_o_nasal_retention,
        *MinhoDialect.ipa_rules,
    ]
)
"""Vila Nova de Famalicão (Alto-Minho): Minho features + -ão → [õ] retention.

Features: conservative_o_nasal_retention + Minho set.
Source: Cintra (1971); whitepaper5 TM3.
"""

FafeDialect = RegionalTransforms(
    ipa_rules=[
        nasal_diphthongization_e,
        *MinhoDialect.ipa_rules,
    ]
)
"""Fafe (inner Minho): Minho features + nasal /ẽ/→[eĩ] diphthongisation.

Features: nasal_diphthongization_e + Minho set.
Source: DIALECT_PATTERNS field notes ("a geinte só sabe verdadeirameinte…").
"""

TrasMontanoDialect = RegionalTransforms(
    ipa_rules=[
        palatal_affrication_ch,
        intervocalic_s_voicing,
        final_nasal_denasalization,
        conservative_o_nasal_retention,
        *MinhoDialect.ipa_rules,
    ]
)
"""Transmontano (northeast): <ch> affricate [tʃ] + apico-alveolar four-sibilant
system + Minho.

Features: palatal_affrication_ch, intervocalic_s_voicing (apico-alveolar PLACE),
final_nasal_denasalization, conservative_o_nasal_retention + Minho set.
``initial_z_devoicing`` is deliberately NOT composed here: word-initial /z/→[s]
is Cintra's GALICIAN trait 6 (1971:451-457), and conservative Transmontano
instead KEEPS the voiced apico-alveolar [z̺]. Cintra's apico-alveolar sibilant
(trait 2) is his single most diagnostic North/South isogloss.
Source: Cintra (1971:93, trait 2; 429-431, trait 3); Álvarez Pérez (2014).
"""

CoimbraDialect = RegionalTransforms(
    ipa_rules=list(_NEUTRAL)
)
"""Coimbra / Centro-Litoral: conservative standard, <ou>/<ei> retained, no betacism.

Features: retain_ou_diphthong, retain_ei_diphthong.
Coimbra lies south of the betacism isogloss (Cintra 1971), so it keeps /v/.
"""

# --- Central-south -------------------------------------------------------

AlentejoDialect = RegionalTransforms(
    ipa_rules=[
        intervocalic_d_deletion,
        simplify_meu_class,
        simplify_nasal_diphthong_em,
        monophthongize_ei,
        fronted_stressed_u,
        sibilant_voicing_sandhi,
    ]
)
"""Alentejo: intervocalic /d/ deletion, meu→[me], -em→[ẽ], ei→[e], u→[y].

Features: intervocalic_d_deletion, simplify_meu_class,
simplify_nasal_diphthong_em, monophthongize_ei, fronted_stressed_u,
sibilant_voicing_sandhi.
Cintra (1971:726) delimits Alto-Alentejo by exactly the tonic u→[y] isogloss
(shared with Beira-Baixa), so the fronting (coda-blocked) is composed here.
Source: Cintra (1971:726); DIALECT_PATTERNS.
"""

AlgarveDialect = RegionalTransforms(
    ipa_rules=[
        simplify_meu_class,
        sibilant_voicing_sandhi,
    ]
)
"""Algarve: meu→[me], coda-sibilant voicing sandhi.

Features: simplify_meu_class, sibilant_voicing_sandhi.
The gold Algarve slice keeps both the -em nasal diphthong [ɐ̃j̃] and the <ei>
diphthong [ɐj]/[aj]; consistent with Cintra placing the Barlavento ei→e
monophthongisation away from the coastal Algarve slice measured here, the
diphthong simplifications are not applied (unlike Alentejo).
Source: Cintra (1971); DIALECT_PATTERNS.
"""

# --- Insular -------------------------------------------------------------

MadeiraDialect = RegionalTransforms(
    ipa_rules=[
        lateral_palatalization,
        nasal_diphthong_to_nasal_plus_n,
    ]
)
"""Madeira: l-palatalisation, nasal diphthong → Ṽ+[n].

Features: lateral_palatalization, nasal_diphthong_to_nasal_plus_n.
The gold Madeira slice keeps the phrase-final coda [ʃ], so the across-boundary
voicing sandhi attested elsewhere in the south is not applied here.
Source: ALEPG (Saramago 2006); DIALECT_PATTERNS.
"""

AzoresDialect = RegionalTransforms(
    ipa_rules=[
        fronted_stressed_u,
        lateral_palatalization,
        monophthongize_oi,
        nasal_diphthong_to_nasal_plus_n,
        sibilant_voicing_sandhi,
    ]
)
"""Açores (São Miguel): stressed /u/→[y], l-palatalisation, oi→[o], Ṽ+[n].

Features: fronted_stressed_u, lateral_palatalization, monophthongize_oi,
nasal_diphthong_to_nasal_plus_n, sibilant_voicing_sandhi.
Source: ALEPG (Saramago 2006); DIALECT_PATTERNS.
"""


if __name__ == "__main__":
    from tugaphone import TugaPhonemizer

    pho = TugaPhonemizer()
    presets = {
        "north": NorthernDialect, "porto": PortoDialect, "minho": MinhoDialect,
        "alentejo": AlentejoDialect, "algarve": AlgarveDialect,
        "madeira": MadeiraDialect, "azores": AzoresDialect,
    }
    sentence = "A vaca está no campo e o vinho verde é bom"
    for name, preset in presets.items():
        print(f"{name:9s} -> {pho.phonemize_sentence(sentence, 'pt-PT', regional_dialect=preset)}")
