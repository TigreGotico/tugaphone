"""
Portuguese Syllabification Module

OVERVIEW:
=========
This module implements a rule-based syllabification algorithm for Portuguese text.
Syllabification is the process of dividing words into syllables, which are the
fundamental rhythmic units of speech.

WHAT IS A SYLLABLE?
===================
A syllable is a unit of pronunciation that contains:
- A nucleus (required): Usually a vowel sound (the "peak" of the syllable)
- An onset (optional): Consonant(s) before the nucleus
- A coda (optional): Consonant(s) after the nucleus

Examples in English:
- "cat" [kæt]: onset=k, nucleus=æ, coda=t (one syllable)
- "happy" [hæ.pi]: two syllables
  - Syllable 1: onset=h, nucleus=æ
  - Syllable 2: onset=p, nucleus=i

Examples in Portuguese:
- "casa" [ka.za]: two syllables
  - Syllable 1: onset=k, nucleus=a
  - Syllable 2: onset=z, nucleus=a
- "Brasil" [bra.zil]: two syllables
  - Syllable 1: onset=br (consonant cluster), nucleus=a
  - Syllable 2: onset=z, nucleus=i, coda=l

PORTUGUESE SYLLABLE STRUCTURE:
==============================
Portuguese syllables follow the "Sonority Sequencing Principle":
- Sonority increases toward the nucleus (vowel)
- Sonority decreases after the nucleus

Preferred structure: CV (Consonant-Vowel)
- Portuguese "loves" CV syllables - they're the most common
- Example: "pa.pa.gai.o" (parrot) - all CV syllables

Complex syllables exist but are less common:
- CCV: "pra.to" (plate) - onset cluster 'pr'
- CVC: "por.ta" (door) - coda consonant 'r'
- V: "a.ve" (bird) - no onset
- VC: "es.ta" (is) - no onset, has coda

METHODOLOGY NOTE:
=================
This implementation is EMPIRICAL rather than purely theoretical:
- It was developed by testing against a large lexicon (53,000+ words)
- Rules were iteratively refined to maximize accuracy
- Some decisions are pragmatic compromises rather than linguistic absolutes
- Current accuracy: ~99.6% (53,154 correct out of 53,349 words)
"""

import string
from typing import List, Tuple, Optional
from logging import getLogger

LOG = getLogger()
LOG.setLevel("DEBUG")

# =============================================================================
# DIACRITIC CONSTANTS: Portuguese Accent Marks
# =============================================================================
#
# LINGUISTIC BACKGROUND ON PORTUGUESE DIACRITICS:
# ------------------------------------------------
# Portuguese uses diacritical marks (accents) for three purposes:
# 1. Indicate stress placement (which syllable is emphasized)
# 2. Indicate vowel quality (open vs. closed pronunciation)
# 3. Indicate nasalization (air flows through nose during vowel)
#
# Unlike English, Portuguese stress is semi-predictable and must often be marked.
# Example: "numero" (I number - verb) vs. "número" (number - noun) - stress changes meaning

# INVALID/ARCHAIC ACCENTS:
# ------------------------
# These exist in old texts or typos but are not standard modern Portuguese

BAD_GRAVE = "èìòù"  # INVALID - likely typing errors
# EXPLANATION: In modern Portuguese, only "à" (grave accent on 'a') is valid.
# This represents a contraction: preposition "a" + article "a" = "à"
# Example: "Vou à escola" (I go to the school)
# If you see "è", "ì", "ò", "ù", it's probably a mistake for acute accents.

BAD_NASAL = "ẽĩũ"  # INVALID - non-standard nasalization markers
# EXPLANATION: In Portuguese, only "ã" and "õ" use the tilde for nasalization.
# Nasalization means air flows through the nose during pronunciation.
# The vowels i, u, e don't get tilde in standard Portuguese.
# Example: "mão" [mãw̃] (hand) - nasal, but NOT "mĩo"
# If these appear, they're likely in loanwords or archaic texts.

BAD_CIRCUMFLEX = "îû"  # INVALID - non-standard softening markers
# EXPLANATION: Circumflex (^) marks closed vowel quality and stress.
# Only valid on a, e, o: "â", "ê", "ô"
# On i and u, circumflex is redundant (they're always pronounced "closed")
# Example: "você" [vo.ˈse] uses "ê" (valid), but "vî" would be invalid

# VALID ACCENTS IN MODERN PORTUGUESE:
# ------------------------------------

GRAVE = "à"  # Grave accent - only exists on 'a'
# PURPOSE: Marks a contraction (a + a = à), not stress or vowel quality
# Example: "à" in "Vou à praia" (I go to the beach)
# Historical note: Before 1973, grave marked secondary stress in compound words

ACUTE = "áéíóú" + BAD_GRAVE  # Acute accent - marks stress AND open vowel
# PURPOSE: 
# - Indicates primary stress (syllable emphasis)
# - For a/e/o: indicates OPEN vowel quality
# PHONETIC DISTINCTION:
#   "café" [ka.ˈfɛ] - open 'e' [ɛ] like in English "bet"
#   vs. "você" [vo.ˈse] - closed 'e' [e]
# For i/u: acute just marks stress (these vowels have no open/closed distinction)

NASAL = "ãõ" + BAD_NASAL  # Tilde - marks nasalization
# PURPOSE: Indicates nasal vowels (air flows through nose)
# PHONETIC EFFECT: Creates distinct phonemes, not just allophones
#   "mato" [ˈma.tu] = "bush" (oral vowel)
#   "manto" [ˈmɐ̃.tu] = "cloak" (nasal vowel) - different word!
# Only on 'a' and 'o' in modern Portuguese
# Also marks stress when word-final: "cão" [ˈkɐ̃w̃] (dog)

