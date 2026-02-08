"""
Portuguese Orthography → IPA Transcription System

This module provides comprehensive conversion from Portuguese orthography to
International Phonetic Alphabet (IPA) notation, following prescriptive norms
for European Portuguese (pt-PT), Brazilian Portuguese (pt-BR), and African
Portuguese variants (pt-AO, pt-MZ, pt-TL).

LINGUISTIC BACKGROUND:
======================
Portuguese orthography uses Latin script with diacritical marks to represent
a rich phonological system. The relationship between spelling and pronunciation
is relatively regular but includes context-sensitive rules, silent letters,
and dialectal variations.

KEY PHONOLOGICAL CONCEPTS:
--------------------------
1. STRESS: Portuguese uses lexical stress (word-level prominence of syllables)
   - Proparoxytone: stress on antepenultimate (third-to-last) syllable - rare, always marked
   - Paroxytone: stress on penultimate (second-to-last) syllable - most common
   - Oxytone: stress on final syllable - less common, specific phonological contexts

2. VOWEL QUALITY: Stressed vs unstressed vowels differ in quality and reduction
   - Stressed: fuller realization, can be open [ɛ, ɔ] or closed [e, o]
   - Unstressed: typically reduced to [ɨ] or [ɐ] in European Portuguese
   - Brazilian: less reduction, maintains [e, o, a] quality

3. NASALIZATION: Vowels can be oral or nasal
   - Marked by tilde (ã, õ) or followed by nasal consonant (m, n)
   - Creates distinct phonemes, not just allophones
   - Less nasalized in Brazilian Portuguese

4. DIPHTHONGS: Sequences of vowel + semivowel or semivowel + vowel
   - Falling/descending: vowel → semivowel (rei [ˈʁej])
   - Rising/ascending: semivowel → vowel (piano [ˈpjɐnu])
   - Can be oral or nasal
   - Brazilian: additional diphthongs from L-vocalization

IMPLEMENTATION ARCHITECTURE:
============================
The code uses a hierarchical tokenization model that mirrors linguistic structure:

Sentence → Words → Graphemes → Characters

- Character: Single letter/symbol
- Grapheme: Minimal spelling unit (can be digraph like 'ch' or diphthong like 'ai')
- Word: Sequence of graphemes with syllable structure
- Sentence: Sequence of words with prosodic information

All indices are computed top-down during initialization to avoid circular dependencies.
Context-sensitive rules are applied bottom-up during IPA generation.

PHONOLOGICAL FEATURE FRAMEWORK:
===============================
This module provides comprehensive phonological and phonetic feature extraction
at all levels of analysis. These features are critical for:

1. MACHINE LEARNING: Feature vectors for TTS, ASR, and NLP models
2. LINGUISTIC ANALYSIS: Studying phonological patterns and distributions
3. IPA GENERATION: Context-sensitive rule application
4. DEBUGGING: Understanding transcription decisions

CHARACTER-LEVEL FEATURES:
------------------------
Articulatory Features (Consonants):
- manner_of_articulation: How airflow is restricted (plosive, fricative, nasal, etc.)
- place_of_articulation: Where in vocal tract (bilabial, alveolar, velar, etc.)
- voicing: Vocal cord vibration (voiced/voiceless)
- Derived: is_sonorant, is_obstruent, is_liquid, is_fricative, is_plosive,
           is_nasal_consonant, is_sibilant, is_rhotic

IPA Relevance: These features determine base consonant symbols and context rules.
Example: 'c' before 'e' → [s] because 'e' is front vowel (palatalization trigger)

Vowel Quality Features:
- vowel_height: Tongue position vertically (high, mid-high, mid-low, low)
- vowel_backness: Tongue position horizontally (front, central, back)
- vowel_roundedness: Lip position (rounded, unrounded)
- Derived: is_front_vowel, is_back_vowel, is_rounded_vowel

IPA Relevance: Determines vowel symbol selection and stress-based quality changes.
Example: Stressed 'e' → [ɛ], Unstressed 'e' → [ɨ] (EP) or [e] (BR)

Positional Features:
- is_onset, is_nucleus, is_coda: Syllable position
- is_intervocalic: Between two vowels (triggers voicing)
- is_first_word_letter, is_last_word_letter

IPA Relevance: Position determines allophonic variants.
Example: 's' intervocalic → [z] (casa [ˈkazɐ])

GRAPHEME-LEVEL FEATURES:
-----------------------
Structural Classification:
- is_digraph, is_trigraph: Multi-letter units (ch, nh, que)
- is_diphthong, is_triphthong: Vowel sequences (ai, miau)
- is_nasal: Nasalization marker
- is_palatal: Palatal articulation (nh, lh)

IPA Relevance: Multi-letter graphemes map to single phonemes or special sequences.
Example: 'nh' → [ɲ] (single palatal nasal phoneme)

Diphthong Classification:
- is_falling_diphthong: V-G sequence (pai [paj])
- is_rising_diphthong: G-V sequence (piano [pjɐnu])
- is_nasal_diphthong: Nasalized (mãe [mɐ̃j̃])

IPA Relevance: Direction and nasalization affect transcription.

Phonotactic Features:
- syllable_position: onset, nucleus, or coda
- has_complex_onset: Part of consonant cluster
- requires_liaison: May link to following word

IPA Relevance: Syllable position affects phoneme realization.
Example: /l/ in coda → [w] in Brazilian Portuguese (Brasil → [bɾaˈziw])

WORD-LEVEL FEATURES:
-------------------
Stress Patterns:
- stress_pattern: oxytone, paroxytone, proparoxytone
- stressed_syllable_idx: Which syllable carries stress

IPA Relevance: Determines placement of stress marker (ˈ) in IPA.
Example: café (oxytone) → [kaˈfɛ], casa (paroxytone) → [ˈkazɐ]

Syllable Structure:
- syllable_structure_pattern: CV pattern (CV.CVC.CV)
- phoneme_count: Total phonemes

IPA Relevance: Shows phonotactic constraints and complexity.

Phonological Inventory:
- has_diphthongs, has_nasal_sounds, has_palatal_sounds
- vowel_sequence, consonant_sequence

IPA Relevance: Identifies key phonological features requiring special handling.

Irregularity:
- is_irregular: Requires dictionary lookup
- is_homograph: POS-dependent pronunciation

IPA Relevance: Irregular words bypass rule-based transcription.
Example: "muito" [ˈmũjtu] (irregular nasal diphthong)

SENTENCE-LEVEL FEATURES:
-----------------------
Currently focused on word-level analysis. Future extensions:
- Liaison patterns across word boundaries
- Phrasal stress and intonation contours
- Resyllabification in connected speech

QUICK REFERENCES:
===========
- http://www.portaldalinguaportuguesa.org
- https://en.wiktionary.org/wiki/Wiktionary:International_Phonetic_Alphabet
- https://en.wiktionary.org/wiki/Appendix:Portuguese_pronunciation
- https://en.wiktionary.org/wiki/Appendix:Portuguese_spellings
- https://european-portuguese.info/vowels
- https://pt.wikipedia.org/wiki/L%C3%ADngua_portuguesa
- https://pt.wikipedia.org/wiki/Ortografia_da_l%C3%ADngua_portuguesa
- https://pt.wikipedia.org/wiki/Gram%C3%A1tica_da_l%C3%ADngua_portuguesa
- https://pt.wikipedia.org/wiki/Fonologia_da_língua_portuguesa
- https://pt.wikipedia.org/wiki/Processo_do_vocalismo_%C3%A1tono_do_portugu%C3%AAs_europeu
- https://pt.wikipedia.org/wiki/Ditongo
- https://pt.wikipedia.org/wiki/Tritongo
- https://pt.wikipedia.org/wiki/Hiato_(lingu%C3%ADstica)
- https://pt.wikipedia.org/wiki/D%C3%ADgrafo
- https://pt.wikipedia.org/wiki/Fonema
- https://pt.wikipedia.org/wiki/Alofonia
"""

import dataclasses
import string
from functools import cached_property
from typing import List, Optional, Dict, Tuple

from tugaphone.number_utils import normalize_numbers
from tugaphone.syl import syllabify
from tugaphone.dialects import (DialectInventory, EuropeanPortuguese, BrazilianPortuguese,
                                AngolanPortuguese, MozambicanPortuguese, TimoresePortuguese)


# =============================================================================
# Helper Functions
# =============================================================================

def detect_stress_position(word: str, syllables: List[str], dialect: DialectInventory) -> int:
    """
    Determine which syllable carries primary stress.

    ALGORITHM:
    ----------
    1. Check for explicit accent marks → stress that syllable
    2. Check word-final pattern against OXYTONE_ENDINGS
    3. Default to penultimate (paroxytone rule)

    Args:
        word: Normalized word string
        syllables: List of syllables
        dialect: DialectInventory with stress rules

    Returns:
        Index of stressed syllable (0-based)

    Examples:
        >>> detect_stress_position("café", ["ca", "fé"], dialect)
        1  # Final syllable (explicit accent)

        >>> detect_stress_position("casa", ["ca", "sa"], dialect)
        0  # Penultimate (default)

        >>> detect_stress_position("falar", ["fa", "lar"], dialect)
        1  # Final (ends in -r)
    """
    n_syllables = len(syllables)

    # Monosyllables are inherently stressed
    if n_syllables == 1:
        return 0

    # Check for explicit accent marks (primary stress markers)
    for idx, syllable in enumerate(syllables):
        if any(char in syllable for char in dialect.PRIMARY_STRESS_MARKERS):
            return idx

    # Check for oxytone word endings (final stress)
    for ending in dialect.OXYTONE_ENDINGS:
        if word.endswith(ending):
            return n_syllables - 1

    # Default: paroxytone (penultimate stress)
    return n_syllables - 2 if n_syllables >= 2 else 0


def is_grapheme_silent(grapheme: str, context_before: str, context_after: str,
                       word: str, dialect: DialectInventory) -> bool:
    """
    Determine if a grapheme has no phonetic realization (silent).

    SILENT CATEGORIES:
    ------------------
    1. H: Always silent except in digraphs (handled separately)
    2. U in QU/GU: Silent before e/i in modern orthography
       - Exception: Some words have pronounced [w] (needs word list)
    3. Archaic consonants: p in mpt/mpc/mpç (pre-2009 spelling)
    4. First letter of doubled consonants in digraphs: rr, ss, ff, ll

    Args:
        grapheme: The grapheme to check
        context_before: Characters immediately before
        context_after: Characters immediately after
        word: Full word (for irregular word lookup)
        dialect: DialectInventory with rules

    Returns:
        True if grapheme is silent, False otherwise

    Examples:
        >>> is_grapheme_silent('h', '', 'oje', 'hoje', dialect)
        True  # h is always silent

        >>> is_grapheme_silent('u', 'q', 'ero', 'quero', dialect)
        True  # u silent in 'que'

        >>> is_grapheme_silent('u', 'q', 'ino', 'equino', dialect)
        False  # u pronounced in 'equino' [eˈkwinu]
        (Note: This would require word list to distinguish)
    """
    g = grapheme.lower()
    before = context_before.lower()
    after = context_after.lower()

    # H is always silent in Portuguese
    if g == "h":
        return True

    # U after Q or G before E or I (modern orthography default: silent)
    # Historical note: Trema (ü) used to mark pronounced u
    # Modern: Requires etymology/word list to determine
    if g == "u" and before in ["q", "g"] and after and after[0] in "ei":
        # Check word list for know exceptions
        if word.lower() in ["equino", "antiguidade, linguiça", "pinguim", "frequente", "frequentemente"]:
            return False
        # assume silent (most common)
        return True

    # Archaic silent P in mpc/mpç/mpt
    if g == "p" and before == "m" and after and after[0] in "cç":
        # Check if word is in archaic word list
        for cluster, words in dialect.ARCHAIC_MUTE_P.items():
            if cluster in word and word in words:
                return True

    # First consonant in geminate digraphs (rr, ss, ff, ll, mm)
    # These are handled at grapheme level, not here
    # (The grapheme would be "rr" as a unit, not two 'r's)

    return False


# =============================================================================
# CHARACTER TOKEN
# =============================================================================

