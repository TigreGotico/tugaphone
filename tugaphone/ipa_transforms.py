"""Post-G2P IPA transforms modelling European Portuguese regional accents.

Each function has the signature ``(word: str, phonemes: str, postag: str) -> str``
and returns a transformed IPA string. A set of transforms, composed in order,
models one regional accent (see :mod:`tugaphone.regional`).

Phonemic grounding follows, in precedence order:
    - Cintra, L. F. Lindley (1971). *Nova proposta de classificação dos
      dialectos galego-portugueses*. Boletim de Filologia 22. The source for
      the North/South isoglosses (betacism, sibilant systems, diphthong
      retention) used throughout.
    - Ashby et al. (2012). *A Rule Based Pronunciation Generator and Regional
      Accent Databank for Portuguese* (Interspeech) — LUPo rule formalism.
    - Saramago (2006) / ALEPG (CLUL) — Atlas Linguístico-Etnográfico de
      Portugal e da Galiza; insular (Madeira/Açores) distributions.
    - Mateus & d'Andrade (2000), *The Phonology of Portuguese* — standard
      EP phoneme inventory and nasal representation.

The standard (Lisbon/Centro-Meridional) variety produced by the base G2P is
the neutral starting point; "retain" rules undo Lisbon-specific reductions
(/ej/→[ɐj], /ow/→[o]) rather than inventing northern features, matching the
de-biasing approach of Cintra's conservative-standard reference point.

Transforms operate on grapheme clusters, not Python characters, so combining
diacritics (nasal tilde U+0303, tie bars) stay attached to their base symbol.
"""

import re
import unicodedata
from typing import List

# Combining diacritics that bind to a preceding base symbol in IPA strings:
# combining tilde (nasalisation), inverted breve below (non-syllabic), tie bar.
_COMBINING = "̯̃͡"


def grapheme_clusters(text: str) -> List[str]:
    """Split an IPA string into grapheme clusters.

    A cluster is a base codepoint followed by any combining marks, so a
    nasalised vowel such as ``ɐ̃`` (U+0250 U+0303) or a non-syllabic glide
    ``j̃`` is returned as a single element. This lets rules slice and count by
    perceived symbol rather than by raw codepoint, avoiding the multi-codepoint
    corruption that plagues naive ``phonemes[:-n]`` slicing.
    """
    clusters: List[str] = []
    for ch in text:
        if clusters and unicodedata.combining(ch):
            clusters[-1] += ch
        else:
            clusters.append(ch)
    return clusters


# Inventory shared by several rules.
_ORAL_VOWELS = "aeiouɐɛɔɨyæøœɘ"
_NASAL_VOWELS = "ãẽĩõũ"  # NFC-composed nasal vowels
_VOWELS = _ORAL_VOWELS + _NASAL_VOWELS + "ɐ̃ɛ̃ɔ̃"
_CONSONANTS = "pbtdkɡgfvszʃʒmnɲɫlrʁɾβð"


# ---------------------------------------------------------------------------
# Diphthong retention (de-biasing Lisbon monophthongisation)
# ---------------------------------------------------------------------------