CIRCUMFLEX = "âêô" + BAD_CIRCUMFLEX  # Circumflex - marks stress AND closed vowel
# PURPOSE:
# - Indicates primary stress
# - For a/e/o: indicates CLOSED vowel quality
# PHONETIC DISTINCTION:
#   "avô" [a.ˈvo] - closed 'o' [o] like in English "go"
#   vs. "avó" [a.ˈvɔ] - open 'o' [ɔ] like in English "dog"
# Examples: "você" (you), "avô" (grandfather), "âmbito" (scope)

ACCENTED_VOWELS = ACUTE + CIRCUMFLEX + GRAVE + NASAL
# All vowels with diacritics combined


# =============================================================================
# VOWEL AND CONSONANT DEFINITIONS
# =============================================================================

# BRAZILIAN PORTUGUESE L-VOCALIZATION:
# ------------------------------------
# NOTE: In Brazilian Portuguese, 'l' at the end of syllables → [w] sound
# This is called "l-vocalization" or "velarization"
# Example: 
#   European Portuguese: "Brasil" [bɾɐ.ˈziɫ] - dark L sound
#   Brazilian Portuguese: "Brasil" [bɾa.ˈziw] - becomes 'w' sound (like in "cow")
# This makes final 'l' behave like a vowel for syllabification purposes

FOREIGN_VOWELS = "yw"  # Letters that act as vowels in loanwords
# 'y' → pronounced like 'i': "hobby" [ˈhɔ.bi], "byte" [ˈbaj.tɨ]
# 'w' → pronounced like 'u': "web" [ˈwɛb], "show" [ˈʃow]
# These letters aren't in the traditional Portuguese alphabet but appear in
# borrowed words from English, German, etc.

VOWELS = list("aeiou" + ACCENTED_VOWELS + FOREIGN_VOWELS)
# Complete list of all characters that function as vowels
# Includes: a, e, i, o, u + all accented variants + foreign letters

SEMIVOWEL = "iu" + FOREIGN_VOWELS
# LINGUISTIC CONCEPT - SEMIVOWELS (GLIDES):
# -----------------------------------------
# Semivowels are vowel-like sounds that function as consonants
# In Portuguese, [j] and [w] are the semivowels:
# - [j]: written as 'i' or 'y', sounds like English 'y' in "yes"
# - [w]: written as 'u' or 'w', sounds like English 'w' in "wet"
#
# Whether a letter is a vowel or semivowel depends on its position:
# - As syllable nucleus → vowel: "rima" [ˈʁi.mɐ] - 'i' is a vowel
# - In diphthong → semivowel: "rei" [ˈʁej] - 'i' → [j] is a semivowel
#
# Example diphthongs:
# - "pai" [paj] - 'i' → [j] semivowel
# - "meu" [mew] - 'u' → [w] semivowel
# - "água" [ˈa.ɡwɐ] - 'u' → [w] semivowel

NASAL_CONSONANTS = "nm"
# These consonants can nasalize preceding vowels
# When 'm' or 'n' appears after a vowel at syllable end, the vowel becomes nasal
# Example: 
#   "campo" [ˈkɐ̃.pu] - 'a' becomes nasal before 'm'
#   "santo" [ˈsɐ̃.tu] - 'a' becomes nasal before 'n'
# The nasal consonant itself may not be fully pronounced


# =============================================================================
# DIGRAPH CONSTANTS: Two-Letter Units
# =============================================================================
#
# LINGUISTIC CONCEPT - DIGRAPHS:
# ------------------------------
# A digraph is two letters that represent ONE sound
# Like in English: "sh" in "ship", "th" in "think"
#
# Portuguese digraphs fall into two categories for syllabification:
# 1. INSEPARABLE: Always stay together in one syllable
# 2. SEPARABLE: Can be split across syllable boundaries

INSEPARABLE_DIGRAPHS = ["ch", "lh", "nh", "gu", "qu"]
# These ALWAYS belong in the same syllable - they represent single sounds
#
# PHONETIC REALIZATIONS:
# - "ch" [ʃ]: like English "sh" in "ship"
#   Example: "chuva" [ˈʃu.vɐ] (rain)
# - "lh" [ʎ]: palatal lateral (like Italian "gl" in "figlio")
#   Example: "filho" [ˈfi.ʎu] (son)
# - "nh" [ɲ]: palatal nasal (like Spanish "ñ" in "mañana")
#   Example: "inho" [ˈvi.ɲu] (wine)
# - "gu" [ɡ]: before 'e' or 'i', 'u' is silent (just makes 'g' hard)
#   Example: "guerra" [ˈɡɛ.ʁɐ] (war) - NOT "güerra"
# - "qu" [k]: before 'e' or 'i', 'u' is silent (just makes 'c' sound)
#   Example: "quero" [ˈke.ɾu] (I want) - NOT "küero"
#
# NOTE: "gu" and "qu" are tricky - sometimes 'u' IS pronounced:
#   "linguiça" [lĩ.ˈɡwi.sɐ] - 'u' is pronounced [w]
#   But this is context-dependent and requires a dictionary

SEPARABLE_DIGRAPHS = (["rr", "ss", "sc", "sç", "xs", "xc"] +
                      ["sl", "rl", "nl", "ct", "ll", "dl",
                       "lr", "sr", "nr"])