@dataclasses.dataclass
class CharToken:
    """
    Represents a single character with its phonological context.

    LINGUISTIC ROLE:
    ----------------
    Characters are the atomic units of orthography.
    Their phonetic realization depends on:
    - Inherent properties (vowel/consonant, diacritics)
    - Linear context (preceding/following characters)
    - Hierarchical context (parent grapheme, syllable, word)
    - Prosodic context (stress, position in word)

    DESIGN RATIONALE:
    -----------------
    We track both the character itself and its context
    to enable context-sensitive phonological rules.
    All indices are computed during initialization to avoid
    circular dependencies.

    Attributes:
        surface: The actual character string (may include diacritics)
        char_idx: Position within parent grapheme (0-based)
        parent_grapheme: GraphemeToken containing this character
    """

    surface: str
    char_idx: int = 0  # parent_grapheme.characters[idx] == self
    parent_grapheme: Optional["GraphemeToken"] = None

    def __post_init__(self):
        """
        Validate and precompute indices.

        Indices are computed top-down during sentence initialization
        to avoid circular dependency issues.
        """
        # Validation
        if len(self.surface) != 1:
            raise ValueError(f"CharToken must contain exactly one character, got: {self.surface}")

    # =========================================================================
    # BASIC PROPERTIES
    # =========================================================================

    @cached_property
    def dialect(self):
        return self.parent_grapheme.dialect

    @cached_property
    def normalized(self) -> str:
        """
        Lowercase, normalized form of character.

        Normalization maps archaic/foreign diacritics to standard equivalents.
        Examples:
            - ü → w (represents [w] sound)
            - è → é (obsolete grave → modern acute)
            - î → i (redundant circumflex → plain)
        """
        s = self.surface.lower().strip()
        return self.dialect.NORMALIZED_VOWELS.get(s, s)

    # =========================================================================
    # INDICES AND CONTEXT
    # =========================================================================

    @cached_property
    def idx_in_syllable(self) -> int:
        """Index of this character in parent syllable."""
        if not self.parent_grapheme:
            return -1
        return self.parent_grapheme.idx_in_syllable + self.char_idx

    @cached_property
    def idx_in_word(self) -> int:
        """Index of this character in parent word."""
        if not self.parent_grapheme:
            return -1
        return self.parent_grapheme.idx_in_word + self.char_idx

    @cached_property
    def idx_in_sentence(self) -> int:
        """Index of this character in parent sentence."""
        if not self.parent_grapheme:
            return -1
        return self.parent_grapheme.idx_in_sentence + self.char_idx

    @cached_property
    def parent_word(self) -> Optional['WordToken']:
        """The word containing this character."""
        if self.parent_grapheme:
            return self.parent_grapheme.parent_word
        return None

    @cached_property
    def parent_sentence(self) -> Optional['Sentence']:
        """The sentence containing this character."""
        if not self.parent_word:
            return None
        return self.parent_word.parent_sentence

    @cached_property
    def prev_char(self) -> Optional['CharToken']:
        """Previous character in the word, or None if first."""
        if not self.parent_grapheme:
            return None
        if self.char_idx == 0:
            # go to prev grapheme
            if self.prev_grapheme:
                return self.prev_grapheme.last_char
            return None
        return self.parent_grapheme.characters[self.char_idx - 1]

    @cached_property
    def next_char(self) -> Optional['CharToken']:
        """Next character in the word, or None if last."""
        if not self.parent_grapheme:
            return None
        if self.char_idx >= len(self.parent_grapheme.characters) - 1:
            # go to next grapheme
            if self.next_grapheme:
                return self.next_grapheme.first_char
            return None
        return self.parent_grapheme.characters[self.char_idx + 1]

    @cached_property
    def prev_grapheme(self) -> Optional['GraphemeToken']:
        if not self.parent_grapheme:
            return None
        return self.parent_grapheme.prev_grapheme

    @cached_property
    def next_grapheme(self) -> Optional['GraphemeToken']:
        if not self.parent_grapheme:
            return None
        return self.parent_grapheme.next_grapheme

    # -------------------------------
    # Look-behind/ahead
    # -------------------------------
    @cached_property
    def prefix(self) -> str:
        if not self.parent_word:
            return ""
        return self.parent_word.normalized[:self.idx_in_word]

    @cached_property
    def suffix(self) -> str:
        if not self.parent_word:
            return ""
        return self.parent_word.normalized[self.idx_in_word + 1:]

    # =========================================================================
    # CHARACTER CLASSIFICATION
    # =========================================================================
    @cached_property
    def is_punct(self) -> bool:
        """True if character is punctuation."""
        return self.surface in self.dialect.PUNCT_CHARS

    @cached_property
    def is_foreign(self) -> bool:
        """
        True if character is not in traditional Portuguese alphabet.

        Foreign letters: k, w, y
        Used in: loanwords, foreign names, scientific terms
        """
        return self.normalized in self.dialect.FOREIGN_CHARS

    @cached_property
    def is_silent(self) -> bool:
        """
        True if character has no phonetic realization.

        Silent letter categories:
        1. H: Always silent (except in digraphs ch, nh, lh)
        2. U in QU/GU: Silent before e/i (modern orthography)
        3. Archaic P: Silent in mpc/mpç/mpt clusters
        4. First letter in doubled consonant digraphs

        Context-dependent - uses word and positional information.
        """
        return is_grapheme_silent(
            self.normalized,
            self.prefix,
            self.suffix,
            self.parent_word.normalized if self.parent_word else "",
            self.dialect
        )

    # =========================================================================
    # VOWEL QUALITY CLASSIFICATION
    # =========================================================================
    @cached_property
    def is_vowel(self) -> bool:
        """
        True if character represents a vowel (with or without diacritics).

        Portuguese vowels: a, e, i, o, u
        With diacritics: á, à, â, ã, é, ê, í, ó, ô, õ, ú
        Archaic: è, ì, ò, ù, ẽ, ĩ, ũ, ä, ë, ï, ö, ü, ÿ
        """
        return self.normalized in (
                self.dialect.VOWEL_CHARS |
                self.dialect.ACUTE_VOWEL_CHARS |
                self.dialect.GRAVE_VOWEL_CHARS |
                self.dialect.CIRCUM_VOWEL_CHARS |
                self.dialect.TILDE_VOWEL_CHARS |
                self.dialect.TREMA_VOWEL_CHARS
        )

    @cached_property
    def is_consonant(self) -> bool:
        """True if character represents a consonant."""
        return not self.is_vowel and not self.is_punct

    @cached_property
    def is_semivowel(self) -> bool:
        """
        True if character can function as semivowel (glide).

        Semivowels in Portuguese:
        - [j]: written as 'i' or 'e'
        - [w]: written as 'u' or 'o'

        Whether it actually IS a semivowel depends on position:
        - In diphthong: semivowel
        - As syllable nucleus: vowel
        """
        if self.is_nucleus:
            return False
        if self.dialect.dialect_code.startswith("pt-BR") and self.normalized == "l":
            return self.parent_grapheme.normalized in self.dialect.PTBR_DIPHTHONGS.values()
        return self.normalized in self.dialect.SEMIVOWEL_CHARS

    @cached_property
    def has_diacritics(self) -> bool:
        """True if character has diacritical marks."""
        return self.normalized in (
                self.dialect.ACUTE_VOWEL_CHARS |
                self.dialect.GRAVE_VOWEL_CHARS |
                self.dialect.CIRCUM_VOWEL_CHARS |
                self.dialect.TILDE_VOWEL_CHARS |
                self.dialect.TREMA_VOWEL_CHARS
        )

    @cached_property
    def is_nasal_vowel(self) -> bool:
        """
        True if vowel is phonemically nasal.

        Two orthographic realizations:
        1. Tilde: ã, õ (and archaic ẽ, ĩ, ũ)
        2. Vowel + nasal consonant: am, an, em, en, etc.
        """
        if not self.is_vowel:
            return False

        # Explicit tilde marking
        if self.normalized in self.dialect.TILDE_VOWEL_CHARS:
            return True

        # Followed by m/n in coda position
        if self.next_char and self.next_char.normalized in "mn":
            # Check if next char is in coda (not before vowel)
            next_next = self.next_char.next_char
            if not next_next or next_next.is_consonant:
                return True

        return False

    @cached_property
    def is_open_vowel(self) -> bool:
        """
        True if vowel is phonetically open (low tongue position).

        Open vowels: [a, ɛ, ɔ]
        Marked with acute accent: á, é, ó

        Linguistic note: Only a, e, o have open/closed distinction.
        i and u are always closed (high vowels).
        """
        return self.normalized in self.dialect.ACUTE_VOWEL_CHARS or self.normalized == "a"

    @cached_property
    def is_closed_vowel(self) -> bool:
        """
        True if vowel is phonetically closed (high tongue position).

        Closed vowels: [i, e, o, u, ɨ]
        High vowels i, u are always closed.
        Mid vowels e, o are closed when marked with circumflex: ê, ô
        """
        return self.normalized in ["i", "u", "ê", "ô"]

    @cached_property
    def is_prepalatal_vowel(self) -> bool:
        if not self.is_vowel:
            return False
        # inside a individual grapheme
        if self.next_char and self.next_char == "j":
            return True
        # inter-grapheme
        if self.next_grapheme:
            if self.next_grapheme.normalized in ["ch", "lh"] or self.next_grapheme.normalized[0] == "j":
                return True
        return False

    # =========================================================================
    # SYLLABLE QUALITY CLASSIFICATION
    # =========================================================================
    @cached_property
    def parent_syllable(self) -> str:
        if not self.parent_grapheme:
            return self.surface
        return self.parent_grapheme.parent_syllable

    @cached_property
    def is_nucleus(self) -> bool:
        if not self.is_vowel:
            return False
        if not self.has_diacritics and self.parent_grapheme and self.parent_grapheme.is_diphthong:
            is_semi = self.normalized in self.dialect.SEMIVOWEL_CHARS
            return not is_semi
        return True

    @cached_property
    def is_onset(self) -> bool:
        return self.idx_in_syllable == 0

    @cached_property
    def is_coda(self) -> bool:
        if self.is_vowel:
            return False
        if self.is_last_word_letter:
            return True
        return self.parent_syllable[-1] == self.surface

    # =========================================================================
    # POSITIONAL PROPERTIES
    # =========================================================================

    @cached_property
    def is_first_word_letter(self) -> bool:
        """True if this is the first letter of the word."""
        return self.idx_in_word == 0

    @cached_property
    def is_last_word_letter(self) -> bool:
        """True if this is the last letter of the word."""
        if not self.parent_word:
            return False
        return self.idx_in_word == len(self.parent_word.normalized) - 1

    @cached_property
    def is_intervocalic(self) -> bool:
        """
        True if character is between two vowels (V-C-V context).

        Relevant for:
        - S voicing: casa [ˈkazɐ] (s → [z] between vowels)
        - R strengthening: caro vs carro
        """
        prev_is_vowel = self.prev_char.is_vowel if self.prev_char else False
        next_is_vowel = self.next_char.is_vowel if self.next_char else False
        return prev_is_vowel and next_is_vowel

    @cached_property
    def is_between_consonant_vowel(self) -> bool:
        """
        True if pattern is C-S-V.

        Relevant for S voicing rules.
        """
        prev_is_cons = self.prev_char.is_consonant if self.prev_char else False
        next_is_vowel = self.next_char.is_vowel if self.next_char else False
        return prev_is_cons and next_is_vowel

    @cached_property
    def is_between_vowel_consonant(self) -> bool:
        """
        True if pattern is V-S-C.

        Relevant for syllable-final consonant rules.
        """
        prev_is_vowel = self.prev_char.is_vowel if self.prev_char else False
        next_is_cons = self.next_char.is_consonant if self.next_char else False
        return prev_is_vowel and next_is_cons

    # =========================================================================
    # PHONOLOGICAL FEATURES (Articulatory & Acoustic)
    # =========================================================================

    @cached_property
    def manner_of_articulation(self) -> Optional[str]:
        """
        Manner of articulation for consonants.

        Categories: plosive, fricative, affricate, nasal, lateral, tap, trill, approximant

        IPA Relevance: Determines basic consonant type, essential for choosing
        correct IPA symbol (e.g., 'p' → [p] plosive vs 'f' → [f] fricative)

        Returns:
            Manner category or None for vowels/punctuation
        """
        if not self.is_consonant:
            return None

        char = self.normalized

        # Plosives (stops): complete closure then release
        if char in 'pbdtkgqc':
            return 'plosive'

        # Fricatives: continuous turbulent airflow
        if char in 'fvszxjç':
            return 'fricative'

        # Nasals: oral closure with nasal airflow
        if char in 'mn':
            return 'nasal'

        # Laterals: central closure, lateral airflow
        if char == 'l':
            return 'lateral'

        # Taps/flaps: brief contact
        # Trills: multiple vibrations
        if char == 'r':
            # Context-dependent: can be tap [ɾ] or trill [r] or fricative [ʁ]
            return 'rhotic'  # General category

        return None

    @cached_property
    def place_of_articulation(self) -> Optional[str]:
        """
        Place of articulation for consonants.

        Categories: bilabial, labiodental, dental, alveolar, postalveolar,
                   palatal, velar, uvular, glottal

        IPA Relevance: Determines where in vocal tract sound is produced,
        critical for consonant identity (e.g., [p] bilabial vs [t] alveolar)

        Returns:
            Place category or None for vowels/punctuation
        """
        if not self.is_consonant:
            return None

        char = self.normalized

        # Bilabial: both lips
        if char in 'pbm':
            return 'bilabial'

        # Labiodental: lower lip + upper teeth
        if char in 'fv':
            return 'labiodental'

        # Dental/alveolar: tongue tip at/near teeth
        if char in 'tdnszl':
            return 'alveolar'

        # Postalveolar: tongue behind alveolar ridge
        if char in 'xj':
            return 'postalveolar'

        # Palatal: tongue body at hard palate
        # In Portuguese, 'nh' [ɲ], 'lh' [ʎ]

        # Velar: tongue back at soft palate
        if char in 'kgq':
            return 'velar'

        # Uvular/alveolar for R (dialect-dependent)
        if char == 'r':
            return 'alveolar_or_uvular'

        if char == 'ç':
            return 'alveolar'  # cedilla → [s]

        return None

    @cached_property
    def voicing(self) -> Optional[str]:
        """
        Voicing status for consonants.

        Categories: voiced, voiceless

        IPA Relevance: Distinguishes consonant pairs like [p]/[b], [t]/[d], [s]/[z].
        Critical for Portuguese intervocalic voicing (casa → [ˈkazɐ])

        Returns:
            'voiced', 'voiceless', or None for vowels
        """
        if not self.is_consonant:
            return 'voiced' if self.is_vowel else None

        char = self.normalized

        # Context-dependent special case
        if char == 's':
            # Intervocalic S → [z] (voiced)
            if self.is_intervocalic:
                return 'voiced'
            return 'voiceless'

        # Voiceless consonants
        if char in 'ptkcfsx':
            return 'voiceless'

        # Voiced consonants
        if char in 'bdgvzjlmnr':
            return 'voiced'

        if char == 'ç':
            return 'voiceless'  # Always [s]

        return None

    @cached_property
    def vowel_height(self) -> Optional[str]:
        """
        Tongue height for vowels.

        Categories: high, mid-high, mid, mid-low, low

        IPA Relevance: Primary dimension for vowel quality.
        - High: [i u] ('i', 'u')
        - Mid-high: [e o] ('ê', 'ô')
        - Mid-low: [ɛ ɔ] ('é', 'ó')
        - Low: [a ɐ] ('a', unstressed)

        Returns:
            Height category or None for consonants
        """
        if not self.is_vowel:
            return None

        char = self.normalized

        # Reduced vowels (context-dependent)
        if char == 'e' and not self.has_primary_stress:
            return 'high'  # [ɨ] or [e]

        if char == 'o' and not self.has_primary_stress:
            return 'high'  # [u]

        # High vowels
        if char in 'iuíú':
            return 'high'

        # Mid-high (close-mid)
        if char in 'eêoô':
            return 'mid-high'

        # Mid-low (open-mid)
        if char in 'éó':
            return 'mid-low'

        # Low
        if char in 'aáàâ':
            return 'low'

        return None

    @cached_property
    def vowel_backness(self) -> Optional[str]:
        """
        Tongue position (front-back) for vowels.

        Categories: front, central, back

        IPA Relevance: Secondary dimension for vowel quality.
        - Front: [i e ɛ] ('i', 'e', 'é')
        - Central: [ɐ ɨ] (unstressed 'a', 'e')
        - Back: [u o ɔ] ('u', 'o', 'ó')

        Returns:
            Backness category or None for consonants
        """
        if not self.is_vowel:
            return None

        char = self.normalized

        # Central vowels (reduced)
        if char in 'a' and not self.has_primary_stress:
            return 'central'  # [ɐ]

        if char == 'e' and not self.has_primary_stress:
            return 'central'  # [ɨ] in EP

        # Front vowels
        if char in 'ieéêí':
            return 'front'

        # Back vowels
        if char in 'uoóôú':
            return 'back'

        # Stressed 'a' is central-low
        if char in 'aáàâ':
            return 'central'

        return None

    @cached_property
    def vowel_roundedness(self) -> Optional[str]:
        """
        Lip rounding for vowels.

        Categories: rounded, unrounded

        IPA Relevance: Distinguishes vowel quality.
        - Rounded: [u o ɔ] ('u', 'o', 'ó')
        - Unrounded: [i e ɛ a] ('i', 'e', 'é', 'a')

        Returns:
            Roundedness or None for consonants
        """
        if not self.is_vowel:
            return None

        char = self.normalized

        # Rounded vowels
        if char in 'uoóôú':
            return 'rounded'

        # Unrounded vowels
        if char in 'ieéêíaáàâ':
            return 'unrounded'

        return None

    @cached_property
    def is_sonorant(self) -> bool:
        """
        True if sound is a sonorant (resonant).

        Sonorants: vowels, nasals, liquids (l, r), glides
        Non-sonorants (obstruents): plosives, fricatives, affricates

        IPA Relevance: Sonorants can form syllable nuclei and affect
        surrounding sound quality through resonance.

        Returns:
            True for vowels, nasals, liquids; False for obstruents
        """
        if self.is_vowel:
            return True

        if self.is_consonant:
            char = self.normalized
            # Nasals, liquids, approximants
            if char in 'mnlr':
                return True

        return False

    @cached_property
    def is_obstruent(self) -> bool:
        """
        True if sound is an obstruent (non-resonant consonant).

        Obstruents: plosives, fricatives, affricates

        IPA Relevance: Obstruents undergo voicing assimilation and
        cannot serve as syllable nuclei.

        Returns:
            True for plosives, fricatives, affricates
        """
        if not self.is_consonant:
            return False

        char = self.normalized
        # Plosives, fricatives, affricates
        return char in 'pbdtkgfvszxjcçq'

    @cached_property
    def is_front_vowel(self) -> bool:
        """
        True if vowel is articulated in front of mouth.

        Front vowels: [i e ɛ]

        IPA Relevance: Affects palatalization and preceding consonant quality.
        E.g., 'c' before front vowels → [s] (centro → [ˈsẽtɾu])

        Returns:
            True for i, e, é, ê, í
        """
        if not self.is_vowel:
            return False
        return self.normalized in 'ieéêí'

    @cached_property
    def is_back_vowel(self) -> bool:
        """
        True if vowel is articulated in back of mouth.

        Back vowels: [u o ɔ]

        IPA Relevance: Affects labialization and rounding.

        Returns:
            True for u, o, ó, ô, ú
        """
        if not self.is_vowel:
            return False
        return self.normalized in 'uoóôú'

    @cached_property
    def is_rounded_vowel(self) -> bool:
        """
        True if vowel requires lip rounding.

        IPA Relevance: Determines lip position during articulation.

        Returns:
            True for u, o, ó, ô, ú
        """
        return self.vowel_roundedness == 'rounded'

    @cached_property
    def is_liquid(self) -> bool:
        """
        True if consonant is a liquid (l, r).

        Liquids: laterals and rhotics

        IPA Relevance: Liquids can form complex onsets (pr, tr, cl, br)
        and affect vowel quality in syllable codas.

        Returns:
            True for 'l' and 'r'
        """
        return self.is_consonant and self.normalized in 'lr'

    @cached_property
    def is_fricative(self) -> bool:
        """
        True if consonant is a fricative.

        Fricatives: continuous turbulent airflow

        IPA Relevance: Fricatives have characteristic acoustic signatures
        and different phonotactic constraints than stops.

        Returns:
            True for f, v, s, z, x, j, ç
        """
        return self.manner_of_articulation == 'fricative'

    @cached_property
    def is_plosive(self) -> bool:
        """
        True if consonant is a plosive (stop).

        Plosives: complete oral closure followed by release

        IPA Relevance: Plosives create silence+burst pattern,
        different from fricative continuous noise.

        Returns:
            True for p, b, t, d, k, g, c, q
        """
        return self.manner_of_articulation == 'plosive'

    @cached_property
    def is_nasal_consonant(self) -> bool:
        """
        True if consonant is nasal.

        Nasal consonants: m, n, (nh → [ɲ])

        IPA Relevance: Nasals trigger vowel nasalization in Portuguese
        and have distinct acoustic properties.

        Returns:
            True for 'm', 'n'
        """
        return self.is_consonant and self.normalized in 'mn'

    @cached_property
    def is_sibilant(self) -> bool:
        """
        True if consonant is a sibilant fricative.

        Sibilants: high-frequency fricatives (s, z, ʃ, ʒ)

        IPA Relevance: Sibilants have characteristic high-frequency noise
        and undergo special voicing rules in Portuguese.

        Returns:
            True for s, z, x, j, ç
        """
        if not self.is_consonant:
            return False
        return self.normalized in 'szxjç'

    @cached_property
    def is_rhotic(self) -> bool:
        """
        True if consonant is rhotic (r-sound).

        Rhotics: various r-sounds (tap, trill, fricative)

        IPA Relevance: Portuguese has multiple r allophones:
        - [ɾ] tap (intervocalic)
        - [r] trill (initial, after l/n/s)
        - [ʁ] uvular fricative (EP)
        - [h] glottal fricative (BR)

        Returns:
            True for 'r'
        """
        return self.is_consonant and self.normalized == 'r'

    # =========================================================================
    # STRESS PROPERTIES
    # =========================================================================

    @cached_property
    def has_primary_stress(self) -> bool:
        """
        True if this vowel carries primary stress.

        For diacritically marked vowels (á, é, etc.), stress is explicit.
        For unmarked vowels, stress is determined by syllable-level rules
        in the parent grapheme/word.
        """
        # Explicit stress markers
        if self.normalized in self.dialect.PRIMARY_STRESS_MARKERS:
            return True

        # Defer to parent grapheme's stress determination
        if self.parent_grapheme:
            return self.parent_grapheme.has_primary_stress

        return False

    @cached_property
    def has_secondary_stress(self) -> bool:
        """
        True if this vowel carries secondary stress.

        Circumflex and grave accents can mark secondary stress
        in compound words and some historical contexts.
        """
        # Explicit secondary stress markers
        if self.normalized in self.dialect.SECONDARY_STRESS_MARKERS:
            return True

        if self.is_vowel and self.prev_char and self.prev_char.normalized == "h":
            return True

        # Defer to parent grapheme
        if self.parent_grapheme:
            return self.parent_grapheme.has_secondary_stress

        return False

    # =========================================================================
    # IPA GENERATION
    # =========================================================================

    def _ipa_for_vowel(self) -> str:
        """
        Generate IPA for vowel character.

        VOWEL REALIZATION RULES:
        ------------------------
        1. Explicit quality: á→[a], é→[ɛ], ê→[e], ó→[ɔ], ô→[o]
        2. Stress-dependent:
           - Stressed a → [a]
           - Unstressed a → [ɐ]
           - Stressed e → [ɛ] or [e] (depends on syllable)
           - Unstressed e → [ɨ] (European) or [e] (Brazilian)
        3. Nasal: ã→[ɐ̃], õ→[õ], a+m/n→[ɐ̃], etc.

        Returns:
            IPA string for this vowel
        """
        s = self.normalized

        if s in self.dialect.SEMIVOWEL_CHARS and self.is_semivowel:
            if s == "i":
                return "j"
            elif s == "u":
                return "w"
            else:
                pass # ????

        if s in self.dialect.DEFAULT_CHAR2PHONEMES:

            # Explicit diacritical marking
            base_ipa = self.dialect.DEFAULT_CHAR2PHONEMES[s]

            word = self.parent_word.normalized if self.parent_word else ""

            # Special case: Single-vowel words
            if word == "a":
                return "ɐ"
            elif word == "e":
                return "i"
            elif word == "é":
                return "ɛ"
            elif word == "o":
                return "u"

            # Special case: prepositions
            preps = ["a", "o", "as", "os",
                     "de", "em", "por"]
            # Special case: determinants
            dets = ["da", "do", "das", "dos"]
            # Special case: contractions
            #   em a/o -> na/o
            #   para -> pra | para a -> prá
            contr = ["na", "no", "nas", "nos", "pra"]
            # Special case: oblique pronouns
            prons = ["me", "te", "se",
                     "le", "lo", "la",
                     "les", "los", "las",
                     "lhe", "lho", "lha",
                     "lhes", "lhos", "lhas"]
            if word in preps + dets + prons + contr:
                # Brazilian Portuguese: less reduction
                if self.dialect.dialect_code.startswith("pt-BR"):
                    if s == "a":
                        return "a"  # Less reduction
                    if s == "e":
                        return "e"  # Less reduction
                    if s == "o":
                        return "o"  # Less reduction
                else:
                    # European/African: more reduction
                    if s == "a":
                        return "ɐ"
                    if s == "e":
                        return "ɨ"
                    if s == "o":
                        return "u"

            # Override with stress-based quality for ambiguous vowels
            if s == "a":
                return "a" if self.has_primary_stress or self.has_secondary_stress else "ɐ"
            elif s == "e":
                if self.has_primary_stress:
                    return "ɛ"
                return "ɨ" if self.dialect.dialect_code.startswith("pt-PT") else "e"
            elif s == "o":
                return "ɔ" if self.has_primary_stress or self.has_secondary_stress else "u"

            return base_ipa

        return s  # Fallback

    def _ipa_for_consonant(self) -> str:
        """
        Generate IPA for consonant character.

        CONTEXT-SENSITIVE CONSONANT RULES:
        -----------------------------------
        1. C: [k] normally, [s] before e/i
        2. G: [ɡ] normally, [ʒ] before e/i
        3. R: [ɾ] normally, [ʁ] word-initially or after l/n/s
        4. S: [s] normally, [z] intervocalically
        5. X: [ʃ] normally, but [ks], [z], [s], [gz] in specific contexts
        6. Z: [z] normally, [ʃ] word-finally (European)

        Returns:
            IPA string for this consonant
        """
        s = self.normalized
        next_char = self.next_char.normalized if self.next_char else ""
        prev_char = self.prev_char.normalized if self.prev_char else ""

        # C before front vowels → [s]
        if s == "c" and next_char in self.dialect.FRONT_VOWEL_CHARS:
            return "s"

        # G before front vowels → [ʒ]
        if s == "g" and next_char in self.dialect.FRONT_VOWEL_CHARS:
            return "ʒ"

        # R after l, n, s → strong R
        if s == "r" and prev_char in ["l", "n", "s"]:
            if self.dialect.dialect_code.startswith("pt-BR"):
                return "h"  # Brazilian [h] or [x]
            elif self.dialect.dialect_code.startswith("pt-PT"):
                return "ʁ"  # European uvular
            else:
                return "r"  # African/Timorese alveolar trill

        # S between consonant and vowel → context-dependent
        if s == "s" and self.is_between_consonant_vowel:
            # Special case: trans- prefix
            word = self.parent_word.normalized if self.parent_word else ""
            if word.startswith(("trans", "trâns")) and self.idx_in_word == 4:
                # Check if followed by vowel (voice) or consonant (voiceless)
                if self.next_char and self.next_char.is_vowel:
                    # Exception: transação [tɾɐ̃zɐˈsɐ̃w]
                    return "z"
            return "s"

        # X rules (complex, context-dependent)
        if s == "x":
            return self._ipa_for_x()

        # Z word-finally → [ʃ] (European) or [s]
        if self.is_consonant and self.is_last_word_letter and s in self.dialect.WORD_FINAL_CHAR2PHONEMES:
            return self.dialect.WORD_FINAL_CHAR2PHONEMES[s]

        # Initial R → strong R [ʁ]
        if self.is_consonant and self.is_first_word_letter and s in self.dialect.WORD_INITIAL_CHAR2PHONEMES:
            return self.dialect.WORD_INITIAL_CHAR2PHONEMES[s]

        # intervocalic consonant rules
        # S between vowels → [z]
        if self.is_intervocalic and self.is_consonant and s in self.dialect.INTERVOCALIC_CHAR2PHONEMES:
            return self.dialect.INTERVOCALIC_CHAR2PHONEMES[s]

        # coda consonant rules
        if self.is_coda and self.is_consonant and s in self.dialect.CODA_CHAR2PHONEMES:
            return self.dialect.CODA_CHAR2PHONEMES[s]

        # onset consonant rules
        if self.is_onset and self.is_consonant and s in self.dialect.ONSET_CHAR2PHONEMES:
            return self.dialect.ONSET_CHAR2PHONEMES[s]

        # Default mapping
        return self.dialect.DEFAULT_CHAR2PHONEMES.get(s, s)

    def _ipa_for_x(self) -> str:
        """
        Generate IPA for the letter X (highly context-dependent).

        X PRONUNCIATION RULES:
        ----------------------
        1. Word-initial: [ʃ] - xadrez, xícara
        2. Word-final: [ks] - tórax, fax
        3. Intervocalic:
           a. [ʃ]: peixe, caixa (default)
           b. [ks]: sexo, máximo (after stressed vowel with accent)
           c. [z]: exemplo, exato (in ex- prefix before vowel)
           d. [s]: próximo (rare)
           e. [gz]: hexa- prefix (rare variant)

        This is one of the most complex orthographic patterns in Portuguese.

        Returns:
            IPA string for X
        """
        prev_char = self.prev_char.normalized if self.prev_char else ""
        next_char = self.next_char.normalized if self.next_char else ""
        word = self.parent_word.normalized if self.parent_word else ""

        # Word-initial: [ʃ]
        if self.is_first_word_letter:
            return "ʃ"

        # Word-final: [ks]
        if self.is_last_word_letter:
            return "ks"

        # Intervocalic context
        if self.is_intervocalic:
            # Check for hexa- prefix: [gz] variant
            if word.startswith("hexa") and self.idx_in_word == 2:
                return "gz"

            # Check for próxim-: [s]
            if word.startswith("próxim") and self.idx_in_word == 3:
                return "s"

            # Ex- prefix before vowel: [z]
            if prev_char == "e" and next_char in "aeiouáéíóú":
                # Examples: exemplo, exato, executivo
                return "z"

            # After stressed vowel with accent: [ks]
            if prev_char in self.dialect.ACUTE_VOWEL_CHARS | set("e"):
                # Examples: máximo, tóxico, sexo
                if prev_char == "ú":
                    # Exception: esdrúxulo [ʃ]
                    return "ʃ"
                return "ks"

            # Default intervocalic: [ʃ]
            return "ʃ"

        # Default: [ʃ]
        return "ʃ"

    @cached_property
    def ipa(self) -> str:
        """
        Generate IPA transcription for this character.

        ALGORITHM:
        ----------
        1. Handle punctuation → prosodic markers
        2. Check for silence
        3. Dispatch to vowel vs consonant rules
        4. Apply special-case overrides

        Returns:
            IPA string (may be empty for silent characters)
        """
        # Punctuation → prosodic markers
        if self.is_punct:
            return self.dialect.PUNCT2IPA.get(self.normalized, self.dialect.HIATUS_TOKEN)

        # Silent characters
        if self.is_silent:
            return ""

        # Dispatch based on vowel vs consonant
        if self.is_vowel:
            return self._ipa_for_vowel()
        else:
            return self._ipa_for_consonant()

    # =========================================================================
    # FEATURE EXTRACTION
    # =========================================================================

    @cached_property
    def features(self) -> Dict[str, any]:
        """
        Extract all linguistic features as a dictionary.

        Useful for:
        - Machine learning feature vectors
        - Debugging
        - Linguistic analysis

        Returns:
            Dictionary mapping feature names to values
        """
        return {
            # Basic identification
            "text": self.normalized,
            "ipa": self.ipa,

            # Positional features
            "is_first_letter": self.is_first_word_letter,
            "is_last_letter": self.is_last_word_letter,
            "is_onset": self.is_onset,
            "is_nucleus": self.is_nucleus,
            "is_coda": self.is_coda,

            # Basic classification
            "is_punct": self.is_punct,
            "is_vowel": self.is_vowel,
            "is_consonant": self.is_consonant,
            "is_foreign": self.is_foreign,
            "is_silent": self.is_silent,

            # Vowel features
            "is_semivowel": self.is_semivowel,
            "is_nasal_vowel": self.is_nasal_vowel,
            "is_open_vowel": self.is_open_vowel,
            "is_closed_vowel": self.is_closed_vowel,
            "is_front_vowel": self.is_front_vowel,
            "is_back_vowel": self.is_back_vowel,
            "is_rounded_vowel": self.is_rounded_vowel,
            "vowel_height": self.vowel_height,
            "vowel_backness": self.vowel_backness,
            "vowel_roundedness": self.vowel_roundedness,

            # Consonant features
            "manner_of_articulation": self.manner_of_articulation,
            "place_of_articulation": self.place_of_articulation,
            "voicing": self.voicing,
            "is_sonorant": self.is_sonorant,
            "is_obstruent": self.is_obstruent,
            "is_liquid": self.is_liquid,
            "is_fricative": self.is_fricative,
            "is_plosive": self.is_plosive,
            "is_nasal_consonant": self.is_nasal_consonant,
            "is_sibilant": self.is_sibilant,
            "is_rhotic": self.is_rhotic,

            # Contextual features
            "is_intervocalic": self.is_intervocalic,
            "is_between_consonant_vowel": self.is_between_consonant_vowel,
            "is_between_vowel_consonant": self.is_between_vowel_consonant,
            "is_prepalatal_vowel": self.is_prepalatal_vowel,

            # Diacritic and stress
            "has_diacritics": self.has_diacritics,
            "has_primary_stress": self.has_primary_stress,
            "has_secondary_stress": self.has_secondary_stress,
        }

    def __eq__(self, other) -> bool:
        """Allow comparison with string for convenience."""
        if isinstance(other, str):
            return self.surface == other
        return super().__eq__(other)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"CharToken('{self.surface}' → [{self.ipa}])"