def retain_ou_diphthong(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Realise graphemic <ou> as the falling diphthong [ow].

    Phenomenon: the standard (Lisbon) variety reduces historical /ow/ to [o]
    (*ouro* [ˈoɾu]); the conservative standard and all northern varieties keep
    the diphthong [ˈowɾu]. This rule restores [ow] for the tonic vowel of a
    word whose orthography contains <ou>, i.e. it undoes the Lisbon
    monophthongisation rather than inventing a feature.

    Distribution: northern third + conservative standard (Cintra 1971, the
    "ou as o-u" isogloss). Words spelled <ô> are genuine monophthongs and are
    never touched.

    Source: Cintra (1971); whitepaper5 rule DB2/N2.
    """
    if "ô" in word:
        return phonemes
    if "ou" not in word.lower():
        return phonemes
    if word.startswith("ou") and phonemes.startswith("ˈo"):
        return "ˈow" + phonemes[len("ˈo"):]
    return re.sub(r"(\w)ˈo(?!w)", r"\1ˈow", phonemes)


def retain_ei_diphthong(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Realise graphemic <ei> as the diphthong [ej].

    Phenomenon: the standard (Lisbon) variety lowers the first element of /ej/
    to [ɐj] (*primeiro* [pɾiˈmɐjɾu]); the conservative standard and the north
    keep [ej] ([pɾiˈmejɾu]). This restores [ej] from the Lisbon [ɐj].

    Distribution: northern + conservative standard (Cintra 1971). The southern
    monophthongisation [ej]→[e] is handled separately by
    :func:`monophthongize_ei`.

    Source: Cintra (1971); whitepaper5 rule DB1/LX1.
    """
    return re.sub(r"(\w)ˈɐj", r"\1ˈej", phonemes)


def monophthongize_ei(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Monophthongise /ej/ (and Lisbon [ɐj]) to [e].

    Phenomenon: central-southern varieties (Ribatejano, Alentejano, Algarvio,
    Beira-Baixa) reduce the <ei> diphthong to a long-mid monophthong [e]:
    *primeiro* [pɾiˈmeɾu], *peixe* [ˈpeʃ(ɨ)].

    Distribution: Ribatejo, Alentejo, Algarve, Beira-Baixa (Cintra 1971;
    whitepaper5 rule RA1).
    """
    phonemes = re.sub(r"ˈ([ɐe])j", "ˈe", phonemes)
    return re.sub(r"([ɐe])j", "e", phonemes)


# ---------------------------------------------------------------------------
# Betacism — the defining northern isogloss
# ---------------------------------------------------------------------------

def betacism(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Merge /v/ into the labial stop /b/ (betacism).

    Phenomenon: in the northern third of Portugal the /v/–/b/ contrast is lost;
    both are realised as the bilabial stop [b] (*vaca* [ˈbakɐ], *vinho* [ˈbiɲu],
    *neve* [ˈnɛbɨ]). Any spirantised allophone [β] from the base G2P is folded
    into [b] as well, so the rule is categorical and position-independent.

    Distribution: all northern varieties — Minhoto, Transmontano, Duriense,
    Beirão — plus Galician (Cintra 1971, the single most-cited northern
    isogloss; whitepaper4 rule N1, whitepaper5 rule N1/DB4).

    This realisation as a stop [b] follows Cintra and the project gold
    transcriptions; an earlier draft modelling it as the approximant [β]
    conflicts with both and is dropped.
    """
    return phonemes.replace("v", "b").replace("β", "b")


# ---------------------------------------------------------------------------
# Northern vocalism
# ---------------------------------------------------------------------------

def reduce_vowel_centralization(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Resist centralisation of unstressed /ɨ/ to [e] between consonants.

    Phenomenon: northern (especially Minhoto) speech reduces unstressed vowels
    less than the standard, so the centralised [ɨ] of the standard surfaces as
    a clearer [e] in inter-consonantal position.

    Distribution: northern, weakly (Cintra 1971; whitepaper5 rule G3a, applied
    to the Portuguese north by analogy with Galician less-reduction). The gold
    northern transcriptions keep [ɨ] in most tokens, so this rule is excluded
    from the categorical northern preset and offered only for the maximal
    Minhoto reading.
    """
    return re.sub(
        rf"(?<=[{_CONSONANTS}])ɨ(?=[{_CONSONANTS}])", "e", phonemes
    )


def open_vowel_preference(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Open unstressed final /ɐ/ to [a] before a nasal or lateral.

    Phenomenon: northern speakers favour a more open [a] for /ɐ/ in final,
    unstressed syllables before /m, n, ɲ, l/.

    Distribution: northern, variable (Cintra 1971; DIALECT_PATTERNS "more open
    vowels"). Conditioned narrowly to avoid over-application; the broad
    de-centralisation of stressed /a/ is left to the base inventory.
    """
    return re.sub(r"ɐ(?=[mnɲl]\b)", "a", phonemes)


def conservative_o_nasal_retention(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Realise final -ão as the conservative nasal monophthong [õ].

    Phenomenon: parts of Trás-os-Montes and Alto-Minho keep the older [õ] where
    the standard has merged it into the nasal diphthong [ɐ̃w̃] (*pão* [põ],
    *irmão* [iɾˈmõ]).

    Distribution: Trás-os-Montes / Alto-Minho (Cintra 1971; whitepaper5 rule
    TM3). The matched ending is sliced by grapheme cluster, so the combining
    nasal tilde never desynchronises from its base vowel.
    """
    if not word.endswith("ão"):
        return phonemes
    clusters = grapheme_clusters(phonemes)
    # canonical tonic [ˈɐ̃w] / espeak variant [ˈɐ̃ʊ̃], possibly with a final
    # nasal tilde on the glide — match the ɐ̃ (+ glide) tail after a stress mark.
    tail = "".join(clusters[-2:])
    head = "".join(clusters[:-2])
    if re.fullmatch(r"ɐ̃[wʊ]̃?", tail):
        if head.endswith("ˈ"):
            return head + "õ"
        # stress mark sits one cluster earlier (ˈɐ̃w)
        if len(clusters) >= 3 and clusters[-3] == "ˈ":
            return "".join(clusters[:-3]) + "ˈõ"
        return head + "õ"
    return phonemes


def nasal_vowel_raising(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Raise the nasal vowel /ɐ̃/ to [ã].

    Phenomenon: northern nasal vowels are slightly raised/fronted relative to
    the standard; /ɐ̃/ tends toward [ã] (*mãe* [mˈãj̃]).

    Distribution: northern (Cintra 1971; DIALECT_PATTERNS). Operates on the
    grapheme cluster ``ɐ̃`` so the tilde is preserved.
    """
    return phonemes.replace("ɐ̃", "ã")


# ---------------------------------------------------------------------------
# Northern consonantism
# ---------------------------------------------------------------------------

def palatal_affrication_ch(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Affricate <ch>-derived /ʃ/ to [tʃ].

    Phenomenon: the historical affricate /tʃ/, merged with /ʃ/ in the standard,
    is preserved in the northeast: *chave* [ˈtʃavɨ], *chouriço* [tʃowˈɾisu].

    Distribution: Transmontano and Alto-Minhoto only — NOT the general north
    (Cintra 1971; whitepaper4 rule N3, whitepaper5 rule TM2). Only as many /ʃ/
    as there are <ch> digraphs are affricated, left to right; a coda-/s/ [ʃ]
    (e.g. *chaves* [ˈʃavɨʃ] → [ˈtʃavɨʃ], not [ˈtʃavɨtʃ]) is left untouched.
    """
    n_ch = word.lower().count("ch")
    if n_ch:
        return phonemes.replace("ʃ", "tʃ", n_ch)
    return phonemes


def rhotic_realization(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Realise onset /ʁ/ as the alveolar trill [r].

    Phenomenon: conservative and rural northern varieties keep the apical trill
    [r] for the strong rhotic where the standard has the uvular [ʁ] (*rio*
    [ˈriu], *carro* [ˈkaru]).

    Distribution: rural/conservative north and much of the interior (Cintra
    1971; DIALECT_PATTERNS). The standard uvular [ʁ] is in fact retained in the
    urban Porto/Braga gold, so this rule belongs to the conservative-Minhoto
    reading, not the categorical northern preset.
    """
    phonemes = re.sub(r"^ʁ", "r", phonemes)
    phonemes = re.sub(rf"(?<=[{_CONSONANTS}])ʁ", "r", phonemes)
    return phonemes


def epenthetic_j_before_palatal(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Insert an epenthetic glide [j] before a palatal consonant.

    Phenomenon: a short [j] is inserted after a low/mid vowel and before a
    palatal /ʎ, ɲ, ʃ/: *velho* [ˈvɛjʎu], *abelha* [aˈbejʎɐ], *bolacha*
    [buˈlajʃɐ], *banha* [ˈbajɲɐ].

    Distribution: Minho and adjacent northwest (Cintra 1971; DIALECT_PATTERNS).
    Fires on stressed and unstressed [a ɐ e ɛ]; ``(?!j)`` prevents a double
    glide. Rule: V → Vj / __[ʎ ɲ ʃ].
    """
    return re.sub(r"(ˈ?[aɐeɛ])(?=[ʎɲʃ])(?!j)", r"\1j", phonemes)


def rising_diphthong_o(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Diphthongise stressed /o/ to the rising diphthong [wo].

    Phenomenon: the Porto / Baixo-Minhoto area diphthongises stressed mid
    vowels (*Porto* [ˈpwoɾtu], *bolo* [ˈbwolu]); the transcription [uo] is used
    here for the rising on-glide.

    Distribution: Porto variety / Douro Litoral, shared with an Astur-Leonese
    archaic stratum (Cintra 1971; whitepaper5 rule PT2, whitepaper4 §3.3).
    """
    return re.sub(r"ˈo(?![wj])", "ˈuo", phonemes)


# ---------------------------------------------------------------------------
# Northeast (Transmontano) sibilants and denasalisation
# ---------------------------------------------------------------------------

def intervocalic_s_voicing(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Voice /s/ to [z] between vowels and word-finally after a vowel.

    Phenomenon: a lenition pattern in Transmontano voicing intervocalic and
    final post-vocalic /s/ (*moço* [ˈmozu]).

    Distribution: Transmontano and adjacent northeast (Cintra 1971;
    DIALECT_PATTERNS).
    """
    phonemes = re.sub(rf"(?<=[{_VOWELS}])s(?=[{_VOWELS}])", "z", phonemes)
    phonemes = re.sub(rf"(?<=[{_VOWELS}])s(?=$)", "z", phonemes)
    return phonemes


def initial_z_devoicing(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Devoice word-initial /z/ to [s] before a vowel.

    Phenomenon: part of the Transmontano four-sibilant reorganisation; initial
    /z/ may surface as [s] (*zero* [ˈseɾu]).

    Distribution: Transmontano (Cintra 1971; DIALECT_PATTERNS).
    """
    return re.sub(rf"^z(?=[{_VOWELS}])", "s", phonemes)


def final_nasal_denasalization(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Denasalise the final vowel of -agem-class words after /ʒ/.

    Phenomenon: Transmontano tends to denasalise unstressed final nasal vowels
    after /ʒ/ (*viagem* [viˈaʒe], *paragem* [pɐˈɾaʒe]).

    Distribution: Transmontano (Cintra 1971; DIALECT_PATTERNS). Matched by
    grapheme cluster so the nasal tilde is consumed with its base vowel.
    """
    phonemes = re.sub(r"ʒẽ$", "ʒe", phonemes)
    phonemes = re.sub(r"ʒɐ̃$", "ʒɐ", phonemes)
    phonemes = re.sub(r"ʒõ$", "ʒo", phonemes)
    return phonemes


def nasal_diphthongization_e(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Diphthongise nasal /ẽ/ to [eĩ] before a consonant.

    Phenomenon: the Fafe-area realisation of nasal /ẽ/ as a nasal diphthong
    [eĩ] in a closed syllable (*gente* [ˈʒeĩtɨ], *doente* [duˈeĩtɨ]).

    Distribution: Fafe / inner Minho (DIALECT_PATTERNS; the user's field notes).
    The negative lookahead keeps /ẽ/ before a vowel intact. The nasal /ẽ/ is
    matched whether the G2P emits it NFC-composed (U+1EBD) or NFD-decomposed
    (e + combining tilde U+0303); output uses the NFC form.
    """
    e_nasal = r"(?:ẽ|ẽ)"
    follow = r"(?![aeiouɐɛɔɲʎ]|ẽ|ẽ|̃)"
    return re.sub(rf"{e_nasal}{follow}", "eĩ", phonemes)


def nasal_glide_palatalization(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Reinforce a final nasal glide into a palatal nasal [ɲ].

    Phenomenon: word-final nasal glides [j̃]/[w̃] after a nasal vowel are
    reinforced into a full palatal nasal in parts of the north (*mãe* [mˈɐ̃j̃ɲ],
    *bem* [bẽɲ]).

    Distribution: Braga area / northwest (DIALECT_PATTERNS). Rule:
    Ṽj̃ → Ṽɲ / _#. Operates on grapheme clusters so the nasalised glide is
    matched as a unit.
    """
    nasal_vowels = "ãẽĩõũ" + "ɐ̃ɛ̃ɔ̃"
    phonemes = re.sub(rf"([{nasal_vowels}])[jw]̃$", r"\1ɲ", phonemes)
    phonemes = re.sub(rf"([{nasal_vowels}])j$", r"\1jɲ", phonemes)
    phonemes = re.sub(rf"([{nasal_vowels}])ĩ̯$", r"\1ɲ", phonemes)
    return phonemes


# ---------------------------------------------------------------------------
# Central-southern (Alentejo / Algarve) features
# ---------------------------------------------------------------------------

def intervocalic_d_deletion(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Delete intervocalic /d/ (often via [ð]).

    Phenomenon: the Alentejo weakens and deletes intervocalic /d/, especially
    in the -ada/-ido participial endings and high-frequency words (*nada*
    [ˈnaɐ], *vida* [ˈviɐ], *comida* [kuˈmiɐ]).

    Distribution: Alentejo, parts of the Algarve and Beira-Baixa (Cintra 1971;
    DIALECT_PATTERNS). Both the stop [d] and its spirantised allophone [ð] are
    deleted between two vowels.
    """
    return re.sub(rf"(?<=[{_VOWELS}])[dð](?=[{_VOWELS}])", "", phonemes)


def simplify_nasal_diphthong_em(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Simplify the -em nasal diphthong [ɐ̃j̃] to the nasal monophthong [ẽ].

    Phenomenon: the central-south reduces the -em/-ém nasal diphthong to a
    nasal monophthong (*bem* [bẽ], *também* [tɐ̃ˈbẽ]).

    Distribution: Alentejo and adjacent central-south (Cintra 1971;
    DIALECT_PATTERNS, "êm" notation). Matched by grapheme cluster so the
    nasalised glide is removed cleanly.
    """
    return re.sub(r"ɐ̃[jw]̃?$", "ẽ", phonemes)


def simplify_meu_class(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Monophthongise the [ew] of the *meu* class to [e].

    Phenomenon: the central-south reduces the falling diphthong [ew] of
    possessives and similar items to [e] (*meu* [me], *teu* [te]); the plural
    keeps the sibilant (*meus* [meʃ]).

    Distribution: Alentejo, Algarve (Cintra 1971; DIALECT_PATTERNS). Restricted
    to words whose orthography ends in <eu>/<eus> to avoid touching unrelated
    [ew] sequences.
    """
    low = word.lower()
    if low.endswith("eus") or low.endswith("eus."):
        return re.sub(r"ew(?=ʃ?$)", "e", phonemes)
    if low.endswith("eu") or low.endswith("eu."):
        return re.sub(r"ew$", "e", phonemes)
    return phonemes


def sibilant_voicing_sandhi(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Voice a word-final /s/-derived [ʃ] before a following vowel to [ʒ].

    Phenomenon: across a word boundary, the coda sibilant voices before a
    vowel-initial word (*mas a* [maʒ ɐ], *muitos amigos* [ˈmũj̃tuʒ ɐˈmiɡuʒ]).
    Applied within a token to its final [ʃ] when the orthography ends in <s>.

    Distribution: general EP sandhi, marked here for the southern/insular
    presets where the gold transcribes it word-internally on plurals (Cintra
    1971; DIALECT_PATTERNS).
    """
    if word.lower().rstrip(".").endswith("s"):
        return re.sub(r"ʃ$", "ʒ", phonemes)
    return phonemes


# ---------------------------------------------------------------------------
# Insular (Madeira / Açores) features
# ---------------------------------------------------------------------------

def lateral_palatalization(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Palatalise /l/ to [ʎ] before [i] (insular l-palatalisation).

    Phenomenon: Madeira and the Azores palatalise /l/ adjacent to a high front
    vowel in specific items (*quilo* → [ˈkiʎu], *mochila* → [muˈʃiʎɐ]).

    Distribution: Madeira and Azores (ALEPG / Segura & Saramago; DIALECT_PATTERNS).
    Conditioned on a preceding [i] to model the lexically restricted set the
    field notes describe.
    """
    return re.sub(r"(?<=i)l(?=u|ɐ|ɨ|$)", "ʎ", phonemes)


def nasal_diphthong_to_nasal_plus_n(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Realise a final nasal diphthong as nasal vowel + [n].

    Phenomenon: in Madeira and the Azores the plural nasal diphthongs surface
    as a nasal vowel followed by an alveolar nasal (*cães* [kɐ̃ns], *verões*
    [vɨˈɾõns]); the final sibilant is absorbed.

    Distribution: Madeira and Azores (ALEPG; DIALECT_PATTERNS). Matched by
    grapheme cluster so the nasal vowel keeps its tilde.
    """
    phonemes = re.sub(r"õj̃?ʃ?$", "õns", phonemes)
    phonemes = re.sub(r"ɐ̃j̃?ʃ?$", "ɐ̃ns", phonemes)
    return phonemes


def fronted_stressed_u(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Front stressed /u/ to [y] (Azorean micaelense fronting).

    Phenomenon: São Miguel (Azores) fronts stressed /u/ to a rounded front [y],
    French-*tu*-like (*tu* [ty], *número* [ˈnymɨɾu]).

    Distribution: Açores, São Miguel (ALEPG / Segura & Saramago;
    DIALECT_PATTERNS). Also documented for Beira-Baixa/Alto-Alentejo
    (whitepaper5 rule BB1).
    """
    return phonemes.replace("ˈu", "ˈy")


def monophthongize_oi(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """Monophthongise the [oj] diphthong to [o] (Azorean *boi* class).

    Phenomenon: the Azores monophthongise <oi> to a mid back [o] (*boi* [bo]).

    Distribution: Açores (DIALECT_PATTERNS). Restricted to orthographic <oi>.
    """
    if "oi" in word.lower():
        return re.sub(r"oj", "o", phonemes)
    return phonemes