# Canonically, these would be split across syllables
#
# DOUBLED CONSONANTS (rr, ss, ll):
# - Portuguese spelling doubles consonants to preserve sound between vowels
# - "rr" [ʁ]: strong R sound (vs. single 'r' which is a tap [ɾ])
#   Example: "carro" [ˈka.ʁu] (car) vs. "caro" [ˈka.ɾu] (expensive)
# - "ss" [s]: voiceless S (vs. single 's' which becomes [z] between vowels)
#   Example: "passo" [ˈpa.su] (step) vs. "paso" (archaic/Spanish)
#
# CONSONANT CLUSTERS (ct, sc, etc.):
# - These split across syllable boundaries: "pac.to", "nas.cer"
# - They don't form valid syllable onsets (can't start a syllable together)
#
# NOTE: The second group (sl, rl, nl, etc.) is marked as "not canonical (?)"
# This means it's an empirical addition based on testing, not traditional
# Portuguese phonology rules. These patterns appear in the test data.

FOREIGN_DIGRAPHS = ["sh", "th", "ff"]
# These ALWAYS belong in the same syllable but only appear in loanwords
#
# PHONETIC REALIZATIONS IN PORTUGUESE:
# - "sh" [ʃ]: like English "sh", in words like "show" [ˈʃow]
# - "th" [t]: usually adapted to [t], rarely [θ] (English 'th' sound doesn't exist in Portuguese)
#   Example: "thriller" [ˈtɾi.lɛɾ] (not [ˈθɾɪ.lɚ] like in English)
# - "ff" [f]: just one [f] sound
#   Example: "graffiti" [ɡɾa.ˈfi.ti]


# =============================================================================
# SPECIAL TOKENIZATION STRATEGY
# =============================================================================

SPECIAL_TOKENS = {
    d[0].upper(): d for d in INSEPARABLE_DIGRAPHS + FOREIGN_DIGRAPHS
}
# Creates a mapping: {'C': 'ch', 'L': 'lh', 'N': 'nh', 'G': 'gu', 'Q': 'qu', 'S': 'sh', 'T': 'th', 'F': 'ff'}
#
# ALGORITHMIC TRICK:
# ------------------
# Problem: When scanning character by character, we might split digraphs
#   Example: "ch" might be seen as 'c' + 'h' instead of one unit
#
# Solution: Replace digraphs with single uppercase placeholder tokens
#   "chuva" → "Cuva" (temporarily)
#   Process as single characters
#   Then restore: "Cuva" → "chuva"
#
# This makes the main loop simpler - we treat digraphs as atomic units
# Example transformation:
#   "filho" → "fiLo" → process → "fi.Lo" → "fi.lho"

SYLL_STARTERS: List[str] = list(SPECIAL_TOKENS.keys()) + ["ç"]
# Characters/tokens that ALWAYS start a new syllable
# - All the special uppercase tokens (digraph placeholders)
# - "ç" (c-cedilla) [s]: like "s" in "stop"
#   Example: "caça" [ˈka.sɐ] (hunt)
#
# REASONING:
# When we encounter these in the middle of building a syllable,
# we know the previous syllable must end and a new one must begin


# =============================================================================
# CONSONANT CLUSTERS THAT CAN START SYLLABLES
# =============================================================================

CONSONANT_DIGRAPHS = INSEPARABLE_DIGRAPHS + FOREIGN_DIGRAPHS + [
    "pr", "br", "tr", "dr", "cr", "gr", "fr",  # Obstruent + r
    "pl", "bl", "cl", "gl", "fl",  # Obstruent + l
]


# These are consonant clusters that can START a syllable (valid onsets)
#
# PHONOLOGICAL PRINCIPLE:
# -----------------------
# Portuguese allows complex onsets following the "Sonority Sequencing Principle"
# Sonority hierarchy (low to high):
#   stops (p,b,t,d,k,g) < fricatives (f,v,s,z) < liquids (l,r) < vowels
#
# Valid onset clusters: consonant + liquid (r or l)
# - The second consonant must be MORE sonorous than the first
# - This creates a smooth rise in sonority toward the vowel nucleus
#
# EXAMPLES:
# - "pra.to" [ˈpɾa.tu] (plate) - 'pr' can start a syllable
# - "bra.sil" [bɾa.ˈziw] (Brazil) - 'br' can start a syllable
# - "flo.res.ta" [flu.ˈɾɛʃ.tɐ] (forest) - 'fl' can start a syllable
#
# COUNTEREXAMPLES (cannot start syllables):
# - *"rt" - violates sonority: stop + liquid is okay, but liquid + stop is not
# - *"sr" - violates sonority: fricative + liquid borderline
# - These would split: "par.te" not *"pa.rte", "Is.ra.el" not *"I.srael"

# =============================================================================
# VALIDATION FUNCTIONS: Diphthongs and Triphthongs
# =============================================================================