# =============================================================================
# GRAPHEME TOKEN
# =============================================================================

@dataclasses.dataclass
class GraphemeToken:
    """
    Represents a grapheme - the minimal distinctive unit of writing.

    GRAPHEME DEFINITION:
    --------------------
    A grapheme is the smallest unit of a writing system.
    In alphabetic systems like Portuguese, graphemes can be:
    - Single letters: a, b, c
    - Digraphs: ch, nh, lh, rr, ss
    - Diphthongs: ai, ou, ei
    - Trigraphs: que, gui, coo
    - Tetragraphs: aien (rare)

    LINGUISTIC MOTIVATION:
    ----------------------
    Portuguese orthography uses multi-character sequences to represent:
    1. Single phonemes: ch → [ʃ], nh → [ɲ]
    2. Phoneme clusters: qu → [kw] or [k] depending on context
    3. Diphthongs: ai → [aj], ou → [ow]

    Tokenizing at grapheme level (not character level) respects
    the structure of the writing system.

    Attributes:
        surface: The grapheme string (1-4 characters)
        grapheme_idx: Position in parent word's grapheme list
        syllable_idx: Which syllable this grapheme belongs to
        characters: List of CharToken objects composing this grapheme
        parent_word: WordToken containing this grapheme
    """

    surface: str
    grapheme_idx: int = 0  # parent_word.graphemes[idx] == self
    syllable_idx: int = 0  # parent_word.normalized_syllables[idx] == self.surface
    characters: List[CharToken] = dataclasses.field(default_factory=list)
    parent_word: Optional["WordToken"] = None

    def __post_init__(self):
        """
        Initialize character tokens and compute indices.

        Characters are created and their indices are computed here
        to avoid circular dependencies during IPA generation.
        """
        if not self.characters:
            self.characters = [
                CharToken(
                    surface=c,
                    char_idx=i,
                    parent_grapheme=self
                )
                for i, c in enumerate(self.surface)
            ]

    # =========================================================================
    # BASIC PROPERTIES
    # =========================================================================
    @cached_property
    def dialect(self):
        return self.parent_word.dialect

    @cached_property
    def normalized(self) -> str:
        """Lowercase form of grapheme."""
        return self.surface.lower()

    @cached_property
    def n_chars(self) -> int:
        """Number of characters in this grapheme."""
        return len(self.characters)

    @cached_property
    def first_char(self) -> CharToken:
        """First character of grapheme."""
        return self.characters[0]

    @cached_property
    def last_char(self) -> CharToken:
        """Last character of grapheme."""
        return self.characters[-1]

    # =========================================================================
    # INDICES AND CONTEXT
    # =========================================================================
    @cached_property
    def idx_in_syllable(self) -> int:
        """Index of this grapheme in parent syllable."""
        if not self.parent_syllable:
            return -1
        if self.syllable_idx == 0:
            return self.idx_in_word
        prevs = [g for g in self.previous_graphemes if g.syllable_idx == self.syllable_idx]
        if prevs:
            return sum(len(g.surface) for g in prevs)
        return 0

    @cached_property
    def idx_in_word(self) -> int:
        """Index of this grapheme in parent word."""
        if not self.parent_word:
            return -1
        prev = self.previous_graphemes
        prev_len = sum(len(w.surface) for w in prev)
        return prev_len

    @cached_property
    def idx_in_sentence(self) -> int:
        """Index of this grapheme in parent sentence."""
        if not self.parent_word:
            return -1
        return self.parent_word.idx_in_sentence + self.idx_in_word

    @cached_property
    def previous_graphemes(self) -> List['GraphemeToken']:
        return [w for w in self.parent_word.graphemes if w.grapheme_idx < self.grapheme_idx]

    @cached_property
    def previous_syllables(self) -> List[str]:
        return [w for idx, w in enumerate(self.parent_word.syllables) if idx < self.syllable_idx]

    @cached_property
    def parent_sentence(self) -> Optional['Sentence']:
        """The sentence containing this grapheme."""
        if not self.parent_word:
            return None
        return self.parent_word.parent_sentence

    @cached_property
    def parent_syllable(self) -> Optional[str]:
        """The syllable string containing this grapheme."""
        if not self.parent_word or self.syllable_idx < 0:
            return None
        if self.syllable_idx >= len(self.parent_word.syllables):
            return None
        return self.parent_word.syllables[self.syllable_idx]

    # ------------------------------------------------------------------
    # Prefix/suffix context
    # ------------------------------------------------------------------
    @cached_property
    def prefix(self) -> str:
        """
        All text before this grapheme in the word.

        Used for checking morphological boundaries (prefixes).
        Example: In "biauricular", prefix of "au" is "bi"
        """
        if not self.parent_word:
            return ""
        return self.parent_word.normalized[:self.idx_in_word]

    @cached_property
    def suffix(self) -> str:
        """
        All text after this grapheme in the word.

        Used for checking word endings and contexts.
        """
        if not self.parent_word:
            return ""
        return self.parent_word.normalized[self.idx_in_word + 1:]

    @cached_property
    def prev_grapheme(self) -> Optional['GraphemeToken']:
        """Previous grapheme in word, or None if first."""
        if self.grapheme_idx == 0 or not self.parent_word:
            return None
        return self.parent_word.graphemes[self.grapheme_idx - 1]

    @cached_property
    def next_grapheme(self) -> Optional['GraphemeToken']:
        """Next grapheme in word, or None if last."""
        if not self.parent_word:
            return None
        if self.grapheme_idx >= len(self.parent_word.graphemes) - 1:
            return None
        return self.parent_word.graphemes[self.grapheme_idx + 1]

    # ------------------------------------------------------------------
    # Syllabic context
    # ------------------------------------------------------------------
    @cached_property
    def prev_syllable(self) -> Optional[str]:
        """Previous syllable string, or None if first."""
        if self.syllable_idx == 0 or not self.parent_syllable:
            return None
        return self.parent_word.normalized_syllables[self.syllable_idx - 1]

    @cached_property
    def next_syllable(self) -> Optional[str]:
        """Next syllable string, or None if last."""
        if self.syllable_idx == -1 or not self.parent_syllable:
            return None
        if self.syllable_idx >= len(self.parent_word.normalized_syllables) - 1:
            return None
        return self.parent_word.normalized_syllables[self.syllable_idx + 1]

    # =========================================================================
    # GRAPHEME CLASSIFICATION
    # =========================================================================

    @cached_property
    def is_archaism(self) -> bool:
        """
        True if grapheme uses archaic orthography.

        Archaic patterns:
        1. Trema (ü): Pre-1945/2009 marker for pronounced u
        2. Grave accents (except à): Pre-1973 secondary stress
        3. Archaic words with ph, mpt, mpc, mpç
        4. Obsolete circumflex: êle

        These may appear in historical texts or proper names.
        """
        s = self.normalized

        # Trema (abolished 1945/2009)
        if "ü" in s:
            return True

        # Grave accents (except à contraction)
        archaic_graves = [c for c in self.dialect.GRAVE_VOWEL_CHARS if c != "à"]
        if any(c in s for c in archaic_graves):
            return True

        # In paroxytones, when the same form existed with an open and a closed vowel, a circumflex accent was placed in the word with the closed vowel.
        # Example: êle (“he”) (/ˈe.li/) and ele (“name of the letter L”) (/ˈɛ.li/).
        # This usage was made obsolete by the 1945 spelling reform in Portugal, and by the 1971 spelling reform in Brazil.
        archaic_words = ["êle"]
        if s in archaic_words:
            return True

        # ph -> /f/ eg. "pharmacia"
        if s == "ph":
            return True

        # Quando, nas seqüências interiores "mpc", "mpç" e "mpt" se eliminar o "p",
        # o "m" passa a "n", escrevendo-se, respectivamente "nc", "nç" e "nt":
        if s in self.dialect.ARCHAIC_MUTE_P:
            # NOTE: a word list is needed, in modern orthography none of the letters is silent
            # we do not know if input text is modern or archaic (before acordo ortográfico)
            # exemplos:
            #   assumpcionista e assuncionista;
            #   assumpção e assunção;
            #   assumptível e assuntível;
            #   peremptório e perentório,
            #   sumptuoso e suntuoso,
            #   sumptuosidade e suntuosidade
            return self.parent_word.normalized in self.dialect.ARCHAIC_MUTE_P[s]
        return False

    @cached_property
    def is_nasal(self) -> bool:
        """
        True if grapheme represents nasal sound(s).

        Nasal patterns:
        1. Nasal digraphs: am, an, em, en, im, in, om, on, um, un
        2. Tilde vowels: ã, õ (and archaic ẽ, ĩ, ũ)
        3. Nasal diphthongs: ão, ãe, õe, em (final)
        """
        s = self.normalized

        # Nasal digraph lookup
        if s in self.dialect.NASAL_DIGRAPHS:
            return True

        # Tilde vowels
        if any(c in s for c in self.dialect.TILDE_VOWEL_CHARS):
            return True

        return False

    # ------------------------------------------------------------------
    # Diphthong classification
    # ------------------------------------------------------------------
    @cached_property
    def is_vocalic_hiatus(self) -> bool:
        # Hiato é quando duas vogais estão juntas porém em sílabas vizinhas.
        # O hiato diferencia-se de um ditongo e de um tritongo pelo fato de ser constituído por duas sílabas e,
        # consequentemente, ser pronunciado em dois esforços de voz.

        # Os outros casos que na escrita costumam estar representados por «i» + vogal ou «u» mais vogal
        # (ou, no português europeu, «e» + vogal ou «o» + vogal),
        # costumam ser considerados como hiatos.
        return False  # TODO

    @cached_property
    def is_diphthong(self) -> bool:
        """
        True if grapheme represents a diphthong.

        Diphthongs are two-vowel sequences in one syllable.
        Examples: ai, ei, ou, ão, ãe

        Note: Diphthong vs hiatus is determined by syllabification.
        Same spelling can be different:
        - caiu [kɐˈju]: hiatus (ca.iu, two syllables)
        - cai [ˈkaj]: diphthong (one syllable)
        """
        s = self.normalized
        # Observação: qu"em : não é um encontro vocálico, pois não se pronuncia o U.
        # Portanto, "qu" é um dígrafo e "ue" não é um ditongo.
        if s == "ue" and self.parent_word.normalized == "quem":
            return False
        if self.dialect.dialect_code.startswith("pt-BR") and s in self.dialect.PTBR_DIPHTHONGS:
            return True
        return s in self.dialect.DIPHTHONG2IPA

    @cached_property
    def is_triphthong(self) -> bool:
        """
        True if grapheme represents a triphthong.

        Triphthongs are three-vowel sequences in one syllable: G-V-G
        Examples: miau [ˈmjaw], Uruguai [uɾuˈɡwaj]

        Very rare in Portuguese.
        """
        return self.normalized in self.dialect.TRIPHTHONG2IPA

    @cached_property
    def is_falling_diphthong(self) -> bool:
        """
        True if diphthong has vowel before semivowel (V-G).

        Examples: pai, rei, meu, céu
        Direction: vowel [a] → glide [j]

        Most Portuguese diphthongs are falling.
        """
        if not self.is_diphthong:
            return False

        if self.dialect.dialect_code.startswith("pt-BR"):
            # Em muitos dialetos brasileiros, devido à Vocalização do fonema /l/ em fim de sílaba,
            # também são considerados ditongos decrescentes os seguintes casos.
            if self.normalized in self.dialect.PTBR_DIPHTHONGS.values():
                # exemplos:
                #     funil /fu.ˈniw/
                #     feltro /few.tɾu/
                #     mel /ˈmɛw/
                #     mal /ˈmaw/
                #     Sol /ˈsɔw/
                #     soldado /sow.ˈda.du/
                #     azul /aˈzuw/
                return True
        # Quando a vogal vem antes da semivogal, o ditongo é classificado como ditongo decrescente
        # exemplos:
        #   leite /ˈlej.ti/ - /ˈlɐj.tɨ/ (Lisboa)
        #   cai /ˈcaj/
        #   dói /ˈdɔj/
        #   foi /ˈfoj/
        #   cuidado /cuj.ˈda.du/
        #   viu /ˈviw/
        #   meu /ˈmew/
        #   céu /ˈcɛw/
        #   mau /ˈmaw/
        #   sou /ˈsow/
        return self.first_char.normalized not in self.dialect.SEMIVOWEL_CHARS

    @cached_property
    def is_rising_diphthong(self) -> bool:
        """
        True if diphthong has semivowel before vowel (G-V).

        Examples: piano, água, qual
        Direction: glide [j] → vowel [a]

        Less common than falling diphthongs in Portuguese.
        """
        if not self.is_diphthong:
            return False
        return self.first_char.normalized in self.dialect.SEMIVOWEL_CHARS

    @cached_property
    def is_nasal_diphthong(self) -> bool:
        """
        True if diphthong is nasalized.

        Examples: mãe [ˈmɐ̃j̃], cão [ˈkɐ̃w̃], põe [ˈpõj̃]

        Nasalization extends across entire diphthong.
        """
        if not self.is_diphthong:
            return False
        return self.first_char.normalized in self.dialect.TILDE_VOWEL_CHARS

    @cached_property
    def is_oral_diphthong(self) -> bool:
        """
        True if diphthong is oral (not nasal).

        Examples: pai, rei, meu, boi
        """
        return self.is_diphthong and not self.is_nasal_diphthong

    @cached_property
    def is_digraph(self) -> bool:
        """
        True if grapheme is a consonant digraph.

        Consonant digraphs (two letters, one consonant phoneme):
        - nh [ɲ]: palatal nasal
        - lh [ʎ]: palatal lateral
        - ch [ʃ]: postalveolar fricative
        - rr [ʁ]: strong R
        - ss [s]: voiceless between vowels
        - ph [f]: archaic

        Does NOT include nasal digraphs (am, em, etc.) - see is_nasal.
        """
        return self.normalized in self.dialect.DIGRAPH2IPA

    @cached_property
    def is_foreign_digraph(self) -> bool:
        """
        True if grapheme is a foreign digraph.

        Examples from loanwords:
        - sh [ʃ]: show, shopping
        - th [t]: thriller
        - ff [f]: graffiti
        - ll [l]: villa
        """
        return self.normalized in self.dialect.FOREIGN_DIGRAPH2IPA

    @cached_property
    def is_trigraph(self) -> bool:
        """
        True if grapheme is a trigraph (3-letter unit).

        Examples:
        - que, qui: q + u + vowel
        - coo: prefix boundary
        - ção: common suffix
        """
        return self.normalized in self.dialect.TRIGRAM2IPA

    @cached_property
    def is_consonant_hiatus(self) -> bool:
        """
        True if grapheme is a consonant cluster spanning syllable boundary.

        Examples:
        - ct: pac.to [ˈpak.tu]
        - cç: fic.ção [fik.ˈsɐ̃w]

        These are NOT pronounced as single units; they split across syllables.
        """
        return self.normalized in self.dialect.HETEROSYLLABIC_CLUSTERS

    # =========================================================================
    # PHONOLOGICAL & PHONETIC PROPERTIES
    # =========================================================================

    @cached_property
    def is_vowel_grapheme(self) -> bool:
        """
        True if grapheme consists only of vowel letters.

        IPA Relevance: Vowel graphemes form syllable nuclei and require
        different transcription rules than consonants.

        Returns:
            True if all characters are vowels
        """
        return all(c.is_vowel for c in self.characters)

    @cached_property
    def is_consonant_grapheme(self) -> bool:
        """
        True if grapheme consists only of consonant letters.

        IPA Relevance: Consonant graphemes include digraphs like 'ch', 'nh', 'lh'
        that map to single phonemes despite multiple letters.

        Returns:
            True if all characters are consonants
        """
        return all(c.is_consonant for c in self.characters)

    @cached_property
    def syllable_position(self) -> str:
        """
        Position within syllable: onset, nucleus, or coda.

        IPA Relevance: Phoneme realization varies by syllable position.
        E.g., /l/ → [w] in syllable coda in Brazilian Portuguese

        Returns:
            'onset', 'nucleus', or 'coda'
        """
        if self.is_vowel_grapheme or self.is_diphthong:
            return 'nucleus'

        # Check if before nucleus
        if self.parent_syllable:
            # Find first vowel in syllable
            for char in self.parent_syllable:
                if char in 'aeiouáéíóúâêôãõ':
                    if self.normalized == char or self.normalized[0] == char:
                        return 'nucleus'
                    # This grapheme comes before first vowel
                    if self.idx_in_word < self.parent_word.normalized.index(char):
                        return 'onset'
                    else:
                        return 'coda'

        return 'onset'  # Default

    @cached_property
    def phonological_weight(self) -> int:
        """
        Number of phonemes (mora count for syllable weight).

        IPA Relevance: Syllable weight affects stress patterns and rhythm.
        - Light syllable: 1 mora (CV)
        - Heavy syllable: 2+ morae (CVC, CVV)

        Returns:
            Estimated phoneme count
        """
        if not self.ipa:
            return 0

        # Diphthongs count as 2 morae
        if self.is_diphthong:
            return 2

        # Each IPA symbol roughly = 1 phoneme
        # Filter out diacritics and stress markers
        # 'ˈ' (primary stress), 'ˌ' (secondary stress), 'ː' (length)
        ipa_clean = self.ipa.replace('ˈ', '').replace('ˌ', '').replace('ː', '')
        # Combining diacritics (nasalization, etc.)
        ipa_clean = ipa_clean.replace('̃', '')

        return len(ipa_clean)

    @cached_property
    def has_complex_onset(self) -> bool:
        """
        True if grapheme is part of complex onset cluster.

        Complex onsets in Portuguese: pr, tr, br, gr, cr, etc.

        IPA Relevance: Complex onsets require precise timing and coordination
        of articulatory gestures.

        Returns:
            True if in consonant cluster before nucleus
        """
        if not self.is_consonant_grapheme:
            return False

        # Check if next grapheme is also consonant before nucleus
        if self.next_grapheme and self.next_grapheme.is_consonant_grapheme:
            if self.syllable_position == 'onset':
                return True

        # Check if previous grapheme is consonant in same syllable
        if self.prev_grapheme and self.prev_grapheme.is_consonant_grapheme:
            if self.prev_grapheme.syllable_idx == self.syllable_idx:
                if self.syllable_position == 'onset':
                    return True

        return False

    @cached_property
    def is_palatal(self) -> bool:
        """
        True if grapheme represents palatal consonant.

        Palatal consonants: nh [ɲ], lh [ʎ], (nhi, lhi)

        IPA Relevance: Palatals have distinctive tongue body position
        at hard palate, affecting adjacent vowels.

        Returns:
            True for palatal digraphs
        """
        s = self.normalized
        return s in ['nh', 'lh'] or (s in ['nhi', 'lhi'])

    @cached_property
    def triggers_palatalization(self) -> bool:
        """
        True if grapheme triggers palatalization of adjacent consonants.

        Front vowels (i, e) can palatalize preceding consonants.

        IPA Relevance: Palatalization changes consonant quality.
        E.g., 't' + 'i' → [tʃi] in some Brazilian dialects

        Returns:
            True if triggers palatalization
        """
        if not self.is_vowel_grapheme:
            return False

        # Front high vowels trigger palatalization
        return self.first_char.is_front_vowel and self.first_char.vowel_height == 'high'

    @cached_property
    def is_onset_cluster(self) -> bool:
        """
        True if grapheme is part of onset consonant cluster.

        IPA Relevance: Onset clusters follow specific phonotactic rules
        in Portuguese (only specific C1+C2 combinations allowed).

        Returns:
            True if in onset cluster
        """
        return self.syllable_position == 'onset' and self.has_complex_onset

    @cached_property
    def requires_liaison(self) -> bool:
        """
        True if grapheme may undergo liaison with following word.

        Liaison: linking final consonant to following initial vowel
        across word boundaries.

        IPA Relevance: Changes syllable structure and affects rhythm.
        E.g., "os amigos" → [u.zɐ.ˈmi.gus]

        Returns:
            True if word-final and potentially liaised
        """
        if not self.next_grapheme:  # Word-final
            if self.is_consonant_grapheme:
                # Check if next word starts with vowel
                parent = self.parent_word
                if parent and parent.next_word:
                    next_word_first = parent.next_word.graphemes[0] if parent.next_word.graphemes else None
                    if next_word_first and next_word_first.is_vowel_grapheme:
                        return True
        return False

    # =========================================================================
    # STRESS PROPERTIES
    # =========================================================================

    @cached_property
    def has_primary_stress(self) -> bool:
        """
        True if this grapheme carries primary word stress.

        Stress determination:
        1. Explicit: any character has primary stress marker (á, é, ã, etc.)
        2. Implicit: this grapheme's syllable is the stressed syllable

        For words with explicit accent marks, that syllable is stressed.
        For unmarked words, stress is predicted by word ending and syllable count.
        """
        if self.parent_word.n_syllables == 1:
            return True
        # Check if any character in this grapheme has explicit primary stress
        if any(c.normalized in self.dialect.PRIMARY_STRESS_MARKERS for c in self.characters):
            return True

        # Check if syllable-level stress applies to this grapheme's syllable
        if not self.parent_word:
            return False

        # Determine stressed syllable index
        stressed_syllable_idx = detect_stress_position(
            self.parent_word.normalized,
            self.parent_word.syllables,
            self.dialect
        )

        return self.syllable_idx == stressed_syllable_idx

    @cached_property
    def has_secondary_stress(self) -> bool:
        """
        True if this grapheme carries secondary stress.

        Secondary stress occurs in:
        - Compound words: semi-automático
        - Long words with complex morphology
        - Historical grave accent usage (obsolete)

        Marked by circumflex or grave accents in non-primary position.
        """
        if self.has_primary_stress:
            return False

        return any(
            c.normalized in self.dialect.SECONDARY_STRESS_MARKERS
            for c in self.characters
        )

    # =========================================================================
    # IPA GENERATION
    # =========================================================================

    @cached_property
    def ipa(self) -> str:
        """
        Generate IPA transcription for this grapheme.

        ALGORITHM:
        ----------
        1. Check irregular word list (highest priority)
        2. Check multi-character lookups (tetragraph → trigraph → digraph)
        3. Fall back to character-by-character IPA

        For multi-character graphemes (digraphs, diphthongs),
        the lookup returns a single IPA unit, not individual characters.

        Returns:
            IPA string for this grapheme
        """
        s = self.normalized
        word = self.parent_word.normalized if self.parent_word else ""

        # Special case: "ui" nasalized in "muito"
        if s == "ui" and word == "muito":
            return "ũj"

        # Check multi-character lookups (longest first)
        if s in self.dialect.TETRAGRAM2IPA:
            return self.dialect.TETRAGRAM2IPA[s]

        if s in self.dialect.TRIGRAM2IPA:
            return self.dialect.TRIGRAM2IPA[s]

        if s in self.dialect.NASAL_DIGRAPHS:
            return self.dialect.NASAL_DIGRAPHS[s]

        if s in self.dialect.DIPHTHONG2IPA:
            return self.dialect.DIPHTHONG2IPA[s]

        if s in self.dialect.DIGRAPH2IPA:
            return self.dialect.DIGRAPH2IPA[s]

        if s in self.dialect.HETEROSYLLABIC_CLUSTERS:
            return self.dialect.HETEROSYLLABIC_CLUSTERS[s]

        # Fall back to character-by-character
        return "".join(c.ipa for c in self.characters)

    # =========================================================================
    # FEATURE EXTRACTION
    # =========================================================================

    @cached_property
    def features(self) -> Dict[str, any]:
        """
        Extract all linguistic features as a dictionary.

        Returns:
            Dictionary with grapheme features and nested character features
        """
        feats = {
            # Basic properties
            "n_chars": self.n_chars,
            "text": self.normalized,
            "ipa": self.ipa,

            # Syllable context
            "parent_syllable": self.parent_syllable,
            "prev_syllable": self.prev_syllable,
            "next_syllable": self.next_syllable,
            "syllable_position": self.syllable_position,

            # Historical/orthographic
            "is_archaism": self.is_archaism,

            # Nasalization
            "is_nasal": self.is_nasal,

            # Multi-character units
            "is_digraph": self.is_digraph,
            "is_trigraph": self.is_trigraph,
            "is_foreign_digraph": self.is_foreign_digraph,
            "is_consonant_hiatus": self.is_consonant_hiatus,

            # Diphthongs
            "is_diphthong": self.is_diphthong,
            "is_triphthong": self.is_triphthong,
            "is_falling_diphthong": self.is_falling_diphthong,
            "is_rising_diphthong": self.is_rising_diphthong,
            "is_nasal_diphthong": self.is_nasal_diphthong,
            "is_oral_diphthong": self.is_oral_diphthong,
            "is_vocalic_hiatus": self.is_vocalic_hiatus,

            # Phonological class
            "is_vowel_grapheme": self.is_vowel_grapheme,
            "is_consonant_grapheme": self.is_consonant_grapheme,

            # Phonetic properties
            "phonological_weight": self.phonological_weight,
            "has_complex_onset": self.has_complex_onset,
            "is_palatal": self.is_palatal,
            "triggers_palatalization": self.triggers_palatalization,
            "is_onset_cluster": self.is_onset_cluster,
            "requires_liaison": self.requires_liaison,

            # Stress
            "has_primary_stress": self.has_primary_stress,
            "has_secondary_stress": self.has_secondary_stress,
        }

        # Add character-level features
        for c in self.characters:
            for k, v in c.features.items():
                feats[f"char_{c.char_idx}_{k}"] = v

        return feats

    def __eq__(self, other) -> bool:
        """Allow comparison with string."""
        if isinstance(other, str):
            return self.surface == other
        return super().__eq__(other)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"GraphemeToken('{self.surface}' → [{self.ipa}])"


