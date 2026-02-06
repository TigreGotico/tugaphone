"""
Portuguese Orthography → IPA Transcription System

This module provides comprehensive conversion from Portuguese orthography to
International Phonetic Alphabet (IPA) notation, following prescriptive norms
for European Portuguese (pt-PT) and Brazilian Portuguese (pt-BR).

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

3. NASALIZATION: Vowels can be oral or nasal
   - Marked by tilde (ã, õ) or followed by nasal consonant (m, n)
   - Creates distinct phonemes, not just allophones

4. DIPHTHONGS: Sequences of vowel + semivowel or semivowel + vowel
   - Falling/descending: vowel → semivowel (rei [ˈʁej])
   - Rising/ascending: semivowel → vowel (piano [ˈpjɐnu])
   - Can be oral or nasal

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

QUICK REFERENCES:
===========
- https://en.wiktionary.org/wiki/Wiktionary:International_Phonetic_Alphabet
- https://en.wiktionary.org/wiki/Appendix:Portuguese_pronunciation
- https://en.wiktionary.org/wiki/Appendix:Portuguese_spellings
- https://european-portuguese.info/vowels
- https://pt.wikipedia.org/wiki/L%C3%ADngua_portuguesa
- https://pt.wikipedia.org/wiki/Fonologia_da_língua_portuguesa
- https://pt.wikipedia.org/wiki/Ortografia_da_l%C3%ADngua_portuguesa
- https://pt.wikipedia.org/wiki/Gram%C3%A1tica_da_l%C3%ADngua_portuguesa
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
from typing import List, Optional, Dict, Set

from tugaphone.syl import syllabify


# =============================================================================
# DIALECT INVENTORY: Phonological Rules and Mappings
# =============================================================================

@dataclasses.dataclass()
class DialectInventory:
    """
    Encapsulates all dialect-specific phonological rules and mappings.

    This class serves as a lookup table and rule repository for converting
    Portuguese orthography to IPA. Different Portuguese dialects (European,
    Brazilian, etc.) can define different inventories.

    DESIGN RATIONALE:
    -----------------
    Centralizing dialect rules in one class allows:
    - Easy comparison between dialects
    - Clean separation of data from logic
    - Simple addition of new dialects
    - Maintenance of linguistic rules in one location

    Attributes:
        dialect_code: IETF BCP 47 language tag (e.g., 'pt-PT', 'pt-BR')
    """

    dialect_code: str = "pt-PT"

    # =========================================================================
    # SYMBOLIC CONSTANTS
    # =========================================================================
    # These are used in IPA output to represent prosodic features

    HIATUS_TOKEN: str = "·"  # Syllable boundary marker
    PRIMARY_STRESS_TOKEN: str = "ˈ"  # IPA primary stress marker (before stressed syllable)
    SECONDARY_STRESS_TOKEN: str = "ˌ"  # IPA secondary stress marker

    # =========================================================================
    # PUNCTUATION MAPPING
    # =========================================================================
    # Maps orthographic punctuation to prosodic IPA markers
    # Rationale: Punctuation affects speech rhythm and pausing

    PUNCT2IPA: Dict[str, str] = dataclasses.field(default_factory=dict)

    # =========================================================================
    # CHARACTER SETS
    # =========================================================================
    # Organized by linguistic function for efficient categorization

    PUNCT_CHARS: Set[str] = dataclasses.field(default_factory=set)

    # Base vowels: a, e, i, o, u
    # Portuguese vowel system is asymmetric - more distinctions in stressed position
    VOWEL_CHARS: Set[str] = dataclasses.field(default_factory=set)

    # DIACRITICS ON VOWELS:
    # Portuguese uses diacritics to mark stress, vowel quality, and nasalization

    # Acute accent (´): Marks primary stress AND open vowel quality
    # Only valid on a, e, o (vowels with open/closed distinction)
    # Examples: café [kɐˈfɛ], está [ɨʃˈta], avó [ɐˈvɔ]
    ACUTE_VOWEL_CHARS: Set[str] = dataclasses.field(default_factory=set)

    # Grave accent (`): ARCHAIC - marked secondary stress (pre-1973 Portugal, pre-1971 Brazil)
    # Modern usage: only 'à' (contraction a + a = à)
    # Historical: sòmente, cafèzinho
    GRAVE_VOWEL_CHARS: Set[str] = dataclasses.field(default_factory=set)

    # Circumflex (^): Marks primary stress AND closed vowel quality
    # Only valid on a, e, o
    # Examples: você [voˈse], avô [ɐˈvo], âmbito [ˈɐ̃bitu]
    CIRCUM_VOWEL_CHARS: Set[str] = dataclasses.field(default_factory=set)

    # Tilde (~): Marks nasalization (air flow through nose)
    # Modern Portuguese: only ã, õ are valid
    # ẽ, ĩ, ũ: archaic or foreign words
    # Examples: mão [ˈmɐ̃w̃], põe [ˈpõj̃]
    TILDE_VOWEL_CHARS: Set[str] = dataclasses.field(default_factory=set)

    # Diaeresis/Trema (¨): ARCHAIC - marked pronounced 'u' in 'gu/qu' contexts
    # Abolished in 1945 (Portugal) and 2009 (Brazil)
    # Historical: lingüiça [lĩˈgwisɐ] vs linguiça [lĩˈgisɐ]
    # Modern German names: Müller, Göring
    TREMA_VOWEL_CHARS: Set[str] = dataclasses.field(default_factory=set)

    # Semivowels: Can function as vowel or consonant depending on position
    # In Portuguese: /j/ (written i, e) and /w/ (written u, o)
    # Examples: rei [ˈʁej] - 'i' is semivowel; rima [ˈʁimɐ] - 'i' is vowel
    SEMIVOWEL_CHARS: Set[str] = dataclasses.field(default_factory=set)

    # Foreign letters: Not in traditional Portuguese alphabet
    # k, w, y: used in loanwords, foreign names, scientific terms
    # Examples: kilo, whisky, yen
    FOREIGN_CHARS: Set[str] = dataclasses.field(default_factory=set)

    # Front vowels: Tongue positioned forward in mouth
    # Relevant for palatalization rules (c→s, g→ʒ before front vowels)
    FRONT_VOWEL_CHARS: Set[str] = dataclasses.field(default_factory=set)

    # STRESS MARKERS (for automatic stress detection)
    # Primary: acute accent and tilde (õ, ã are always stressed when final)
    PRIMARY_STRESS_MARKERS: Set[str] = dataclasses.field(default_factory=set)
    # Secondary: grave and circumflex
    SECONDARY_STRESS_MARKERS: Set[str] = dataclasses.field(default_factory=set)

    # =========================================================================
    # IPA VOWEL INVENTORY
    # =========================================================================
    # Portuguese has one of the richest vowel systems in Romance languages

    # ORAL VOWELS (air flows only through mouth):
    # High: i [i] (si), ɨ [ɨ] (pedir-unstressed), u [u] (tu)
    # Mid-closed: e [e] (você), o [o] (avô)
    # Mid-open: ɛ [ɛ] (pé), ɔ [ɔ] (pó)
    # Low: a [a] (lá-stressed), ɐ [ɐ] (casa-unstressed), ə [ə] (reduction)
    ORAL_VOWELS: Set[str] = dataclasses.field(default_factory=set)

    # NASAL VOWELS (air flows through nose AND mouth):
    # Nasalization is phonemic in Portuguese (changes meaning)
    # Examples: mato [ˈmatu] "bush" vs manto [ˈmɐ̃tu] "cloak"
    NASAL_VOWELS: Set[str] = dataclasses.field(default_factory=set)

    # VOWEL CATEGORIES BY OPENNESS (relevant for stress rules):
    # These categories determine whether acute (´) or circumflex (^) is used
    CLOSED_VOWELS: Set[str] = dataclasses.field(default_factory=set)  # High vowels
    SEMI_CLOSED_VOWELS: Set[str] = dataclasses.field(default_factory=set)  # Mid-closed
    OPEN_VOWELS: Set[str] = dataclasses.field(default_factory=set)  # Low
    SEMI_OPEN_VOWELS: Set[str] = dataclasses.field(default_factory=set)  # Mid-open

    ALL_VOWEL_CHARS: Set[str] = dataclasses.field(default_factory=set)

    # =========================================================================
    # DIPHTHONG INVENTORIES
    # =========================================================================
    # Diphthongs are single-syllable vowel sequences
    # Structure: V+G (vowel + glide/semivowel) or G+V

    # ORAL FALLING DIPHTHONGS (vowel → semivowel)
    # Format: IPA → orthographic representation
    # The /j/ glide is written 'i' or 'e', /w/ glide is written 'u' or 'o'
    RISING_ORAL_DIPHTHONGS: Dict[str, str] = dataclasses.field(default_factory=dict)

    # NASAL DIPHTHONGS
    # Nasalization extends across the entire diphthong
    # Examples: mãe [ˈmɐ̃j̃], cão [ˈkɐ̃w̃], põe [ˈpõj̃]
    FALLING_NASAL_DIPHTHONGS: Dict[str, str] = dataclasses.field(default_factory=dict)

    # BRAZILIAN PORTUGUESE SPECIAL DIPHTHONGS
    # In Brazilian dialects, coda /l/ vocalizes to [w]
    # This creates diphthongs not present in European Portuguese
    # Examples: Brasil [bɾaˈziw] vs [bɾɐˈziɫ] (European)
    PTBR_DIPHTHONGS: Dict[str, str] = dataclasses.field(default_factory=dict)

    # =========================================================================
    # NORMALIZATION MAPPINGS
    # =========================================================================
    # Maps archaic/invalid diacritics to modern standard equivalents
    # Rationale: Historical texts use obsolete orthography

    NORMALIZED_VOWELS: Dict[str, str] = dataclasses.field(default_factory=dict)

    # =========================================================================
    # GRAPHEME → IPA MAPPINGS
    # =========================================================================
    # Organized by complexity: multigraphs first, then digraphs, then single chars

    # TETRAGRAPHS (4-letter sequences with special pronunciation)
    TETRAGRAPH2IPA: Dict[str, str] = dataclasses.field(default_factory=dict)

    # TRIGRAPHS (3-letter sequences)
    TRIGRAPH2IPA: Dict[str, str] = dataclasses.field(default_factory=dict)

    # TRIPHTHONGS (vowel + semivowel + vowel in one syllable)
    # Rare in Portuguese: mostly in derived forms
    # Example: Paraguai [pɐɾɐˈgwaj]
    TRIPHTHONG2IPA: Dict[str, str] = dataclasses.field(default_factory=dict)

    # DIPHTHONGS (reverse mapping: orthography → IPA)
    DIPHTHONG2IPA: Dict[str, str] = dataclasses.field(default_factory=dict)

    # DIGRAPHS - CONSONANTAL
    # Two letters representing one consonant phoneme
    # nh [ɲ]: palatal nasal (like Spanish ñ, Italian gn)
    # lh [ʎ]: palatal lateral (like Italian gl)
    # ch [ʃ]: voiceless postalveolar fricative (like English sh)
    # rr [ʁ]: uvular trill (strong R)
    # ss [s]: voiceless between vowels (otherwise 's' → [z])
    DIGRAPH2IPA: Dict[str, str] = dataclasses.field(default_factory=dict)

    # DIGRAPHS - NASAL VOWELS
    # Vowel + nasal consonant (m/n) at syllable boundary → nasal vowel
    # The 'm/n' is not pronounced separately; it nasalizes the vowel
    # Examples: campo [ˈkɐ̃pu], antes [ˈɐ̃tɨʃ]
    NASAL_DIGRAPHS: Dict[str, str] = dataclasses.field(default_factory=dict)

    # CONSONANT HIATUS (intervocalic consonant clusters)
    # These clusters span syllable boundaries with preserved articulation
    # Examples: ficção [fik·ˈsɐ̃w̃], pacto [ˈpak·tu]
    HETEROSYLLABIC_CLUSTERS: Dict[str, str] = dataclasses.field(default_factory=dict)

    # ARCHAIC SILENT CONSONANTS
    # Pre-2009 orthography included etymological consonants
    # These were eliminated in Acordo Ortográfico
    # Example: assumpção → assunção
    ARCHAIC_MUTE_P: Dict[str, Set[str]] = dataclasses.field(default_factory=dict)

    # FOREIGN DIGRAPHS (in loanwords)
    FOREIGN_DIGRAPH2IPA: Dict[str, str] = dataclasses.field(default_factory=dict)

    # =========================================================================
    # HIATUS CONTEXTS
    # =========================================================================
    # Prefixes that force vowel separation (prevent diphthong formation)
    # Example: bi·aturar [bi.ɐtu.ˈɾaɾ] not *[bjɐ.tu.ˈɾaɾ]
    HIATUS_PREFIXES: Set[str] = dataclasses.field(default_factory=set)

    # =========================================================================
    # DEFAULT CHARACTER MAPPINGS
    # =========================================================================
    # Single character → IPA mapping (context-free baseline)
    # Many characters have context-sensitive variants applied later
    DEFAULT_CHAR2PHONEMES: Dict[str, str] = dataclasses.field(default_factory=dict)

    # =========================================================================
    # IRREGULAR WORD MAPPINGS
    # =========================================================================
    # Words with exceptional pronunciations that don't follow regular rules
    # These override all other rules
    IRREGULAR_WORDS: Dict[str, str] = dataclasses.field(default_factory=dict)

    # =========================================================================
    # STRESS RULES
    # =========================================================================
    # Portuguese stress is semi-predictable based on word endings

    # OXYTONE ENDINGS (stress on final syllable)
    # Words ending in these patterns are stressed on final syllable
    # Examples: café, funil, rapaz, caju
    OXYTONE_ENDINGS: Set[str] = dataclasses.field(default_factory=set)

    # =========================================================================
    # COMPILED GRAPHEME INVENTORY
    # =========================================================================
    # All valid multi-character graphemes for tokenization
    # Ordered by length (longest first) for greedy matching
    GRAPHEME_INVENTORY: List[str] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        """
        Initialize all mapping dictionaries with default values.

        This method populates the dialect-specific rules. It's called automatically
        after dataclass initialization. Subclasses can override individual mappings.

        DESIGN DECISION:
        ----------------
        Using __post_init__ allows:
        - Empty initialization for inheritance
        - Default values for base dialect
        - Override flexibility for subclasses
        """
        self._initialize_char_lists()
        self._initialize_normalized_vowels()
        self._initialize_punctuation()
        self._initialize_consonant_digraphs()
        self._initialize_nasal_digraphs()
        self._initialize_consonant_hiatus()
        self._initialize_archaic_forms()
        self._initialize_foreign_digraphs()
        self._initialize_hiatus_prefixes()
        self._initialize_diphthongs()
        self._initialize_triphthongs()
        self._initialize_trigraphs()
        self._initialize_tetragraphs()
        self._initialize_default_chars()
        self._initialize_stress_rules()
        self._compile_grapheme_inventory()

        # Até ao início do século XX, tanto em Portugal como no Brasil,
        # seguia-se uma ortografia que, por regra, baseava-se nos étimos latino ou grego para escrever cada palavra
        # TODO: mapping to modern word equivalent, normalize for IPA parsing
        self.ARCHAIC_WORDS = {
            "architectura",
            "caravella",
            "diccionario",
            "diphthongo",
            "estylo",
            "grammatica",
            "lyrio",
            "parochia",
            "kilometro",
            "orthographia",
            "pharmacia",
            "phleugma",
            "prompto",
            "psychologia",
            "psalmo",
            "rheumatismo",
            "sanccionar",
            "theatro"
        }

    def _initialize_char_lists(self):
        if not self.PUNCT_CHARS:
            self.PUNCT_CHARS = set(string.punctuation)
        if not self.VOWEL_CHARS:
            self.VOWEL_CHARS = set("aeiou")
        if not self.ACUTE_VOWEL_CHARS:
            self.ACUTE_VOWEL_CHARS = set("áéíóú")
        if not self.GRAVE_VOWEL_CHARS:
            self.GRAVE_VOWEL_CHARS = set("àèìòù")
        if not self.CIRCUM_VOWEL_CHARS:
            self.CIRCUM_VOWEL_CHARS = set("âêîôû")
        if not self.TILDE_VOWEL_CHARS:
            self.TILDE_VOWEL_CHARS = set("ãõẽĩũ")
        if not self.TREMA_VOWEL_CHARS:
            self.TREMA_VOWEL_CHARS = set("äëïöü")
        if not self.SEMIVOWEL_CHARS:
            self.SEMIVOWEL_CHARS = set("iueo")
        if not self.FOREIGN_CHARS:
            self.FOREIGN_CHARS = set("wkyÿ")
        if not self.FRONT_VOWEL_CHARS:
            self.FRONT_VOWEL_CHARS = set("eiéêí")
        if not self.PRIMARY_STRESS_MARKERS:
            self.PRIMARY_STRESS_MARKERS = self.ACUTE_VOWEL_CHARS | self.TILDE_VOWEL_CHARS
        if not self.SECONDARY_STRESS_MARKERS:
            self.SECONDARY_STRESS_MARKERS = self.GRAVE_VOWEL_CHARS | self.CIRCUM_VOWEL_CHARS | self.TREMA_VOWEL_CHARS

        if not self.ALL_VOWEL_CHARS:
            self.ALL_VOWEL_CHARS = self.VOWEL_CHARS | self.ACUTE_VOWEL_CHARS | self.GRAVE_VOWEL_CHARS | self.CIRCUM_VOWEL_CHARS | self.TREMA_VOWEL_CHARS

        # IPA vowel mappings
        if not self.ORAL_VOWELS:
            self.ORAL_VOWELS = set("ieɛɨɐəauoɔ")
        if not self.NASAL_VOWELS:
            self.NASAL_VOWELS = set("ĩẽɐ̃ũõ")
        if not self.CLOSED_VOWELS:
            self.CLOSED_VOWELS = set("iɨu")
        if not self.SEMI_CLOSED_VOWELS:
            self.SEMI_CLOSED_VOWELS = set("eo")
        if not self.OPEN_VOWELS:
            self.OPEN_VOWELS = set("a")
        if not self.SEMI_OPEN_VOWELS:
            self.SEMI_OPEN_VOWELS = set("ɛɐɔ")

    def _initialize_normalized_vowels(self):
        """
        Map archaic and foreign diacritics to modern Portuguese equivalents.

        LINGUISTIC BACKGROUND:
        ----------------------
        Portuguese orthography has evolved through several reforms:
        - 1911: Major reform in Portugal
        - 1943: Brazil's orthographic convention
        - 1945: Portugal aligns with Brazil
        - 1971/1973: Further simplifications
        - 1990/2009: Acordo Ortográfico (unified orthography)

        Obsolete marks must be normalized for consistent processing.
        """
        if not self.NORMALIZED_VOWELS:
            self.NORMALIZED_VOWELS = {
                # CIRCUMFLEX ON HIGH VOWELS (î, û)
                # Rule: High vowels /i, u/ have no open/closed distinction
                # Therefore circumflex is redundant → removed
                "î": "i",  # Historical: used for emphasis
                "û": "u",  # Historical: used for emphasis

                # TILDE ON MID VOWELS (ẽ, ĩ, ũ)
                # Rule: Nasalization of mid/high vowels is allophonic
                # Only /ɐ̃/ and /õ/ are phonemic
                # These appear in foreign words or archaic texts
                "ẽ": "ê",  # Maps to closed mid vowel
                "ĩ": "i",  # Maps to high vowel
                "ũ": "u",  # Maps to high vowel

                # GRAVE ACCENT (obsolete stress marker)
                # Pre-1973: marked secondary stress in suffixed words
                # Example: só + -mente → sòmente
                # Modern: stress is not marked in these contexts
                "è": "é",
                "ì": "í",
                "ò": "ó",
                "ù": "ú",

                # DIAERESIS/TREMA (obsolete hiatus marker)
                # Pre-1945/2009: ü indicated pronounced /w/ after g/q
                # Example: lingüiça [lĩˈgwisɐ] vs linguiça [lĩˈgisɐ]
                # Modern: context must be learned (etymology required)
                "ä": "á",
                "ë": "é",
                "ï": "í",
                "ö": "ó",
                "ü": "w",  # Special: indicates [w] realization
                "ÿ": "í"
            }

    def _initialize_punctuation(self):
        """
        Map orthographic punctuation to prosodic IPA representations.

        PROSODIC INTERPRETATION:
        ------------------------
        Punctuation affects speech prosody (rhythm, pausing, intonation).
        While full prosodic annotation requires ToBI or similar systems,
        we use simplified IPA conventions.

        Hiatus tokens (·) represent pause length:
        - Short pause: 1 token (comma, hyphen)
        - Medium pause: 2 tokens (semicolon)
        - Long pause: 3 tokens (period)

        Intonation markers (!, ?) require dedicated tone notation
        which is beyond standard IPA segmental transcription.
        """
        if not self.PUNCT2IPA:
            self.PUNCT2IPA = {
                "-": self.HIATUS_TOKEN,  # Hyphen: brief pause
                ",": self.HIATUS_TOKEN,  # Comma: brief pause
                ";": self.HIATUS_TOKEN * 2,  # Semicolon: medium pause
                ".": self.HIATUS_TOKEN * 3,  # Period: long pause
                "!": self.PRIMARY_STRESS_TOKEN + self.HIATUS_TOKEN,  # Exclamation: stress + pause
                "?": "↗" + self.HIATUS_TOKEN,  # Question: rising intonation + pause
            }

    def _initialize_consonant_digraphs(self):
        """
        Define two-letter sequences representing single consonant phonemes.

        PHONETIC BACKGROUND:
        --------------------
        Portuguese inherited Latin digraphs and developed new ones:

        - NH [ɲ]: Palatal nasal (tongue blade touches hard palate)
          Etymology: Latin -gn- > Portuguese -nh-
          Examples: vinho [ˈviɲu] < Latin vīnum

        - LH [ʎ]: Palatal lateral (lateral with palatal contact)
          Etymology: Latin -ll-, -cl-, -gl- > Portuguese -lh-
          Examples: filho [ˈfiʎu] < Latin fīlius

        - CH [ʃ]: Voiceless postalveolar fricative
          Etymology: Latin -cl-, -pl-, fl- > Portuguese -ch-
          Examples: chuva [ˈʃuvɐ] < Latin plŭvia

        - RR [ʁ]: Strong R (uvular/velar fricative or trill)
          Rule: 'rr' only occurs intervocalically
          Contrast: caro [ˈkaɾu] "expensive" vs carro [ˈkaʁu] "car"

        - SS [s]: Ensures voiceless [s] between vowels
          Rule: single 's' between vowels → [z]
          Contrast: casa [ˈkazɐ] "house" vs cassa [ˈkasɐ] (archaic "cancel")

        - PH [f]: Archaic Greek etymological spelling
          Modern: ph → f in orthographic reforms
          Examples: pharmacia → farmácia
        """
        if not self.DIGRAPH2IPA:
            self.DIGRAPH2IPA = {
                "nh": "ɲ",
                "lh": "ʎ",
                "ch": "ʃ",
                "rr": "ʀ",  # Alternative: ʁ for uvular fricative
                "ss": "s",

                # Abolidos na Reforma Ortográfica de 1911
                "th": "t",
                "rh": "r",
                "ph": "f"  # O dígrafo ph foi substituído pela letra f.
                           # No entanto, manteve-se a pronúncia do ph com som de f, sobretudo no caso de nomes próprios e marcas comerciais de uso corrente.
                           # Exemplo: iPhone, Philips e Phebo.
            }

    def _initialize_nasal_digraphs(self):
        """
        Define vowel + nasal consonant sequences that create nasal vowels.

        NASALIZATION RULES:
        -------------------
        In Portuguese, nasal vowels have two orthographic realizations:

        1. Tilde: ã, õ (direct nasal marking)
        2. Vowel + m/n: Nasalizes the vowel when m/n is in coda position

        CODA POSITION DEFINITION:
        --------------------------
        m/n is in coda (nasalizes vowel) when:
        - Word-final: tem [ˈtẽj̃], bom [ˈbõ]
        - Before consonant: campo [ˈkɐ̃pu], ponte [ˈpõtɨ]

        m/n is in onset (does NOT nasalize) when:
        - Before vowel: caminho [kɐˈmiɲu], bonito [buˈnitu]

        PHONETIC RESULT:
        ----------------
        The nasal consonant is not pronounced separately;
        it triggers nasal airflow throughout the vowel.

        ALLOPHONIC VARIATION:
        ---------------------
        Exact nasal vowel quality varies by context:
        - /am/, /an/ → [ɐ̃] in most contexts
        - /am/, /an/ → [ə̃] in European Portuguese final position

        We use phonemic representations, abstracting over fine detail.
        """
        if not self.NASAL_DIGRAPHS:
            self.NASAL_DIGRAPHS = {
                # Low vowel nasalization: /a/ + nasal
                "am": "ɐ̃",  # Example: campo [ˈkɐ̃pu]
                "âm": "ɐ̃",  # With circumflex (stress marker)
                "an": "ɐ̃",  # Example: santo [ˈsɐ̃tu]
                "ân": "ɐ̃",

                # Mid-high vowel nasalization: /e/ + nasal
                "em": "ẽ",  # Example: tempo [ˈtẽpu]
                "êm": "ẽ",
                "en": "ẽ",  # Example: dente [ˈdẽtɨ]
                "ên": "ẽ",

                # High front vowel nasalization: /i/ + nasal
                "im": "ĩ",  # Example: sim [ˈsĩ]
                "in": "ĩ",  # Example: tinta [ˈtĩtɐ]

                # Mid-back vowel nasalization: /o/ + nasal
                "om": "õ",  # Example: som [ˈsõ]
                "ôm": "õ",
                "on": "õ",  # Example: fonte [ˈfõtɨ]
                "ôn": "õ",

                # High back vowel nasalization: /u/ + nasal
                "um": "ũ",  # Example: um [ˈũ]
                "un": "ũ",  # Example: fundo [ˈfũdu]
            }

    def _initialize_consonant_hiatus(self):
        """
        Define consonant clusters that span syllable boundaries.

        SYLLABIFICATION PRINCIPLE:
        --------------------------
        Portuguese syllables prefer CV (consonant-vowel) structure.
        Certain consonant clusters cannot be parsed as single onsets,
        so they split across syllables with a hiatus (break).

        HETEROSYLLABIC CLUSTERS:
        ------------------------
        These clusters are always split:

        - cc, cç [k·s]: Represents /ks/ cluster
          Examples: ficção [fik·ˈsɐ̃w̃], acção [ak·ˈsɐ̃w̃]
          Note: Modern spelling often simplifies to ç: ação

        - ct [k·t]: Voiceless stops across syllable boundary
          Examples: pacto [ˈpak·tu], convicto [kõˈvik·tu]

        - pt [p·t]: Bilabial + alveolar across boundary
          Examples: apto [ˈap·tu], eucalipto [ew·kɐˈlip·tu]
          Note: In some archaic words, 'p' was silent

        - pç, pc [p·s]: Bilabial + fricative
          Examples: opção [op·ˈsɐ̃w̃], núpcias [ˈnup·sjɐʃ]

        SYLLABIFICATION ALGORITHM:
        --------------------------
        The syllabifier should recognize these as split clusters,
        not as single onsets. The hiatus token (·) marks the boundary.
        """
        if not self.HETEROSYLLABIC_CLUSTERS:
            self.HETEROSYLLABIC_CLUSTERS = {
                "cç": "k·s",  # convicção, ficção, friccionar,
                "cc": "k·s",  # friccionar, cóccix, facciosa, ficcionado, infecciologia, fraccionamento
                "ct": "k·t",  # compacto, convicto, pacto, pictural;
                "pt": "p·t",  # adepto, apto, díptico, inepto, rapto. eucalipto,
                "pç": "p·s",  # erupção, opção, recepção
                "pc": "p·s",  # núpcias
            }

    def _initialize_archaic_forms(self):
        """
        Define archaic silent consonant patterns.

        HISTORICAL ORTHOGRAPHY:
        -----------------------
        Pre-2009, Portuguese preserved etymological consonants from Latin
        even when not pronounced. The Acordo Ortográfico eliminated these.

        SILENT CONSONANT RULES:
        -----------------------
        When 'p' appeared in clusters mpc, mpç, mpt:
        - If 'p' was silent: m + p → n (in modern spelling)
        - If 'p' was pronounced: cluster retained

        Examples of elimination:
        - assumpcão → assunção [ɐsũˈsɐ̃w̃]
        - assumptível → assuntível
        - peremptório → perentório

        IMPLEMENTATION CHALLENGE:
        -------------------------
        Modern texts may still contain archaic spellings.
        We need word lists to distinguish:
        - Truly archaic: 'p' silent in both old and new spelling
        - Etymological retention: 'p' pronounced (Egito [ˈɛʒitu] retained)

        For now, we flag known archaic forms.
        Future: Integrate comprehensive etymological dictionary.
        """
        if not self.ARCHAIC_MUTE_P:
            self.ARCHAIC_MUTE_P = {
                "mpc": {"assumpcionista"},  # → assuncionista
                "mpç": {"assumpção"},  # → assunção
                "mpt": {
                    "assumptível",  # → assuntível
                    "peremptório",  # → perentório
                    "sumptuoso",  # → suntuoso
                    "sumptuosidade"  # → suntuosidade
                },
            }

    def _initialize_foreign_digraphs(self):
        """
        Define digraphs from loanwords and foreign names.

        ADAPTATION RULES:
        -----------------
        Portuguese adapts foreign orthography to native phonology:

        - ff [f]: Geminate f in Italian, French loanwords
          Realized as single [f] in Portuguese
          Examples: graffiti, buffet

        - ll [l]: Geminate l (not palatal ʎ)
          Realized as single [l]
          Examples: Llosa, villa

        - sh [ʃ]: English/Russian orthography
          Adapted to Portuguese [ʃ]
          Examples: show, shopping, Shostakovich

        - th [t] or [d]: English/Greek orthography
          Usually adapted to [t] (voiceless) or [d] (voiced)
          Examples: thriller [ˈtɾilɛɾ], Athens [ɐˈtenɐʃ]
          Note: Some speakers use [θ] (interdental), but non-standard

        PRONUNCIATION VARIATION:
        ------------------------
        Loanword pronunciation varies by:
        - Speaker's education/exposure
        - Degree of word integration
        - Formality of context

        We provide standard Portuguese adaptations.
        """
        if not self.FOREIGN_DIGRAPH2IPA:
            self.FOREIGN_DIGRAPH2IPA = {
                "ff": "f",  # Italian/French: graffiti
                "ll": "l",  # Spanish: paella (note: not palatal)
                "sh": "ʃ",  # English: show, shopping
                "th": "t",  # English: thriller (some use [d])
            }

    def _initialize_hiatus_prefixes(self):
        """
        Define prefixes that force vowel hiatus (block diphthong formation).

        HIATUS vs DIPHTHONG:
        --------------------
        When two vowels meet, they can form:
        1. Diphthong: Single syllable (e.g., pai [ˈpaj])
        2. Hiatus: Separate syllables (e.g., pa·ís [pɐˈiʃ])

        MORPHOLOGICAL HIATUS:
        ---------------------
        Prefix boundaries often block diphthongization:
        - bi- + auricular → bi·auricular [bi.aw.ɾi.ku.ˈlaɾ]
          NOT *[bjaw.ɾi.ku.ˈlaɾ]
        - semi- + automático → semi·automático
        - ante- + ontem → ante·ontem

        PHONOLOGICAL MOTIVATION:
        ------------------------
        Hiatus preservation maintains morphological transparency
        (clear prefix + root boundaries) and aids comprehension.

        IMPLEMENTATION:
        ---------------
        During grapheme tokenization, if a prefix is detected,
        insert a syllable boundary marker to prevent diphthong parsing.
        """
        if not self.HIATUS_PREFIXES:
            self.HIATUS_PREFIXES = {
                "ante",  # ante-histórico, ante-ontem
                "bi",  # bi-auricular, bi-anual
                "semi",  # semi-automático, semi-urbano
                "mini",  # mini-autocarro, mini-ópera
                "anti",  # anti-inflação, anti-oxidante
                "multi",  # multi-étnico, multi-uso
                "auto",  # auto-observação (when doubled)
                "contra",  # contra-ataque
                "extra",  # extra-oficial
                "hiper",  # hiper-ativo
                "inter",  # inter-urbano
                "intra",  # intra-ocular
                "neo",  # neo-ortodoxo
                "pré",  # pré-escolar
                "pró",  # pró-ativo
                "re",  # re-eleger (when doubled)
                "sub",  # sub-humano
                "super",  # super-homem
                "supra",  # supra-ocular
                "ultra",  # ultra-ortodoxo
            }

    # TODO - hiatus suffixes. eg. for suffix "inha" - Vinha -> V.inha

    def _initialize_diphthongs(self):
        """
        Define all Portuguese diphthongs (oral and nasal).

        DIPHTHONG STRUCTURE:
        --------------------
        A diphthong is a vocalic sequence pronounced in one syllable,
        consisting of a vowel (nucleus) and a semivowel (glide).

        Classification:
        1. By direction:
           - Falling/descending: V + G (rei, pau)
           - Rising/ascending: G + V (piano, água)

        2. By nasalization:
           - Oral: only oral airflow (rei)
           - Nasal: nasal + oral airflow (mãe, cão)

        FALLING ORAL DIPHTHONGS:
        ------------------------
        Ending in [j] (spelled i or e):
        - [aj]: pai, cai, vai
        - [ɐj]: unstressed variant (casa > casais)
        - [ɛj]: rei, papéis
        - [ej]: leite, sei
        - [ɔj]: herói, dói
        - [oj]: boi, foi
        - [uj]: fui, azuis

        Ending in [w] (spelled u or o):
        - [iw]: viu, partiu
        - [ew]: meu, seu
        - [ɛw]: céu, véu
        - [aw]: mau, pau
        - [ɐw]: unstressed (casa > casão)
        - [ow]: sou, ou

        FALLING NASAL DIPHTHONGS:
        -------------------------
        - [ɐ̃j̃]: mãe, cães (spelled ãe)
        - [ẽj̃]: bem, também (spelled em final)
        - [õj̃]: põe, õfões (spelled õe)
        - [ɐ̃w̃]: cão, mão (spelled ão)
        - [ũj̃]: muito, muitos (special case)

        BRAZILIAN PORTUGUESE L-VOCALIZATION:
        ------------------------------------
        In most Brazilian dialects, syllable-final /l/ → [w]:
        - mal [ˈmaw] (European: [ˈmaɫ])
        - sol [ˈsɔw] (European: [ˈsɔɫ])
        - Brasil [bɾaˈziw] (European: [bɾɐˈziɫ])

        This creates additional diphthongs not present in European Portuguese.
        """
        if not self.RISING_ORAL_DIPHTHONGS:
            self.RISING_ORAL_DIPHTHONGS = {
                # Falling diphthongs ending in [j]
                "aj": "ai",  # pai, cai (stressed)
                "ɐj": "ai",  # variant (unstressed)
                "ɛj": "éi",  # rei, papéis
                "ej": "ei",  # leite, sei
                "ɔj": "ói",  # herói, dói
                "oj": "oi",  # boi, foi
                "uj": "ui",  # fui, azuis

                # Falling diphthongs ending in [w]
                "iw": "iu",  # viu, partiu
                "ew": "eu",  # meu, seu
                "ɛw": "éu",  # céu, véu
                "aw": "au",  # mau, pau
                "ɐw": "ao",  # unstressed variant
                "ow": "ou",  # sou, ou
            }

        if not self.FALLING_NASAL_DIPHTHONGS:
            self.FALLING_NASAL_DIPHTHONGS = {
                "ɐ̃j": "ãe",  # mãe, cães, pães
                "ẽj": "em",  # bem, também (final position)
                "õj": "õe",  # põe, limões
                "ɐ̃w": "ão",  # cão, mão, pão
                "ũj": "ui",  # muito (special nasalized case)
            }

        if not self.PTBR_DIPHTHONGS:
            # Brazilian Portuguese L-vocalization diphthongs
            self.PTBR_DIPHTHONGS = {
                "aw": "al",  # mal [ˈmaw]
                "ɛw": "el",  # mel [ˈmɛw]
                "ew": "el",  # feltro [ˈfew.tɾu]
                "iw": "il",  # funil [fu.ˈniw]
                "ɔw": "ol",  # sol [ˈsɔw]
                "ow": "ol",  # soldado [sow.ˈda.du]
                "uw": "ul",  # azul [a.ˈzuw]
            }

        # Compile reverse mapping: orthography → IPA
        if not self.DIPHTHONG2IPA:
            self.DIPHTHONG2IPA = {
                **{v: k for k, v in self.RISING_ORAL_DIPHTHONGS.items()},
                **{v: k for k, v in self.FALLING_NASAL_DIPHTHONGS.items()},
            }

    def _initialize_triphthongs(self):
        """
        Define Portuguese triphthongs (rare, mostly in foreign words).

        TRIPHTHONG DEFINITION:
        ----------------------
        A sequence of three vowel-like sounds in one syllable:
        semivowel + vowel + semivowel (G-V-G)

        Examples:
        - Uruguai [u.ɾu.ˈgwaj]: G[w] + V[a] + G[j]
        - Paraguai [pɐ.ɾɐ.ˈgwaj]
        - miau [ˈmjaw]: G[j] + V[a] + G[w]

        PHONETIC REALITY:
        -----------------
        True triphthongs are rare cross-linguistically.
        Many apparent triphthongs are:
        - Diphthong + separate vowel across syllable boundary
        - Regional variants that simplify to diphthongs

        In European Portuguese, many potential triphthongs reduce:
        - iei → [jej] or [jɐj] depending on dialect
          Examples: fieira, macieira

        ORTHOGRAPHIC AMBIGUITY:
        -----------------------
        Portuguese orthography doesn't distinguish triphthongs clearly.
        Syllabification and stress determine the parse:
        - ca.iu [kɐ.ˈju]: hiatus (two syllables)
        - miau [ˈmjaw]: triphthong (one syllable)

        We include common patterns and flag for special handling.
        """
        if not self.TRIPHTHONG2IPA:
            self.TRIPHTHONG2IPA = {
                # [j-e-j] sequence
                "iei": "jej",  # chieira, macieira, pardieiro
                # Alternative Lisbon realization:
                # "iei": "jɐj",  # with vowel reduction

                # [j-a-w] sequence
                "iau": "jaw",  # miau

                # [w-a-j] sequence
                "uai": "waj",  # rare: Uruguai, Paraguai

                # [w-ɐ̃-j] nasal sequence
                "uão": "wɐ̃w",  # rare: saguão
            }

    def _initialize_trigraphs(self):
        """
        Define three-letter graphemes with special pronunciations.

        TYPES OF TRIGRAPHS:
        -------------------
        1. QU/GU before E/I with explicit vowel
        2. Vowel sequences in hiatus or special contexts
        3. Foreign word patterns

        QUE/QUI/GUE/GUI AMBIGUITY:
        --------------------------
        These sequences are ambiguous in modern Portuguese:
        - 'u' can be silent: quero [ˈkeɾu], guerra [ˈɡɛʁɐ]
        - 'u' can be pronounced: equino [eˈkwinu], ambíguo [ɐ̃ˈbiɡwu]

        Historical solution: Trema (ü) marked pronounced u
        - lingüiça [lĩˈgwisɐ]: u pronounced
        - linguiça [lĩˈgisɐ]: u silent

        Modern challenge: No marking, must learn from context/etymology

        DOUBLE-O SEQUENCES:
        -------------------
        When prefix/root boundary creates -oo-, typically pronounced as:
        - Separate syllables: co.operação [ko.o.pɛ.ɾɐ.ˈsɐ̃w̃]
        - But may reduce in rapid speech

        Special cases:
        - voo [ˈvo.u] or [ˈvow]: "flight" (noun from voar)
        - zoo [ˈzɔ.u] or [ˈzow]: "zoo"

        We mark these for context-sensitive handling.
        """
        if not self.TRIGRAPH2IPA:
            self.TRIGRAPH2IPA = {
                "tch": "tʃ", # the only true trigraph in portuguese

                # QU/GU patterns (context-dependent, flagged for special handling)
                "que": "kɨ",  # quero (default: u silent)
                "qui": "ki",  # quia
                "gue": "ɡɨ",  # guerra
                "gui": "ɡi",  # guia
                "qué": "kɛ",  # with explicit stress
                "gué": "ɡɛ",
                "quê": "ke",
                "guê": "ɡe",

                # Double-O patterns (prefix boundaries)
                "coo": "ku.u",  # cooperar, coordenar
                "joo": "ʒo.u",  # enjoo
                "noo": "nu.u",  # noológico
                "zoo": "zu.u",  # zoologia, zoo
                "voo": "vo.u",  # voo, revoo

                # Foreign patterns
                "boo": "bu.u",  # booleano
                "too": "tu.u",  # cartoonista
                "woo": "wu.u",  # Hollywood
                "hoo": "u.u",  # hooliganismo

                # Nasal patterns
                "ção": "sɐ̃w̃",  # -ção suffix (very common)
                "ões": "õj̃ʃ",  # plural -ões
            }

    def _initialize_tetragraphs(self):
        """
        Define four-letter graphemes (very rare).

        TETRAGRAPH CONTEXTS:
        --------------------
        Four-letter sequences with special pronunciation arise from:
        1. Suffix attachment: -ense, -iano
        2. Compound formation
        3. Loanwords

        Most are analyzable as diphthong + digraph or similar,
        but we list them explicitly for pattern recognition.

        GENTILICS (DEMONYMS):
        ---------------------
        -iense suffix (indicating origin) creates potential tetragraphs:
        - gaiense: from Gaia [ɡɐj.ˈẽ.sɨ] or [ɡɐ.jẽ.sɨ]
        - praiense: from Praia
        - xangaiense: from Shanghai

        Syllabification is variable and dialect-dependent.
        """
        if not self.TETRAGRAPH2IPA:
            self.TETRAGRAPH2IPA = {
                "aien": "ɐj.ẽ",  # gaiense, praiense, xangaiense

                # Foreign words / proper nouns
                "guai": "gwaj",  # Uruguai, Paraguai
                "quai": "kwaj",

                # hiatus
                "iaiá": "i.ɐ.ˈja",  # iaiá (Brazilian: nanny, lady)
            }

    def _initialize_default_chars(self):
        """
        Define baseline character-to-phoneme mappings.

        DESIGN PRINCIPLE:
        -----------------
        These are CONTEXT-FREE default mappings.
        Many characters have context-sensitive realizations
        that override these defaults. Context rules are applied
        during IPA generation in the CharToken class.

        VOWELS:
        -------
        Portuguese has 9 oral vowel phonemes in stressed position:
        /i, e, ɛ, a, ɐ, ɔ, o, u/ (plus nasal vowels)

        Unstressed vowels reduce to smaller inventory:
        /i, ɨ, u, ɐ/ (European Portuguese)
        /i, u, a/ (Brazilian Portuguese - less reduction)

        Default mapping uses neutral/unstressed values where ambiguous.

        CONSONANTS:
        -----------
        Most consonants have straightforward mappings.
        Exceptions (context-sensitive):
        - c: [k] default, but [s] before e/i
        - g: [ɡ] default, but [ʒ] before e/i
        - r: [ɾ] default (tap), but [ʁ]/[ʀ] word-initially or after n/l/s
        - s: [s] default, but [z] intervocalically
        - x: [ʃ] default, but can be [ks], [z], [s], [gz] contextually
        - z: [z] default, but [ʃ]/[s] word-finally

        SILENT LETTERS:
        ---------------
        - h: Always silent except in digraphs (ch, nh, lh)
        - u: Silent in que/qui, gue/gui contexts (modern orthography)
        """
        if not self.DEFAULT_CHAR2PHONEMES:
            self.DEFAULT_CHAR2PHONEMES = {
                # VOWELS
                # Low vowel: stressed [a], unstressed [ɐ]
                "a": "ɐ",  # Default: reduced (unstressed) value
                "á": "a",  # Acute: stressed open value
                "à": "a",  # Grave: (rare) stressed
                "â": "ɐ",  # Circumflex: stressed closed value (often [ɐ])
                "ã": "ɐ̃",  # Nasal low vowel

                # Mid-front vowel: stressed [e] or [ɛ], unstressed [ɨ]
                "e": "ɨ",  # Default: reduced (European Portuguese)
                "é": "ɛ",  # Acute: stressed open value
                "ê": "e",  # Circumflex: stressed closed value

                # High-front vowel: always [i]
                "i": "i",
                "í": "i",  # Stress marker only (no quality change)

                # Mid-back vowel: stressed [o] or [ɔ], unstressed [u]
                "o": "u",  # Default: reduced (European Portuguese)
                "ó": "ɔ",  # Acute: stressed open value
                "ô": "o",  # Circumflex: stressed closed value
                "õ": "õ",  # Nasal mid-back vowel

                # High-back vowel: always [u]
                "u": "u",
                "ú": "u",  # Stress marker only

                # CONSONANTS
                # Stops
                "p": "p",  # Voiceless bilabial stop
                "b": "b",  # Voiced bilabial stop
                "t": "t",  # Voiceless alveolar stop
                "d": "d",  # Voiced alveolar stop
                "k": "k",  # Voiceless velar stop (foreign)
                "c": "k",  # Default: voiceless velar stop
                "q": "k",  # Always voiceless velar (+ u)
                "g": "ɡ",  # Default: voiced velar stop

                # Fricatives
                "f": "f",  # Voiceless labiodental fricative
                "v": "v",  # Voiced labiodental fricative
                "s": "s",  # Default: voiceless alveolar fricative
                "z": "z",  # Voiced alveolar fricative
                "ç": "s",  # Voiceless alveolar fricative (c-cedilla)
                "j": "ʒ",  # Voiced postalveolar fricative
                "x": "ʃ",  # Default: voiceless postalveolar fricative

                # Nasals
                "m": "m",  # Bilabial nasal
                "n": "n",  # Alveolar nasal

                # Liquids
                "l": "l",  # Alveolar lateral
                "r": "ɾ",  # Default: alveolar tap

                # Semivowels (in consonantal position)
                "w": "w",  # Labiovelar approximant (foreign)
                "y": "j",  # Palatal approximant (foreign, rare)

                # Silent
                "h": "",  # Always silent in Portuguese
            }

    def _initialize_stress_rules(self):
        """
        Define patterns that predict stress placement.

        PORTUGUESE STRESS SYSTEM:
        -------------------------
        Portuguese stress is SEMI-PREDICTABLE based on word shape:

        DEFAULT RULE (Paroxytone):
        - Stress falls on penultimate (second-to-last) syllable
        - Applies to ~80% of words
        - Examples: casa, livro, falam

        OXYTONE EXCEPTIONS (final syllable stress):
        - Words ending in: -r, -l, -z, -im, -um, nasal vowels
        - Examples: falar, azul, rapaz, jardim, atum, maçã
        - Loanwords often follow this pattern: hotel, bar

        PROPAROXYTONE (antepenultimate stress):
        - ALWAYS marked with written accent
        - Less common (~5% of words)
        - Examples: médico, lâmpada, ótimo
        - Mostly erudite words, Latin borrowings

        MONOSYLLABLES:
        - Inherently stressed (no choice of syllable)
        - May have accent for semantic distinction:
          - pé [ˈpɛ] "foot" vs pê [ˈpe] "letter P"

        WRITTEN ACCENT RULES:
        ---------------------
        Accents are written to mark:
        1. Unexpected stress position (proparoxytones)
        2. Vowel quality (é [ɛ] vs ê [e])
        3. Disambiguation (pára "stops" vs para "for")

        NOTE: The 1990/2009 Acordo Ortográfico changed some rules,
        eliminating some accents (e.g., trema) and disambiguators.
        """
        if not self.OXYTONE_ENDINGS:
            self.OXYTONE_ENDINGS = {
                # Consonant endings that trigger final stress
                "r",  # falar, comer, partir
                "l",  # azul, papel, farol
                "z",  # rapaz, feliz, capaz
                "x",  # fax, latex (loanwords)

                # Nasal endings (final nasal vowels are stressed)
                "m",  # jardim, atum, homem
                "n",  # hífen (rare, mostly foreign)
                "ão",  # cão, mão (diphthong)
                "ãe",  # mãe, cães
                "õe",  # põe, limões

                # Diphthong endings
                "éi",  # papéis, hotéis
                "éu",  # troféu, céu
                "ói",  # herói, anzóis
                "au",  # grau, pau
                "áu",  #

                # Explicit stress markers (always stressed)
                "á", "é", "í", "ó", "ú",
                "â", "ê", "ô",
                "ã", "õ",
            }

    def _compile_grapheme_inventory(self):
        """
        Compile sorted list of all multi-character graphemes.

        PURPOSE:
        --------
        During tokenization, we need to recognize multi-character units
        (digraphs, diphthongs, etc.) before processing individual characters.

        GREEDY MATCHING PRINCIPLE:
        --------------------------
        Longer sequences must be checked first to avoid incorrect parses:
        - Incorrect: "ch" → ['c', 'h'] → [k, (silent)]
        - Correct: "ch" → ['ch'] → [ʃ]

        SORTING:
        --------
        We sort by length (descending) to ensure longest match wins.
        Within same length, alphabetical order for deterministic behavior.

        INVENTORY SOURCES:
        ------------------
        - Tetragraphs (4 chars)
        - Trigraphs (3 chars)
        - Triphthongs (3 chars)
        - Digraphs: consonant, nasal, foreign
        - Diphthongs (2 chars)
        - Consonant hiatus patterns
        - Hiatus prefixes
        - Archaic forms

        Single characters are NOT included (handled separately).
        """
        if not self.GRAPHEME_INVENTORY:
            # Collect all multi-character graphemes
            all_graphemes = set()

            # add vowel inventory
            all_graphemes.update(self.ALL_VOWEL_CHARS)

            # Add from all mapping dictionaries
            all_graphemes.update(self.TETRAGRAPH2IPA.keys())
            all_graphemes.update(self.TRIGRAPH2IPA.keys())
            all_graphemes.update(self.TRIPHTHONG2IPA.keys())
            all_graphemes.update(self.DIGRAPH2IPA.keys())
            all_graphemes.update(self.DIPHTHONG2IPA.keys())
            all_graphemes.update(self.FOREIGN_DIGRAPH2IPA.keys())
            all_graphemes.update(self.HETEROSYLLABIC_CLUSTERS.keys())
            all_graphemes.update(self.NASAL_DIGRAPHS.keys())

            # Add prefixes and archaic forms
            all_graphemes.update(self.HIATUS_PREFIXES)
            all_graphemes.update(self.ARCHAIC_MUTE_P.keys())

            # Add single characters for completeness
            all_graphemes.update(string.ascii_lowercase)
            all_graphemes.update(string.punctuation)

            # Sort: longest first (for greedy matching), then alphabetical
            self.GRAPHEME_INVENTORY = sorted(
                all_graphemes,
                key=lambda x: (-len(x), x)
            )


# =============================================================================
# DIALECT INSTANCES
# =============================================================================

class EuropeanPortuguese(DialectInventory):
    """
    European Portuguese (Portugal) phonological inventory.

    CHARACTERISTIC FEATURES:
    ------------------------
    1. Vowel reduction: Unstressed vowels reduce to [ɨ], [ɐ], [u]
       - casa [ˈkazɐ]: first 'a' → [ɐ]
       - pedir [pɨˈdiɾ]: first 'e' → [ɨ]

    2. Fricative coda: Final /s/ and /z/ → [ʃ] and [ʒ]
       - três [ˈtɾeʃ]
       - luz [ˈluʃ]

    3. Dark L: Coda /l/ realized as velarized [ɫ] or vocalized [w]
       - Brasil [bɾɐˈziɫ]

    4. Uvular R: /ʁ/ (uvular fricative) common in Lisbon
       - rato [ˈʁatu]

    Regional variation exists (Porto vs Lisbon vs Algarve),
    but we implement a standard/Lisbon-based system.
    """

    def __init__(self):
        super().__init__(dialect_code="pt-PT")
        # European-specific irregular words
        self.IRREGULAR_WORDS = {
            # "ui" nasalized in "muito"
            "muito": "ˈmũj.tu",
            # Single-syllable special cases
            "miau": "ˈmjaw",
        }


class EuropeanPortugueseLisbon(EuropeanPortuguese):
    """
    Lisbon dialect of European Portuguese.

    DISTINGUISHING FEATURES:
    ------------------------
    1. Diphthong reduction: [ej] → [ɐj] in unstressed position
       - caseira [kɐˈzɐjɾɐ] (Lisbon) vs [kɐˈzejɾɐ] (general)

    2. /ɛ/ raising: Sometimes [ɛ] → [ɐ] in unstressed syllables

    3. Vowel centralization: More extreme reduction than other regions

    This is a placeholder for future Lisbon-specific rules.
    """

    def __init__(self):
        super().__init__()
        self.dialect_code = "pt-PT-x-lisbon"


class BrazilianPortuguese(DialectInventory):
    """
    Brazilian Portuguese phonological inventory.

    MAJOR DIFFERENCES FROM EUROPEAN:
    --------------------------------
    1. Less vowel reduction: Unstressed vowels keep fuller quality
       - casa [ˈkazɐ] (European) vs [ˈkaza] (Brazilian)
       - pedir [pɨˈdiɾ] (European) vs [peˈdʒiɾ] (Brazilian)

    2. Palatalization: /t, d/ → [tʃ, dʒ] before [i]
       - tia [ˈtʃiɐ] (Brazilian) vs [ˈtiɐ] (European)
       - dia [ˈdʒiɐ] (Brazilian) vs [ˈdiɐ] (European)

    3. L-vocalization: Coda /l/ → [w] (creates new diphthongs)
       - Brasil [bɾaˈziw]
       - mal [ˈmaw]
       - sol [ˈsɔw]

    4. Different R: [h], [x], or [ʁ] depending on region
       - Rio: carro [ˈkaху]
       - São Paulo: carro [ˈkaʁu]
       - Rural: carro [ˈkaʀu] (trill preserved)

    5. Final /s/: Stays [s], doesn't palatalize to [ʃ]
       - três [ˈtɾes] (Brazilian) vs [ˈtɾeʃ] (European)

    6. Nasal vowels: Less nasalization than European

    Regional variation is EXTENSIVE (Northeast vs Southeast vs South).
    We implement a relatively neutral/São Paulo-based system.
    """

    def __init__(self):
        super().__init__(dialect_code="pt-BR")

        # Brazilian-specific features
        # TODO: Implement palatalization rules (t/d before i)
        # TODO: Implement L-vocalization (activate PTBR_DIPHTHONGS)
        # TODO: Implement different vowel reduction patterns


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
        dialect: DialectInventory with phonological rules
    """

    surface: str
    char_idx: int = 0  # parent_grapheme.characters[idx] == self
    parent_grapheme: Optional["GraphemeToken"] = None
    dialect: DialectInventory = dataclasses.field(default_factory=EuropeanPortuguese)

    # Precomputed indices (set during initialization)
    _idx_in_word: int = -1
    _idx_in_sentence: int = -1

    def __post_init__(self):
        """
        Validate and precompute indices.

        Indices are computed top-down during sentence initialization
        to avoid circular dependency issues.
        """
        # Validation
        if len(self.surface) != 1:
            raise ValueError(f"CharToken must contain exactly one character, got: {self.surface}")

        self._idx_in_word = self.parent_grapheme.idx_in_word + self.char_idx
        self._idx_in_sentence = self.parent_grapheme.idx_in_sentence + self.char_idx

    # =========================================================================
    # BASIC PROPERTIES
    # =========================================================================

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

    @property
    def idx_in_word(self) -> int:
        """Index of this character in parent word."""
        return self._idx_in_word

    @property
    def idx_in_sentence(self) -> int:
        """Index of this character in parent sentence."""
        return self._idx_in_sentence

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
        """Previous character in the grapheme, or None if first."""
        if not self.parent_grapheme:
            return None
        if self.char_idx == 0:
            # TODO: go to prev grapheme
            return None
        return self.parent_grapheme.characters[self.char_idx - 1]

    @cached_property
    def next_char(self) -> Optional['CharToken']:
        """Next character in the grapheme, or None if last."""
        if self.char_idx == -1 or not self.parent_grapheme:
            return None
        if self.char_idx >= len(self.parent_grapheme.characters) - 1:
            # TODO: go to next grapheme
            return None
        return self.parent_grapheme.characters[self.char_idx + 1]

    # -------------------------------
    # Look-behind/ahead
    # -------------------------------
    @property
    def prefix(self) -> str:
        return self.parent_grapheme.prefix + "".join([c.normalized for c in self._prev_chars])

    @property
    def suffix(self) -> str:
        return "".join([c.normalized for c in self._next_chars]) + self.parent_grapheme.suffix

    @cached_property
    def _prev_chars(self) -> List['CharToken']:
        if self.char_idx == 0:
            return []
        return [w for w in self.parent_grapheme.characters if w.char_idx < self.char_idx]

    @cached_property
    def _next_chars(self) -> List['CharToken']:
        return [w for w in self.parent_grapheme.characters if w.char_idx > self.char_idx]

    # =========================================================================
    # CHARACTER CLASSIFICATION
    # =========================================================================

    @cached_property
    def is_punct(self) -> bool:
        """True if character is punctuation."""
        return self.surface in self.dialect.PUNCT_CHARS

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
        return self.normalized in self.dialect.SEMIVOWEL_CHARS

    @cached_property
    def is_consonant(self) -> bool:
        """True if character represents a consonant."""
        return not self.is_vowel and not self.is_punct

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
    def is_foreign(self) -> bool:
        """
        True if character is not in traditional Portuguese alphabet.

        Foreign letters: k, w, y
        Used in: loanwords, foreign names, scientific terms
        """
        return self.normalized in self.dialect.FOREIGN_CHARS

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

        # Explicit diacritical marking
        if s in self.dialect.DEFAULT_CHAR2PHONEMES:
            base_ipa = self.dialect.DEFAULT_CHAR2PHONEMES[s]

            word = self.parent_word.normalized if self.parent_word else ""

            # TODO: per dialect handling

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
                return "ɛ" if self.has_primary_stress else "ɨ"
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
            print(s, next_char, self.dialect.FRONT_VOWEL_CHARS)
            return "s"

        # G before front vowels → [ʒ]
        if s == "g" and next_char in self.dialect.FRONT_VOWEL_CHARS:
            return "ʒ"

        # Initial R → strong R [ʁ]
        if s == "r" and self.is_first_word_letter:
            return "ʁ"

        # R after l, n, s → strong R
        if s == "r" and prev_char in "lns":
            return "ʁ"

        # S between vowels → [z]
        if s == "s" and self.is_intervocalic:
            return "z"

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
        if s == "z" and self.is_last_word_letter:
            return "ʃ" if self.dialect.dialect_code.startswith("pt-PT") else "s"

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

    @property
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
            "text": self.normalized,
            "ipa": self.ipa,
            "is_first_letter": self.is_first_word_letter,
            "is_last_letter": self.is_last_word_letter,
            "is_punct": self.is_punct,
            "is_vowel": self.is_vowel,
            "is_semivowel": self.is_semivowel,
            "is_nasal_vowel": self.is_nasal_vowel,
            "is_open_vowel": self.is_open_vowel,
            "is_closed_vowel": self.is_closed_vowel,
            "is_consonant": self.is_consonant,
            "is_foreign": self.is_foreign,
            "is_silent": self.is_silent,
            "is_intervocalic": self.is_intervocalic,
            "is_between_consonant_vowel": self.is_between_consonant_vowel,
            "is_between_vowel_consonant": self.is_between_vowel_consonant,
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
        dialect: DialectInventory with rules
    """

    surface: str
    grapheme_idx: int = 0  # parent_word.graphemes[idx] == self
    syllable_idx: int = 0  # parent_word.normalized_syllables[idx] == self.surface
    characters: List[CharToken] = dataclasses.field(default_factory=list)
    parent_word: Optional["WordToken"] = None
    dialect: DialectInventory = dataclasses.field(default_factory=EuropeanPortuguese)

    # Precomputed indices
    _idx_in_word: int = -1
    _idx_in_sentence: int = -1

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
                    parent_grapheme=self,
                    dialect=self.dialect
                )
                for i, c in enumerate(self.surface)
            ]

    # =========================================================================
    # BASIC PROPERTIES
    # =========================================================================

    @cached_property
    def normalized(self) -> str:
        """Lowercase form of grapheme."""
        return self.surface.lower()

    @property
    def n_chars(self) -> int:
        """Number of characters in this grapheme."""
        return len(self.characters)

    @property
    def first_char(self) -> CharToken:
        """First character of grapheme."""
        return self.characters[0]

    @property
    def last_char(self) -> CharToken:
        """Last character of grapheme."""
        return self.characters[-1]

    # =========================================================================
    # INDICES AND CONTEXT
    # =========================================================================

    @property
    def idx_in_word(self) -> int:
        """Character index of first char in parent word."""
        return self._idx_in_word

    @property
    def idx_in_sentence(self) -> int:
        """Character index of first char in parent sentence."""
        return self._idx_in_sentence

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
    @property
    def prefix(self) -> str:
        """
        All text before this grapheme in the word.

        Used for checking morphological boundaries (prefixes).
        Example: In "biauricular", prefix of "au" is "bi"
        """
        if not self.parent_word:
            return ""

        prev_graphemes = [
            g.normalized for g in self.parent_word.graphemes
            if g.grapheme_idx < self.grapheme_idx
        ]
        return "".join(prev_graphemes)

    @property
    def suffix(self) -> str:
        """
        All text after this grapheme in the word.

        Used for checking word endings and contexts.
        """
        if not self.parent_word:
            return ""

        next_graphemes = [
            g.normalized for g in self.parent_word.graphemes
            if g.grapheme_idx > self.grapheme_idx
        ]
        return "".join(next_graphemes)

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
    @property
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
        return self.normalized in self.dialect.TRIGRAPH2IPA

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
        if s in self.dialect.TETRAGRAPH2IPA:
            return self.dialect.TETRAGRAPH2IPA[s]

        if s in self.dialect.TRIGRAPH2IPA:
            return self.dialect.TRIGRAPH2IPA[s]

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

    @property
    def features(self) -> Dict[str, any]:
        """
        Extract all linguistic features as a dictionary.

        Returns:
            Dictionary with grapheme features and nested character features
        """
        feats = {
            "n_chars": self.n_chars,
            "text": self.normalized,
            "ipa": self.ipa,
            "parent_syllable": self.parent_syllable,
            "prev_syllable": self.prev_syllable,
            "next_syllable": self.next_syllable,
            "is_archaism": self.is_archaism,
            "is_nasal": self.is_nasal,
            "is_digraph": self.is_digraph,
            "is_trigraph": self.is_trigraph,
            "is_foreign_digraph": self.is_foreign_digraph,
            "is_consonant_hiatus": self.is_consonant_hiatus,
            "is_diphthong": self.is_diphthong,
            "is_triphthong": self.is_triphthong,
            "is_falling_diphthong": self.is_falling_diphthong,
            "is_rising_diphthong": self.is_rising_diphthong,
            "is_nasal_diphthong": self.is_nasal_diphthong,
            "is_oral_diphthong": self.is_oral_diphthong,
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
    parent_sentence: Optional["Sentence"] = None
    dialect: DialectInventory = dataclasses.field(default_factory=EuropeanPortuguese)

    # Precomputed index
    _idx_in_sentence: int = -1

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

        # Step 3: Compute all indices top-down
        self._compute_indices()

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
                                parent_word=self,
                                dialect=self.dialect
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
                            parent_word=self,
                            dialect=self.dialect
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

    def _compute_indices(self):
        """
        Compute all character and grapheme indices top-down.

        This is called after grapheme tokenization to set:
        - Grapheme indices in word
        - Character indices in word
        - Character indices in sentence

        Top-down computation avoids circular dependencies.
        """
        char_idx_in_word = 0

        for grapheme in self.graphemes:
            # Set grapheme's index in word
            grapheme._idx_in_word = char_idx_in_word
            grapheme._idx_in_sentence = self._idx_in_sentence + char_idx_in_word

            # Set character indices
            for char in grapheme.characters:
                char._idx_in_word = char_idx_in_word
                char._idx_in_sentence = self._idx_in_sentence + char_idx_in_word
                char_idx_in_word += 1

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

    @property
    def n_syllables(self) -> int:
        """Number of syllables in word."""
        return len(self.syllables)

    @property
    def idx_in_sentence(self) -> int:
        """Character index of first letter in sentence."""
        return self._idx_in_sentence

    @cached_property
    def is_archaic(self) -> bool:
        return self.normalized in self.dialect.ARCHAIC_WORDS

    # =========================================================================
    # LINKED PROPERTIES
    # =========================================================================

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

    @property
    def features(self) -> Dict[str, any]:
        """
        Extract all linguistic features.

        Returns:
            Dictionary with word features and nested grapheme features
        """
        feats = {
            "n_syllables": self.n_syllables,
            "idx_in_sentence": self.idx_in_sentence,
            "stressed_syllable_idx": self.stressed_syllable_idx,
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
                # Find word in original sentence (preserve case)
                word_start = self.surface.lower().find(word_surface, char_position)

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

    # =========================================================================
    # BASIC PROPERTIES
    # =========================================================================

    @cached_property
    def normalized(self) -> str:
        """Lowercase, stripped form of sentence."""
        # Remove leading/trailing punctuation and whitespace
        return self.surface.lower().strip(string.punctuation + string.whitespace)

    @property
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

    @property
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

    sentence = Sentence(text, dialect=dialect)

    print(f"Sentence: {sentence.surface}")
    print(f"IPA: [{sentence.ipa}]")
    print()
    print("Words:")

    for word in sentence.words:
        print(f"{word.word_idx + 1}. {word.surface} [{word.ipa}]")
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
        "Um homem tem compaixão.",
    ]

    european = EuropeanPortuguese()

    for example in examples:
        demonstrate_transcription(example, european)
        print("=" * 80)
        print()

    print("\nTranscription complete!")