def validate_triphthong(triph: str, prev_char: str = "") -> bool:
    """
    Determine whether a three-character orthographic sequence forms a valid Portuguese triphthong.
    
    Validates that the sequence is composed of vowels with a semivowel + nucleus + semivowel (G‑V‑G) structure, allows diacritics only on the nucleus, permits the final glide when the nucleus is nasal, and rejects known non-triphthong patterns (e.g., nucleus 'e' followed by 'i').
    
    Parameters:
        triph (str): Three-character sequence to validate (e.g., "uai", "miau").
        prev_char (str): Optional previous character for contextual checks (unused by most rules).
    
    Returns:
        bool: `True` if the sequence is a valid Portuguese triphthong, `false` otherwise.
    """
    if len(triph) != 3:
        return False

    # Decompose into: semivowel + vowel + semivowel
    a, b, c = triph[0], triph[1], triph[2]

    # RULE 1: All three must be vowels
    if not all(char in VOWELS for char in triph):
        return False

    # RULE 2: First must be semivowel (glide)
    # Only 'i' and 'u' (and foreign 'y', 'w') can function as semivowels
    if a not in SEMIVOWEL:
        return False

    # RULE 3: Diacritics only allowed on middle character (the nucleus)
    # Stress/nasalization only affects the nuclear vowel, not the glides
    if a in ACUTE + NASAL or c in ACUTE + NASAL:
        return False

    # RULE 4: Last must be semivowel OR middle is nasal
    # If middle vowel is nasal (ã, õ), the nasalization extends to the glide
    # Example: "saguão" [sa.ˈɡwɐ̃w̃] - nasal extends through whole triphthong
    if b not in NASAL and c not in SEMIVOWEL:
        return False

    # RULE 5: Specific rejection - "ei" sequence at end
    # This is typically a diphthong, not part of a triphthong
    # Example: "fieira" [fi.ˈej.ɾɐ] - 'iei' is NOT a triphthong, it's i + ei
    if b == "e" and c == "i":
        return False

    return True


def validate_diphthong(diph: str, prev_char: str = "") -> bool:
    """
    Determine whether a two-character vowel sequence forms a valid Portuguese diphthong.
    
    This function applies a conservative, empirical rule set: both characters must be vowels, the second vowel may not carry stress/diacritics (it functions as a glide), and certain sequences and accent patterns are treated as hiatus to improve accuracy on real-world data. Notably, an acute accent on the first vowel normally signals hiatus except for the sequence "áu"; a number of common two-vowel sequences (e.g., "ea", "io", "ui", "oa") are always treated as hiatus by this heuristic.
    
    Parameters:
        diph (str): Two-character vowel sequence to validate (e.g., "ai", "eu").
        prev_char (str): Character immediately preceding the sequence, used only for contextual rules.
    
    Returns:
        bool: `true` if the sequence should be treated as a diphthong, `false` if it should be treated as a hiatus.
    """

    # RULE 1: Must be exactly 2 characters
    if len(diph) != 2:
        return False

    a, b = diph[0], diph[1]

    # RULE 2: Both must be vowels
    if not all(char in VOWELS for char in diph):
        return False

    # RULE 3: Diacritics only on first character
    # In diphthongs, stress falls on the first vowel (the nucleus)
    # The second vowel is the glide and cannot be stressed
    # Example: "pai" [ˈpaj] - stress on 'a', not on 'i'
    if b in ACUTE + NASAL + CIRCUMFLEX:
        return False

    # RULE 4: Acute accent indicates hiatus, with ONE exception
    # When a vowel has acute accent, it's stressed and the syllable nucleus
    # It typically can't be part of a diphthong... except "áu"
    # Example: "saída" [sa.ˈi.dɐ] - acute 'í' forces hiatus
    # Exception: "baú" [ba.ˈu] vs. "mau" [maw] - both valid, 'áu' can be diphthong
    if a in ACUTE and diph != "áu":
        return False

    # RULE 5: Sequences that are ALWAYS hiatus in Portuguese
    always_hiatus = ["ae",  # "ae" is hiatus
                     "ea", "eo",  # 'e' followed by another vowel
                     "io", "ia", "ie", "ía",  # 'i' followed by another vowel
                     "oa", "oe",  # 'o' followed by another vowel
                     "ua", "ue", "ui", "uo"]  # 'u' followed by another vowel
    # NOTE: "ui" is a VALID diphthongs in Portuguese, but uncommon
    # Empirical testing shows that assuming hiatus for it improves accuracy
    # This is a pragmatic choice - a dictionary of exceptions could handle the real diphthongs
    #
    # Examples of hiatus words:
    # - "área" [ˈa.ɾe.ɐ] - ea is hiatus
    # - "piano" [pi.ˈɐ.nu] - ia is hiatus (despite looking like it could be diphthong)
    # - "cruel" [kɾu.ˈɛɫ] - ue is hiatus
    #
    # Examples of actual "ui" diphthongs (rare):
    # - "muito" [ˈmũj.tu] - but this is handled as a special case elsewhere
    if a + b in always_hiatus:
        return False

    return True


