"""Post-G2P IPA transforms modelling European Portuguese regional accents.

Each function has the signature ``(word: str, phonemes: str) -> str`` and
returns a transformed IPA string. A set of transforms, composed in order, models
one regional accent (see :mod:`tugaphone.regional`).

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
# Orthographic (grapheme) vowels, for rules that condition on spelling.
_ORTHO_VOWELS = "aeiouáéíóúàâêôãõ"

# ---------------------------------------------------------------------------
# Diphthong retention (de-biasing Lisbon monophthongisation)
# ---------------------------------------------------------------------------

def retain_ou_diphthong(word: str, phonemes: str) -> str:
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

def retain_ei_diphthong(word: str, phonemes: str) -> str:
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

def monophthongize_ei(word: str, phonemes: str) -> str:
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

def betacism(word: str, phonemes: str) -> str:
    """Merge /v/ into the single labial phoneme /b/ (betacism).

    Phenomenon: in the northern third of Portugal the /v/–/b/ contrast is lost;
    both fall together in one labial phoneme. Cintra (BF 22:87) is explicit that
    the merged phoneme "é realizado ora como oclusiva, ora como fricativa (ou
    espirante): b ou β" — i.e. it surfaces as the stop [b] in strong position
    (word-initial, post-consonant: *vaca* [ˈbakɐ], *vinho* [ˈbiɲu]) and as the
    spirant [β] intervocalically (*neve* [ˈnɛβɨ], *uva* [ˈuβɐ]), exactly the
    positional [b]~[β] allophony EP already applies to underlying /b/. The
    merger is categorical; the *realisation* is positionally conditioned, so an
    existing intervocalic spirant [β] is kept, not folded to a stop.

    Distribution: all northern varieties — Minhoto, Transmontano, Duriense,
    Beirão — plus Galician (Cintra 1971:87, the single most-cited northern
    isogloss; whitepaper4 rule N1, whitepaper5 rule N1/DB4). o2i models the same
    two realisations (allophones ``v: [b, β]`` in the porto/trásosmontes specs).

    Source: Cintra (1971), *Boletim de Filologia* 22:87 ("b ou β").
    """
    # /v/ between vowels merges to the spirant realisation [β]; elsewhere to [b].
    phonemes = re.sub(rf"(?<=[{_VOWELS}])v(?=[{_VOWELS}])", "β", phonemes)
    return phonemes.replace("v", "b")

# ---------------------------------------------------------------------------
# Northern vocalism
# ---------------------------------------------------------------------------

def reduce_vowel_centralization(word: str, phonemes: str) -> str:
    """Resist centralisation of unstressed /ɨ/ to [e] between consonants.

    Phenomenon: northern (especially Minhoto) speech reduces unstressed vowels
    less than the standard, so the centralised [ɨ] of the standard surfaces as
    a clearer [e] in inter-consonantal position.

    Distribution: northern, weakly (Cintra 1971; whitepaper5 rule G3a, applied
    to the Portuguese north by analogy with Galician less-reduction). The gold
    northern transcriptions keep [ɨ] in most tokens, so this rule is excluded
    from the categorical northern preset and offered only for the maximal
    Minhoto reading.

    PARTIALLY-VERIFIED — the direction (less northern atonic reduction) is
    Cintra's trait 7, but the exact [ɨ]→[e] target mapping is not pinned to a
    source. Use with caution.
    """
    return re.sub(
        rf"(?<=[{_CONSONANTS}])ɨ(?=[{_CONSONANTS}])", "e", phonemes
    )

def open_vowel_preference(word: str, phonemes: str) -> str:
    """Open unstressed final /ɐ/ to [a] before a nasal or lateral.

    Phenomenon: northern speakers favour a more open [a] for /ɐ/ in final,
    unstressed syllables before /m, n, ɲ, l/.

    Distribution: northern, variable (DIALECT_PATTERNS "more open vowels").
    Conditioned narrowly to avoid over-application.

    UNVERIFIED — the general "more open a" direction is Cintra's trait 7, but
    that concerns the TONIC /a/; the specific conditioning here (final-atonic
    /ɐ/ before a nasal/lateral) is not attested in a source. Use with caution.
    """
    return re.sub(r"ɐ(?=[mnɲl]\b)", "a", phonemes)

def conservative_o_nasal_retention(word: str, phonemes: str) -> str:
    """Realise final -ão as the conservative nasal monophthong [õ].

    Phenomenon: parts of Trás-os-Montes and Alto-Minho keep the older [õ] where
    the standard has merged it into the nasal diphthong [ɐ̃w̃] (*pão* [põ],
    *irmão* [iɾˈmõ]).

    Distribution: Trás-os-Montes / Alto-Minho (whitepaper5 rule TM3). The
    matched ending is sliced by grapheme cluster, so the combining nasal tilde
    never desynchronises from its base vowel.

    PARTIALLY-VERIFIED — the archaic interior -ão→[õ] outcome is real
    dialectology (Trás-os-Montes/Alto-Minho), but no explicit Cintra page was
    located for the [õ] realisation; corroborate against Segura (2013)/ALEPG
    before trusting. Plausible.
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