# =============================================================================
# WORD TOKEN
# =============================================================================

@dataclasses.dataclass
class WordToken:
    """
    Represents a word with syllable structure and grapheme tokenization.

    LINGUISTIC STRUCTURE:
    ---------------------
    A word is analyzed at multiple levels:
    1. Orthographic: sequence of characters
    2. Graphemic: sequence of graphemes (digraphs, diphthongs, etc.)
    3. Syllabic: sequence of syllables
    4. Phonological: stress pattern and IPA transcription

    SYLLABIFICATION:
    ----------------
    Portuguese syllables follow a preferred CV (consonant-vowel) structure.
    The syllabifier handles:
    - Onset maximization: consonants go with following vowel
    - Complex onsets: pr, tr, br, etc.
    - Coda constraints: only l, r, s, n allowed in syllable-final position
    - Hiatus vs diphthong: vowel sequences may be one or two syllables

    STRESS ASSIGNMENT:
    ------------------
    Stress is determined by:
    1. Explicit accent marks (highest priority)
    2. Word-final pattern (oxytone exceptions)
    3. Default paroxytone rule (penultimate syllable)

    Attributes:
        surface: The word as it appears in text
        word_idx: Position in parent sentence
        graphemes: List of GraphemeToken objects
        syllables: List of syllable strings
        parent_sentence: Sentence containing this word
        dialect: DialectInventory with rules
    """
    surface: str
    word_idx: int  # parent_sentence.words[idx] == self
    graphemes: List[GraphemeToken] = dataclasses.field(default_factory=list)
    syllables: List[str] = dataclasses.field(default_factory=list)
    postag: Optional[str] = None
    parent_sentence: Optional["Sentence"] = None
    dialect: DialectInventory = dataclasses.field(default_factory=EuropeanPortuguese)

    def __post_init__(self):
        """
        Initialize syllables and graphemes with proper indexing.

        INITIALIZATION ORDER:
        ---------------------
        1. Syllabify word (using external syllabifier)
        2. Tokenize into graphemes with syllable alignment
        3. Create character tokens with computed indices

        This top-down approach avoids circular dependencies.
        """
        # Step 1: Syllabification
        if not self.syllables:
            self.syllables = syllabify(self.normalized)

        # Step 2: Grapheme tokenization with syllable alignment
        if not self.graphemes:
            self.graphemes = self._tokenize_graphemes()

        if not self.dialect and self.parent_sentence:
            self.dialect = self.parent_sentence.dialect

    def _tokenize_graphemes(self) -> List[GraphemeToken]:
        """
        Tokenize word into graphemes aligned with syllables.

        TOKENIZATION STRATEGY:
        ----------------------
        1. Normalize word and syllables
        2. For each syllable, scan for longest matching grapheme
        3. Greedy match: try tetragraphs → trigraphs → digraphs → chars
        4. Track which syllable each grapheme belongs to

        SYLLABLE ALIGNMENT:
        -------------------
        We need to know which grapheme belongs to which syllable
        for stress assignment and phonological rules.

        DOUBLED CONSONANT HANDLING:
        ---------------------------
        Portuguese syllabification splits doubled consonants:
        - bairro → bair.ro (not bai.rro)
        - muitíssimo → mui.tís.si.mo

        But these represent single phonemes. We normalize:
        - Move first letter to following syllable for phonological unity

        Returns:
            List of GraphemeToken objects with syllable indices
        """
        # Normalize syllables for consonant doubling
        normalized_syllables = self._normalize_syllables()

        graphemes = []
        # char_to_syllable = self._build_char_to_syllable_map(normalized_syllables)

        # Process each syllable
        for syl_idx, syllable in enumerate(normalized_syllables):
            syl_pos = 0

            while syl_pos < len(syllable):
                # Try longest match first (greedy)
                matched = False

                for grapheme in self.dialect.GRAPHEME_INVENTORY:
                    if syllable[syl_pos:].startswith(grapheme):
                        # Found match
                        graphemes.append(
                            GraphemeToken(
                                surface=syllable[syl_pos:syl_pos + len(grapheme)],
                                grapheme_idx=len(graphemes),
                                syllable_idx=syl_idx,
                                parent_word=self
                            )
                        )
                        syl_pos += len(grapheme)
                        matched = True
                        break

                if not matched:
                    # Single character fallback
                    graphemes.append(
                        GraphemeToken(
                            surface=syllable[syl_pos],
                            grapheme_idx=len(graphemes),
                            syllable_idx=syl_idx,
                            parent_word=self
                        )
                    )
                    syl_pos += 1

        return graphemes

    def _normalize_syllables(self) -> List[str]:
        """
        Normalize syllables for doubled consonant handling.

        Portuguese syllabification splits rr, ss, etc.:
        - carro → car.ro

        But phonologically, these are single consonants [ʁ], [s].
        We want them in the second syllable for correct IPA generation.

        Normalization: Move first letter of doubled consonant to next syllable.
        - car.ro → ca.rro (for processing)
        - baír.ris.mo → baí.rris.mo

        Returns:
            List of normalized syllable strings
        """
        norm_syllables = list(self.syllables)

        for idx in range(len(norm_syllables) - 1):
            current = norm_syllables[idx]
            next_syl = norm_syllables[idx + 1]

            # Check if syllable boundary splits doubled consonant
            for consonant in ["r", "s", "f", "l"]:
                if current.endswith(consonant) and next_syl.startswith(consonant):
                    # Move first consonant to next syllable
                    norm_syllables[idx] = current[:-1]
                    norm_syllables[idx + 1] = consonant + next_syl
                    break

        return norm_syllables

    @staticmethod
    def _build_char_to_syllable_map(syllables: List[str]) -> Dict[int, int]:
        """
        Map character index to syllable index.

        Needed for aligning graphemes with syllables during tokenization.

        Args:
            syllables: List of syllable strings

        Returns:
            Dictionary mapping character position to syllable index
        """
        char_to_syl = {}
        char_pos = 0

        for syl_idx, syl in enumerate(syllables):
            for _ in syl:
                char_to_syl[char_pos] = syl_idx
                char_pos += 1

        return char_to_syl

    # =========================================================================
    # BASIC PROPERTIES
    # =========================================================================
    @cached_property
    def normalized(self) -> str:
        """Lowercase, stripped form of word."""
        return self.surface.lower().strip()

    @cached_property
    def normalized_syllables(self) -> List[str]:
        """Syllables after consonant doubling normalization."""
        return self._normalize_syllables()

    @cached_property
    def n_syllables(self) -> int:
        """Number of syllables in word."""
        return len(self.syllables)

    @cached_property
    def is_archaic(self) -> bool:
        return self.normalized in self.dialect.ARCHAIC_WORDS

    # =========================================================================
    # LINKED PROPERTIES
    # =========================================================================
    @cached_property
    def idx_in_sentence(self) -> int:
        """Index of this character in parent sentence."""
        if not self.parent_sentence:
            return -1
        if self.word_idx == 0:
            return 0
        prev = self.previous_words
        whitespace_len = len(prev) - 1
        prev_len = sum(len(w.surface) for w in prev)
        return prev_len + whitespace_len

    @cached_property
    def all_chars(self) -> List[CharToken]:
        return [c for g in self.graphemes for c in g.characters]

    @cached_property
    def previous_words(self) -> List['WordToken']:
        return [w for w in self.parent_sentence.words if w.word_idx < self.word_idx]

    @cached_property
    def prev_word(self) -> Optional['WordToken']:
        """Previous word in sentence, or None if first."""
        if self.word_idx == 0 or not self.parent_sentence:
            return None
        return self.parent_sentence.words[self.word_idx - 1]

    @cached_property
    def next_word(self) -> Optional['WordToken']:
        """Next word in sentence, or None if last."""
        if self.word_idx == -1 or not self.parent_sentence:
            return None
        if self.word_idx >= len(self.parent_sentence.words) - 1:
            return None
        return self.parent_sentence.words[self.word_idx + 1]

    # =========================================================================
    # WORD-LEVEL PHONOLOGICAL PROPERTIES
    # =========================================================================

    @cached_property
    def stress_pattern(self) -> str:
        """
        Stress pattern classification: oxytone, paroxytone, or proparoxytone.

        IPA Relevance: Stress pattern determines which syllable receives prominence.
        Essential for correct IPA stress marking (ˈ placement).

        Categories:
        - Proparoxytone: stress on antepenult (3rd from end) - médico [ˈmɛdiku]
        - Paroxytone: stress on penult (2nd from end) - casa [ˈkazɐ]
        - Oxytone: stress on final - café [kɐˈfɛ]
        - Monosyllable: single syllable - pé [ˈpɛ]

        Returns:
            'monosyllable', 'oxytone', 'paroxytone', or 'proparoxytone'
        """
        n_syl = self.n_syllables
        stressed_idx = self.stressed_syllable_idx

        if n_syl == 1:
            return 'monosyllable'
        elif stressed_idx == n_syl - 1:
            return 'oxytone'
        elif stressed_idx == n_syl - 2:
            return 'paroxytone'
        elif stressed_idx == n_syl - 3:
            return 'proparoxytone'
        else:
            return 'irregular'  # Stress on 4th from end or earlier (very rare)

    @cached_property
    def has_diphthongs(self) -> bool:
        """
        True if word contains any diphthongs.

        IPA Relevance: Diphthongs are transcribed as two-vowel sequences
        within a single syllable nucleus.

        Returns:
            True if any grapheme is a diphthong
        """
        return any(g.is_diphthong for g in self.graphemes)

    @cached_property
    def has_nasal_sounds(self) -> bool:
        """
        True if word contains nasal vowels or nasal consonants.

        IPA Relevance: Nasalization (◌̃) is marked in IPA with combining diacritic
        or by using nasal vowel symbols.

        Returns:
            True if any grapheme is nasal
        """
        return any(g.is_nasal for g in self.graphemes)

    @cached_property
    def syllable_structure_pattern(self) -> str:
        """
        Syllable structure pattern using C (consonant) and V (vowel).

        IPA Relevance: Syllable structure determines phonotactic constraints
        and affects rhythm and prosody.

        Examples:
        - "ca.sa" → CV.CV
        - "trans.por.te" → CCVC.CVC.CV
        - "a.mi.go" → V.CV.CV

        Returns:
            Dot-separated syllable structure pattern
        """
        patterns = []
        for syl in self.syllables:
            pattern = ""
            for char in syl:
                if char in 'aeiouáéíóúâêôãõ':
                    pattern += "V"
                elif char.isalpha():
                    pattern += "C"
            patterns.append(pattern)
        return ".".join(patterns)

    @cached_property
    def is_homograph(self) -> bool:
        """
        True if word has multiple pronunciations based on POS.

        Homographs in Portuguese require POS tagging for disambiguation.

        IPA Relevance: Different POS → different stress/pronunciation
        Examples:
        - "gosto" (noun) [ˈgoʃtu] vs (verb) [ˈɡɔstu]

        Returns:
            True if in homograph dictionary
        """
        return self.normalized in self.dialect.HOMOGRAPHS

    @cached_property
    def phoneme_count(self) -> int:
        """
        Approximate number of phonemes in word.

        IPA Relevance: Phoneme count affects speech duration and complexity.

        Returns:
            Estimated phoneme count
        """
        # Sum phonological weight of all graphemes
        return sum(g.phonological_weight for g in self.graphemes)

    @cached_property
    def has_consonant_clusters(self) -> bool:
        """
        True if word contains consonant clusters.

        IPA Relevance: Consonant clusters require precise articulatory timing.

        Returns:
            True if any complex onsets or codas
        """
        return any(g.has_complex_onset for g in self.graphemes)

    @cached_property
    def has_palatal_sounds(self) -> bool:
        """
        True if word contains palatal consonants.

        Palatal sounds: nh [ɲ], lh [ʎ]

        IPA Relevance: Palatals are transcribed with special symbols.

        Returns:
            True if any palatal graphemes
        """
        return any(g.is_palatal for g in self.graphemes)

    @cached_property
    def vowel_sequence(self) -> str:
        """
        Sequence of vowels in word (for vowel harmony analysis).

        IPA Relevance: Vowel sequences show patterns of raising/lowering.

        Returns:
            Concatenated vowel characters
        """
        vowels = []
        for g in self.graphemes:
            if g.is_vowel_grapheme or g.is_diphthong:
                vowels.append(g.normalized)
        return ".".join(vowels)

    @cached_property
    def consonant_sequence(self) -> str:
        """
        Sequence of consonants in word.

        IPA Relevance: Shows phonotactic patterns and cluster types.

        Returns:
            Concatenated consonant graphemes
        """
        consonants = []
        for g in self.graphemes:
            if g.is_consonant_grapheme or g.is_digraph:
                consonants.append(g.normalized)
        return ".".join(consonants)

    @cached_property
    def is_irregular(self) -> bool:
        """
        True if word has irregular/exceptional pronunciation.

        IPA Relevance: Irregular words require dictionary lookup
        rather than rule-based transcription.

        Returns:
            True if in irregular words dictionary
        """
        return self.normalized in self.dialect.IRREGULAR_WORDS

    # =========================================================================
    # STRESS PROPERTIES
    # =========================================================================

    @cached_property
    def stressed_syllable_idx(self) -> int:
        """
        Index of syllable carrying primary stress.

        Uses detect_stress_position() helper function.
        """
        return detect_stress_position(
            self.normalized,
            self.syllables,
            self.dialect
        )

    # =========================================================================
    # IPA GENERATION
    # =========================================================================

    @cached_property
    def ipa(self) -> str:
        """
        Generate IPA transcription for entire word.

        ALGORITHM:
        ----------
        1. Check irregular word list (overrides all rules)
        2. Generate IPA for each grapheme
        3. Insert syllable boundaries (·)
        4. Insert stress marker (ˈ) before stressed syllable

        STRESS MARKING:
        ---------------
        IPA convention: ˈ precedes stressed syllable
        Example: português [puɾ.tu.ˈɡeʃ] → "ˈ" before "ɡeʃ"

        Returns:
            Full IPA transcription with stress and syllable marks
        """
        # Check irregular words first
        if self.postag and self.normalized in self.dialect.HOMOGRAPHS and self.postag in self.dialect.HOMOGRAPHS[self.normalized]:
            return self.dialect.HOMOGRAPHS[self.normalized][self.postag]
        if self.normalized in self.dialect.IRREGULAR_WORDS:
            return self.dialect.IRREGULAR_WORDS[self.normalized]

        # Generate grapheme IPAs grouped by syllable
        syllable_ipas = [[] for _ in self.syllables]

        for grapheme in self.graphemes:
            syl_idx = grapheme.syllable_idx
            if 0 <= syl_idx < len(syllable_ipas):
                grapheme_ipa = grapheme.ipa
                if grapheme_ipa:  # Skip empty (silent) graphemes
                    syllable_ipas[syl_idx].append(grapheme_ipa)

        # Join graphemes within syllables
        syllable_strings = ["".join(ipa_list) for ipa_list in syllable_ipas]

        # Insert stress marker before stressed syllable
        stressed_idx = self.stressed_syllable_idx
        if 0 <= stressed_idx < len(syllable_strings):
            syllable_strings[stressed_idx] = (
                    self.dialect.PRIMARY_STRESS_TOKEN + syllable_strings[stressed_idx]
            )

        # Join syllables with hiatus marker
        return self.dialect.HIATUS_TOKEN.join(syllable_strings)

    # =========================================================================
    # FEATURE EXTRACTION
    # =========================================================================

    @cached_property
    def features(self) -> Dict[str, any]:
        """
        Extract all linguistic features.

        Returns:
            Dictionary with word features and nested grapheme features
        """
        feats = {
            # Basic properties
            "surface": self.surface,
            "normalized": self.normalized,
            "ipa": self.ipa,
            "n_syllables": self.n_syllables,
            "idx_in_sentence": self.idx_in_sentence,

            # POS tagging
            "pos": self.postag,

            # Stress
            "stressed_syllable_idx": self.stressed_syllable_idx,
            "stress_pattern": self.stress_pattern,

            # Syllable structure
            "syllables": ".".join(self.syllables),
            "syllable_structure_pattern": self.syllable_structure_pattern,

            # Phonological content
            "has_diphthongs": self.has_diphthongs,
            "has_nasal_sounds": self.has_nasal_sounds,
            "has_consonant_clusters": self.has_consonant_clusters,
            "has_palatal_sounds": self.has_palatal_sounds,

            # Phoneme inventory
            "phoneme_count": self.phoneme_count,
            "vowel_sequence": self.vowel_sequence,
            "consonant_sequence": self.consonant_sequence,

            # Irregularity
            "is_irregular": self.is_irregular,
            "is_homograph": self.is_homograph,
            "is_archaic": self.is_archaic,
        }

        for grapheme in self.graphemes:
            for k, v in grapheme.features.items():
                feats[f"graph_{grapheme.grapheme_idx}_{k}"] = v

        return feats

    def __eq__(self, other) -> bool:
        """Allow comparison with string."""
        if isinstance(other, str):
            return self.surface == other
        return super().__eq__(other)

    def __repr__(self) -> str:
        """String representation for debugging."""
        syllables_str = ".".join(self.syllables)
        return f"WordToken('{self.surface}' [{syllables_str}] → [{self.ipa}])"