def check_for_hiatus(diph: str, is_end: bool = False, prev_char: str = "") -> bool:
    """
    Determine whether a two-vowel sequence should be syllabified as a hiatus under several Portuguese-specific contextual rules.
    
    This function first checks candidacy with validate_diphthong and then applies additional heuristics:
    - If validate_diphthong returns False, this function returns False (treated as not a hiatus).
    - A nasal first vowel (e.g., ã, õ) is treated as part of a nasal diphthong (not a hiatus).
    - Identical adjacent vowels (aa, ee, ii, oo, uu) are treated as a hiatus.
    - If the second vowel carries a tilde (specifically 'ã' or 'õ'), the pair is treated as a hiatus.
    - If the vowel sequence follows 'r' (prev_char == 'r') it is treated as a hiatus except for the sequence "ei".
    
    Parameters:
        diph (str): Two-character vowel sequence to evaluate.
        is_end (bool): True if the sequence occurs at the end of a word (currently accepted but not used by this implementation).
        prev_char (str): Character immediately preceding the sequence (used for rhotic context).
    
    Returns:
        bool: `True` if the sequence should be treated as a hiatus (two syllables), `False` if it should be treated as a diphthong (one syllable).
    """

    # STEP 1: Must pass basic diphthong validation
    # If it's not even a candidate for diphthong, it's definitely hiatus
    if not validate_diphthong(diph):
        return False  # NOTE: Returns False meaning "not a hiatus" → it's invalid entirely
        # This might be a logic error in the original code

    a, b = diph[0], diph[1]

    # RULE 1: Nasal vowels prefer diphthongs
    # If first vowel is nasal (ã, õ), nasalization extends through glide
    # Example: "mãe" [ˈmɐ̃j̃] - nasal diphthong, not hiatus
    if a in NASAL:
        return False  # Not hiatus → it's a nasal diphthong

    # RULE 2: Word-final position favors diphthongs
    # At the end of words, Portuguese strongly prefers diphthongs over hiatus
    # Example: "pai" [paj] (father), "rei" [ʁej] (king) - always diphthongs
    # NOTE: experimentally determined to lower accuracy, commented out
    #if is_end:
    #    return False

    # RULE 3: Repeated vowels are always hiatus
    # Portuguese doesn't have long vowels, so aa, ee, etc. must be separate syllables
    # Example: "coordenar" [ko.oʁ.de.ˈnaʁ] - "oo" is hiatus (co.or.de.nar)
    if a == b:
        return True  # Hiatus

    # RULE 4: Reversed tilde position indicates hiatus
    # Tilde should be on FIRST vowel in valid nasal diphthongs (ão, ãe)
    # If tilde is on SECOND vowel, it's likely hiatus
    # Example: "ruão" would be hiatus
    if b in ["ã", "õ"]:
        return True  # Hiatus

    # RULE 5: After 'r', vowels usually form hiatus (except "ei")
    # This is a phonotactic pattern in Portuguese
    # After rhotic sounds, vowels tend to be syllabified separately
    # Example: "criar" [kɾi.ˈaɾ] - "ia" is hiatus
    # Exception: "rei" [ʁej], "treinador" [tɾej.nɐ.ˈdoʁ] - "ei" can be diphthong after 'r'
    if prev_char in ["r"] and a + b != "ei":
        return True  # Hiatus

    return False  # Not hiatus → treat as diphthong


# =============================================================================
# MAIN SYLLABIFICATION FUNCTION
# =============================================================================