def nasal_vowel_raising(word: str, phonemes: str) -> str:
    """Raise the nasal vowel /ɐ̃/ to [ã].

    Phenomenon: northern nasal vowels are slightly raised/fronted relative to
    the standard; /ɐ̃/ tends toward [ã] (*mãe* [mˈãj̃]).

    Distribution: northern (DIALECT_PATTERNS). Operates on the grapheme cluster
    ``ɐ̃`` so the tilde is preserved.

    UNVERIFIED — not corroborated by an academic source; rests only on the
    repo's own DIALECT_PATTERNS field notes. Use with caution.
    """
    return phonemes.replace("ɐ̃", "ã")

# ---------------------------------------------------------------------------
# Northern consonantism
# ---------------------------------------------------------------------------

def palatal_affrication_ch(word: str, phonemes: str) -> str:
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

def rhotic_realization(word: str, phonemes: str) -> str:
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

def epenthetic_j_before_palatal(word: str, phonemes: str) -> str:
    """Insert an epenthetic glide [j] before a palatal consonant.

    Phenomenon: a short [j] is inserted after a low/mid vowel and before a
    palatal /ʎ, ɲ, ʃ/: *velho* [ˈvɛjʎu], *abelha* [aˈbejʎɐ], *bolacha*
    [buˈlajʃɐ], *banha* [ˈbajɲɐ].

    Distribution: Minho and adjacent northwest (DIALECT_PATTERNS). Fires on
    stressed and unstressed [a ɐ e ɛ]; ``(?!j)`` prevents a double glide. Rule:
    V → Vj / __[ʎ ɲ ʃ].

    UNVERIFIED — the yod before a palatal ([ɐj]ʎ, *telha*) also occurs in
    STANDARD EP (Mateus & d'Andrade 2000), so the Minho-only attribution is
    doubtful and no source pins it as a distinctive Minho feature. Use with
    caution.
    """
    return re.sub(r"(ˈ?[aɐeɛ])(?=[ʎɲʃ])(?!j)", r"\1j", phonemes)

def rising_diphthong_o(word: str, phonemes: str) -> str:
    """Diphthongise stressed close /o/ to the rising diphthong [wo].

    Phenomenon: the Porto / Baixo-Minho / Douro-Litoral area diphthongises the
    tonic close mid vowels. Cintra (1971:684) names it "a ditongação, tão
    caracterizadora, das vogais tónicas fechadas [e] em [je], [o] em [wo] (por
    vezes [wɔ])" — the single defining Porto marker. The back-vowel half is
    *Porto* [ˈpwoɾtu], *bolo* [ˈbwolu], *avô* [ɐˈbwo]. The on-glide is [w], so
    the diphthong is [wo] (matching o2i ``PT_PORTO_DIPHTHONGISE_O``); the front
    counterpart /e/→[je] is :func:`rising_diphthong_e`.

    Distribution: Porto variety / Baixo-Minho / Douro-Litoral (Cintra 1971:684;
    whitepaper5 rule PT2, whitepaper4 §3.3).

    Source: Cintra (1971:684), *Boletim de Filologia* 22 ("[o] em [wo]").
    """
    return re.sub(r"ˈo(?![wj])", "ˈwo", phonemes)

def rising_diphthong_e(word: str, phonemes: str) -> str:
    """Diphthongise stressed close /e/ to the rising diphthong [je].

    Phenomenon: the front-vowel half of the defining Porto tonic-vowel
    diphthongisation — Cintra's "[e] em [je]" (*mês* [ˈmjeʃ], *ele* [ˈjelɨ],
    *pêlo* [ˈpjelu]). Companion to :func:`rising_diphthong_o` ("[o] em [wo]");
    the two together are Cintra's "ditongação, tão caracterizadora, das vogais
    tónicas fechadas". Fires on the close [e] the base G2P yields; genuinely
    open tonic [ɛ] (*pé*, *café*) does not diphthongise, matching o2i
    ``PT_PORTO_DIPHTHONGISE_E``.

    Distribution: Porto variety / Baixo-Minho / Douro-Litoral (Cintra 1971:684).


    Source: Cintra (1971:684), *Boletim de Filologia* 22 ("[e] em [je]").
    """
    return re.sub(r"ˈe(?![wji])", "ˈje", phonemes)