# =============================================================================
# SENTENCE
# =============================================================================

@dataclasses.dataclass
class Sentence:
    """
    Represents a sentence with full phonological analysis.

    SENTENCE-LEVEL PHONOLOGY:
    -------------------------
    While most phonological rules operate at word level,
    sentences introduce:
    1. Liaison: linking between words (resyllabification)
    2. Phrasal stress: prominence patterns across words
    3. Intonation: pitch contours for questions, statements, etc.

    CURRENT IMPLEMENTATION:
    -----------------------
    This version focuses on word-level analysis.
    Sentence-level prosody (liaison, phrasal stress, intonation)
    is simplified or not yet implemented.

    Future extensions could include:
    - Liaison rules (final consonant + initial vowel)
    - Phrasal stress patterns
    - Intonation contours (ToBI annotation)

    Attributes:
        surface: Raw sentence text
        words: List of WordToken objects
        dialect: DialectInventory with rules
    """
    surface: str
    words: List[WordToken] = dataclasses.field(default_factory=list)
    dialect: DialectInventory = dataclasses.field(default_factory=EuropeanPortuguese)

    @staticmethod
    def from_postagged(surface: str, tags: List[Tuple[str, str]],
                       dialect: Optional[DialectInventory] = None) -> "Sentence":
        words: List[WordToken] = []

        # Compute word positions in sentence
        char_position = 0
        for idx, (word_surface, pos) in enumerate(tags):
            # Find word in original sentence
            word_start = surface.find(word_surface, char_position)

            # Create word token
            word_token = WordToken(
                surface=word_surface,
                word_idx=idx,
                postag=pos,
                dialect=dialect
            )
            word_token._idx_in_sentence = word_start

            words.append(word_token)

            # Update position (word length + space)
            char_position = word_start + len(word_surface) + 1

        return Sentence(surface, words=words, dialect=dialect)

    def __post_init__(self):
        """
        Initialize word tokens with computed indices.

        TOKENIZATION:
        -------------
        Simple whitespace tokenization.
        Punctuation is kept attached to words for now.

        More sophisticated tokenization could handle:
        - Clitics: dar-lhe → dar + lhe
        - Contractions: do → de + o
        - Punctuation separation
        """
        if not self.words:
            # Tokenize on whitespace and hyphen
            word_surfaces = self.normalized.replace('-', ' ').split()

            # Compute word positions in sentence
            char_position = 0
            for idx, word_surface in enumerate(word_surfaces):
                word_start = self.normalized.find(word_surface, char_position)

                # Create word token
                word_token = WordToken(
                    surface=word_surface,
                    word_idx=idx,
                    parent_sentence=self,
                    dialect=self.dialect
                )
                word_token._idx_in_sentence = word_start

                self.words.append(word_token)

                # Update position (word length + space)
                char_position = word_start + len(word_surface) + 1

        else:
            # ensure parent sentence object is linked
            for w in self.words:
                w.parent_sentence = self
                w.dialect = w.dialect or self.dialect  # allow mixing dialects if manually constructed

    # =========================================================================
    # BASIC PROPERTIES
    # =========================================================================
    @cached_property
    def normalized(self) -> str:
        """Lowercase, stripped form of sentence."""
        # Remove leading/trailing punctuation and whitespace
        text = self.surface.lower().strip(string.punctuation + string.whitespace)
        return normalize_numbers(text)

    @cached_property
    def n_words(self) -> int:
        """Number of words in sentence."""
        return len(self.words)

    # =========================================================================
    # IPA GENERATION
    # =========================================================================

    @cached_property
    def ipa(self) -> str:
        """
        Generate IPA transcription for entire sentence.

        ALGORITHM:
        ----------
        1. Generate IPA for each word
        2. Join with word boundary markers (space)

        SIMPLIFICATION:
        ---------------
        This treats each word independently.
        A full implementation would handle:
        - Liaison across word boundaries
        - Resyllabification (e.g., "os amigos" → "o.za.mi.gos")
        - Phrasal stress patterns

        Returns:
            Space-separated IPA transcription
        """
        word_ipas = [word.ipa for word in self.words]
        return " ".join(word_ipas)

    # =========================================================================
    # FEATURE EXTRACTION
    # =========================================================================

    @cached_property
    def features(self) -> Dict[str, any]:
        """
        Extract all linguistic features.

        WARNING: Can produce very large feature dictionaries
        for long sentences. Consider alternative representations
        (e.g., arrays, DataFrames) for ML applications.

        Returns:
            Dictionary with sentence features and nested word features
        """
        feats = {
            "n_words": self.n_words,
            "n_whitespaces": self.n_words - 1,
        }

        for word in self.words:
            for k, v in word.features.items():
                feats[f"word_{word.word_idx}_{k}"] = v

        return feats

    def __eq__(self, other) -> bool:
        """Allow comparison with string."""
        if isinstance(other, str):
            return self.surface == other
        return super().__eq__(other)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Sentence('{self.surface}' → [{self.ipa}])"