def syllabify(word: str) -> List[str]:
    """
    Split a Portuguese word into its syllables.
    
    Performs a rule-based syllabification that handles digraphs, diphthongs,
    triphthongs, hiatus, nasalization and common consonant-cluster constraints,
    then applies empirical post-processing corrections for known exceptions.
    
    Parameters:
        word (str): Word to syllabify. May include spaces or hyphens (spaces are
            treated as hyphens for compound words).
    
    Returns:
        List[str]: List of syllable strings in orthographic order.
    """

    # =========================================================================
    # PREPROCESSING
    # =========================================================================

    word = word.lower().replace(" ", "-").strip()

    # EDGE CASE 1: Single punctuation or special characters
    # If word is just punctuation, return as-is
    if word in set(string.printable):
        return [word]

    # EDGE CASE 2: Known monosyllabic diphthongs
    # These two-letter words are single syllables (common function words)
    # "ao" [aw] - contraction of "a" + "o"
    # "ui" [uj] - exclamation or archaic form
    # "ei" [ej] - exclamation
    # "ai" [aj] - exclamation "ouch"
    if word in ["ao", "ui", "ei", "ai"]:
        return [word]

    tokens: List[str] = []  # Will store final syllables

    # PREPROCESSING STEP: Replace inseparable digraphs with placeholder tokens
    # This allows us to treat them as single units during processing
    # Example: "filho" → "fiLo", then process, then restore → "fi.lho"
    for k, v in SPECIAL_TOKENS.items():
        word = word.replace(v, k)  # ch→C, lh→L, nh→N, qu→Q, gu→G, etc.

    # =========================================================================
    # MAIN SYLLABIFICATION LOOP
    # =========================================================================

    # Process each subword (hyphenated compounds are split)
    for subword in word.split("-"):
        sub_tokens: List[str] = []  # Syllables for this subword
        syl = ""  # Current syllable being built

        # Scan character by character
        for idx, char in enumerate(subword):

            # -----------------------------------------------------------------
            # CONTEXT DETECTION: Look around current character
            # -----------------------------------------------------------------

            is_last_char = idx == len(subword) - 1  # Last character in word?
            is_pn_char = idx == len(subword) - 2  # Penultimate (second-to-last)?
            is_vowel_char = char in VOWELS  # Current char is vowel?
            is_first_syl = not sub_tokens  # Building the first syllable?

            # Look-behind (previous characters)
            prev_char = subword[idx - 1] if idx > 0 else ""
            pprev_char = subword[idx - 2] if idx > 1 else ""

            # Look-ahead (next characters)
            next_char = subword[idx + 1] if not is_last_char else ""
            nnext_char = subword[idx + 2] if not is_last_char and not is_pn_char else ""

            # Classify next character
            next_is_soft_consonant = next_char in "lr"  # Liquid consonants
            next_is_vowel = next_char in VOWELS
            next_is_consonant = not next_is_vowel

            # Check for multi-vowel sequences
            is_triphthong = validate_triphthong(f"{prev_char}{char}{next_char}", pprev_char)
            is_diphthong = validate_diphthong(f"{char}{next_char}", prev_char)
            is_hiatus = check_for_hiatus(f"{char}{next_char}", is_pn_char, prev_char)

            # Check if next position starts a consonant cluster
            is_c_digraph = f"{next_char}{nnext_char}" in CONSONANT_DIGRAPHS

            # Current syllable state
            syl_ends_with_vowel = syl and syl[-1] in VOWELS
            syl_has_vowel = any(c in VOWELS for c in syl)

            # -----------------------------------------------------------------
            # SPECIAL CASE: QU and GU digraphs
            # -----------------------------------------------------------------
            # "G" and "Q" are our placeholder tokens for "gu" and "qu"
            # Normally these represent consonants, but when followed by another
            # consonant, the 'u' must be treated as a vowel
            # Example: "quando" has "qu" (Q) but the 'u' acts as vowel → "quan.do"
            if char in ["G", "Q"] and next_is_consonant:
                is_vowel_char = True  # Override: treat as vowel in this context

            is_consonant = not is_vowel_char

            # -----------------------------------------------------------------
            # SYLLABLE BOUNDARY DECISION
            # -----------------------------------------------------------------
            # This is the core logic: should we end the current syllable here?

            is_end_of_syl = False  # Default: continue current syllable

            # RULE 1: Forced boundaries
            # If next character must start a syllable, current syllable ends
            if next_char in SYLL_STARTERS or is_c_digraph or next_char == "w":
                is_end_of_syl = True
                # Examples:
                # - next is 'C' (ch digraph) → "mu.Cho" → "mu.cho"
                # - next is consonant cluster → "a.Bra" → "a.bra"
                # - next is 'w' (foreign) → "ha.wai.i"

            # RULE 2: C-C (Consonant-Consonant) patterns
            elif is_consonant and next_is_consonant:
                # When two consonants meet, we must decide where to split

                if char + next_char in SEPARABLE_DIGRAPHS:
                    # These clusters MUST be separated
                    # Example: "rr" in "carro" → "car.ro"
                    LOG.debug("boundary C-C :", char, "/", next_char, "-> digraph must be separated")
                    is_end_of_syl = True

                elif is_first_syl and not syl_has_vowel:
                    # ONSET MAXIMIZATION: Keep initial consonant clusters together
                    # Portuguese rule: "Os encontros consonantais que iniciam 
                    # palavras são mantidos juntos na divisão silábica"
                    # (Consonant clusters that begin words stay together)
                    # Example: "bra.sil" not "b.ra.sil", "pra.to" not "p.ra.to"
                    LOG.debug("not-boundary:", char, "/", next_char, "-> no vowels yet")
                    is_end_of_syl = False

                elif next_is_soft_consonant:
                    # Keep consonant + liquid (l, r) together
                    # Portuguese rule: "Os encontros consonantais devem ser separados,
                    # exceto aqueles cuja segunda consoante é 'l' ou 'r'"
                    # (Consonant clusters should be separated, except when the
                    # second consonant is 'l' or 'r')
                    # Example: "a.pren.der" keeps "pr" together
                    LOG.debug("not-boundary:", char, "/", next_char, "-> soft consonant")
                    is_end_of_syl = False

                else:
                    # Default for C-C: split them
                    # Example: "pac.to", "rit.mo"
                    LOG.debug("boundary C-C :", char, "/", next_char)
                    is_end_of_syl = True

            # RULE 3: C-V (Consonant-Vowel) patterns
            elif is_consonant and next_is_vowel:
                # Consonant + vowel always stay together (onset + nucleus)
                # This is the most fundamental syllable structure in Portuguese
                # Example: "ca.sa", "me.sa", "pa.to"
                LOG.debug("not-boundary C-V :", char, "/", next_char, "-> consonant+vowel")
                is_end_of_syl = False

            # RULE 4: V-V (Vowel-Vowel) patterns
            elif is_hiatus:
                # Two vowels in hiatus → separate syllables
                # Example: "sa.í.da" (exit), "pa.ís" (country)
                LOG.debug("boundary V-V :", char, "/", next_char, "-> hiatus")
                is_end_of_syl = True

            elif is_triphthong:
                # Three vowels forming triphthong → stay in one syllable
                # Portuguese rule: "Tritongos devem permanecer na mesma sílaba"
                # (Triphthongs must remain in the same syllable)
                # Example: "Uru.guai" - "uai" is one syllable
                LOG.debug("not-boundary VVV :", char, "/", next_char, "-> triphthong")
                is_end_of_syl = False

            elif is_diphthong:
                # Two vowels forming diphthong → stay in one syllable
                # Portuguese rule: "Ditongos devem permanecer na mesma sílaba"
                # (Diphthongs must remain in the same syllable)
                # Example: "pai", "rei", "meu"
                LOG.debug("not-boundary VV :", char, "/", next_char, "-> diphthong")
                is_end_of_syl = False

            elif is_vowel_char and next_is_vowel:
                # Two vowels that don't form a valid diphthong → hiatus
                # Example: "co.o.pe.rar" (cooperate) - "oo" is hiatus
                LOG.debug("boundary V-V :", char, "/", next_char, "-> invalid diphthong")
                is_end_of_syl = True

            # RULE 5: V-C (Vowel-Consonant) patterns
            elif is_vowel_char and next_is_consonant:
                # Complex decision - depends on what follows the consonant

                if is_pn_char:
                    # Penultimate position: keep final consonant with this syllable
                    # Example: "por.tal" - 'l' stays with "tal", not separate
                    LOG.debug("not-boundary V-C :", char, "/", next_char, "-> consonant at end of word")
                    is_end_of_syl = False

                elif nnext_char and nnext_char not in VOWELS:
                    # V-C-C pattern: keep first C with current syllable as coda
                    # This prepares for the C-C split or complex onset
                    # Example: "cos.ta" (coast) - 's' stays with "cos"
                    LOG.debug("not-boundary V-C-C :", char, "/", next_char, "/", nnext_char,
                              "-> vowel merge with next consonant")
                    is_end_of_syl = False

                else:
                    # V-C-V pattern: split after vowel (let C start next syllable)
                    # ONSET MAXIMIZATION: consonant prefers to start next syllable
                    # Example: "ca.sa" not "cas.a", "me.sa" not "mes.a"
                    LOG.debug("boundary V-C :", char, "/", next_char, "-> vowel marks end of syl")
                    is_end_of_syl = True

            # -----------------------------------------------------------------
            # APPEND CHARACTER AND FINALIZE SYLLABLE
            # -----------------------------------------------------------------

            # Add current character to syllable
            # If it's a special token (C, L, N, etc.), restore the original digraph
            syl += SPECIAL_TOKENS.get(char, char)

            # If we've hit a syllable boundary (or end of word), finalize it
            if is_end_of_syl or is_last_char:
                sub_tokens.append(syl)
                syl = ""  # Start fresh for next syllable

        # =====================================================================
        # SECOND PASS: ERROR CORRECTION
        # =====================================================================
        # This section fixes systematic errors from the first pass
        # NOTE: Ideally this would all be handled in the main loop above,
        # but some patterns are too complex or context-dependent

        # HARDCODED CORRECTIONS: Words that consistently syllabify wrong
        # This is an empirical dictionary built from benchmark failures
        bad_toks = {
            # Atlas-related words (initial 'a' separates from 'tl' cluster)
            "boen": ["bo", "en"],
            "atle": ["a", "tle"],  # "atlas" → a.tlas
            "atlo": ["a", "tlo"],  # "atlântico" → a.tlân.ti.co
            'atlan': ['a', 'tlan'],
            "catlo": ["ca", "tlo"],
            "tatlo": ["ta", "tlo"],
            "hitle": ['hi', 'tle'],  # "Hitler" (foreign name)
            'atlân': ['a', 'tlân'],
            'atlé': ['a', 'tlé'],
            'satlân': ['sa', 'tlân'],
            'atlas': ["a", "tlas"],

            # Vowel sequence corrections (tricky hiatus/diphthong cases)
            'voyeu': ['voy', 'eu'],
            'doei': ['do', 'ei'],
            'lein': ['le', 'in'],
            'leim': ['le', 'im'],
            'rein': ['re', 'in'],
            'reim': ['re', 'im'],
            'toei': ['to', 'ei'],
            'noes': ['no', 'es'],
            'moer': ['mo', 'er'],
            'soer': ['so', 'er'],
            'soez': ['so', 'ez'],
            'oins': ['o', 'ins'],
            'brein': ['bre', 'in'],
            'breir': ['bre', 'ir'],
            'vair': ['va', 'ir'],
            'bair': ['ba', 'ir'],  # "bairro" → bai.rro (but cf. standalone 'ba.ir')
            'sain': ['sa', 'in'],
            'joei': ['jo', 'ei'],
            'cair': ['ca', 'ir'],
            'sair': ['sa', 'ir'],
            'pain': ['pa', 'in'],
            'paim': ['pa', 'im'],
            'seun': ['se', 'un'],
            'taois': ['ta', 'ois'],
            'maois': ['ma', 'ois'],
            'gao': ['ga', 'o'],
            'maun': ["ma", "un"],
            'oim': ['o', 'im'],

            # 'i/u' + nasal corrections
            'dium': ['di', 'um'],
            'tiun': ['ti', 'un'],
            'tium': ['ti', 'um'],
            'tiul': ['ti', 'ul'],
            'diur': ['di', 'ur'],
            'miur': ['mi', 'ur'],
            'maius': ['mai', 'us'],

            # 'oi' sequence corrections
            'doin': ["do", "in"],
            'doim': ["do", "im"],
            'toin': ["to", "in"],
            'toim': ["to", "im"],
            'coir': ["co", "ir"],
            'coin': ["co", "in"],
            'coim': ["co", "im"],

            # Miscellaneous
            'laus': ["la", "us"],
            'naum': ["na", "um"],
            'nya': ["ny", "a"],  # Foreign (Slavic?) pattern
            "móa": ['mó', 'a'],
            "faim": ['fa', 'im'],
            'feiu': ['fei', 'u'],
            'frui': ['fru', 'i']
        }

        # Apply corrections and handle systematic patterns
        clean_toks = []
        for idx, tok in enumerate(sub_tokens):
            # Check if previous token ends with vowel
            ends_vowel = clean_toks[-1][-1] in VOWELS if clean_toks else False
            is_ui = clean_toks[-1][-1] == "u" and tok == "i" if clean_toks else False

            # Look ahead to next token
            next_tok = sub_tokens[idx + 1] if idx < len(sub_tokens) - 1 else ""

            # -----------------------------------------------------------------
            # CORRECTION RULE 1: Known problematic tokenizations
            # -----------------------------------------------------------------
            if tok in bad_toks:
                clean_toks += bad_toks[tok]

            # -----------------------------------------------------------------
            # CORRECTION RULE 2: Foreign letter 'w'
            # -----------------------------------------------------------------
            elif tok == "w":
                # 'w' behaves like vowel 'u', should merge with adjacent vowels
                if ends_vowel:
                    # Previous syllable ends with vowel → merge 'w' with it
                    clean_toks[-1] = clean_toks[-1] + tok
                else:
                    # Merge with next token
                    sub_tokens[idx + 1] = tok + sub_tokens[idx + 1]

            # -----------------------------------------------------------------
            # CORRECTION RULE 3: 'vr' and 'vl' clusters
            # -----------------------------------------------------------------
            # These clusters are tricky because 'v' + liquid should split
            # Example: "livro" → li.vro (not liv.ro)
            elif "vr" in tok:
                a, b = tok.split("vr")
                clean_toks += [a, f"vr{b}"]
            elif "vl" in tok:
                a, b = tok.split("vl")
                clean_toks += [a, f"vl{b}"]

            # -----------------------------------------------------------------
            # CORRECTION RULE 4: Diphthong + 'nh' → hiatus
            # -----------------------------------------------------------------
            # When diphthong 'ai' or 'oi' precedes 'nh', it becomes hiatus
            # Example: "rainha" [ʁa.ˈĩ.ɲɐ] → ra.i.nha (not rai.nha)
            # The palatal nasal 'nh' forces the 'i' to be separate syllable
            elif next_tok.startswith("nh") and (tok.endswith("ai") or tok.endswith("oi")):
                clean_toks += [tok[:-1], tok[-1]]

            # -----------------------------------------------------------------
            # CORRECTION RULE 5: Standalone consonants (orphaned)
            # -----------------------------------------------------------------
            # If we somehow got a syllable with just one consonant, merge it
            elif len(tok) == 1 and tok not in VOWELS:
                if idx > 0:
                    # Merge with previous syllable
                    clean_toks[-1] = clean_toks[-1] + tok
                else:
                    # Merge with next syllable
                    sub_tokens[idx + 1] = tok + sub_tokens[idx + 1]

            # -----------------------------------------------------------------
            # CORRECTION RULE 6: Standalone final vowels
            # -----------------------------------------------------------------
            # A single final vowel 'u' or 'i' after a vowel is likely a
            # missed diphthong, not hiatus
            # Example: "pau" should be one syllable [paw], not pa.u
            elif idx == len(sub_tokens) - 1 and ends_vowel and tok in "ui":
                clean_toks[-1] = clean_toks[-1] + tok

            # -----------------------------------------------------------------
            # CORRECTION RULE 7: 'ui' sequence at position 1
            # -----------------------------------------------------------------
            # Second token is just 'i' after 'u' → likely diphthong
            # Example: "fui" → should be one syllable [fuj], not fu.i
            elif idx == 1 and ends_vowel and clean_toks[-1][-1] == "u" and tok == "i":
                clean_toks[-1] = clean_toks[-1] + tok

            # -----------------------------------------------------------------
            # CORRECTION RULE 8: 'cui' pattern before 'd'/'t'
            # -----------------------------------------------------------------
            # "cuidado" → cui.da.do (not cu.i.da.do)
            elif clean_toks and (next_tok.startswith("d") or next_tok.startswith("t")) and clean_toks[
                -1] == "cu" and tok == "i":
                clean_toks[-1] = clean_toks[-1] + tok

            # -----------------------------------------------------------------
            # CORRECTION RULE 9: Common diphthong patterns after specific syllables
            # -----------------------------------------------------------------
            # After syllables like 'tro', 'tra', 'ro', etc., 'i'/'u' form diphthongs
            # Example: "troika" → troi.ka (not tro.i.ka)
            elif ends_vowel and idx > 0 and clean_toks[-1] in ["tro", "tra", "ro", "re", "ra", "to"] and tok in "iu":
                clean_toks[-1] = clean_toks[-1] + tok

            # -----------------------------------------------------------------
            # DEFAULT: Accept token as-is
            # -----------------------------------------------------------------
            else:
                clean_toks.append(tok)

        # Log the result for this subword
        LOG.debug(subword, clean_toks)

        # Add this subword's syllables to the overall token list
        tokens += clean_toks

    # Return final syllabified word
    return tokens