# ---------------------------------------------------------------------------
# Northeast (Transmontano) sibilants and denasalisation
# ---------------------------------------------------------------------------

def intervocalic_s_voicing(word: str, phonemes: str) -> str:
    """Mark the northeast four-sibilant contrast: apico-alveolar ⟨s,ss⟩.

    Re-scoped correction. Cintra's trait 2 (his single most diagnostic
    North/South isogloss, 1971:93) is NOT a voicing of /s/ — it is a PLACE
    contrast: Transmontano/Alto-Minhoto keep a medieval four-sibilant system in
    which the graphemes ⟨s⟩ (initial, final) and ⟨ss⟩ (interior) realise the
    apico-alveolar [s̺] (with its voiced intervocalic-⟨s⟩ counterpart [z̺]),
    contrasting with the laminal (predorsodental) [s] of ⟨c,ç⟩ and [z] of ⟨z⟩.
    The minimal pairs stay distinct: *passo* [ˈpas̺u] vs *paço* [ˈpasu], *coser*
    [kuˈz̺eɾ] vs *cozer* [kuˈzeɾ]. The earlier rule voiced ⟨ç⟩ (*moço*→[ˈmozu]),
    which no source describes — ⟨ç⟩ is laminal /s/ and is now left untouched.

    Only orthographically unambiguous positions are marked (a phoneme-level,
    orthography-blind engine cannot fully reconstruct the source grapheme; the
    complete four-sibilant model is the o2i pt-PT-x-trasosmontes spec). ⟨s⟩/⟨ss⟩
    apical realisations are surface-equivalent to the retroflex-like [ʂ ʐ] Cintra
    calls "s beirão / reverso"; the [s̺ z̺] symbols follow o2i.

    Distribution: Transmontano and Alto-Minhoto (Cintra 1971:93 note 29;
    Álvarez Pérez 2014:37 §4).

    Source: Cintra (1971:93) — "um sistema de quatro sibilantes… [s̺] e [z̺]
    ápico-alveolares (grafemas s e ss)… opondo-se a… [s] e [z] predorsodentais
    (grafemas c e,i, ç e z)".
    """
    low = word.lower()
    # word-initial ⟨s⟩ + vowel → apico-alveolar [s̺]
    if re.match(rf"s[{_ORTHO_VOWELS}]", low):
        phonemes = re.sub(r"^(ˈ?)s", r"\1s̺", phonemes)
    # interior ⟨ss⟩ → apico-alveolar [s̺]; unambiguous only without a laminal
    # ⟨ç/ce/ci⟩ in the same token that would also yield an intervocalic [s].
    if "ss" in low and "ç" not in low and not re.search(r"c[eiéí]", low):
        phonemes = re.sub(rf"(?<=[{_VOWELS}])s(?=[{_VOWELS}])", "s̺", phonemes)
    # intervocalic single ⟨s⟩ (base G2P voices it to [z]) → apico-alveolar [z̺];
    # unambiguous only when no ⟨z⟩ grapheme could account for the [z].
    if re.search(rf"[{_ORTHO_VOWELS}]s[{_ORTHO_VOWELS}]", low) and "ss" not in low and "z" not in low:
        phonemes = re.sub(rf"(?<=[{_VOWELS}])z(?=[{_VOWELS}])", "z̺", phonemes)
    return phonemes

def initial_z_devoicing(word: str, phonemes: str) -> str:
    """Devoice word-initial /z/ to [s] before a vowel — a GALICIAN trait.

    Re-attributed correction. This is Cintra's trait 6, the *Galician* loss of
    the voiced/voiceless sibilant opposition through devoicing ("de /z/ a /s/",
    1971:451–457), NOT a Portuguese Transmontano feature. Conservative NE
    Portuguese (Transmontano/Alto-Minhoto) does the OPPOSITE: it keeps the
    voiced apico-alveolar [z̺] (see :func:`intervocalic_s_voicing` and the o2i
    pt-PT-x-trasosmontes spec). This primitive is therefore removed from the
    Transmontano preset and is offered only as a Galician-contact reading.

    Phenomenon (Galician): word-initial /z/ surfaces as [s] (*zero* [ˈseɾu]).

    Distribution: Galician and the Galician-Portuguese contact fringe (Cintra
    1971:451–457, trait 6). Do NOT compose into a Transmontano accent.


    Source: Cintra (1971:451–457), *Boletim de Filologia* 22, trait 6.
    """
    return re.sub(rf"^z(?=[{_VOWELS}])", "s", phonemes)

