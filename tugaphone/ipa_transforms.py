"""
NOTE: dialect modeling is a work in progress. Use at your own risk.

each function in this file is a transformation of ipa: str -> ipa: str

any number of transformations can be applied at runtime, a set of transformations models a regional accent
"""

import re


# Minho Vocalism: Suppression of Standard EP Vowel Centralization
#   Minho speakers are known for favoring "more open vowels".
#   This is interpreted as a resistance to the extreme centralization of unstressed vowels common in the south.

def reduce_vowel_centralization(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Replace the centralized vowel ɨ with e when it occurs between consonants (targeting unstable/unstressed environments).

    This transformation targets occurrences of the centralized vowel /ɨ/ in consonant---consonant positions and replaces them with /e/, modelling resistance to vowel centralization in pre-tonic or unstressed contexts.

    Parameters:
        word (str): The orthographic word (unused by the transformation but kept for API consistency).
        phonemes (str): The IPA phoneme string to transform.
        postag (str): Part-of-speech tag (unused by the transformation).

    Returns:
        str: The transformed phoneme string with qualifying instances of ɨ replaced by e.
    """
    # Replace central vowel /ɨ/ with /e/ when between consonants (unstressed environments)
    # Example: /pɨtɨ/ → /petɨ/, /bɨ/ → /be/
    phonemes = re.sub(r'(?<=[pbtdkgfvszʃʒmnɲlr])ɨ(?=[pbtdkgfvszʃʒmnɲlr])', 'e', phonemes)
    return phonemes


def open_vowel_preference(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Placeholder for an "open vowel" preference that would realize /ɐ/ as a more open [a] in final and unstressed syllables before nasal or lateral consonants (target: ɐ → a / __[mnɲl]\b).

    Currently this function is a no-op and returns the input `phonemes` unchanged.

    Minho speakers tend to realize /ɐ/ as a slightly more open [a] in final and unstressed syllables,
    especially before nasal or lateral consonants.
    /ɐ/ → [a] / __[mnɲl]\b

    Returns:
        The (possibly transformed) phoneme string; currently identical to the input `phonemes`.
    """
    # phonemes = re.sub(r'ɐ(?=[mnɲl]\b)', 'a', phonemes)
    return phonemes


# Minho Diphthong Realization (Non-Monophthongization)
#   Minho speakers pronounce diphthongs clearly and distinctly, resisting the southern tendency to reduce them.
def retain_ou_diphthong(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Ensure graphemic <ou> is realized as an /ow/ diphthong in the phoneme string.

    Retention of 'ou':
        The diphthong represented by <ou> must be retained as a distinct diphthong [ou] or [ow],
        overriding the standard EP tendency to reduce it to [o] in unstressed contexts.
        /o/ → [ow] / (derived from <ou>). eg. "ouro" instead of "ôro"

    This restores or preserves the diphthong produced by the grapheme sequence "ou" (typically /ou/ or /ow/) when it has been reduced to /o/ by upstream processing. Special behaviours:
    - If the word starts with "ou" and phonemes start with "ˈo", the leading tonic /ˈo/ is changed to /ˈow/.
    - If the orthography contains "ô", the phonemes are left unchanged.
    - If "ou" occurs elsewhere in the word, tonic occurrences of `ˈo` are promoted to `ˈow`.
    - The word "boa" is returned as the fixed mapping "bˈowɐ".

    Returns:
        str: The phoneme string with `/ow/` diphthong restored where applicable.
    """
    # NOTE: the lisbon accent reduces ˈow to ˈo
    # this restores "proper portuguese phonetics"
    # rather than adding a transform for minho accent,
    # it's undoing one from lisbon accent that affects the base G2P
    if word.startswith('ou') and phonemes.startswith("ˈo"):
        return "ˈow" + phonemes[2:]
    if "ô" in word:
        return phonemes
    if "ou" in word:
        return re.sub(r'(\w)ˈo(?!w)', r'\1ˈow', phonemes)
    if word == "boa":
        return "bˈowɐ"
    return phonemes


def retain_ei_diphthong(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Retains the grapheme <ei> as the diphthong [ej] in the provided phoneme string.

    Replaces tonic ˈɐj sequences (produced by Lisbon-style reduction) with ˈej to restore the original /ej/ diphthong.

    Retention of 'ei':
        The diphthong <ei> must be retained as [ej], counteracting any tendency towards monophthongization or reduction to [e].
        /e/ → [ej] / __(If derived from grapheme <ei>). eg. "leite" instead of "laite"

    Returns:
        The updated phoneme string with restored `ˈej` diphthongs.
    """
    # NOTE: the lisbon accent reduces ˈej to ˈɐj
    # this restores "proper portuguese phonetics"
    # rather than adding a transform for minho accent,
    # it's undoing one from lisbon accent that affects the base G2P
    return re.sub(r'(\w)ˈɐj', r'\1ˈej', phonemes)


def conservative_o_nasal_retention(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Preferentially realize final -ão as /õ/ to conservatively retain the older nasal vowel.

    If the input word ends with "ão" and the phoneme string uses the merged nasal diphthong forms (`ˈɐ̃w` or `ˈɐ̃ʊ̃`), returns a phoneme string where that ending is replaced by `ˈõ`. Otherwise returns the original phoneme string unchanged.

    Conservative Retention of /õ/ :
        Minho retains the older pronunciation of /õ/
        where SEP has generally merged this sound with the nasal diphthong /ɐ̃w/ (written ão).
        Examples include pão and irmão

    Returns:
        The possibly modified phoneme string with final -ão realized as `ˈõ` when applicable.
    """
    if word.endswith("ão") and phonemes.endswith("ˈɐ̃w"):
        return phonemes[:-4] + "ˈõ"
    if word.endswith("ão") and phonemes.endswith("ˈɐ̃ʊ̃"):  # common espeak mistake
        return phonemes[:-5] + "ˈõ"
    return phonemes


#  Minho Consonant Shifts and Affrication (Inventory Divergence)
# The Minho accent introduces explicit changes to the consonant inventory and distribution.
def labial_fricative_stop_merger(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Realize lexical /v/ as the bilabial approximant [β] in weak word-initial onsets.

    When the orthographic word begins with "v" and the phoneme sequence indicates an initial lexical /v/ in onset position (e.g., phonemes starting with "vˈ", "vˌ", or the "vɨ" sequence after "ve"), replace the leading "v" with "β"; otherwise return the phoneme string unchanged.

    Parameters:
        word (str): The original orthographic word.
        phonemes (str): The IPA phoneme string for the word.

    Returns:
        str: The phoneme string with an initial "v" replaced by "β" when the rule applies, or the original phoneme string otherwise.
    """
    if word.startswith('v') and (phonemes.startswith("vˈ") or phonemes.startswith("vˌ")):
        return "β" + phonemes[1:]
    if word.startswith('ve') and phonemes.startswith("vɨ"):
        return "β" + phonemes[1:]
    return phonemes


def palatal_affrication_ch(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Palatal Affrication of ch:
        Standard EP reduces the historical affricate to the fricative /ʃ/ (e.g., in chaleira 'kettle').
        Minho, however, realizes the digraph <ch> as the voiceless postalveolar affricate /tʃ/ (as in chamber),
        a feature sometimes compared to Spanish pronunciation.

    If the orthographic `word` contains the digraph "ch", replaces occurrences of the fricative ʃ in `phonemes` with the affricate tʃ; otherwise returns `phonemes` unchanged.

    Parameters:
        word (str): Original orthographic word used to detect the digraph "ch".
        phonemes (str): IPA phoneme string to be transformed.

    Returns:
        str: The potentially transformed phoneme string where ʃ is replaced by tʃ when `word` contains "ch".
    """
    if "ch" in word:
        # Replace any /ʃ/ in the phonemes with /tʃ/ if <ch> is in the word
        return phonemes.replace('ʃ', 'tʃ')
    return phonemes


def rhotic_realization(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Realizes rhotics as an alveolar trill `/r/` in syllable onset positions.

    Replaces instances of `/ʁ/` occurring at the start of the phoneme string or immediately after a consonant with `/r/`.

    Returns:
        str: The transformed `phonemes` string with onset `/ʁ/` → `/r/`.
    """
    # Replace /ʁ/ at the start of a word
    phonemes = re.sub(r'^ʁ', 'r', phonemes)
    # Replace /ʁ/ after any consonant (syllable onset)
    phonemes = re.sub(r'(?<=[pbtdkgfvszʃʒmnɲlr])ʁ', 'r', phonemes)
    return phonemes


# Other regionalisms
def epenthetic_j_before_palatal(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Epenthetic [j] before palatals:
        In Minho speech, a short glide [j] is often inserted before palatal consonants.
        This phenomenon occurs after a vowel and before /ʎ/, /ɲ/, or /ʃ/ (and sometimes /tʃ/).
        It gives pronunciations like:
            - 'velho'  [ˈvɛʎu] → [ˈvɛjʎu]
            - 'abelha' [aˈbeʎɐ] → [aˈbejʎɐ]
            - 'bolacha' [boˈlaʃɐ] → [boˈlaiʃɐ]
            - 'banha' [ˈbɐɲɐ] → [ˈbajɲɐ]
            - 'ranho' [ˈʁɐɲu] → [ˈʁajɲu]

        Rule:
            V → Vj / __ [ʎ, ɲ, ʃ, tʃ]
    """
    # Insert [j] after a vowel if immediately followed by a palatal consonant.
    #   - (ˈ[aɐeɛ]) captures a preceding tonic vowel ("a" or "e")
    #   - (?=[ʎɲʃ]) is a lookahead that checks if the next char is palatal /ʎ/, /ɲ/, or /ʃ/
    #   - (?!j) avoids double 'j' insertions if already present
    return re.sub(r'(ˈ[aɐeɛ])(?=[ʎɲʃ])(?!j)', r'\1j', phonemes)


def nasal_diphthongization_e(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Nasal Diphthongization of /ẽ/:
        Transform nasal /ẽ/ → [eĩ] when followed by a consonant,
        especially /t, d, n, s, m/

        Examples:
            casamento → kɐzɐˈmẽtu → kɐzɐˈmeĩtu
            doente → duˈẽtɨ → duˈeĩtɨ
            gente → ˈʒẽtɨ → ˈʒeĩtɨ
            quente → ˈkẽtɨ → ˈkeĩtɨ
            acidente → ɐsiˈdẽtɨ → ɐsiˈdeĩtɨ
    """

    # Replace nasal /ẽ/ with diphthong [eĩ] when followed by consonant (not vowel)
    # Negative lookahead (?![aeiouɐɛɔẽɲʎ]) ensures we don’t touch /ẽ/ before vowels
    # Example match: "ˈʒẽtɨ" → "ˈʒeĩtɨ"

    phonemes = re.sub(r'ẽ(?![aeiouɐɛɔẽɲʎ])', 'eĩ', phonemes)
    return phonemes


def nasal_diphthongization_o(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Diphthongizes the nasal vowel /õ/ to [oũ] when it is followed by a consonant.

    Replaces occurrences of `õ` that are not followed by a vowel with `oũ`.

    Returns:
        str: Phonemes with `õ` → `oũ` in consonant-followed positions; unchanged otherwise.
    """
    # Northern speakers often also realize /õ/ → [oũ] in the same way.
    phonemes = re.sub(r'õ(?![aeiouɐɛɔẽɲʎ])', 'oũ', phonemes)
    return phonemes


def rising_diphthong_o(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Realizes stressed /o/ as the rising diphthong /uo/ in an IPA phoneme string.

    Replaces tonic marker sequence `ˈo` with `ˈuo`, producing rising-diphthong realizations for stressed /o/ (e.g., Porto: /puoɾtu/, Bolo: /buoɫu/).

    Example:
        Porto  → /puoɾtu/
        Bolo   → /buoɫu/

    Returns:
        The input phoneme string with stressed /o/ converted to /uo/.
    """
    # Match tonic /o/ (ˈo) at word-initial or after consonant in stressed syllable
    phonemes = re.sub(r'ˈo', 'ˈuo', phonemes)  # tonic /o/ → /uo/

    return phonemes


def nasal_glide_palatalization(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Palatalizes final nasal glides after a nasal vowel into a palatal nasal at the end of a word.

    Converts sequences where a nasal vowel is followed by a nasalized glide (e.g., Ṽj̃ or Ṽw̃) into the nasal vowel followed by the palatal nasal `ɲ` at word-final position; also handles common variant encodings produced by different phonemizers.

    Nasal Glide Palatalization:
        In Northern Portugal, the final nasal glides [j̃] or [w̃] that follow
        a nasal vowel (e.g., in mãe, põe, bem) are often reinforced or realized
        as a full palatal nasal [ɲ].

        Rule:
            Ṽj̃ → Ṽɲ / _#
            Ṽw̃ → Ṽɲ / _#

        Examples:
            'mãe' [mˈɐ̃j] → [mˈɐ̃jɲ]
            'põe' [põj̃]  → [põɲ]
            'bem' [bẽj̃]  → [bẽɲ]
    Parameters:
        word (str): The original orthographic word (provided for contextual checks; not modified).
        phonemes (str): The IPA phoneme string to transform.
        postag (str): Part-of-speech tag (unused by this rule).

    Returns:
        str: The phoneme string with final nasal glides palatalized to `ɲ`.
    """
    nasal_vowels = "ãẽĩõũɐ̃ɛ̃ɔ̃"
    # Match nasal vowel + nasalized glide at word end → nasal vowel + palatal nasal
    phonemes = re.sub(rf'([{nasal_vowels}])[jw]̃$', r'\1ɲ', phonemes)

    # Handle alternative phonemizer outputs that use combining tildes or nasal glides differently
    # e.g. 'ẽj' or 'ẽĩ̯' at the end
    phonemes = re.sub(rf'([{nasal_vowels}])j$', r'\1jɲ', phonemes)
    phonemes = re.sub(rf'([{nasal_vowels}])ĩ̯$', r'\1ɲ', phonemes)

    return phonemes


def nasal_vowel_raising(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Nasal Vowel Raising:
        In Northern Portugal, nasal vowels tend to be slightly raised and/or fronted
        compared to Standard European Portuguese. This is especially evident in /ɐ̃/
        , which may be realized as [ã].

        Rules:
            ɐ̃ → ã

        Examples:
            'mãe'  [mˈɐ̃j] → [mˈãj]
    """
    # /ɐ̃/ → [ã]
    phonemes = phonemes.replace("ɐ̃", "ã")
    return phonemes


## Trasmontano

def intervocalic_s_voicing(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Intervocalic /s/ Voicing:
        In Transmontano and other northern dialects, /s/ is often voiced to [z]
        between vowels or in word-final position after a vowel.
        This mirrors a general lenition pattern found in voiced environments.

        Rules:
            /s/ → [z] / V__V
            /s/ → [z] / V__#

        Examples:
            'moço' [ˈmosu] → [ˈmozu]
            'seis' [ˈsejs] → [ˈzejz]
    """
    vowels = "aeiouɐɛɔɨẽõɐ̃"
    # Intervocalic voicing
    phonemes = re.sub(rf'(?<=[{vowels}])s(?=[{vowels}])', 'z', phonemes)
    # Word-final after vowel
    phonemes = re.sub(rf'(?<=[{vowels}])s(?=$)', 'z', phonemes)
    return phonemes


def initial_z_devoicing(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Word-Initial /z/ Devoicing:
        In Transmontano Portuguese, initial /z/ may be realized as [s] before vowels.
        This can create minimal-pair-like alternations such as:
            'zero' [ˈzeɾu] → [ˈseɾu]
            'zona' [ˈzonɐ] → [ˈsonɐ]

        Rule:
            /z/ → [s] / #__V
    """
    vowels = "aeiouɐɛɔɨẽõɐ̃"
    phonemes = re.sub(rf'(?<=^)(z)(?=[{vowels}])', 's', phonemes)
    return phonemes


def final_nasal_denasalization(word: str, phonemes: str, postag: str = "NOUN") -> str:
    """
    Final Nasal Denasalization:
        In Transmontano Portuguese, final nasal vowels — especially those in -agem words —
        tend to lose nasalization, yielding oral [e] or [ɐ] realizations.

        This reflects a broader tendency toward denasalization in unstressed
        final syllables across northern varieties.

        Rules:
            /ʒẽ$/ → [ʒe]
            /ʒɐ̃$/ → [ʒɐ]
            /ʒõ$/ → [ʒo]

        Examples:
            'viagem' [viˈaʒẽ] → [viˈaʒe]
            'paragem' [pɐˈɾaʒẽ] → [pɐˈɾaʒe]
    """
    phonemes = re.sub(r'ʒẽ$', 'ʒe', phonemes)
    phonemes = re.sub(r'ʒɐ̃$', 'ʒɐ', phonemes)
    phonemes = re.sub(r'ʒõ$', 'ʒo', phonemes)
    return phonemes


if __name__ == "__main__":
    from tugaphone import TugaPhonemizer

    pho = TugaPhonemizer()

    sentences = [
        "O gato dorme.",
        "Tu falas português muito bem.",
        "O comboio chegou à estação.",
        "A menina comeu o pão todo.",
        "Vou pôr a manteiga no frigorífico.",
        "Ele está a trabalhar no escritório.",
        "Choveu muito ontem à noite.",
        "A rapariga comprou um telemóvel novo.",
        "Vamos tomar um pequeno-almoço.",
        "O carro ficou sem gasolina.",
        "boa roupa touro pouco ouro",  # ou
        'beira peixe feito pequeno reino meio',  # ei
        'verdade verde verdadeira boi vaca bacalhau',  # v
        "pão irmão cagão bolhão cão"  # õ
    ]

    for s in sentences:
        for word in s.split():
            word = word.lower()
            phonemes = pho.phonemize_sentence(word, "pt-PT")
            phonemes_m_v1 = reduce_vowel_centralization(word, phonemes)
            phonemes_m_v2 = open_vowel_preference(word, phonemes_m_v1)
            phonemes_m_d1 = retain_ou_diphthong(word, phonemes_m_v2)
            phonemes_m_d2 = retain_ei_diphthong(word, phonemes_m_d1)
            phonemes_m_d3 = conservative_o_nasal_retention(word, phonemes_m_d2)
            phonemes_m_c1 = labial_fricative_stop_merger(word, phonemes_m_d3)
            phonemes_m_c2 = palatal_affrication_ch(word, phonemes_m_c1)
            phonemes_m_c3 = rhotic_realization(word, phonemes_m_c2)

            print(word, "->", phonemes)
            if phonemes_m_c3 != phonemes:
                if phonemes_m_v2 != phonemes:
                    print(phonemes, "-(m_v1)->", phonemes_m_v1, "-(m_v2)->", phonemes_m_v2)
                if phonemes_m_d3 != phonemes_m_v2:
                    print(phonemes_m_v2, "-(m_d1)->", phonemes_m_d1, "-(m_d2)->", phonemes_m_d2, "-(m_d3)->",
                          phonemes_m_d3)
                if phonemes_m_c3 != phonemes_m_d3:
                    print(phonemes_m_d3, "-(m_c1)->", phonemes_m_c1, "-(m_c2)->", phonemes_m_c2, "-(m_c3)->",
                          phonemes_m_c3)

        print("######")