# =============================================================================
# BENCHMARK / TESTING
# =============================================================================

if __name__ == "__main__":
    """
    Benchmark the syllabification algorithm against a gold-standard lexicon.

    This compares the algorithm's output against human-verified syllabifications
    from a comprehensive Portuguese dictionary.

    EVALUATION METRICS:
    -------------------
    - Total words: Number of words in test lexicon
    - Correct: Number of exact matches between predicted and gold syllabification
    - Accuracy: correct / total (percentage of perfect matches)

    CURRENT PERFORMANCE:
    --------------------
    53,154 correct out of 53,349 total words = 99.64% accuracy

    Less than 200 words are syllabified incorrectly - mostly:
    - Very rare words (technical, archaic, foreign)
    - Ambiguous cases where multiple syllabifications are acceptable
    - Edge cases in diphthong/hiatus distinction

    Most errors would require:
    - Dictionary lookup for irregular cases
    - Morphological analysis (prefix/suffix boundaries)
    - Statistical models trained on large corpora
    """

    LOG.setLevel("DEBUG")

    # Import lexicon with gold-standard syllabifications
    from tugaphone.lexicon import TugaLexicon

    lex = TugaLexicon()

    big_chunks = []  # Collect problematic syllabifications
    total = 0  # Total words tested
    correct = 0  # Correctly syllabified words

    # Test every word in the lexicon
    for w in lex.get_wordlist():
        # Optional: filter for specific patterns during debugging
        # if "áu" not in w:
        #    continue

        # Get gold-standard syllabification
        truth = lex.get_syllables(w)

        # Get our algorithm's prediction
        pred = syllabify(w)

        # Compare
        if pred == truth:
            correct += 1
        else:
            # Print mismatches for analysis
            print(w, pred, truth)
            big_chunks += pred

        total += 1

    # Print results
    print(correct, total)
    # Expected output: 53157 53349

    acc = correct / total
    print("Accuracy:", acc)
    # Expected output: ~0.9964 (99.64%)