def final_nasal_denasalization(word: str, phonemes: str) -> str:
    """Denasalise the final vowel of -agem-class words after /ʒ/.

    Phenomenon: Transmontano tends to denasalise unstressed final nasal vowels
    after /ʒ/ (*viagem* [viˈaʒe], *paragem* [pɐˈɾaʒe]).

    Distribution: Transmontano (DIALECT_PATTERNS). Matched by grapheme cluster
    so the nasal tilde is consumed with its base vowel.

    UNVERIFIED — not corroborated by an academic source; rests only on the
    repo's own DIALECT_PATTERNS field notes. Use with caution.
    """
    phonemes = re.sub(r"ʒẽ$", "ʒe", phonemes)
    phonemes = re.sub(r"ʒɐ̃$", "ʒɐ", phonemes)
    phonemes = re.sub(r"ʒõ$", "ʒo", phonemes)
    return phonemes

def nasal_diphthongization_e(word: str, phonemes: str) -> str:
    """Diphthongise nasal /ẽ/ to [eĩ] before a consonant.

    Phenomenon: the Fafe-area realisation of nasal /ẽ/ as a nasal diphthong
    [eĩ] in a closed syllable (*gente* [ˈʒeĩtɨ], *doente* [duˈeĩtɨ]).

    Distribution: Fafe / inner Minho (DIALECT_PATTERNS; the user's field notes).
    The negative lookahead keeps /ẽ/ before a vowel intact. The nasal /ẽ/ is
    matched whether the G2P emits it NFC-composed (U+1EBD) or NFD-decomposed
    (e + combining tilde U+0303); output uses the NFC form.

    UNVERIFIED — a single Fafe field note ("a geinte"); no academic source
    locates this realisation. Use with caution.
    """
    e_nasal = r"(?:ẽ|ẽ)"
    follow = r"(?![aeiouɐɛɔɲʎ]|ẽ|ẽ|̃)"
    return re.sub(rf"{e_nasal}{follow}", "eĩ", phonemes)

def nasal_glide_palatalization(word: str, phonemes: str) -> str:
    """Reinforce a final nasal glide into a palatal nasal [ɲ].

    Phenomenon: word-final nasal glides [j̃]/[w̃] after a nasal vowel are
    reinforced into a full palatal nasal in parts of the north (*mãe* [mˈɐ̃j̃ɲ],
    *bem* [bẽɲ]).

    Distribution: Braga area / northwest (DIALECT_PATTERNS). Rule:
    Ṽj̃ → Ṽɲ / _#. Operates on grapheme clusters so the nasalised glide is
    matched as a unit.

    UNVERIFIED — northern reinforcement of final -em is reported
    impressionistically (Braga field note) but not pinned to an academic
    source. Use with caution.
    """
    nasal_vowels = "ãẽĩõũ" + "ɐ̃ɛ̃ɔ̃"
    phonemes = re.sub(rf"([{nasal_vowels}])[jw]̃$", r"\1ɲ", phonemes)
    phonemes = re.sub(rf"([{nasal_vowels}])j$", r"\1jɲ", phonemes)
    phonemes = re.sub(rf"([{nasal_vowels}])ĩ̯$", r"\1ɲ", phonemes)
    return phonemes

# ---------------------------------------------------------------------------
# Central-southern (Alentejo / Algarve) features
# ---------------------------------------------------------------------------

def intervocalic_d_deletion(word: str, phonemes: str) -> str:
    """Delete intervocalic /d/ (often via [ð]).

    Phenomenon: the Alentejo weakens and deletes intervocalic /d/, especially
    in the -ada/-ido participial endings and high-frequency words (*nada*
    [ˈnaɐ], *vida* [ˈviɐ], *comida* [kuˈmiɐ]).

    Distribution: Alentejo, parts of the Algarve and Beira-Baixa (Cintra 1971;
    DIALECT_PATTERNS). Both the stop [d] and its spirantised allophone [ð] are
    deleted between two vowels.
    """
    return re.sub(rf"(?<=[{_VOWELS}])[dð](?=[{_VOWELS}])", "", phonemes)

def simplify_nasal_diphthong_em(word: str, phonemes: str) -> str:
    """Simplify the -em nasal diphthong [ɐ̃j̃] to the nasal monophthong [ẽ].

    Phenomenon: the central-south reduces the -em/-ém nasal diphthong to a
    nasal monophthong (*bem* [bẽ], *também* [tɐ̃ˈbẽ]).

    Distribution: Alentejo and adjacent central-south (Cintra 1971;
    DIALECT_PATTERNS, "êm" notation). Matched by grapheme cluster so the
    nasalised glide is removed cleanly.
    """
    return re.sub(r"ɐ̃[jw]̃?$", "ẽ", phonemes)