# =============================================================================
# UTILITY FUNCTIONS FOR TESTING AND DEMONSTRATION
# =============================================================================

def demonstrate_transcription(text: str, dialect: DialectInventory = None):
    """
    Demonstrate IPA transcription with detailed linguistic analysis.

    This function provides a pedagogical view of the transcription process,
    showing intermediate steps and linguistic features.

    Args:
        text: Portuguese text to transcribe
        dialect: DialectInventory to use (default: European Portuguese)

    Example:
        >>> demonstrate_transcription("O cão comeu o pão.")
        Sentence: O cão comeu o pão.
        IPA: [u ˈkɐ̃w ko·ˈmew u ˈpɐ̃w]

        Words:
        1. o [u]
           Syllables: o
           Stress: syllable 0
        2. cão [ˈkɐ̃w]
           Syllables: cão
           Stress: syllable 0 (final -ão)
           Graphemes: c[k] ão[ɐ̃w]
           Nasal diphthong: ão
        ...
    """
    if dialect is None:
        dialect = EuropeanPortuguese()

    from tugaphone.pos import TugaTagger
    pos = TugaTagger(engine="brill")
    #sentence = Sentence.from_postagged(text, tags=pos.tag(text), dialect=dialect)
    sentence = Sentence(text, dialect=dialect)

    print(f"Sentence: {sentence.surface}")
    print(f"IPA: [{sentence.ipa}]")
    print()
    print("Words:")

    for word in sentence.words:
        print(f"{word.word_idx + 1}. {word.surface} [{word.ipa}]")
        print(f"   Postag: {word.postag}")
        print(f"   Syllables: {'.'.join(word.syllables)}")
        print(f"   Stress: syllable {word.stressed_syllable_idx}")

        # Show graphemes
        grapheme_strs = []
        for g in word.graphemes:
            label = f"{g.surface}[{g.ipa}]"
            if g.is_diphthong:
                label += "(diphthong)"
            if g.is_digraph:
                label += "(digraph)"
            grapheme_strs.append(label)

        print(f"   Graphemes: {' '.join(grapheme_strs)}")
        print()