def simplify_meu_class(word: str, phonemes: str) -> str:
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

def sibilant_voicing_sandhi(word: str, phonemes: str) -> str:
    """Voice a coda [ʃ] to [ʒ] across a word boundary before a vowel-initial word.

    Corrected mechanism. This is genuinely EXTERNAL sandhi — the coda sibilant
    voices only before a following vowel-initial word (*mas a* [maʒ ɐ], *muitos
    amigos* [ˈmũj̃tuʒ ɐˈmiɡuʃ], PWL "tá-**j** a ver", "muito**j** amigos"). The
    earlier rule applied it word-INTERNALLY to any token whose spelling ends in
    ⟨s⟩, wrongly yielding [meʒ] for *meus* said in isolation. It is now gated on
    a real cross-word seam: it fires only when ``word``/``phonemes`` hold a
    multi-word span and the [ʃ] is immediately followed by a space and a
    vowel-initial word. A single token in isolation is left unchanged (the true
    seam handling belongs to the o2i sentence-level ``sandhi_rules``).

    Distribution: general EP external sandhi, strongest in the south/insular
    presets (Algarve/São Miguel; Cintra 1971; DIALECT_PATTERNS).

    Source: EP external voicing sandhi (Mateus & d'Andrade 2000); native PWL
    transcripts (pwl-8-accents.md).
    """
    return re.sub(rf"ʃ(?=\s+ˈ?[{_VOWELS}])", "ʒ", phonemes)

# ---------------------------------------------------------------------------
# Insular (Madeira / Açores) features
# ---------------------------------------------------------------------------

def lateral_palatalization(word: str, phonemes: str) -> str:
    """Palatalise /l/ to [ʎ] before [i] (insular l-palatalisation).

    Phenomenon: Madeira and the Azores palatalise /l/ adjacent to a high front
    vowel in specific items (*quilo* → [ˈkiʎu], *mochila* → [muˈʃiʎɐ]).

    Distribution: Madeira and Azores (Segura 2013; ALEPG; DIALECT_PATTERNS).
    Conditioned on a preceding [i] AND a FOLLOWING vowel — matching o2i
    ``MAD_L_PALATALISATION``, which requires an onset /l/ (a following vowel).
    The earlier ``$`` (word-final) branch is dropped: it wrongly palatalised a
    coda /l/ (*mil*→[miʎ]); a coda /l/ is realised dark [ɫ] and is never
    palatalised.

    Source: Segura (2013); o2i MAD_L_PALATALISATION.
    """
    return re.sub(rf"(?<=i)l(?=[{_VOWELS}])", "ʎ", phonemes)

def nasal_diphthong_to_nasal_plus_n(word: str, phonemes: str) -> str:
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

def fronted_stressed_u(word: str, phonemes: str) -> str:
    """Front stressed /u/ to [y] (Azorean micaelense fronting).

    Phenomenon: São Miguel (Azores) fronts stressed /u/ to a rounded front [y],
    French-*tu*-like (*tu* [ty], *número* [ˈnymɨɾu]).

    Distribution: Açores, São Miguel (ALEPG / Segura & Saramago;
    DIALECT_PATTERNS); also Alto-Alentejo and Beira-Baixa, which Cintra
    (1971:726) delimits by exactly this u→[y] isogloss ("palatalização… da
    vogal tónica u"), and whitepaper5 rule BB1.

    The fronting is blocked before a tautosyllabic coda liquid or sibilant
    (*azul* [ɐˈzuɫ], *Furnas* [ˈfuɾnɐʃ]), where São Miguel keeps [u] — matching
    o2i ``ACO_U_KEEP_BEFORE_CODA`` (followed by ``ɫ l ɾ ʁ ʃ ʒ``).

    Source: Cintra (1971:726); o2i ACO_U_KEEP_BEFORE_CODA + ACO_STRESSED_U_FRONTING
    (Rogers 1948).
    """
    return re.sub(r"ˈu(?![ɫlɾʁʃʒ])", "ˈy", phonemes)

def monophthongize_oi(word: str, phonemes: str) -> str:
    """Monophthongise the [oj] diphthong to [o] (Azorean *boi* class).

    Phenomenon: the Azores monophthongise <oi> to a mid back [o] (*boi* [bo]).

    Distribution: Açores (DIALECT_PATTERNS). Restricted to orthographic <oi>.
    """
    if "oi" in word.lower():
        return re.sub(r"oj", "o", phonemes)
    return phonemes