# =============================================================================
# MAIN DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    """
    Demonstrate the transcription system with various Portuguese examples.

    These examples showcase:
    - Different stress patterns
    - Diphthongs and nasal vowels
    - Consonant digraphs
    - Challenging orthographic patterns
    """
    print("=" * 80)
    print("PORTUGUESE ORTHOGRAPHY → IPA TRANSCRIPTION SYSTEM")
    print("=" * 80)
    print()

    # Example sentences showcasing different phenomena
    examples = [
        # Basic sentence with nasal diphthongs
        "O cão comeu o pão.",

        # Stress patterns
        "O médico português está no café.",

        # Diphthongs and digraphs
        "A rainha viu o vinho.",

        # Complex consonants
        "O carro chegou rápido.",

        # X variants
        "O exemplo do táxi é exato.",

        # Nasal patterns
        "Um homem tem compaixão."
    ]

    european = EuropeanPortuguese()

    for example in examples:
        demonstrate_transcription(example, european)
        print("=" * 80)
        print()

    print("\nTranscription complete!")

    examples = [
        "O cão comeu o pão.",
        "Três tigres tristes.",
        "Brasil é bonito.",
        "A tia comeu muito.",
    ]

    dialects = [
        ("European", EuropeanPortuguese()),
        ("Brazilian", BrazilianPortuguese()),
        ("Angolan", AngolanPortuguese()),
        ("Mozambican", MozambicanPortuguese()),
        ("Timorese", TimoresePortuguese()),
    ]

    for example in examples:
        print(f"\nExample: {example}")
        print("-" * 80)
        for name, dialect in dialects:
            sent = Sentence(example, dialect=dialect)
            print(f"{name:15} [{dialect.dialect_code}]: {sent.ipa}")
        print()

    print("\nDetailed analysis: pt-BR")
    print("=" * 80)
    demonstrate_transcription("A tia comeu muito pão.", BrazilianPortuguese())
