"""
DIALECTAL VARIATION:
====================
Portuguese exhibits significant phonological variation across regions:

1. EUROPEAN PORTUGUESE (pt-PT):
   - Heavy vowel reduction in unstressed positions
   - Post-alveolar fricatives for syllable-final /s, z/
   - Velarized/dark [ɫ] in coda position
   - Uvular [ʁ] for strong R in most regions

2. BRAZILIAN PORTUGUESE (pt-BR):
   - Less vowel reduction (fuller vowel quality)
   - Palatalization: /t, d/ → [tʃ, dʒ] before [i]
   - L-vocalization: coda /l/ → [w] (creates new diphthongs)
   - Glottal/velar [h, x] for strong R (region-dependent)
   - Alveolar [s] for syllable-final /s/ (not palatalized)
   - Nasal vowels less nasalized than European

3. ANGOLAN PORTUGUESE (pt-AO):
   - Similar to European but with substrate influence
   - Less vowel reduction than European
   - Consistent alveolar trill [r] for R
   - Substrate-influenced prosody from Bantu languages

4. MOZAMBICAN PORTUGUESE (pt-MZ):
   - Similar to European with Bantu substrate
   - Less vowel reduction
   - May preserve distinctions lost in European
   - Regional variation (north vs. south)

5. TIMORESE PORTUGUESE (pt-TL):
   - Influenced by Tetum and other Austronesian languages
   - Similar to European base with local adaptations
   - Less widespread native use (L2 features common)

QUICK REFERENCES:
===========
- http://www.portaldalinguaportuguesa.org
- https://pt.wikipedia.org/wiki/Dialeto
- https://pt.wikipedia.org/wiki/Dialetos_da_l%C3%ADngua_portuguesa
- https://pt.wikipedia.org/wiki/L%C3%ADnguas_galaico-portuguesas
- https://pt.wikipedia.org/wiki/Galego-portugu%C3%AAs

pt-PT dialects:
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_europeu
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_do_Norte
- https://pt.wikipedia.org/wiki/Dialecto_alentejano
- https://pt.wikipedia.org/wiki/Dialecto_algarvio
- https://pt.wikipedia.org/wiki/Dialecto_estremenho
- https://pt.wikipedia.org/wiki/Dialecto_transmontano
- https://pt.wikipedia.org/wiki/Dialecto_a%C3%A7oriano
- https://pt.wikipedia.org/wiki/Dialecto_madeirense
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_oliventino

pt-BR dialects:
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_brasileiro
- https://pt.wikipedia.org/wiki/Dialeto_neutro
- https://pt.wikipedia.org/wiki/Dialeto_da_costa_norte
- https://pt.wikipedia.org/wiki/Dialeto_caipira
- https://pt.wikipedia.org/wiki/Dialeto_baiano
- https://pt.wikipedia.org/wiki/Dialeto_fluminense
- https://pt.wikipedia.org/wiki/Dialeto_ga%C3%BAcho
- https://pt.wikipedia.org/wiki/Dialeto_mineiro
- https://pt.wikipedia.org/wiki/Dialeto_nordestino
- https://pt.wikipedia.org/wiki/Dialeto_nortista
- https://pt.wikipedia.org/wiki/Dialeto_paulistano
- https://pt.wikipedia.org/wiki/Dialeto_sertanejo
- https://pt.wikipedia.org/wiki/Dialeto_sulista_(Brasil)
- https://pt.wikipedia.org/wiki/Dialeto_florianopolitano
- https://pt.wikipedia.org/wiki/Dialeto_Carioca
- https://pt.wikipedia.org/wiki/Dialeto_brasiliense
- https://pt.wikipedia.org/wiki/Dialeto_da_serra_amaz%C3%B4nica
- https://pt.wikipedia.org/wiki/Dialeto_recifense
- https://pt.wikipedia.org/wiki/Amazofonia#Dialeto_Amaz%C3%B4nico_Ocidental

African dialects:
- https://pt.wikipedia.org/wiki/L%C3%ADngua_portuguesa_em_%C3%81frica
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_de_Angola
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_cabo-verdiano
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_da_Guin%C3%A9-Bissau
- https://pt.wikipedia.org/wiki/L%C3%ADnguas_da_Guin%C3%A9_Equatorial#Portugu%C3%AAs
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_de_S%C3%A3o_Tom%C3%A9_e_Pr%C3%ADncipe
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_de_Mo%C3%A7ambique

Angolan dialects:
- https://pt.wikipedia.org/wiki/Dialeto_benguelense
- https://pt.wikipedia.org/wiki/Dialeto_luandense
- https://pt.wikipedia.org/wiki/Dialeto_sulista_(Angola)
- https://pt.wikipedia.org/wiki/Dialeto_huambense

Asian dialects:
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_de_Goa
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_de_Timor-Leste
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_de_Macau

portuguese adjacent minority languages:
- https://pt.wikipedia.org/wiki/L%C3%ADngua_mirandesa
- https://pt.wikipedia.org/wiki/Dialeto_barranquenho
- https://es.wikipedia.org/wiki/Leon%C3%A9s_rionor%C3%A9s
- https://bibliotecadigital.ipb.pt/bitstream/10198/213/1/64%20-%20Dialecto%20rionor%C3%AAs.pdf
- https://pt.wikipedia.org/wiki/Xalimego

portuguese as a minority language
- https://pt.wikipedia.org/wiki/L%C3%ADngua_portuguesa_na_Espanha
- https://pt.wikipedia.org/wiki/Portugu%C3%AAs_uruguaio
- https://pt.wikipedia.org/wiki/L%C3%ADnguas_da_%C3%81frica_do_Sul#L%C3%ADngua_portuguesa
- https://pt.wikipedia.org/wiki/L%C3%ADnguas_de_Maur%C3%ADcio#L%C3%ADngua_portuguesa
- https://pt.wikipedia.org/wiki/L%C3%ADnguas_da_Nam%C3%ADbia#L%C3%ADngua_portuguesa
- https://pt.wikipedia.org/wiki/L%C3%ADnguas_do_Senegal#Portugu.C3.AAs
- https://pt.wikipedia.org/wiki/L%C3%ADnguas_de_Essuat%C3%ADni#L%C3%ADngua_portuguesa
- https://pt.wikipedia.org/wiki/L%C3%ADnguas_da_Z%C3%A2mbia#L.C3.ADngua_portuguesa

portuguese creoles
- https://pt.wikipedia.org/wiki/L%C3%ADnguas_crioulas_de_base_portuguesa
- https://pt.wikipedia.org/wiki/Crioulos_afro-portugueses
- https://pt.wikipedia.org/wiki/Crioulos_indo-portugueses
- https://pt.wikipedia.org/wiki/Crioulos_malaio-portugueses
- https://pt.wikipedia.org/wiki/Crioulos_sino-portugueses
- https://pt.wikipedia.org/wiki/Crioulos_luso-americanos
"""
import dataclasses
import string
from typing import List, Dict, Set

from tugaphone.lexicon import TugaLexicon

# singleton - load .csv into memory only once
LEXICON = TugaLexicon()


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
    TETRAGRAM2IPA: Dict[str, str] = dataclasses.field(default_factory=dict)

    # TRIGRAPHS (3-letter sequences)
    TRIGRAM2IPA: Dict[str, str] = dataclasses.field(default_factory=dict)

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

    # Single character → IPA mapping for specific syllabic positions
    INTERVOCALIC_CHAR2PHONEMES: Dict[str, str] = dataclasses.field(default_factory=dict)
    ONSET_CHAR2PHONEMES: Dict[str, str] = dataclasses.field(default_factory=dict)
    CODA_CHAR2PHONEMES: Dict[str, str] = dataclasses.field(default_factory=dict)

    # Single character → IPA mapping for specific word positions
    WORD_INITIAL_CHAR2PHONEMES: Dict[str, str] = dataclasses.field(default_factory=dict)
    WORD_FINAL_CHAR2PHONEMES: Dict[str, str] = dataclasses.field(default_factory=dict)

    # =========================================================================
    # IRREGULAR WORD MAPPINGS
    # =========================================================================
    # Words with exceptional pronunciations that don't follow regular rules
    # These override all other rules
    IRREGULAR_WORDS: Dict[str, str] = dataclasses.field(default_factory=dict)

    # words with different IPA depending on postag
    HOMOGRAPHS: Dict[str, Dict[str, str]] = dataclasses.field(default_factory=dict)

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
        self._initialize_trigrams()
        self._initialize_tetragrams()
        self._initialize_default_chars()
        self._initialize_stress_rules()
        self._compile_grapheme_inventory()

        # words with different IPA depending on postag
        self.HOMOGRAPHS = self.HOMOGRAPHS or {
            "para": {"ADP": "ˈpɐɾɐ", "VERB": "ˈpaɾɐ"}, # para (preposição) vs pára (verbo) - sem distinção desde o AO1990
            "pelo": {"ADP": "ˈpɨlu", "NOUN": "ˈpelu", "VERB": "ˈpɛlu"}, # pelo, pélo, pêlo - sem distinção desde o AO1990

            "tola": {"NOUN": "ˈtɔlɐ", "ADJ": "ˈtolɐ"},  # tola (feminino de tolo, «tonto») – tola («cabeça», informal);
            "seco": {"ADJ": "ˈseku", "VERB": "ˈsɛku"},  # "sêco" vs "séco"

            "acordo": {"NOUN": "ɐˈkoɾdu", "VERB": "ɐˈkɔɾdu"}, # acordo («entendimento») – acordo (verbo acordar);
            "acerto": {"NOUN": "ɐˈseɾtu", "VERB": "ɐˈsɛɾtu"}, # acerto («acordo», «correção») – acerto (verbo acertar);
            "cerro": {"NOUN": "ˈseʁu", "VERB": "ˈsɛʁu"}, # cerro («elevação, colina») – cerro (verbo cerrar);
            "choro": {"NOUN": "ˈʃoɾu", "VERB": "ˈʃɔɾu"}, # choro («pranto») – choro (verbo chorar);
            "colher": {"NOUN": "kuˈʎɛɾ", "VERB": "kuˈʎeɾ"}, # colher («utensílio de mesa») – colher («apanhar»);
            "começo": {"NOUN": "kuˈmesu", "VERB": "kuˈmɛsu"}, # começo («início») – começo (verbo começar);
            "conserto": {"NOUN": "kõˈseɾtu", "VERB": "kõˈsɛɾtu"}, #  conserto (substantivo) - conserto (1.ª pess.sing. pres. ind. - verbo consertar)
            "coro": {"NOUN": "ˈkoɾu", "VERB": "ˈkɔɾu"}, # coro («conjunto de cantores») – coro (verbo corar);
            "corte": {"NOUN": "ˈkoɾtɨ", "VERB": "ˈkɔɾtɨ"}, # corte («morada do rei») – corte («ato de cortar»; verbo cortar);
            "gozo": {"NOUN": "ˈgozu", "VERB": "ˈgɔzu"}, # gozo («prazer»; «troça») – gozo (verbo gozar);
            "gosto": {"NOUN": "ˈgoʃtu", "VERB": "ˈgɔʃt"}, #   gosto (substantivo) - gosto (1.ª pess.sing. pres. ind. - verbo gostar)
            "jogo": {"NOUN": "ˈʒoɡu", "VERB": "ˈʒɔɡu"}, # jogo («divertimento») – jogo (verbo jogar);
            "molho": {"NOUN": "ˈmoʎu", "VERB": "ˈmɔʎu"}, # molho («líquido, caldo») – molho («feixe»; verbo molhar);
            "olho": {"NOUN": "ˈoʎu", "VERB": "ˈɔʎu"}, # olho («órgão da visão») – olho (verbo olhar);
            "rego": {"NOUN": "ˈʁeɡu", "VERB": "ˈʁɛɡu"}, # rego («sulco, vala») – rego (verbo regar);
            "sede": {"NOUN": "ˈsɛdɨ", "VERB": "ˈsedɨ"}, # sede («vontade de beber») – sede («lugar»);
            "sobre": {"NOUN": "ˈsobɾɨ", "VERB": "ˈsɔbɾɨ"}, # sobre («em cima») – sobre (verbo sobrar);
            "torre": {"NOUN": "ˈtoʁɨ", "VERB": "ˈtɔʁɨ"}, # torre («coluna») – torre (verbo torrar);
            "transtorno": {"NOUN": "tɾɐ̃ʃˈtoɾnu", "VERB": "tɾɐ̃ʃˈtɔɾnu"}, # transtorno («contrariedade») – transtorno (verbo transtornar);

            "peso":  {"NOUN": "ˈpezu",  "VERB": "ˈpɛzu"},  # "pêso" vs "péso"
            "porto": {"NOUN": "ˈpoɾtu", "VERB": "ˈpɔɾtu"},
            "posto": {"NOUN": "ˈpoʃtu", "VERB": "ˈpɔʃtu"}, # eu "pósto" , o meu "pôsto", está "pôsto"
            #"borra": {"NOUN": "ˈboʁɐ", "VERB": "ˈbɔʁɐ"}, # borra («resíduo») – borra (verbo borrar);  SKIP: uncommon - dialectal

            # SKIP: disambiguation based on verb tense out of scope
            # "vede": {"VERB": "ˈveðɨ", "VERB": "ˈvɛðɨ"}, # vede (verbo ver) – vede (verbo vedar).'
            # "pode": {"PRESENT": "ˈpɔðɨ", "PAST": "ˈpoðɨ"},  # pode vs pôde
        }

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
               # "re",  # re-eleger (when doubled)
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
            if self.dialect_code.startswith("pt-BR"):
                self.DIPHTHONG2IPA.update({v: k for k, v in self.PTBR_DIPHTHONGS.items()})

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
                # [w-a-j] sequence
                "uai": "waj",  # rare: Uruguai, Paraguai
                # [w-ɐ̃-j] nasal sequence
                "uão": "wɐ̃w",  # rare: saguão
            }

    def _initialize_trigrams(self):
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
        if not self.TRIGRAM2IPA:
            self.TRIGRAM2IPA = {
                "tch": "tʃ",  # the only true trigraph in portuguese

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

    def _initialize_tetragrams(self):
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
        if not self.TETRAGRAM2IPA:
            self.TETRAGRAM2IPA = {
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
        if not self.WORD_INITIAL_CHAR2PHONEMES:
            self.WORD_INITIAL_CHAR2PHONEMES = {
                "r": "ʁ",  # European uvular
                #"r": "r",  # African/Timorese alveolar trill
                #"r": "h",  # Brazilian [h] or [x]
            }
        if not self.WORD_FINAL_CHAR2PHONEMES:
            self.WORD_FINAL_CHAR2PHONEMES = {
                "z": "ʃ",
                # "z": "s", # pt-BR
            }
        if not self.ONSET_CHAR2PHONEMES:
            self.ONSET_CHAR2PHONEMES = {

            }
        if not self.CODA_CHAR2PHONEMES:
            self.CODA_CHAR2PHONEMES = {
               # "l": "ɫ", # pt-PT
               # "l": "w", # pt-BR
            }
        if not self.INTERVOCALIC_CHAR2PHONEMES:
            self.INTERVOCALIC_CHAR2PHONEMES = {
                "s": "z",
            }
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
            all_graphemes.update(self.TETRAGRAM2IPA.keys())
            all_graphemes.update(self.TRIGRAM2IPA.keys())
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


# the base ruleset is based on Acordo Ortográfico de 1990, in effect since 2009
# https://pt.wikipedia.org/wiki/Acordo_Ortogr%C3%A1fico_de_1990
# http://www.portaldalinguaportuguesa.org/acordo.php
AO1990 = DialectInventory(
    dialect_code="pt",
    IRREGULAR_WORDS={
        # "ui" nasalized in "muito"
        "muito": "ˈmũj.tu",
        # Single-syllable special case
        "miau": "ˈmjaw",
    }
)


# =============================================================================
# DIALECT INSTANCES
# =============================================================================

class EuropeanPortuguese(DialectInventory):
    """
    European Portuguese (Portugal) phonological inventory.

    CHARACTERISTIC FEATURES:
    ------------------------
    1. VOWEL REDUCTION: Unstressed vowels reduce heavily
       - /a/ → [ɐ] in unstressed positions
       - /e/ → [ɨ] (close central) in unstressed positions
       - /o/ → [u] in unstressed positions
       Example: "pedir" [pɨˈdiɾ], "casa" [ˈkazɐ]

    2. FRICATIVE PALATALIZATION: Final /s, z/ → [ʃ, ʒ]
       - "três" [ˈtɾeʃ]
       - "luz" [ˈluʃ]
       - Before voiceless consonants: /s/ → [ʃ]
       - Before voiced consonants: /s/ → [ʒ]

    3. DARK L: Coda /l/ realized as velarized [ɫ]
       - "Brasil" [bɾɐˈziɫ]
       - "mal" [ˈmaɫ]

    4. UVULAR R: Strong /R/ often realized as uvular [ʁ]
       - "rato" [ˈʁatu]
       - "carro" [ˈkaʁu]
       (Some regions use alveolar trill [r])

    5. NASAL VOWELS: Highly nasalized
       - "mão" [ˈmɐ̃w̃]
       - "bem" [ˈbẽj̃]
    """

    def __init__(self, **kwargs):
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-PT"
        if "INTERVOCALIC_CHAR2PHONEMES" not in kwargs:
            kwargs["INTERVOCALIC_CHAR2PHONEMES"] = {
                **AO1990.INTERVOCALIC_CHAR2PHONEMES,
                "s": "z",
                "b": "β",  # <- Voiced bilabial fricative
                "d": "ð", # <- Voiced alveolar non-sibilant fricative (not present in southern dialects)
            }
        if "CODA_CHAR2PHONEMES" not in kwargs:
            kwargs["CODA_CHAR2PHONEMES"] = {
                **AO1990.CODA_CHAR2PHONEMES,
                "l": "ɫ",
            }
        if "FALLING_NASAL_DIPHTHONGS" not in kwargs:
            kwargs["FALLING_NASAL_DIPHTHONGS"] = {
                **AO1990.FALLING_NASAL_DIPHTHONGS,
                "ũj": "ui",  # muito (special nasalized case)
            }
        if "TRIPHTHONG2IPA" not in kwargs:
            kwargs["TRIPHTHONG2IPA"] = {
                **AO1990.TRIPHTHONG2IPA,
                # [j-e-j] sequence
                "iei": "jej",  # chieira, macieira, pardieiro
                # Alternative Lisbon realization:
                # "iei": "jɐj",  # with vowel reduction
                # [j-a-w] sequence
                "iau": "jaw",  # miau
            }
        if "IRREGULAR_WORDS" not in kwargs:
            kwargs["IRREGULAR_WORDS"] = LEXICON.get_ipa_map(region="lbx")
        super().__init__(**kwargs)


class NorthernPortuguese(EuropeanPortuguese):
    """
    Northern Portuguese phonological inventory (Minho, Douro Litoral).

    LINGUISTIC OVERVIEW:
    --------------------
    Northern Portuguese dialects form a dialectal continuum with Galician,
    preserving several archaic features lost in Central-Southern varieties.
    These dialects are spoken in the regions of Minho, Trás-os-Montes, and
    parts of Douro Litoral, representing the most conservative varieties of
    European Portuguese.

    CHARACTERISTIC FEATURES:
    ------------------------
    1. BETACISM: Merger of /b/ and /v/ → [b] or [β]
       - LINGUISTIC CONTEXT: Common in Iberian Romance; reflects historical
         lack of /v/ phoneme in Latin
       - "vinho" [ˈbiɲu] or [ˈβiɲu] (not [ˈviɲu])
       - "bola" [ˈbɔlɐ] or [ˈβɔlɐ]
       - Intervocalic position strongly favors fricative [β]
       - Also affects <f> → [ɸ] (bilabial fricative) in some sub-dialects

    2. DIPHTHONG PRESERVATION: Maintains historical diphthongs
       a) /ej/ in <ei> stays [ej] (not monophthongized to [ɐj])
          - "primeiro" [pɾiˈmejɾu] (Lisbon: [pɾiˈmɐjɾu])
          - "feito" [ˈfejtu] (Lisbon: [ˈfɐjtu])
          - INSIGHT: Reflects medieval Portuguese pronunciation

       b) /ow/ in <ou> stays [ow] (not monophthongized to [o])
          - "ouro" [ˈowɾu] (Lisbon: [ˈoɾu])
          - "pouco" [ˈpowku] (Lisbon: [ˈpoku])
          - HISTORICAL: This diphthong comes from Latin -AU-

    3. AFFRICATE PRESERVATION: /tʃ/ maintained in <ch>
       - "chuva" [ˈtʃuβɐ] (not [ˈʃuvɐ])
       - "achar" [ɐˈtʃaɾ] (not [ɐˈʃaɾ])
       - INSIGHT: Medieval Portuguese had /tʃ/ which simplified to [ʃ]
         in most dialects but persists in the North

    4. FRICATIVIZATION: Lenition of voiced stops in intervocalic position
       - /d/ → [ð] (voiced dental fricative)
       - /b/ → [β] (voiced bilabial fricative)
       - "cada" [ˈkaðɐ] (not [ˈkadɐ])
       - "saber" [sɐˈβeɾ] (not [sɐˈbeɾ])

    GEOGRAPHICAL DISTRIBUTION:
    --------------------------
    - Spoken from the Spanish border (Galicia) south to the Douro River
    - Strongholds: Braga, Viana do Castelo, Vila Real
    - Forms transitional zone with Galician in the north
    - More conservative in rural areas; urban centers show Lisbon influence

    SOCIOLINGUISTIC NOTES:
    ----------------------
    - Stigmatized in some urban contexts (seen as "rural")
    - Strong regional identity and pride in traditional speech
    - Young speakers increasingly adopt Lisbon norms
    - Galician-Portuguese cultural continuity maintained
    """
    def __init__(self, **kwargs):
        # Northern European Portuguese dialects, closely related with Galician, are characterized by:
        #     Betacism: [b] and [v] are realized as [b] or [β] (e.g.: chuva: [ˈt͡ʃu.βɐ], vela: [ˈbɛ.lɐ], [ˈβɛ.lɐ]).
        #     Conservation the diphthong /ej/ in <ei>, instead of realizing it as /ɐj/ (e.g.: ceifar: [sej.ˈfaɾ], feito: [ˈfej.tu])
        #     Conservation of the diphthong /ow/ in <ou>, instead of merging it with /o/ (e.g.: ouro: [ˈow.ɾu], ouvir: [ow.ˈβiɾ]).
        #     Conservation of the affricate /t͡ʃ/ in <ch>, instead of merging it with /ʃ/ (e.g.: chuva: [ˈt͡ʃu.βɐ], chamar: [t͡ʃɐ.ˈmaɾ]).
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-PT-x-north"
        if "DEFAULT_CHAR2PHONEMES" not in kwargs:
            kwargs["DEFAULT_CHAR2PHONEMES"] ={
                **AO1990.DEFAULT_CHAR2PHONEMES,
                # "f": "ɸ", # <- Voiceless bilabial fricative
                "v": "b" # <- Betacism
            }
        if "INTERVOCALIC_CHAR2PHONEMES" not in kwargs:
            kwargs["INTERVOCALIC_CHAR2PHONEMES"] = {
                **AO1990.INTERVOCALIC_CHAR2PHONEMES,
                "d": "ð",  # <- Voiced alveolar non-sibilant fricative
                "b": "β",  # <- Voiced bilabial fricative
                "v": "β",  # <- Betacism
            }
        if "DIPHTHONG2IPA" not in kwargs:
            kwargs["DIPHTHONG2IPA"] = {
                **AO1990.DIPHTHONG2IPA,
                "ei": "ej",  # aj in south
            }
        if "IRREGULAR_WORDS" not in kwargs:
            kwargs["IRREGULAR_WORDS"] = {
                "têm": "tẽjẽj",
                "rei": "ʀˈej",
                "frio": "fɾi·u",
                "rio": "ʁi·u",
            }
        super().__init__(**kwargs)


class TransmontanoPortuguese(NorthernPortuguese):
    """
    Transmontano (Trás-os-Montes) Portuguese phonological inventory.

    LINGUISTIC OVERVIEW:
    --------------------
    Transmontano Portuguese, spoken in the northeastern interior region of
    Portugal (Trás-os-Montes), represents one of the most archaic and
    phonologically rich Portuguese dialects. It uniquely preserves a medieval
    sibilant contrast that has been lost in virtually all other Portuguese
    varieties worldwide.

    THE SIBILANT DISTINCTION (Most Distinctive Feature):
    -----------------------------------------------------
    Transmontano is the ONLY Portuguese dialect that maintains the medieval
    four-way sibilant distinction that existed in 16th-century Portuguese:

    1. APICO-ALVEOLAR SIBILANTS (from medieval affricates):
       - Voiceless [s̺] in <ss>: "passo" [ˈpas̺u] (step)
       - Voiced [z̺] in <s>: "coser" [kuˈz̺eɾ] (to sew)
       - Articulated with tongue tip raised (apical)
       - Retracted, "darker" sound quality
       - Similar to Spanish <s>

    2. PREDORSO-DENTAL SIBILANTS (from medieval fricatives):
       - Voiceless [s] in <ç>: "paço" [ˈpasu] (palace)
       - Voiced [z] in <z>: "cozer" [kuˈzeɾ] (to cook)
       - Articulated with tongue blade (laminal)
       - More "fronted" sound quality
       - Standard in rest of Portuguese-speaking world

    HISTORICAL LINGUISTICS:
    -----------------------
    In medieval Galician-Portuguese (12th-13th centuries):
    - <ç>, <z> were AFFRICATES: [ts], [dz]
    - <ss>, <s> were already FRICATIVES: [s̺], [z̺]

    By the 16th century:
    - Affricates de-affricated: [ts] > [s], [dz] > [z]
    - Creating a 4-way contrast: [s]/[z] vs. [s̺]/[z̺]

    In most of Portugal (16th-17th centuries):
    - Coastal/Southern: Merged toward [s]/[z] (predorso-dental)
    - Interior North: Merged toward [s̺]/[z̺] (apico-alveolar)
    - Transmontano: PRESERVED BOTH (unique!)
    - Brazil/Africa: Inherited only [s]/[z] (no apicals)

    MINIMAL PAIRS DEMONSTRATING THE CONTRAST:
    ------------------------------------------
    - "cozer" [kuˈzeɾ] (to cook) vs. "coser" [kuˈz̺eɾ] (to sew)
    - "paço" [ˈpasu] (palace) vs. "passo" [ˈpas̺u] (step)
    - These sound IDENTICAL in all other Portuguese dialects!

    OTHER NORTHERN FEATURES (inherited from NorthernPortuguese):
    -------------------------------------------------------------
    - Betacism: /v/ → [b] or [β]
    - Affricate preservation: <ch> → [tʃ] (not [ʃ])
    - Diphthong preservation: <ei> → [ej], <ou> → [ow]
    - Intervocalic fricativization: /d/ → [ð], /b/ → [β]

    GEOGRAPHICAL AND SOCIOLINGUISTIC CONTEXT:
    -----------------------------------------
    - Covers: Bragança, Miranda do Douro, parts of Vila Real
    - Most isolated Portuguese dialect (mountainous interior)
    - Strong substrate from Leonese and Asturian
    - Neighboring Mirandese (separate Romance language) influence
    - Highly stigmatized, rapid decline among young speakers
    - Academic/linguistic prestige as archaic treasure

    ORTHOGRAPHIC NOTE:
    ------------------
    Standard Portuguese spelling does NOT distinguish these sounds:
    - Writers must know etymology to spell correctly
    - "cozer" vs. "coser" look different but sound same (elsewhere)
    - In Transmontano, spelling actually reflects pronunciation!

    REFERENCES:
    -----------
    The preservation of this distinction is documented in:
    - Lindley Cintra's work on Portuguese dialectology
    - Studies of medieval Portuguese phonology
    - Comparative Romance linguistics (cf. Spanish apical /s/)
    """
    def __init__(self, **kwargs):
        # Lack of Sesseio:
        #   [s] and [z] are distinguished from apical alveolar fricatives, [s̺] and [z̺], respectively
        #   (e.g.: cozer: [kuˈzeɾ] vs. coser: [kuˈz̺eɾ]; paço: [paˈsu] vs. passo: [paˈs̺u])
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-PT-x-transmontano"
        if "INTERVOCALIC_CHAR2PHONEMES" not in kwargs:
            kwargs["INTERVOCALIC_CHAR2PHONEMES"] = {
                **AO1990.INTERVOCALIC_CHAR2PHONEMES,
                "s": "ʐ",  # <- Voiced retroflex fricative

                # common with NorthernPortuguese
                "d": "ð",  # <- Voiced alveolar non-sibilant fricative
                "b": "β",  # <- Voiced bilabial fricative
                "v": "β",  # <- Betacism
            }
        if "DIGRAPH2IPA" not in kwargs:
            kwargs["DIGRAPH2IPA"] = {
                **AO1990.DIGRAPH2IPA,
                "ch": "tʃ", # <- Voiceless postalveolar affricate
                "ss": "ʂ"  # <- Voiceless retroflex fricative
            }
        super().__init__(**kwargs)


class CentralPortuguese(EuropeanPortuguese):
    """
    Central Portuguese phonological inventory (Estremadura, Ribatejo).

    LINGUISTIC OVERVIEW:
    --------------------
    Central Portuguese represents the dialectal basis for Standard European
    Portuguese. Centered on Lisbon and surrounding regions (Estremadura and
    Ribatejo), this variety became prestigious through political and cultural
    dominance of the capital. Most phonological innovations that distinguish
    modern European Portuguese from historical forms and from Brazilian
    Portuguese originated in or spread from this region.

    CHARACTERISTIC INNOVATIONS:
    ---------------------------
    1. DIPHTHONG REDUCTION: /ej/ → [ɐj] (the "Lisbon change")
       - Historical: Medieval /ej/ from Latin -ARIU, -E
       - "primeiro" [pɾiˈmɐjɾu] (North: [pɾiˈmejɾu])
       - "feito" [ˈfɐjtu] (North: [ˈfejtu])
       - "leite" [ˈlɐjtɨ] (North: [ˈlejtɨ])
       - SPREAD: This feature diffused from Lisbon throughout Central-South
       - PRESTIGE: Became marker of educated/urban speech

    2. MONOPHTHONGIZATION: /ow/ → [o]
       - Historical: Medieval /ow/ from Latin -AU-
       - "ouro" [ˈoɾu] (North: [ˈowɾu])
       - "pouco" [ˈpoku] (North: [ˈpowku])
       - "couro" [ˈkoɾu] (North: [ˈkowɾu])
       - INSIGHT: Creates homophony with original /o/
       - "ouro" [ˈoɾu] = "oro" (if it existed)

    3. FRICATIVIZATION PATTERNS:
       a) Intervocalic /s/ → [z] (voicing)
          - "casa" [ˈkazɐ]
          - "coisa" [ˈkojzɐ]

       b) Intervocalic /d/ → [ð] (spirantization)
          - "nada" [ˈnaðɐ]
          - "cedo" [ˈseðu]
          - NOTE: Less consistent than in Northern varieties

    4. NASAL DIPHTHONG EVOLUTION (Lisbon-specific, see LisbonPortuguese):
       - /ẽj/ → [ẽj] in most Central, but [ɐ̃j] in Lisbon proper
       - "bem" [ˈbẽj] (general Central) vs. [ˈbɐ̃j] (Lisbon)

    VOWEL REDUCTION (Standard European Feature):
    ---------------------------------------------
    - Full reduction in unstressed syllables (inherited from EuropeanPortuguese)
    - /a/ → [ɐ]: "banana" [bɐˈnɐnɐ]
    - /e/ → [ɨ]: "pede" [ˈpɛðɨ]
    - /o/ → [u]: "bonito" [buˈnitu]
    - This is STRONGEST in Central varieties, weaker in North/South

    GEOGRAPHICAL DISTRIBUTION:
    --------------------------
    - Core: Greater Lisbon, Setúbal Peninsula, Ribatejo
    - Influence zone: Extends north to Leiria, south to northern Alentejo
    - Urban vs. Rural: Urban areas more innovative; rural pockets preserve features

    SOCIOLINGUISTIC PRESTIGE:
    -------------------------
    - BASIS for Standard European Portuguese
    - Used in media, education, government
    - Lisboa accent = prestige norm (though see LisbonPortuguese for specifics)
    - Non-Lisbon speakers often adopt these features for upward mobility
    - Brazilian Portuguese speakers learning EP learn this variety

    HISTORICAL DEVELOPMENT:
    -----------------------
    - Medieval base: Similar to Northern dialects (Galician-Portuguese)
    - 15th-16th centuries: Lisbon becomes capital, court speech innovates
    - 17th-18th centuries: Innovations spread to educated classes
    - 19th-20th centuries: Standardization codifies Lisbon-based norms
    - Today: Continues to innovate (e.g., new vowel qualities)

    COMPARISON WITH NORTHERN DIALECTS:
    -----------------------------------
    Feature              | Central        | Northern
    ---------------------|----------------|------------------
    <ei> pronunciation   | [ɐj]           | [ej]
    <ou> pronunciation   | [o]            | [ow]
    Betacism            | No (/v/ ≠ /b/) | Yes (/v/ = /b/)
    <ch> pronunciation   | [ʃ]            | [tʃ] (affricate)
    Vowel reduction     | Heavy          | Moderate

    COMPARISON WITH SOUTHERN DIALECTS:
    -----------------------------------
    - Southern tends to further reduce diphthongs (see SouthernPortuguese)
    - Southern drops intervocalic /d/ more frequently
    - Central more conservative in some respects
    """
    def __init__(self, **kwargs):
        # Realization of /ej/ in <ei> as /ɐj/ (e.g.: ceifar: [sɐj.ˈfaɾ], feito: [ˈfɐj.tu])
        # (characteristic of the Lisbon dialect that spread to the rest of the country)
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-PT-x-central"
        if "DIPHTHONG2IPA" not in kwargs:
            kwargs["DIPHTHONG2IPA"] = {
                **AO1990.DIPHTHONG2IPA,
                "ei": "ɐj", # ej in the north
                "ou": "o"
            }
        if "INTERVOCALIC_CHAR2PHONEMES" not in kwargs:
            kwargs["INTERVOCALIC_CHAR2PHONEMES"] = {
                **AO1990.INTERVOCALIC_CHAR2PHONEMES,
                "s": "z",
                "d": "ð",
            }
        if "IRREGULAR_WORDS" not in kwargs:
            kwargs["IRREGULAR_WORDS"] = {
                "têm": "tɐ̃jɐ̃j",
                "rei": "ʀˈɐj",
                "frio": "fɾi·u",
                "rio": "ʁi·u",
            }
        super().__init__(**kwargs)


class LisbonPortuguese(CentralPortuguese):
    """
    Lisbon Portuguese phonological inventory (Lisboa/Lisbon metropolitan area).

    LINGUISTIC OVERVIEW:
    --------------------
    Lisbon Portuguese (locally "lisboeta" or "alfacinha") represents the
    most prestigious and influential variety of European Portuguese. As the
    accent of Portugal's capital and largest city, it serves as the de facto
    standard for media, education, and formal contexts. However, Lisbon has
    its own unique phonological innovations beyond general Central Portuguese.

    THE "LISBON SOUND":
    -------------------
    Lisbon Portuguese is characterized by particularly innovative and
    distinctive phonological changes, some of which spread to other regions,
    while others remain markers of the capital's speech.

    UNIQUE LISBON FEATURES:
    -----------------------
    1. NASAL DIPHTHONG LOWERING: /ẽj/ → [ɐ̃j]
       - "bem" [ˈbɐ̃j] (elsewhere: [ˈbẽj])
       - "também" [tɐ̃ˈbɐ̃j] (elsewhere: [tɐ̃ˈbẽj])
       - "vem" [ˈvɐ̃j] (elsewhere: [ˈvẽj])
       - This is THE most distinctive Lisbon feature
       - Spread: Now common in much of Central Portugal
       - Prestige: Seen as sophisticated urban speech

    2. OPEN VOWEL BEFORE PALATALS: /e/ → [a] / _[palatal]
       - "madeira" [mɐˈdajɾɐ] (not [mɐˈdejɾɐ])
       - "empenho" [ɐ̃ˈpɐɲu] (not [ɐ̃ˈpeɲu])
       - "grelha" [ˈɡɾaʎɐ] (not [ˈɡɾeʎɐ])
       - Affects /e/ before /j/, /ɲ/, /ʎ/
       - Very salient Lisbon marker
       - NOT adopted widely outside Lisbon

    3. FINAL /i.u/ DIPHTHONGIZATION: -io → [iw]
       - "rio" [ˈʁiw] (elsewhere: [ˈʁiu] or [ˈʁiw])
       - "frio" [ˈfɾiw] (elsewhere: [ˈfɾiu])
       - "médio" [ˈmɛðiw] (elsewhere: [ˈmɛðiu])
       - Creates new falling diphthong
       - Variable even within Lisbon

    4. /ɐj/ REALIZATION OF <ei>:
       - Inherits Central Portuguese /ej/ → [ɐj]
       - But in Lisbon often realized as [aj] (more open)
       - "leite" [ˈlajtɨ] (not [ˈlɐjtɨ])
       - "primeiro" [pɾiˈmajɾu] (not [pɾiˈmɐjɾu])
       - Highly stigmatized as "overly Lisbon"

    SHARED CENTRAL FEATURES (see CentralPortuguese):
    -------------------------------------------------
    - /ow/ → [o] monophthongization
    - Heavy vowel reduction
    - Intervocalic /s/ → [z], /d/ → [ð]
    - No betacism (/v/ ≠ /b/)
    - <ch> → [ʃ] (not affricate)

    SOCIOLINGUISTIC DYNAMICS:
    --------------------------
    1. PRESTIGE PARADOX:
       - Lisbon = standard/prestige
       - But SOME Lisbon features stigmatized as "too Lisbon"
       - e.g., [aj] for <ei> seen as affected/snobbish
       - "Good Portuguese" = educated Lisbon WITHOUT the most marked features

    2. INTERNAL VARIATION:
       - Old Lisbon (Alfama, Mouraria): More conservative, working-class
       - New Lisbon (Avenidas Novas): More innovative, middle-class
       - Suburbs (Amadora, Sintra): Mixed, influenced by migration

    3. NATIONAL INFLUENCE:
       - Media accent = moderate Lisbon (not extreme)
       - Politicians often moderate Lisbon features
       - RTP (state broadcaster) uses educated Lisbon norm

    4. AGE AND CLASS:
       - Older speakers: More marked Lisbon features
       - Younger speakers: Some features declining
       - Upper-middle class: Most innovative
       - Working class: May preserve older features

    COMPARISON WITH OTHER EUROPEAN VARIETIES:
    ------------------------------------------
    Feature              | Lisbon         | Oporto (North) | Coimbra
    ---------------------|----------------|----------------|------------------
    <ém>, <éns>          | [ɐ̃j]          | [ẽj]           | [ẽj]
    <ei> realization     | [aj] ~ [ɐj]    | [ej]           | [ɐj]
    /e/ before palatals  | [a]            | [e]            | [e]
    Vowel reduction      | Heavy          | Moderate       | Heavy
    Prestige            | Highest        | Regional       | Academic

    HISTORICAL DEVELOPMENT:
    -----------------------
    - 15th-16th c.: Lisbon becomes capital, court develops distinct accent
    - 17th-18th c.: Great Earthquake (1755) reshapes city and speech
    - 19th c.: Industrialization, population growth, new Lisbon quarters
    - 20th c.: Standardization around Lisbon norms
    - 21st c.: Some leveling toward pan-European standard

    ORTHOGRAPHY AND PRONUNCIATION:
    -------------------------------
    Standard spelling does NOT reflect Lisbon-specific features:
    - "bem" spelled same everywhere, pronounced [ˈbɐ̃j] in Lisbon
    - Learners must acquire these rules separately
    - No orthographic reform has addressed this

    RECEPTION BY OTHER PORTUGUESE SPEAKERS:
    ----------------------------------------
    - Portuguese: Seen as standard/proper
    - Brazilians: Often find it hard to understand (heavy reduction)
    - Africans: Model for formal speech, but may sound foreign
    - Other Portuguese regions: Mixed admiration and resentment
    """
    def __init__(self, **kwargs):
        # The "standard" European Portuguese of Lisbon is a member of the Central-Southern Portuguese dialects. It is characterized by:
        #     Monophthongization of /ow/ in <ou> to /o/ (e.g.: ouro: [ˈo.ɾu], ouvir: [o.ˈviɾ]). (conserved in Northern Portugal dialects)
        #     Realization of /ej/ in <ei> as /ɐj/ (e.g.: ceifar: [sɐj.ˈfaɾ], feito: [ˈfɐj.tu]) (characteristic of the Lisbon dialect that spread to the rest of the country)
        #     Realization of /ẽj/ and /ɛ̃j/ in <ém>/<éns> as /ɐ̃j/ (e.g.: bem: [ˈbɐ̃j], vens: [ˈvɐ̃jʃ]) (characteristic of the Lisbon dialect that spread to the rest of the country)
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-PT-x-lisbon"

        # TODO: Diphthongization of final /i.u/ in <io> to /iw/ (e.g.: rio: [ˈʁiw], frio: [ˈfɾiw])
        if "IRREGULAR_WORDS" not in kwargs:
            kwargs["IRREGULAR_WORDS"] = {
                **LEXICON.get_ipa_map(region="lbx"),
                "frio": "fɾiw",
                "rio": "ʁiw",
                "têm": "tɐ̃jɐ̃j",
                "rei": "ʀˈɐj"
            }

        # TODO: Em Lisboa o ditongo [ej] pronuncia-se [αj]; aliás, na capital todos os [e] tónicos antes
        #       de um fonema palatal passam a [α], cf. p.ex. madeira [mαđαjrα], empenho [ẽpαñu], grelha [grαλα]
        # TODO - add self.is_prepalatal property to CharToken
        super().__init__(**kwargs)


class SouthernPortuguese(CentralPortuguese):
    """
    Southern Portuguese phonological inventory (Alentejo, Algarve).

    LINGUISTIC OVERVIEW:
    --------------------
    Southern Portuguese encompasses the dialects of Portugal's southern
    regions: Alentejo (interior) and Algarve (southern coast). These varieties
    share the Central Portuguese base but exhibit distinctive features,
    particularly more extensive monophthongization and consonant deletion.
    Southern Portuguese shows influences from historical Arabic/Mozarabic
    substrates and prolonged isolation from the northern population centers.

    CHARACTERISTIC FEATURES:
    ------------------------
    1. EXTENSIVE MONOPHTHONGIZATION: /ej/ → [e] (not [ɐj])
       - Goes BEYOND Central Portuguese
       - Central: /ej/ → [ɐj]
       - Southern: /ej/ → [e] (complete monophthongization)
       - "primeiro" [pɾiˈmeɾu] (Lisbon: [pɾiˈmɐjɾu], North: [pɾiˈmejɾu])
       - "feito" [ˈfetu] (Lisbon: [ˈfɐjtu], North: [ˈfejtu])
       - "leite" [ˈletɨ] (Lisbon: [ˈlɐjtɨ])
       - INSIGHT: Southern completes what Central started
       - RESULT: Creates more homophones (simplification)

    2. /ow/ → [o] MONOPHTHONGIZATION:
       - Shared with Central Portuguese
       - "ouro" [ˈoɾu], "pouco" [ˈpoku]
       - But Southern may have completed this earlier historically

    3. REDUCED INTERVOCALIC FRICATIVIZATION:
       - LESS /d/ → [ð] than Central/Northern
       - Often complete deletion instead: /d/ → ∅
       - "nada" [ˈnaɐ] (not [ˈnaðɐ])
       - "cedo" [ˈseu] (not [ˈseðu])
       - "comida" [kuˈmiɐ] (not [kuˈmiðɐ])
       - Creates hiatus or vowel mergers

    4. INTERVOCALIC /s/ VOICING:
       - Shares with Central: /s/ → [z]
       - "casa" [ˈkazɐ]
       - But may delete in rapid speech

    5. PROSODIC FEATURES:
       - Slower, more deliberate tempo (especially Alentejo)
       - Less vowel reduction than Lisbon (despite being Central-based)
       - Clearer articulation of vowels
       - "Singing" intonation (especially Alentejo)

    REGIONAL SUB-VARIETIES:
    -----------------------
    A) ALENTEJO PORTUGUESE:
       - Interior, rural, agricultural region
       - Most distinctive prosody (slow, melodic)
       - Conservative in some ways, innovative in others
       - Strong regional identity and pride
       - "Alentejano" often sung in fado tradition
       - Extensive /d/ deletion
       - Clear vowels despite reduction

    B) ALGARVE PORTUGUESE (Algarvio):
       - Southern coast, tourism-influenced
       - More contact with Andalusian Spanish historically
       - Some Arabic/Mozarabic substrate influence
       - Coastal vs. interior variation
       - Tourism bringing leveling toward standard
       - Less distinctive than Alentejo

    HISTORICAL AND SUBSTRATE INFLUENCES:
    -------------------------------------
    1. ARABIC/MOZARABIC (711-1249 CE):
       - Southern Portugal under Moorish rule longest
       - Algarve last to be reconquered (1249)
       - Substrate influence on:
         * Lexicon (many Arabic loanwords)
         * Possibly prosody (rhythm, intonation)
         * Place names (Algarve < al-Gharb "the West")

    2. ISOLATION:
       - Alentejo sparsely populated, isolated from North
       - Developed independently from Lisbon innovations
       - Slower to adopt standard features
       - Preserved some archaic features

    3. SPANISH CONTACT:
       - Border region with Spain (Andalusia)
       - Some lexical and phonological borrowing
       - Especially in Algarve

    COMPARISON WITH OTHER VARIETIES:
    ---------------------------------
    Feature              | Southern       | Central/Lisbon | Northern
    ---------------------|----------------|----------------|------------------
    <ei> pronunciation   | [e]            | [ɐj] ~ [aj]    | [ej]
    <ou> pronunciation   | [o]            | [o]            | [ow]
    Intervocalic /d/     | ∅ (deleted)    | [ð]            | [ð] ~ [d]
    Vowel reduction      | Moderate       | Heavy          | Moderate
    Tempo               | Slow           | Fast           | Moderate
    Prosody             | Melodic        | Reduced        | Varied

    SOCIOLINGUISTIC NOTES:
    ----------------------
    1. STIGMA AND PRIDE:
       - Alentejano often stereotyped as "slow" (negative)
       - But also valued as authentic, rural, traditional (positive)
       - Associated with farming, countryside, simplicity
       - Strong regional identity, resistance to Lisbon norms

    2. MEDIA REPRESENTATION:
       - Alentejo accent featured in folk music (modas, fado)
       - Used in literature for regional characters
       - Comedy sometimes exaggerates features
       - Rarely in formal media (Lisbon dominates)

    3. DEMOGRAPHIC CHANGES:
       - Rural depopulation affecting Alentejo
       - Young people moving to Lisbon, adopting standard
       - Algarve tourism bringing linguistic contact
       - Traditional features declining in urban areas

    4. LINGUISTIC ATTITUDES:
       - Northern speakers: May find Southern "lazy" (consonant deletion)
       - Lisbon speakers: May find Southern "provincial"
       - Southern speakers: Pride in distinctiveness vs. pressure to standardize
       - Brazilians: Often easier to understand than Lisbon (less reduction)

    PHONOLOGICAL PROCESSES:
    -----------------------
    1. CONSONANT DELETION CASCADE:
       /d/ → [ð] → ∅
       "comida" /koˈmidɐ/ → [kuˈmiðɐ] → [kuˈmiɐ]

    2. DIPHTHONG REDUCTION CASCADE:
       /ej/ → [ɐj] → [e]
       "primeiro" /pɾiˈmejɾu/ → [pɾiˈmɐjɾu] → [pɾiˈmeɾu]

    3. HIATUS CREATION:
       Consonant deletion creates vowel sequences
       "cidade" /siˈdadɨ/ → [siˈdaðɨ] → [siˈdaɨ]

    LEXICAL NOTES:
    --------------
    - Many Arabic-origin words preserved (especially place names)
    - Distinctive vocabulary for agriculture, food, local culture
    - Some archaisms lost elsewhere
    - Regional expressions and idioms

    FUTURE OUTLOOK:
    ---------------
    - Leveling toward Lisbon standard in urban areas
    - Rural features declining with depopulation
    - Tourism in Algarve bringing change
    - But strong regional identity may preserve some features
    - Academic interest in documentation and preservation
    """
    def __init__(self, **kwargs):
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-PT-x-south"
        if "DIPHTHONG2IPA" not in kwargs:
            kwargs["DIPHTHONG2IPA"] = {
                **AO1990.DIPHTHONG2IPA,
                "ei": "e", # Monophthongization of /ej/ in <ei> to /e/ (e.g.: ceifar: [se.ˈfaɾ], feito: [ˈfe.tu])
                "ou": "o"
            }
        if "INTERVOCALIC_CHAR2PHONEMES" not in kwargs:
            kwargs["INTERVOCALIC_CHAR2PHONEMES"] = {
                **AO1990.INTERVOCALIC_CHAR2PHONEMES,
                "s": "z",
                "d": "d",
            }
        super().__init__(**kwargs)


class AlentejanoPortuguese(SouthernPortuguese):
    """
    Alentejo Portuguese phonological inventory.

    LINGUISTIC OVERVIEW:
    --------------------
    Alentejano, spoken in Portugal's vast southern interior region (Alentejo),
    is one of the most distinctive and culturally significant Portuguese
    dialects. Known for its remarkably slow tempo, melodic "singing" quality,
    and extensive consonant deletion, Alentejano is instantly recognizable
    and deeply tied to regional identity. The dialect preserves archaic
    features while also innovating in striking ways.


    DEFINING PROSODIC CHARACTER:
    ----------------------------
    The MOST SALIENT feature of Alentejano is not segmental phonology but
    PROSODY - the rhythm, tempo, and melody of speech.

    Utilização regular do gerúndio no tempo presente (à semelhança do português brasileiro)
    Paragoge em i, nos verbos no infinitivo. Ex: fazêri (fazer)

    1. EXCEPTIONALLY SLOW TEMPO:
       - Deliberate, unhurried articulation
       - Longest average syllable duration in Portuguese
       - Pauses between phrases/clauses
       - PERCEPTION: Sounds "relaxed," "lazy," or "contemplative"
       - CULTURAL: Reflects agricultural lifestyle, hot climate
       - STEREOTYPE: "Alentejanos speak slowly like their oxen walk"

    2. MELODIC INTONATION ("Canto alentejano"):
       - Wide pitch range, musical quality
       - Rising-falling patterns on stressed syllables
       - Final syllable lengthening and pitch movement
       - Similar patterns found in traditional Alentejo singing (modas)
       - Creates impression of "singing" rather than speaking
       - UNIQUE: Most melodic mainland Portuguese variety

    3. VOWEL LENGTHENING:
       - Stressed vowels notably longer than other dialects
       - Unstressed vowels less reduced than Lisbon
       - Clearer vowel quality overall
       - "casa" [ˈkaːzɐ] (long [aː])

    SEGMENTAL PHONOLOGY:
    --------------------
    1. EXTENSIVE INTERVOCALIC /d/ DELETION:
       - Most consistent /d/ deletion of any Portuguese dialect
       - /d/ → ∅ in most intervocalic contexts
       - "nada" [ˈnaɐ] → [ˈnɐː] (often with compensatory lengthening)
       - "cedo" [ˈseu] → [ˈseː]
       - "comida" [kuˈmiɐ] → [kuˈmiː]
       - "cidade" [siˈdaɨ] → [siˈdaː]
       - Even in careful speech: deletion very common
       - Creates many hiatus contexts and long vowels

    2. COMPLETE /ej/ MONOPHTHONGIZATION:
       - Inherits from SouthernPortuguese: /ej/ → [e]
       - "primeiro" [pɾiˈmeɾu]
       - "feito" [ˈfetu]
       - No variation - categorical rule

    3. /ow/ MONOPHTHONGIZATION:
       - Also from SouthernPortuguese: /ow/ → [o]
       - "ouro" [ˈoɾu]
       - "pouco" [ˈpoku]

    4. SIBILANT VOICING:
       - Intervocalic /s/ → [z]
       - But may delete in rapid speech: "casa" [ˈkazɐ] ~ [ˈkaɐ]

    5. FINAL CONSONANT WEAKENING:
       - Less consistent than /d/ deletion
       - Final /r/ may delete: "falar" → [fɐˈla]
       - Final /l/ → [w]: "mal" [ˈmaw] (standard Brazilian pattern)

    VOWEL SYSTEM:
    -------------
    - LESS reduction than Lisbon despite being Southern
    - Stressed vowels: Clear, long, well-articulated
    - Unstressed vowels: Reduced but not as much as Central
    - /a/ → [ɐ] in unstressed (but longer, clearer than Lisbon)
    - /e/ → [ɨ] in unstressed (but not as centralized)
    - Open vowels [ɛ, ɔ] very clear in stressed position

    GEOGRAPHICAL AND CULTURAL CONTEXT:
    -----------------------------------
    1. REGION:
       - Covers: Évora, Beja, Portalegre districts
       - Interior Alentejo (not coast - that's more Algarve-influenced)
       - Vast agricultural plains ("planície")
       - Low population density, rural character
       - Hot, dry climate (influences slow tempo?)

    2. TRADITIONAL ECONOMY:
       - Agriculture (wheat, cork, olives, wine)
       - Pastoralism (sheep, cattle)
       - Rural, traditional lifestyle
       - Seasonal rhythms, slow pace of life

    3. CULTURAL ASSOCIATIONS:
       - "Modas" (traditional Alentejo songs) - use dialect prosody
       - "Cante alentejano" (polyphonic singing) - UNESCO heritage
       - Rural traditions, festivals
       - Strong regional identity and pride
       - Resistance to outside influence (political history)

    SOCIOLINGUISTIC PROFILE:
    ------------------------
    1. STIGMA AND PRIDE:
       - STIGMA: Often mocked by other Portuguese
         * "Slow" = lazy, backward, unintelligent (stereotype)
         * Urban Portuguese find it comical
         * Comedy shows exaggerate features
       - PRIDE: Strong regional identity
         * Seen as authentic, traditional, honest
         * Connected to land and heritage
         * Cultural prestige (music, poetry)
         * Resistance to standardization

    2. CLASS AND AGE:
       - Working class, rural: Strong Alentejano features
       - Middle class, urban (Évora): More standard, but retain prosody
       - Older speakers: Most extreme features
       - Younger speakers: Influenced by Lisbon, but prosody remains
       - PERSISTENCE: Prosody very resistant to change

    3. MEDIA REPRESENTATION:
       - Folk music: Authentic Alentejano
       - Comedy: Exaggerated stereotypes (often offensive)
       - Literature: Regional novels use dialect
       - Film: Character actors use Alentejano for rural roles
       - News/formal: Never (Lisbon standard only)

    HISTORICAL DEVELOPMENT:
    -----------------------
    - Roman period: Alentejo = breadbasket of Lusitania
    - Moorish period (711-1249): Long Arabic influence
      * Later reconquest than north
      * Arabic substrate in lexicon, place names
      * Possible prosodic influence?
    - Medieval: Depopulated after reconquest, resettled from north
    - Modern: Isolation preserved archaic features
    - 20th c.: Political significance (leftist stronghold)
    - Today: Depopulation, aging, but dialect persists

    ARCHAIC FEATURES PRESERVED:
    ---------------------------
    - Some lexical items lost elsewhere
    - Morphological forms (verb conjugations)
    - Prosodic patterns may reflect older Portuguese
    - Less influence from Lisbon innovations

    PHONOLOGICAL PROCESSES:
    -----------------------
    1. /d/ DELETION CASCADE:
       /d/ → [ð] → ∅ → compensatory vowel lengthening
       "comida" /koˈmidɐ/ → [kuˈmiðɐ] → [kuˈmiɐ] → [kuˈmiː]

    2. HIATUS RESOLUTION:
       After /d/ deletion, hiatus often resolved by:
       - Vowel lengthening: /i.a/ → [iː]
       - Diphthongization: /e.u/ → [ew]
       - Glide insertion: /a.i/ → [aj]

    3. COMPENSATORY LENGTHENING:
       Deleted consonants often leave vowel length
       "nada" /ˈnadɐ/ → [ˈnaː] (long vowel compensates)

    COMPARISON WITH ALGARVE:
    ------------------------
    Feature              | Alentejo       | Algarve
    ---------------------|----------------|------------------
    Tempo               | Very slow      | Moderate
    Intonation          | Very melodic   | Less melodic
    /d/ deletion        | Extensive      | Moderate
    Tourism influence   | Minimal        | Heavy
    Arabic substrate    | Lexical        | Lexical + some phonology
    Regional identity   | Very strong    | Diluted by tourism

    COMPARISON WITH LISBON:
    -----------------------
    Feature              | Alentejo       | Lisbon
    ---------------------|----------------|------------------
    Tempo               | Very slow      | Fast
    Vowel reduction     | Less           | Heavy
    /d/ deletion        | Complete (∅)   | Partial ([ð])
    <ei> realization    | [e]            | [ɐj] ~ [aj]
    Prestige            | Regional       | National
    Melodic quality     | Extreme        | Reduced

    LINGUISTIC CURIOSITIES:
    -----------------------
    1. "TEMPO ALENTEJANO":
       - Expression: "devagar como um alentejano"
       - "Slowly like an Alentejo person"
       - Speed is THE defining feature

    2. MUSICAL PARALLELISM:
       - Speech prosody parallels traditional singing
       - Modas use speech-like melodic patterns
       - Cante alentejano uses dialect intonation
       - Hard to separate speech from song

    3. COMPENSATORY LENGTHENING:
       - Unusually extensive in Portuguese
       - Deleted consonants preserved as vowel length
       - Creates quasi-phonemic length distinction

    EXAMPLES WITH FULL PROSODIC TRANSCRIPTION:
    -------------------------------------------
    1. "Não sei nada" (I don't know anything)
       - Standard: [nɐ̃w sɐj ˈnadɐ] (fast, clipped)
       - Alentejano: [ˈnɐ̃ːw ˌsɐːj ˈnaːː] (slow, drawn out, melodic)

    2. "Está tudo bem" (Everything is fine)
       - Standard: [ʃˈta ˈtudu bɐ̃j] (rapid)
       - Alentejano: [ʃˈtaː ˈtuːu ˈbẽːj] (slow, vowels lengthened)

    FUTURE OUTLOOK:
    ---------------
    - Rural depopulation threatens dialect
    - Young people moving to Lisbon
    - But prosody very persistent (identity marker)
    - Cultural prestige (music) helps preservation
    - Tourism in some areas (Évora) bringing change
    - Academic interest in documentation
    - May survive in modified form in urban Évora

    RESEARCH AND DOCUMENTATION:
    ---------------------------
    - Extensively documented in Portuguese dialectology
    - Featured in sociolinguistic studies
    - Recordings in music archives
    - Literature: Regional novels by Alentejo authors
    - Ongoing documentation projects
    """

    def __init__(self, **kwargs):
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-PT-x-alentejo"

        if "INTERVOCALIC_CHAR2PHONEMES" not in kwargs:
            kwargs["INTERVOCALIC_CHAR2PHONEMES"] = {
                **AO1990.INTERVOCALIC_CHAR2PHONEMES,
                "s": "z",
                "d": "ː",
            }

        if "DIPHTHONG2IPA" not in kwargs:
            kwargs["DIPHTHONG2IPA"] = {
                **AO1990.DIPHTHONG2IPA,
                # lengthen nasal diphthongs
                "ão": "ɐ̃ːw",
                "õe": "õːj",
                "ãe": "ɐ̃ːj",
                "em": "ẽːj",
            }

        # Paragoge em i, nos verbos no infinitivo. Ex: fazêri (fazer)
        # TODO - add END_OF_WORD_CHAR2PHONEMES
        # r -> ri
        super().__init__(**kwargs)


class AlgarvePortuguese(SouthernPortuguese):
    """
    Algarve Portuguese (Algarvio) phonological inventory.

    LINGUISTIC OVERVIEW:
    --------------------
    Algarvio, the Portuguese variety of the Algarve (Portugal's southernmost
    region), represents a transitional dialect influenced by multiple factors:
    prolonged Arabic rule, proximity to Andalusian Spanish, maritime trade,
    and modern mass tourism. While sharing the Southern Portuguese base,
    Algarvio has distinctive features and is undergoing rapid change due to
    tourism-driven linguistic contact.

    GEOGRAPHICAL AND HISTORICAL CONTEXT:
    ------------------------------------
    1. LOCATION:
       - Southernmost region of Portugal
       - Mediterranean climate, coastal orientation
       - Border with Spain (Andalusia) to the east
       - Atlantic coast to the south and west

    2. HISTORICAL SIGNIFICANCE:
       - "Al-Gharb" (Arabic: "the West") - origin of name "Algarve"
       - Under Moorish rule 711-1249 (longest in Portugal)
       - Last Portuguese territory reconquered (1249)
       - Strategic maritime position (Age of Discovery)
       - Fishing and agriculture (traditional economy)
       - Tourism boom (1960s-present) - massive change

    3. MODERN CHARACTER:
       - Mass tourism destination (beaches, golf, resorts)
       - Large expatriate community (British, German, etc.)
       - Seasonal population influx
       - Coastal vs. interior division
       - Economic transformation from primary to tertiary sector

    PHONOLOGICAL FEATURES:
    ----------------------
    1. SOUTHERN BASE (from SouthernPortuguese):
       - /ej/ → [e] monophthongization
         * "primeiro" [pɾiˈmeɾu]
         * "feito" [ˈfetu]
       - /ow/ → [o] monophthongization
         * "ouro" [ˈoɾu]
       - Intervocalic /d/ deletion (but less than Alentejo)
         * "nada" [ˈnaɐ] ~ [ˈnaðɐ] (variable)

    2. ARABIC/MOZARABIC SUBSTRATE:
       - Extensive Arabic loanwords (especially place names)
       - Possible prosodic influence (rhythm patterns)
       - Some phonological patterns:
         * Pharyngeal articulation in some loanwords
         * Emphasis (velarization) in Arabic loans
       - Examples: "Albufeira," "Alcoutim," "Alvor" (al- = Arabic article)

    3. ANDALUSIAN SPANISH CONTACT:
       - Border region (eastern Algarve near Ayamonte)
       - Some Spanish phonological features:
         * Seseo-like patterns (s/θ merger - but Spanish not Portuguese)
         * Aspiration of final /s/ in some speakers
         * Intonation patterns similar to Andalusian
       - Lexical borrowing from Spanish
       - Code-switching in border towns

    4. PROSODIC FEATURES:
       - Less melodic than Alentejo
       - Moderate tempo (not as slow as Alentejo)
       - Some "singing" quality but less extreme
       - Coastal areas: Faster, more clipped
       - Interior (Serra): More traditional, slower

    REGIONAL VARIATION:
    -------------------
    1. COASTAL ALGARVE (Litoral):
       - Tourism-influenced, more standard Portuguese
       - Contact with foreign languages (English, German)
       - Younger speakers: Lisbon-influenced
       - Service industry: Need for standard Portuguese
       - Traditional features declining rapidly
       - "Algarve de plástico" (plastic Algarve) - criticism

    2. INTERIOR ALGARVE (Barrocal & Serra):
       - More conservative, traditional features
       - Less tourism impact
       - Agricultural communities
       - Preserves archaic vocabulary and pronunciation
       - Similar to Alentejo in some respects
       - Depopulation threatening dialect

    3. EASTERN ALGARVE (Border):
       - Spanish influence strongest
       - Bilingualism not uncommon
       - Mixed phonological features
       - Trade and family ties across border

    TOURISM IMPACT (Critical Factor):
    ----------------------------------
    1. LINGUISTIC CONSEQUENCES:
       - Massive exposure to foreign languages
       - English loanwords in hospitality vocabulary
       - Pressure toward "neutral" Portuguese (intelligibility)
       - Young people in tourism: Standard Portuguese
       - Code-switching: Portuguese/English/German
       - Traditional dialect stigmatized as "rural"

    2. GENERATIONAL SHIFT:
       - Older speakers (60+): Strong Algarvio features
       - Middle-aged (30-60): Mixed (tourism workers vs. traditional)
       - Young speakers (<30): Mostly standard with some prosody
       - Children in coastal areas: Lisbon-influenced
       - Interior youth: Emigrating to coast or Lisbon

    3. SOCIAL STRATIFICATION:
       - Tourism workers: Standard Portuguese (job requirement)
       - Traditional sectors (fishing, agriculture): Algarvio
       - Urban middle class: Mixed, situation-dependent
       - Expatriate communities: Portuguese as L2, no dialect acquisition

    ARABIC SUBSTRATE EVIDENCE:
    --------------------------
    1. LEXICAL:
       - Extensive place names: Albufeira, Aljezur, Alcantarilha
       - Agricultural terms: "nora" (water wheel), "açude" (dam)
       - Food/cooking: "almôndega" (meatball), "açorda" (bread soup)
       - Architecture: "açoteia" (terrace)

    2. PHONOLOGICAL (Debated):
       - Some scholars argue for Arabic prosodic influence
       - Possible pharyngeal quality in some sounds
       - But evidence is limited and controversial
       - Most Arabic features are lexical, not phonological

    3. CULTURAL:
       - Moorish architectural influence (chimneys, tiles)
       - Agricultural techniques (irrigation)
       - Cuisine (almonds, figs, Arab-origin dishes)

    COMPARISON WITH ALENTEJO:
    -------------------------
    Feature              | Algarve        | Alentejo
    ---------------------|----------------|------------------
    Tempo               | Moderate       | Very slow
    Tourism impact      | Extreme        | Minimal
    /d/ deletion        | Variable       | Categorical
    Spanish influence   | Moderate       | Minimal
    Standardization     | Advanced       | Resistant
    Regional identity   | Weakening      | Strong
    Arabic substrate    | Strong lexical | Moderate lexical

    COMPARISON WITH ANDALUSIAN SPANISH:
    -----------------------------------
    Despite proximity, Algarvio and Andalusian Spanish are clearly distinct:
    - Different vowel systems (5 vs. 5 but realized differently)
    - Portuguese nasal vowels (Spanish lacks)
    - Different sibilant systems
    - But: Some shared prosodic patterns
    - And: Heavy lexical borrowing (both directions)

    SOCIOLINGUISTIC ATTITUDES:
    --------------------------
    1. EXTERNAL PERCEPTIONS:
       - Other Portuguese: "Algarvios são diferentes" (are different)
       - Associated with tourism, beaches, foreign influence
       - Less strong regional identity than Alentejo
       - Sometimes seen as "sold out" to tourism
       - But also: Beautiful region, desirable place

    2. INTERNAL ATTITUDES:
       - Older speakers: Pride in traditional culture
       - Tourism workers: Dialect as barrier to advancement
       - Youth: Often prefer standard Portuguese
       - Interior: Resentment of coastal development
       - Mixed: Economic benefits vs. cultural loss

    3. LINGUISTIC INSECURITY:
       - Tourism creates pressure for "correct" Portuguese
       - Traditional features stigmatized in service contexts
       - But: Some tourism markets traditional culture
       - "Authentic Algarve" as marketing (selective)

    PHONOLOGICAL PROCESSES:
    -----------------------
    1. VARIABLE /d/ DELETION:
       - Less categorical than Alentejo
       - "comida" [kuˈmiðɐ] ~ [kuˈmiɐ] (both heard)
       - Depends on: Age, region, formality
       - Coastal/young: Less deletion
       - Interior/old: More deletion

    2. SIBILANT PATTERNS:
       - Generally standard Portuguese [s, z, ʃ, ʒ]
       - But some eastern areas: Andalusian influence
       - Final /s/ aspiration in some older speakers (Spanish-like)
       - "as casas" [aʰ ˈkazaʰ] (rare, stigmatized)

    3. VOWEL QUALITY:
       - Less reduction than Lisbon
       - Clearer articulation (Southern feature)
       - But coastal areas: Moving toward Lisbon norms

    LEXICAL DISTINCTIVENESS:
    ------------------------
    - Arabic loanwords (see above)
    - Maritime/fishing vocabulary
    - Traditional agriculture terms
    - Place names highly distinctive
    - Some archaisms preserved in interior

    FUTURE OUTLOOK:
    ---------------
    1. TOURISM IMPACT CONTINUING:
       - Dialect features declining in coastal areas
       - Standardization accelerating
       - Foreign language influence growing
       - Traditional culture marketed selectively

    2. INTERIOR VS. COAST DIVERGENCE:
       - Coast: Rapid change toward standard
       - Interior: Maintaining features but depopulating
       - Growing gap between two Algarves

    3. POSSIBLE OUTCOMES:
       - Coastal: Nearly complete leveling to standard
       - Interior: Preservation in isolated pockets
       - Overall: Algarvio becoming residual/vestigial
       - But: Prosodic features may persist longer
       - Tourism marketing may preserve some features superficially

    4. DOCUMENTATION URGENCY:
       - Rapid change means urgent need for documentation
       - Academic projects recording traditional speakers
       - Cultural organizations preserving vocabulary
       - But: Economic pressures work against preservation

    RESEARCH AND CULTURAL PRESERVATION:
    -----------------------------------
    - Less documented than Alentejo (less distinctive?)
    - But: Growing interest due to rapid change
    - Tourism creates some interest in "authentic" culture
    - Local museums and cultural centers
    - Academic studies of tourism impact on language
    - Endangered dialect - documentation needed

    ALGARVIO IN TOURISM CONTEXT:
    ----------------------------
    - "Authentic Algarve" marketing uses some dialect features
    - Traditional restaurants, cultural shows
    - But: Superficial, selective use
    - Real dialect seen as barrier, not asset
    - Paradox: Market tradition while eliminating it
    - English dominance in tourism areas
    """

    def __init__(self, **kwargs):
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-PT-x-algarve"
        # Inherits SouthernPortuguese features
        # Could add specific lexicon here if available
        # if "IRREGULAR_WORDS" not in kwargs:
        #     kwargs["IRREGULAR_WORDS"] = LEXICON.get_ipa_map(region="algarve")
        super().__init__(**kwargs)


class AzoreanPortuguese(EuropeanPortuguese):
    """
    Azorean Portuguese (Açoriano) phonological inventory.

    LINGUISTIC OVERVIEW:
    --------------------
    Açoriano, spoken in the Azores archipelago (nine volcanic islands in the
    mid-Atlantic), represents one of the most archaic and distinctive
    Portuguese varieties. Island isolation, diverse settlement origins, and
    conservative tendencies have preserved medieval features lost on the
    mainland while also fostering unique innovations. Each island has its own
    sub-variety, creating remarkable diversity within a small population.

    GEOGRAPHICAL AND SETTLEMENT CONTEXT:
    ------------------------------------
    1. THE AZORES ARCHIPELAGO:
       - Nine islands, three groups (Eastern, Central, Western)
       - 1,500 km from Lisbon, mid-Atlantic location
       - Settled 15th century (uninhabited before Portuguese)
       - Population ~250,000 (concentrated on São Miguel, Terceira)
       - Strategic location (historically and militarily)

    2. SETTLEMENT PATTERNS (Critical for understanding dialects):
       - Settlers from ALL regions of Portugal
       - Also: Flemings, Italians, Jews, Moors (forced converts)
       - Each island settled by different mix
       - São Miguel: Northern Portuguese + Madeiran
       - Terceira: Central Portuguese + Flemish
       - Flores/Corvo: Western Portuguese + Flemish
       - Result: Each island = different dialect mix

    3. ISOLATION EFFECTS:
       - Limited mainland contact (until 20th century)
       - Inter-island contact also limited (until recently)
       - Preserved archaic features (15th-16th century Portuguese)
       - Also: Innovation in isolation (unique changes)
       - Result: Time capsule + innovation = distinctive variety

    DEFINING ARCHAIC FEATURES:
    --------------------------
    1. DIPHTHONG PRESERVATION (Medieval Continuity):
       - /ow/ often preserved as [ow] (not monophthongized)
         * "ouro" [ˈowɾu] (Lisbon: [ˈoɾu])
         * "pouco" [ˈpowku] (Lisbon: [ˈpoku])
       - BUT: Variable by island and age
       - São Miguel: More [ow] preservation
       - Terceira: More [o] (Lisbon-like)

    2. AFFRICATE TENDENCIES:
       - Some islands preserve/develop affricates
       - <ch> → [tʃ] in some contexts (not pure [ʃ])
       - "chamar" [tʃɐˈmaɾ] ~ [ʃɐˈmaɾ] (variable)
       - Northern Portuguese influence in settlement

    3. CONSONANT PRESERVATION:
       - Less deletion than mainland
       - Intervocalic /d/ usually maintained
         * "nada" [ˈnadɐ] (not [ˈnaðɐ] or [ˈnaɐ])
       - Word-final /l/ sometimes preserved (archaic)
         * "mal" [ˈmal] (not [ˈmaw])
       - Conservative tendency overall

    DISTINCTIVE INNOVATIONS:
    ------------------------
    1. SYLLABLE-FINAL /s/ PALATALIZATION (Like Brazilian):
       - /s/ → [ʃ] in coda position (many islands)
       - "nós" [ˈnɔʃ] (like Rio, unlike Lisbon)
       - "três" [ˈtɾeʃ]
       - "estar" [ʃˈtaɾ] (with /s/ reduction)
       - INSIGHT: Independent innovation? Or archaic feature?
       - Pattern: São Miguel strongest, Terceira less consistent

    2. EXTREME VOWEL RAISING:
       - Unstressed /e, o/ raised more than mainland
       - /e/ → [i] in some contexts: "dizer" [diˈziɾ]
       - /o/ → [u] consistently: "bonito" [buˈnitu]
       - Creates potential for merger with /i, u/
       - Variable by island and speaker

    3. PROSODIC DISTINCTIVENESS:
       - "Singing" quality (melodic, wide pitch range)
       - Similar to Northern Portuguese in some ways
       - But also unique island patterns
       - Each island has characteristic intonation
       - São Miguel: Very distinctive, easily recognized

    4. NASAL VOWEL REALIZATION:
       - Variable, some islands more nasalized
       - May preserve older nasal patterns
       - "não" [ˈnɐ̃w] with strong nasalization
       - But variable by island

    INTER-ISLAND VARIATION (Remarkable Diversity):
    -----------------------------------------------
    1. EASTERN GROUP:
       São Miguel (largest island, ~140,000 people):
       - Most distinctive Azorean variety
       - Strong /s/ palatalization: [ʃ]
       - Vowel raising extreme
       - Very melodic prosody
       - Recognized instantly by other Portuguese
       - Some unique lexical items

       Santa Maria (smallest, ~5,500):
       - Similar to São Miguel but more conservative
       - Less innovation
       - Some archaic vocabulary

    2. CENTRAL GROUP:
       Terceira (~55,000):
       - More Lisbon-influenced (military base, connection)
       - Less /s/ palatalization
       - More standard-like
       - But still distinctively Azorean

       Graciosa, São Jorge, Pico, Faial:
       - Each with own sub-variety
       - Generally more conservative than Terceira
       - Pico and Faial: Whaling vocabulary (historical)
       - Less studied than major islands

    3. WESTERN GROUP:
       Flores and Corvo (most isolated):
       - Most archaic features
       - Least mainland influence
       - Smallest populations (~4,000 and ~400)
       - Some unique phonological patterns
       - Endangered due to depopulation

    PHONOLOGICAL INVENTORY:
    -----------------------
    1. CONSONANTS:
       - Generally conservative European Portuguese
       - But: /s, z/ → [ʃ, ʒ] in many contexts (innovation)
       - /ɾ/ (tap) and /ʁ/ (uvular/fricative) distinguished
       - Some islands: More trilled [r] (archaic)
       - Palatals /ʎ, ɲ/ well preserved

    2. VOWELS:
       - Oral: /i, e, ɛ, a, ɔ, o, u/ (7-vowel system stressed)
       - Unstressed: Extreme reduction (beyond Lisbon?)
       - Or: Less reduction (varies by island!)
       - Nasal: /ĩ, ẽ, ɐ̃, õ, ũ/
       - Variable realization of unstressed vowels

    3. DIPHTHONGS:
       - More than mainland in some cases
       - /ow/ preservation creates extra diphthong
       - Also: New diphthongs from vowel sequences

    SUBSTRATE AND CONTACT INFLUENCES:
    ----------------------------------
    1. FLEMISH SETTLEMENT:
       - Islands: Terceira, Flores, Corvo
       - Possible phonological influence (debated)
       - Lexical borrowings (limited)
       - Place names: Flamengos (Flemish area)

    2. MAINLAND DIVERSITY:
       - Mixed settlers brought different dialects
       - Created unique blend on each island
       - Northern + Southern + Central features
       - Leveled in unique ways

    3. ISOLATION = PRESERVATION:
       - Limited contact preserved 15th-16th c. features
       - Also: Prevented Lisbon innovations from spreading
       - Result: Different evolutionary path

    SOCIOLINGUISTIC PROFILE:
    ------------------------
    1. IDENTITY:
       - STRONG Azorean identity (distinct from mainland)
       - "Açorianos" vs. "Continentais" (mainlanders)
       - Dialect = major identity marker
       - Pride in distinctiveness
       - But also: Some linguistic insecurity

    2. MAINLAND ATTITUDES:
       - Often mocked by mainlanders
       - Seen as "backward," "rural," "funny"
       - Comedy sketches exaggerate features
       - Stereotype: Simple island folk
       - But: Also admired (authentic, traditional)

    3. EMIGRATION IMPACT:
       - Massive emigration (USA, Canada, Brazil)
       - Azorean communities worldwide
       - Dialect preserved in diaspora
       - But: Second generation often loses it
       - USA: "Portuguese" often = Azorean Portuguese

    4. STANDARDIZATION PRESSURE:
       - Education: Lisbon standard taught
       - Media: Mainland Portuguese dominant
       - Young people: Moving toward standard
       - But: Strong resistance (identity)
       - Features persist even in educated speakers

    AZOREAN PORTUGUESE IN NORTH AMERICA:
    -------------------------------------
    - Large communities: Massachusetts, California, Rhode Island, Ontario
    - Preserved archaic features from emigration era
    - But: English influence, code-switching
    - Second generation: Often understands but doesn't speak
    - Third generation: Usually lost
    - Heritage language classes: Teaching standard, not Azorean
    - Result: Dialect dying in diaspora

    COMPARISON WITH MAINLAND:
    -------------------------
    Feature              | Azores         | Mainland (Lisbon)
    ---------------------|----------------|-------------------
    /ow/ in <ou>         | [ow] ~ [o]     | [o]
    Final /s/            | [ʃ] (variable) | [ʃ]
    Intervocalic /d/     | [d] ~ [ð]      | [ð]
    Vowel reduction      | Variable       | Heavy
    Prosody             | Very melodic   | Reduced melody
    Archaisms           | Many           | Few
    Innovation          | Isolated       | Lisbon-driven

    COMPARISON WITH MADEIRA:
    ------------------------
    Feature              | Azores         | Madeira
    ---------------------|----------------|------------------
    Settlement          | 15th c., diverse| 15th c., southern
    /s/ palatalization  | Common         | Less common
    Prosody             | Very melodic   | Melodic
    Standardization     | Resistant      | More advanced
    Tourism impact      | Growing        | Heavy

    EXAMPLES BY ISLAND:
    -------------------
    "Os homens estão a falar" (The men are talking)

    São Miguel: [uʃ ˈõmẽjʃ ʃˈtɐ̃w ɐ fɐˈlaɾ]
    - Strong [ʃ] for /s/
    - Extreme reduction
    - Very melodic

    Terceira: [uʃ ˈomẽjʃ ʃˈtɐ̃w ɐ fɐˈlaɾ]
    - Less extreme
    - More like Lisbon

    Flores: [ow ˈomẽjʃ iʃˈtɐ̃w a faˈlaɾ]
    - More conservative
    - Less reduction
    - Archaic features

    CURRENT SITUATION AND FUTURE:
    ------------------------------
    1. VITALITY:
       - Still spoken by all age groups
       - But: Young people more standard-influenced
       - Education and media = Lisbon norms
       - Emigration removes speakers
       - Tourism bringing mainland contact

    2. CHANGE PATTERNS:
       - Prosody: Most resistant (persists longest)
       - Lexicon: Being replaced by standard
       - Phonology: Variable, age-graded change
       - Some features strengthening (identity marker)
       - Others weakening (standardization)

    3. DOCUMENTATION:
       - Growing academic interest
       - Recording projects on all islands
       - Dialect atlases published
       - Cultural organizations preserving
       - But: Rapid change necessitates urgency

    4. PROSPECTS:
       - Will persist in modified form
       - Prosody likely to remain distinctive
       - Some phonological features maintained
       - But: Leveling toward standard ongoing
       - Strong identity may slow change
       - Tourism may commodify dialect

    CULTURAL SIGNIFICANCE:
    ----------------------
    - Music: Chamarrita (traditional song/dance) uses dialect
    - Literature: Azorean authors write in dialect
    - Festivals: Espírito Santo (religious tradition) - dialect context
    - Identity: Language = culture = Azorean-ness
    - UNESCO: Intangible cultural heritage interest

    RESEARCH IMPORTANCE:
    --------------------
    - Window into 15th-16th century Portuguese
    - Archaic features document language history
    - Island isolation = natural laboratory
    - Each island = different experiment
    - Comparative dialectology opportunities
    - Emigration studies (language contact)
    """

    def __init__(self, **kwargs):
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-PT-x-azores"

        # Azorean shares European base but with distinctive features
        if "DIPHTHONG2IPA" not in kwargs:
            # Some islands preserve /ow/
            kwargs["DIPHTHONG2IPA"] = {
                **AO1990.DIPHTHONG2IPA,
                "ou": "ow",  # Preservation (unlike Lisbon [o])
                "ei": "ɐj",  # Like Central Portuguese
            }

        # Less intervocalic fricativization than mainland
        if "INTERVOCALIC_CHAR2PHONEMES" not in kwargs:
            kwargs["INTERVOCALIC_CHAR2PHONEMES"] = {
                **AO1990.INTERVOCALIC_CHAR2PHONEMES,
                "s": "z",
                # Less /d/ fricativization than mainland
                # "d": "ð" - more often [d] preserved
                "d": "d"
            }

        # Could add Azorean-specific lexicon if available
        # if "IRREGULAR_WORDS" not in kwargs:
        #     kwargs["IRREGULAR_WORDS"] = LEXICON.get_ipa_map(region="azores")

        super().__init__(**kwargs)


class MadeiraPortuguese(EuropeanPortuguese):
    """
    Madeiran Portuguese (Madeirense) phonological inventory.

    LINGUISTIC OVERVIEW:
    --------------------
    Madeirense, spoken on the Madeira archipelago (Madeira and Porto Santo
    islands), is a distinctive Atlantic Portuguese variety sharing some
    features with Azorean but with its own unique character. Settled earlier
    and from different regions than the Azores, Madeira developed a variety
    influenced by southern Portuguese dialects, subsequent Azorean migration,
    and heavy tourism. The dialect preserves some archaic features while also
    showing extensive standardization.

    GEOGRAPHICAL AND HISTORICAL CONTEXT:
    ------------------------------------
    1. MADEIRA ARCHIPELAGO:
       - Madeira Island (main island, ~260,000 people)
       - Porto Santo (smaller, ~5,000 people)
       - Desertas and Selvagens (uninhabited)
       - 1,000 km southwest of Lisbon
       - Discovered/settled 1419-1420 (earlier than Azores)

    2. SETTLEMENT HISTORY (Different from Azores):
       - PRIMARY settlers: Southern Portugal (Algarve, Alentejo)
       - Also: Northern Portuguese (Minho)
       - Later: Azorean migrants (adding Azorean features)
       - Some: Genoese, Flemish, enslaved Africans
       - Result: Predominantly Southern base + mixed influences

    3. ECONOMIC HISTORY:
       - Sugar production (15th-16th c.) - wealth and contact
       - Wine trade (Madeira wine) - international connections
       - Emigration (Brazil, Venezuela, South Africa)
       - Tourism boom (20th c.) - massive change
       - Today: Tourism-dependent economy

    PHONOLOGICAL FEATURES:
    ----------------------
    1. SOUTHERN PORTUGUESE BASE:
       - Shares features with mainland Southern dialects
       - /ej/ → [e] monophthongization (variable)
         * "primeiro" [pɾiˈmeɾu] ~ [pɾiˈmɐjɾu]
         * More [e] in traditional speech
         * More [ɐj] in Funchal (capital, Lisbon-influenced)

       - /ow/ → [o] monophthongization
         * "ouro" [ˈoɾu]
         * "pouco" [ˈpoku]
         * More consistent than /ej/

    2. INTERVOCALIC CONSONANTS:
       - Variable /d/ treatment
       - Less deletion than mainland Southern
       - More like Central Portuguese
       - "nada" [ˈnadɐ] ~ [ˈnaðɐ] (not usually deleted)
       - Conservative in this respect

    3. SIBILANT PATTERNS:
       - Generally standard European [s, z, ʃ, ʒ]
       - Less palatalization than Azores
       - Final /s/ → [ʃ] (standard European pattern)
       - "nós" [ˈnɔʃ]
       - No special innovations here

    4. VOWEL SYSTEM:
       - Moderate reduction (between Southern and Lisbon)
       - Unstressed /a/ → [ɐ]
       - Unstressed /e/ → [ɨ] (but less extreme than Lisbon)
       - Unstressed /o/ → [u]
       - Stressed vowels: Clear articulation
       - Open vowels [ɛ, ɔ] well-maintained

    5. RHOTIC CONSONANTS:
       - Generally European pattern
       - Strong R: /ʁ/ (uvular fricative) in Funchal
       - Rural areas: May use trill [r] (archaic)
       - Tap [ɾ] in intervocalic position
       - Variable by region and age

    PROSODIC CHARACTERISTICS:
    -------------------------
    1. MELODIC QUALITY:
       - "Singing" intonation (similar to Azorean)
       - But: Less extreme than São Miguel (Azores)
       - Wide pitch range
       - Final syllable lengthening
       - Characteristic rising-falling patterns

    2. TEMPO:
       - Moderate (not as slow as Alentejo)
       - Faster than Azores generally
       - Urban (Funchal): Approaching Lisbon speed
       - Rural: More deliberate, traditional

    3. RHYTHM:
       - Tends toward stress-timing
       - Similar to European Portuguese generally
       - But with distinctive island melody

    REGIONAL VARIATION:
    -------------------
    1. FUNCHAL (Capital, South Coast):
       - Population ~110,000
       - Most Lisbon-influenced
       - Tourism center
       - More standard Portuguese
       - But: Prosody still distinctive
       - Young speakers: Very Lisbon-like
       - Service workers: "Neutral" Portuguese

    2. NORTH COAST (Porto Moniz, São Vicente):
       - More traditional features
       - Less tourism exposure
       - Agricultural communities
       - Preserves archaic vocabulary
       - More distinctive pronunciation
       - But: Depopulation threatening

    3. INTERIOR MOUNTAINS:
       - Most conservative variety
       - Isolated villages
       - Archaic features strongest
       - Traditional agriculture
       - Aging population
       - Features rapidly declining

    4. PORTO SANTO (Second Island):
       - Small population (~5,000)
       - Own sub-variety
       - Some unique features
       - More isolated historically
       - Tourism now changing (beach resort)
       - Less documented than Madeira proper

    DISTINCTIVE MADEIRAN FEATURES:
    ------------------------------
    1. PALATALIZATION PATTERNS:
       - Some unique palatalization not found on mainland
       - /l/ → [lʲ] (palatalized) in some contexts
       - Variable and declining
       - Mostly in older, rural speakers

    2. LEXICAL DISTINCTIVENESS:
       - Many unique words (especially agriculture, fishing)
       - African substrate vocabulary (historical enslaved population)
       - Some Arabic loanwords (via Southern Portuguese)
       - Maritime vocabulary (sailing, fishing)
       - Sugar production terms (historical)

    3. SUBSTRATE INFLUENCES:
       - African (Bantu, West African): Limited but present
         * Some lexical items
         * Possible prosodic influence (debated)
       - Genoese: Very limited (mostly place names)
       - Azorean: Later influence from migration

    TOURISM IMPACT (Critical Factor):
    ----------------------------------
    1. MASSIVE STANDARDIZATION:
       - Tourism industry since 1960s
       - Even more developed than Algarve
       - Year-round destination (mild climate)
       - International exposure (British especially)
       - Pressure for "correct" Portuguese

    2. LINGUISTIC CONSEQUENCES:
       - Traditional dialect declining rapidly
       - Funchal: Nearly standard Portuguese
       - Rural areas: Maintaining features but depopulating
       - Young people: Mostly standard
       - Service sector: English/Portuguese bilingualism

    3. GENERATIONAL SHIFT:
       - Elderly (70+): Strong Madeirense features
       - Middle-aged (40-70): Mixed, situation-dependent
       - Young (under 40): Mostly standard + prosody
       - Children: Standard with some prosodic traces
       - Clear age-grading toward standardization

    SOCIOLINGUISTIC PROFILE:
    ------------------------
    1. IDENTITY:
       - Strong Madeiran identity (vs. mainland)
       - "Madeirenses" distinct from "Continentais"
       - But: Less linguistically distinct than Azoreans
       - Identity more cultural than linguistic
       - Tourism has created cosmopolitan outlook

    2. ATTITUDES:
       - EXTERNAL (Mainland Portuguese):
         * Less mocked than Azorean
         * Seen as more "sophisticated" (tourism, wealth)
         * But still recognizably "island Portuguese"
         * Associated with tourism, beauty, wine

       - INTERNAL (Madeirans):
         * Some pride in traditional speech
         * But: Linguistic insecurity common
         * Standard Portuguese = prestige
         * Traditional dialect = "backwards"
         * Mixed feelings about change

    3. STANDARDIZATION ACCEPTANCE:
       - More acceptance than Azores
       - Economic incentives (tourism jobs)
       - Education system: Lisbon norms
       - Media: Mainland Portuguese dominant
       - Less resistance than other dialects

    COMPARISON WITH AZORES:
    -----------------------
    Feature              | Madeira        | Azores
    ---------------------|----------------|------------------
    Settlement base      | Southern PT    | Mixed all regions
    /s/ palatalization  | Standard EP    | Innovative [ʃ]
    /ej/ realization    | [e] ~ [ɐj]     | Variable
    Vowel reduction      | Moderate       | Variable/extreme
    Prosody             | Melodic        | Very melodic
    Standardization     | Advanced       | Moderate
    Tourism impact      | Extreme        | Growing
    Identity marker     | Weaker         | Stronger
    Documentation       | Moderate       | Better

    COMPARISON WITH MAINLAND SOUTHERN:
    ----------------------------------
    Feature              | Madeira        | Alentejo/Algarve
    ---------------------|----------------|-------------------
    Tempo               | Moderate       | Slow (Alentejo)
    /d/ deletion        | Rare           | Common
    Tourism influence   | Extreme        | Heavy (Algarve)
    Isolation effects   | Historical     | Geographic
    Archaisms           | Some           | Many (Alentejo)

    EMIGRATION AND DIASPORA:
    ------------------------
    1. DESTINATIONS:
       - Venezuela (historically large community)
       - South Africa (significant population)
       - Brazil (especially São Paulo)
       - United Kingdom (recent, service workers)
       - Also: Angola, Mozambique (colonial period)

    2. DIASPORA VARIETIES:
       - Venezuela: Preserved early 20th c. features
       - South Africa: Mixed with local Portuguese
       - Brazil: Mostly assimilated to Brazilian
       - UK: Recent migrants, L2 English influence
       - Generally: Second generation loses dialect

    PHONOLOGICAL PROCESSES:
    -----------------------
    1. VARIABLE MONOPHTHONGIZATION:
       - /ej/ → [e] in traditional speech
       - But /ej/ → [ɐj] in standard-influenced speech
       - Age and region dependent
       - Ongoing change toward [ɐj]

    2. SIBILANT PATTERNS:
       - Standard European pattern maintained
       - /s/ → [z] intervocalic voicing
       - /s/ → [ʃ] before voiceless consonants
       - No special innovations

    3. VOWEL REDUCTION:
       - Less than Lisbon, more than Southern mainland
       - Intermediate pattern
       - Unstressed vowels reduced but clear

    LEXICAL CHARACTERISTICS:
    ------------------------
    - Sugar production vocabulary (historical)
    - Wine-making terminology (Madeira wine)
    - Unique agricultural terms (levadas - irrigation channels)
    - Maritime vocabulary
    - Some African-origin words
    - Tourism vocabulary (modern loans)

    CURRENT SITUATION:
    ------------------
    1. VITALITY:
       - Declining rapidly in urban areas
       - Maintained in rural areas (but depopulating)
       - Prosody most resistant feature
       - Lexicon being replaced fastest
       - Phonology variable, age-graded

    2. DOCUMENTATION:
       - Less studied than Azorean
       - Some academic work exists
       - Cultural organizations preserving
       - But: Limited compared to need
       - Urgent documentation needed

    3. FUTURE PROSPECTS:
       - Urban: Near-complete standardization likely
       - Rural: Possible preservation in pockets
       - Prosody: Will remain distinctive
       - Most phonological features: Will level
       - Overall: Becoming vestigial

    CULTURAL CONTEXT:
    -----------------
    - Traditional music: Uses dialect features
    - Local festivals: Context for traditional speech
    - Literature: Some authors write in dialect
    - Tourism marketing: Selective use of "traditional"
    - But: Economic pressure against maintenance

    EDUCATIONAL CONTEXT:
    --------------------
    - Schools: Lisbon standard exclusively
    - No dialect teaching or maintenance
    - Standard Portuguese = academic success
    - Traditional speech = stigmatized in school
    - Teachers often from mainland
    - Result: Strong pressure toward standardization

    MEDIA REPRESENTATION:
    ---------------------
    - Local media: Mainland Portuguese
    - Tourism materials: Standard Portuguese/English
    - Cultural programs: Sometimes feature traditional speech
    - National media: Rare Madeiran speakers
    - Overall: Limited dialect visibility

    SUMMARY:
    --------
    Madeiran Portuguese represents a once-distinctive Atlantic variety now
    rapidly converging with mainland standard Portuguese due to tourism,
    education, and economic integration. While prosodic features persist and
    some elderly speakers maintain traditional phonology, the trajectory is
    clear: standardization is advanced and accelerating. Unlike Azorean,
    which maintains stronger resistance through identity, Madeiran is more
    accepting of standard norms, partly due to economic incentives and less
    distinctive features to begin with. Documentation is urgently needed
    before traditional varieties disappear entirely.
    """

    def __init__(self, **kwargs):
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-PT-x-madeira"

        # Madeira has Southern Portuguese base with some distinctive features
        if "DIPHTHONG2IPA" not in kwargs:
            kwargs["DIPHTHONG2IPA"] = {
                **AO1990.DIPHTHONG2IPA,
                "ou": "o",  # Monophthongization like Central/Southern
                "ei": "e",  # Variable: [e] in traditional, [ɐj] in standard-influenced
            }

        if "INTERVOCALIC_CHAR2PHONEMES" not in kwargs:
            kwargs["INTERVOCALIC_CHAR2PHONEMES"] = {
                **AO1990.INTERVOCALIC_CHAR2PHONEMES,
                "s": "z",
                # Less /d/ deletion than Southern mainland
                "d": "ð",  # Fricativization but not deletion
            }

        # Could add Madeiran-specific lexicon if available
        # if "IRREGULAR_WORDS" not in kwargs:
        #     kwargs["IRREGULAR_WORDS"] = LEXICON.get_ipa_map(region="madeira")

        super().__init__(**kwargs)


# =============================================================================
# BRAZILIAN PORTUGUESE (pt-BR)
# =============================================================================

class BrazilianPortuguese(DialectInventory):
    """
    Brazilian Portuguese phonological inventory.

    MAJOR DIFFERENCES FROM EUROPEAN:
    --------------------------------
    1. LESS VOWEL REDUCTION: Unstressed vowels maintain quality
       - European: "pedir" [pɨˈdiɾ] vs. Brazilian: "pedir" [peˈdʒiɾ]
       - European: "casa" [ˈkazɐ] vs. Brazilian: "casa" [ˈkaza]
       - /a/ stays [a] (not reduced to [ɐ])
       - /e/ stays [e] (not reduced to [ɨ])
       - /o/ stays [o] (not reduced to [u])

    2. PALATALIZATION: /t, d/ → [tʃ, dʒ] before [i]
       - "tia" [ˈtʃiɐ] (European: [ˈtiɐ])
       - "dia" [ˈdʒiɐ] (European: [ˈdiɐ])
       - "noite" [ˈnojtʃi] (European: [ˈnojtɨ])
       - "grande" [ˈɡɾɐ̃dʒi] (European: [ˈɡɾɐ̃dɨ])

    3. L-VOCALIZATION: Syllable-final /l/ → [w]
       - "Brasil" [bɾaˈziw] (European: [bɾɐˈziɫ])
       - "mal" [ˈmaw] (European: [ˈmaɫ])
       - "sol" [ˈsɔw] (European: [ˈsɔɫ])
       - Creates new diphthongs: -al, -el, -il, -ol, -ul

    4. DIFFERENT R SOUNDS: Regional variation
       - São Paulo/South: [ɾ] (tap) and [x]/[h] (velar/glottal fricative)
       - Rio: [ʁ] (uvular) and [x]/[h]
       - Rural areas: May preserve alveolar trill [r]
       - "carro" [ˈkaxu] (SP) vs. [ˈkaʁu] (Rio) vs. [ˈkaru] (rural)

    5. FINAL /s/: Stays [s], doesn't palatalize
       - "três" [ˈtɾes] (European: [ˈtɾeʃ])
       - "nós" [ˈnɔs] (European: [ˈnɔʃ])

    6. LESS NASAL: Nasal vowels less nasalized than European
       - Nasalization is lighter
       - May have shorter nasal quality

    7. OPEN VOWELS IN STRESSED POSITION:
       - Greater tendency toward open vowels [ɛ, ɔ] when stressed
       - "café" [kaˈfɛ]
       - "avô" [aˈvɔ]
    """

    def __init__(self, **kwargs):
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-BR"
        if "DEFAULT_CHAR2PHONEMES" not in kwargs:
            kwargs["DEFAULT_CHAR2PHONEMES"] = {
                **AO1990.DEFAULT_CHAR2PHONEMES,
                # VOWELS - LESS REDUCTION IN BRAZILIAN
                "a": "a",  # DIVERGENCE: stays [a], not [ɐ]
                "â": "a",  # DIVERGENCE: stays [a], not [ɐ]
                "e": "e",  # DIVERGENCE: stays [e], not [ɨ]
                "o": "o",  # DIVERGENCE: stays [o], not [u]
                # CONSONANTS
                "r": "ɾ",  # DIVERGENCE: tap, strong R is [h]
            }
        if "CODA_CHAR2PHONEMES" not in kwargs:
            kwargs["CODA_CHAR2PHONEMES"] = {
                "l": "w",
            }
        if "WORD_FINAL_CHAR2PHONEMES" not in kwargs:
            kwargs["WORD_FINAL_CHAR2PHONEMES"] = {
                "z": "s",
                "l": "w", # already covered by CODA_CHAR2PHONEMES
            }
        if "DIGRAPH2IPA" not in kwargs:
            kwargs["DIGRAPH2IPA"] = {
                **AO1990.DIGRAPH2IPA,
                "rr": "h",  # DIVERGENCE: Brazilian uses [h] or [x] instead of [ʁ] - override per subdialect
                "di": "dʒi",  # d palatalization before [i]
                "ti": "tʃi",  # d palatalization before [i]
            }
        if "IRREGULAR_WORDS" not in kwargs:
            kwargs["IRREGULAR_WORDS"] = LEXICON.get_ipa_map(region="rjx")
        super().__init__(**kwargs)


class RioJaneiroPortuguese(BrazilianPortuguese):
    """
    Rio de Janeiro Portuguese (Carioca) phonological inventory.

    LINGUISTIC OVERVIEW:
    --------------------
    Carioca Portuguese, spoken in Rio de Janeiro city and state, represents
    one of the most distinctive and internationally recognized Brazilian
    Portuguese varieties. Historically, Rio was Brazil's capital (1763-1960),
    giving Carioca speech prestige and national influence. The accent is
    characterized by unique phonological innovations, especially in sibilant
    and rhotic articulation, and is instantly recognizable to other
    Portuguese speakers.

    THE "CARIOCA SOUND":
    --------------------
    Carioca is perhaps the most phonologically innovative Brazilian dialect,
    with several features that distinguish it sharply from other varieties.

    DEFINING FEATURES:
    ------------------
    1. PALATALIZED SIBILANTS: /s/ → [ʃ] / _# (syllable-final)
       - MOST DISTINCTIVE Carioca feature
       - Final /s/ becomes [ʃ] (not [s] as in São Paulo)
       - "nós" [ˈnɔʃ] (SP: [ˈnɔs])
       - "três" [ˈtɾeʃ] (SP: [ˈtɾes])
       - "as casas" [aʃ ˈkazɐʃ] (SP: [as ˈkazas])
       - Before voiceless consonants: "está" [iʃˈta]
       - Before voiced consonants: "mesmo" [ˈmeʒmu]
       - INSIGHT: Parallels European Portuguese, but NOT from EP influence

    2. UVULAR/PHARYNGEAL RHOTIC: /ʁ/ (strong R)
       - "carro" [ˈkaʁu] (not [ˈkaxu] as in São Paulo)
       - "rato" [ˈʁatu]
       - "terra" [ˈtɛʁɐ]
       - Articulation varies:
         * Uvular fricative [ʁ] (most common)
         * Pharyngeal fricative [ʕ] (older speakers)
         * Uvular trill [ʀ] (rare, archaic)
       - PRESTIGE: Associated with educated urban Carioca speech
       - Tap /ɾ/ remains: "caro" [ˈkaɾu] vs. "carro" [ˈkaʁu]

    3. EXTREME PALATALIZATION: /t, d/ → [tʃ, dʒ] before [i]
       - Shared with Brazilian Portuguese generally
       - But Carioca extends to more contexts
       - "tia" [ˈtʃiɐ]
       - "dia" [ˈdʒiɐ]
       - "noite" [ˈnojtʃi]
       - Before unstressed [i] from /e/: "de" [dʒi]
       - EXTENT: More palatalization than interior varieties

    4. DIPHTHONG REDUCTION IN CASUAL SPEECH:
       - /ej/ → [e]: "leite" [ˈletʃi]
       - /ow/ → [o]: "ouro" [ˈoɾu]
       - Varies by speaker and formality

    5. OPEN VOWELS:
       - Tendency toward open mid-vowels [ɛ, ɔ]
       - "escola" [iʃˈkɔlɐ] (more open than SP)
       - "festa" [ˈfɛʃtɐ]

    6. FINAL /l/ VOCALIZATION: /l/ → [w]
       - Shared Brazilian feature, but very consistent in Rio
       - "Brasil" [bɾaˈziw]
       - "mal" [ˈmaw]
       - "azul" [aˈzuw]

    PROSODIC FEATURES:
    ------------------
    - "Singing" intonation (melodic, varying pitch)
    - Characteristic rhythm (stress-timed tendency)
    - Final syllable lengthening in questions
    - Rising intonation on statements (sounds like questions)
    - Often described as "musical" or "lilting"

    SOCIOLINGUISTIC STRATIFICATION:
    -------------------------------
    1. BY GEOGRAPHY:
       - Zona Sul (South Zone): Most prestigious (Copacabana, Ipanema)
         * Most innovative features
         * Media/entertainment standard
       - Zona Norte (North Zone): More conservative
         * Less extreme sibilant palatalization
         * More traditional features
       - Baixada Fluminense (suburbs): Different again
         * Mixed features from migration

    2. BY CLASS:
       - Upper/Middle class: Strong Carioca features
         * [ʃ] for final /s/
         * [ʁ] for strong R
       - Working class: Variable
         * May use [x] or [h] for R
         * May reduce sibilant palatalization

    3. BY AGE:
       - Older speakers: [ʁ] or [ʕ] for R
       - Younger speakers: [ʁ] or moving toward [x]/[h]
       - Some features intensifying, others leveling

    HISTORICAL DEVELOPMENT:
    -----------------------
    - Colonial period: Port city, African influence (enslaved population)
    - 1763: Becomes colonial capital (was Salvador)
    - 19th c.: Portuguese royal family arrives (1808), European influence
    - Early 20th c.: Sibilant palatalization develops/spreads
    - Mid 20th c.: Golden age of Carioca as prestige variety
    - 1960: Capital moves to Brasília (Carioca prestige declines slightly)
    - Late 20th c: Bossa nova, samba internationalize Carioca sound
    - Today: Still highly prestigious, media dominance

    CULTURAL ASSOCIATIONS:
    ----------------------
    - Samba, bossa nova (musical styles)
    - Carnival (world-famous celebration)
    - Beach culture (Copacabana, Ipanema)
    - "Carioca lifestyle" (relaxed, fun-loving stereotype)
    - Media/entertainment industry
    - Telenovelas (soap operas) often use Carioca accent

    COMPARISON WITH OTHER BRAZILIAN VARIETIES:
    -------------------------------------------
    Feature              | Rio (Carioca)  | São Paulo      | Nordeste
    ---------------------|----------------|----------------|------------------
    Final /s/            | [ʃ]            | [s]            | [s]
    Strong R             | [ʁ]            | [x]/[h]        | [h]/[x]
    /t,d/ before /i/     | [tʃ, dʒ]       | [tʃ, dʒ]       | [t, d] (variable)
    Intonation          | Very melodic   | Flatter        | Very melodic
    Prestige            | High           | High           | Variable

    RECEPTION BY OTHER SPEAKERS:
    ----------------------------
    - São Paulo: Sometimes mock as affected/pretentious
    - Nordeste: Often admire as sophisticated
    - South: May find difficult to understand
    - European Portuguese: Find similarities (final [ʃ]) but still distant
    - International: Most recognizable Brazilian accent (media exposure)

    MEDIA REPRESENTATION:
    ---------------------
    - Historically THE prestige Brazilian accent
    - Rede Globo (major network) based in Rio
    - Many famous singers, actors are Cariocas
    - But São Paulo media growing (economic shift)
    - Still dominant in entertainment, declining in business/politics

    FUTURE OUTLOOK:
    ---------------
    - Economic shift to São Paulo affecting prestige
    - But cultural prestige remains strong
    - Some features spreading (sibilant palatalization)
    - Others declining (uvular R in younger speakers)
    - Media standard increasingly "neutral" (less marked Carioca)

    PHONOLOGICAL CURIOSITIES:
    -------------------------
    1. "Chiado" (the hissing sound):
       - Nickname for Carioca [ʃ] pronunciation
       - Instantly recognizable marker
       - Source of much regional humor/identity

    2. R-LESSNESS:
       - Infinitives often lose final -r in speech
       - "falar" → [faˈla] (not [faˈlaʁ])
       - "comer" → [koˈme]
       - Very stigmatized, but common in casual speech

    3. AFRICAN SUBSTRATE:
       - Possible influence from Bantu languages on prosody
       - Large African-descended population
       - Some lexical items from African languages
    """
    def __init__(self, **kwargs):
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-BR-x-rio-janeiro"

        if "DIGRAPH2IPA" not in kwargs:
            kwargs["DIGRAPH2IPA"] = {
                **AO1990.DIGRAPH2IPA,
                "rr": "h",  # DIVERGENCE: Brazilian uses [h] or [x] instead of [ʁ]
                "di": "dʒi",  # d palatalization before [i]
                "ti": "tʃi",  # d palatalization before [i]
            }
        super().__init__(**kwargs)


class SaoPauloPortuguese(BrazilianPortuguese):
    """
    São Paulo Portuguese (Paulistano/Paulista) phonological inventory.

    LINGUISTIC OVERVIEW:
    --------------------
    Paulistano (São Paulo city) and Paulista (São Paulo state) Portuguese
    represents the accent of Brazil's economic powerhouse. While Rio de
    Janeiro was historically the cultural/prestige center, São Paulo's
    massive economic growth in the 20th century made Paulistano increasingly
    influential. The accent is characterized by retroflex rhotics, alveolar
    sibilants, and distinctive prosody, and is often considered more
    "neutral" or "standard" than Carioca by Brazilians themselves.

    DEFINING FEATURES:
    ------------------
    1. RETROFLEX RHOTIC (CAIPIRA INFLUENCE): /ɾ/ → [ɻ] in coda position
       - MOST DISTINCTIVE feature of interior Paulista
       - Syllable-final /r/ becomes retroflex approximant [ɻ]
       - "porta" [ˈpɔɻtɐ] (Rio: [ˈpɔʁtɐ])
       - "carta" [ˈkaɻtɐ]
       - "mar" [ˈmaɻ]
       - Origin: Caipira (rural) dialect influence
       - Distribution: Strong in interior, variable in capital
       - Stigma: Mixed - rural/caipira associations vs. regional pride
       - Younger urban speakers: May avoid retroflex, use [ɾ] or delete

    2. ALVEOLAR SIBILANTS: /s/ stays [s] (not [ʃ])
       - MAJOR CONTRAST with Rio
       - Final /s/ remains alveolar: "nós" [ˈnɔs] (Rio: [ˈnɔʃ])
       - "três" [ˈtɾes] (Rio: [ˈtɾeʃ])
       - "as casas" [as ˈkazas] (Rio: [aʃ ˈkazɐʃ])
       - Before voiceless: "gosto" [ˈɡostu]
       - Before voiced: "mesmo" [ˈmezmu] (may voice to [z])
       - INSIGHT: More conservative than Rio in this respect

    3. VELAR/GLOTTAL RHOTIC: Strong R = [x] or [h]
       - "carro" [ˈkaxu] ~ [ˈkahu] (Rio: [ˈkaʁu])
       - "rato" [ˈxatu] ~ [ˈhatu]
       - "terra" [ˈtɛxɐ] ~ [ˈtɛhɐ]
       - [x] (velar) more in interior/formal
       - [h] (glottal) more in capital/casual
       - NEVER uvular [ʁ] like Rio
       - Tap [ɾ] maintained: "caro" [ˈkaɾu] (intervocalic)

    4. PALATALIZATION: /t, d/ → [tʃ, dʒ] before [i]
       - Standard Brazilian feature
       - "tia" [ˈtʃiɐ]
       - "dia" [ˈdʒiɐ]
       - "noite" [ˈnojtʃi]
       - Less extreme than Rio in casual speech

    5. L-VOCALIZATION: /l/ → [w] in coda
       - Standard Brazilian feature
       - "Brasil" [bɾaˈziw]
       - "mal" [ˈmaw]
       - Very consistent in all contexts

    6. VOWEL QUALITY:
       - Less extreme opening than Rio
       - Moderate [ɛ, ɔ] in stressed position
       - "festa" [ˈfɛstɐ]
       - "porta" [ˈpɔɻtɐ]

    PROSODIC FEATURES:
    ------------------
    - FLATTER intonation than Rio (less melodic)
    - Faster speech rate (especially in capital)
    - Less final syllable lengthening
    - More "monotone" (often described as more "neutral")
    - Clipped, efficient delivery
    - PERCEPTION: Sounds more businesslike, less playful than Carioca

    INTERNAL VARIATION:
    -------------------
    1. PAULISTANO (São Paulo City):
       - More "neutral" Brazilian Portuguese
       - Less retroflex (stigma of caipira)
       - Faster, urban speech patterns
       - Influenced by massive immigration (Italian, Japanese, etc.)
       - Young speakers: Avoid retroflex, use [ɾ] deletion
       - "porta" [ˈpɔɾtɐ] or [ˈpɔtɐ] (not [ˈpɔɻtɐ])

    2. PAULISTA (Interior):
       - Strong retroflex /r/ (caipira influence)
       - "porta" [ˈpɔɻtɐ]
       - More conservative features
       - Rural influence stronger
       - Regional pride in distinctive speech

    3. CAIPIRA SUBSTRATE:
       - Rural dialect of São Paulo interior
       - Source of retroflex /r/
       - Also: rhotic deletion, vowel nasalization patterns
       - Stigmatized but influential
       - Many paulistano speakers have caipira-speaking relatives

    IMMIGRATION INFLUENCE:
    ----------------------
    São Paulo received massive immigration (late 19th-mid 20th century):
    - Italian (largest group): Possible prosodic influence
    - Japanese (largest Japanese diaspora): Some phonological influence
    - Spanish: Lexical and some phonological borrowing
    - Portuguese (from Portugal): Reinforced some features
    - Arabic, German, others: Lexical influence
    - RESULT: São Paulo Portuguese has unique cosmopolitan character
    - Leveling of extreme regional features
    - Some loan phonemes (e.g., Italian /ʎ/ in loanwords)

    SOCIOLINGUISTIC STRATIFICATION:
    -------------------------------
    1. BY CLASS:
       - Upper/Middle class: Avoid retroflex, "neutral" Brazilian
       - Working class: May retain retroflex, more caipira features
       - Upward mobility: Adopt "neutral" accent

    2. BY AGE:
       - Older speakers: More retroflex, more caipira
       - Younger speakers: Avoid retroflex, more "neutral"
       - Generation gap in r-pronunciation

    3. BY REGION (within state):
       - Capital: More "neutral," less retroflex
       - Interior: More retroflex, more caipira
       - Coast (Santos area): Some carioca influence
       - Border areas: Influence from neighboring states

    ECONOMIC AND MEDIA POWER:
    --------------------------
    - São Paulo = Brazil's economic capital
    - Largest city in Southern Hemisphere
    - Financial center, business hub
    - Growing media presence (challenging Rio)
    - "Neutral" accent increasingly used in business, advertising
    - Less cultural prestige than Rio, but more economic power

    COMPARISON WITH RIO:
    --------------------
    Feature              | São Paulo      | Rio (Carioca)
    ---------------------|----------------|------------------
    Final /s/            | [s]            | [ʃ]
    Coda /r/             | [ɻ] ~ [ɾ] ~ ∅  | [ʁ]
    Strong R             | [x] ~ [h]      | [ʁ]
    Intonation          | Flat           | Melodic
    Speed               | Fast           | Moderate
    Prestige type       | Economic       | Cultural
    "Neutrality"        | More neutral   | More marked

    THE "NEUTRAL" BRAZILIAN ACCENT:
    --------------------------------
    - Paulistano increasingly seen as "neutral" or "standard" Brazilian
    - Features:
      * No retroflex
      * Alveolar sibilants (not palatal)
      * Moderate vowel quality
      * Flat intonation
      * Standard palatalization
    - Used in:
      * National newscasts
      * Corporate communications
      * Dubbing/voice acting
      * Language teaching
    - BUT: Not truly neutral - still regionally marked
    - Alternative "neutral": Brasília, Goiás (truly central)

    ATTITUDES TOWARD PAULISTANO:
    ----------------------------
    - Other Brazilians:
      * Respect economic power
      * May mock as cold, businesslike
      * Admire efficiency, modernity
      * Sometimes resent São Paulo dominance
    - Within São Paulo:
      * Pride in cosmopolitan, modern identity
      * Tension between urban/rural (caipira stigma)
      * Some nostalgia for traditional paulista speech
    - International:
      * Often taught as "standard" Brazilian
      * Seen as easier to understand (less marked)

    HISTORICAL DEVELOPMENT:
    -----------------------
    - Colonial: Bandeirantes (explorers) spread paulista features inland
    - 19th c.: Coffee boom, economic growth begins
    - Late 19th-early 20th c.: Mass immigration shapes accent
    - Mid 20th c.: Industrialization, urbanization
    - Late 20th c.: Economic dominance, media growth
    - Today: Increasingly influential as "standard"

    FUTURE OUTLOOK:
    ---------------
    - Retroflex /r/ declining in capital, stable in interior
    - "Neutral" Paulistano spreading as business standard
    - Immigration influence continuing (now from Northeast)
    - Media standard increasingly Paulistano (not Carioca)
    - But Carioca retains cultural prestige
    - Possible emergence of pan-Brazilian "neutral" accent

    RELATIONSHIP TO CAIPIRA:
    ------------------------
    Caipira = traditional rural dialect of São Paulo interior
    - Strong retroflex /r/
    - Rhotic deletion
    - Distinctive vowel system
    - Archaic features
    - Stigmatized as "hick" accent
    - But: Source of many paulista features
    - Complex relationship: pride + stigma
    - Urban speakers distance themselves
    - But many have caipira-speaking relatives
    - Influence undeniable but often denied

    PHONOLOGICAL PROCESSES:
    -----------------------
    1. R-DELETION in casual speech:
       - Infinitives: "falar" → [faˈla]
       - Coda position: "porta" → [ˈpɔtɐ]
       - Stigmatized but common

    2. Vowel reduction in rapid speech:
       - "porque" [ˈpuɾki] → [pɾki]
       - "para" [ˈpaɾɐ] → [pɾa]

    3. Palatalization variability:
       - Formal: Less palatalization
       - Casual: More palatalization
       - "de" [di] vs. [dʒi]
    """
    def __init__(self, **kwargs):
        if "dialect_code" not in kwargs:
            kwargs["dialect_code"] = "pt-BR-x-sao-paulo"

        if "IRREGULAR_WORDS" not in kwargs:
            kwargs["IRREGULAR_WORDS"] = LEXICON.get_ipa_map(region="spx")

        if "DIGRAPH2IPA" not in kwargs:
            kwargs["DIGRAPH2IPA"] = {
                **AO1990.DIGRAPH2IPA,
                "rr": "x",  # DIVERGENCE: Brazilian uses [h] or [x] instead of [ʁ]
                "di": "dʒi",  # d palatalization before [i]
                "ti": "tʃi",  # d palatalization before [i]
            }
        super().__init__(**kwargs)


# =============================================================================
# ANGOLAN PORTUGUESE (pt-AO)
# =============================================================================

class AngolanPortuguese(DialectInventory):
    """
    Angolan Portuguese phonological inventory.

    CHARACTERISTIC FEATURES:
    ------------------------
    1. BASE: Similar to European Portuguese but with modifications

    2. VOWEL REDUCTION: Less reduction than European, more than Brazilian
       - Intermediate between European and Brazilian
       - Influenced by Bantu substrate (Kimbundu, Umbundu, Kikongo)

    3. R SOUNDS: Consistent alveolar trill [r]
       - Preserves distinction between tap [ɾ] and trill [r]
       - More conservative than European or Brazilian
       - "carro" [ˈkaru] (not [ˈkaʁu] or [ˈkaxu])

    4. PROSODY: Influenced by Bantu tone languages
       - May have different intonation patterns
       - Stress patterns similar to European

    5. FINAL /s/: Generally [ʃ] like European
       - "três" [ˈtɾeʃ]

    6. SUBSTRATE INFLUENCE: Phonological features from Bantu languages
       - May preserve some consonant distinctions
       - Prosodic patterns influenced by L1 Bantu speakers
    """

    def __init__(self):
        super().__init__(dialect_code="pt-AO",
                         DIGRAPH2IPA={
                             **AO1990.DIGRAPH2IPA,
                             "rr": "r",  # DIVERGENCE: Angolan uses alveolar trill [r]
                         },
                         # Moderate vowel reduction (between European and Brazilian)
                         DEFAULT_CHAR2PHONEMES={
                             **AO1990.DEFAULT_CHAR2PHONEMES,
                             "e": "e",  # DIVERGENCE: Less reduction than European [ɨ]
                             "o": "o",  # DIVERGENCE: Less reduction than European [u]
                             "r": "ɾ",  # DIVERGENCE: Strong R is [r], not [ʁ]
                         },
                         IRREGULAR_WORDS=LEXICON.get_ipa_map(region="lda") # Luanda
         )


# =============================================================================
# MOZAMBICAN PORTUGUESE (pt-MZ)
# =============================================================================

class MozambicanPortuguese(DialectInventory):
    """
    Mozambican Portuguese phonological inventory.

    CHARACTERISTIC FEATURES:
    ------------------------
    1. BASE: Similar to European Portuguese with Bantu substrate

    2. VOWEL REDUCTION: Variable, generally less than European
       - Influenced by substrate languages (Makhuwa, Tsonga, Sena)
       - May preserve more vowel distinctions

    3. R SOUNDS: Alveolar trill [r] common
       - Similar to Angolan Portuguese
       - "carro" [ˈkaru]

    4. REGIONAL VARIATION:
       - North (Nampula): More substrate influence
       - South (Maputo): Closer to European/South African Portuguese

    5. FINAL /s/: Generally [ʃ] like European
       - "nós" [ˈnɔʃ]

    6. PROSODY: Bantu-influenced intonation
       - May have different rhythm patterns
    """

    def __init__(self):
        super().__init__(dialect_code="pt-MZ",
                         DIGRAPH2IPA={
                             **AO1990.DIGRAPH2IPA,
                             "rr": "r",  # DIVERGENCE: Angolan uses alveolar trill [r]
                         },
                         # Moderate vowel reduction (between European and Brazilian)
                         DEFAULT_CHAR2PHONEMES={
                             **AO1990.DEFAULT_CHAR2PHONEMES,
                             "e": "e",  # DIVERGENCE: Less reduction than European [ɨ]
                             "o": "o",  # DIVERGENCE: Less reduction than European [u]
                             "r": "ɾ",  # DIVERGENCE: Strong R is [r], not [ʁ]
                         },
                         IRREGULAR_WORDS=LEXICON.get_ipa_map(region="mpx") # Maputo
         )


# =============================================================================
# TIMORESE PORTUGUESE (pt-TL)
# =============================================================================

class TimoresePortuguese(DialectInventory):
    """
    Timorese Portuguese (East Timor) phonological inventory.

    CHARACTERISTIC FEATURES:
    ------------------------
    1. BASE: European Portuguese with Austronesian substrate influence
       - Primary substrate: Tetum
       - Also influenced by Indonesian

    2. L2 FEATURES: Portuguese often learned as second language
       - May show substrate transfer from Tetum
       - More conservative/formal pronunciation
       - Less naturalistic reduction

    3. VOWEL SYSTEM: Similar to European but may be simpler
       - Less vowel reduction than European
       - May neutralize some distinctions

    4. R SOUNDS: Variable
       - May use alveolar tap [ɾ] and trill [r]
       - Less uvular [ʁ] than European

    5. FINAL /s/: Generally [ʃ] like European
       - "nós" [ˈnɔʃ]

    6. SMALLER SPEAKER BASE: Portuguese is official but less widely native
       - More formal/prescriptive forms common
       - Less dialectal innovation
    """

    def __init__(self):
        super().__init__(dialect_code="pt-TL",
                         DIGRAPH2IPA={
                             **AO1990.DIGRAPH2IPA,
                             "rr": "r",  # DIVERGENCE: Angolan uses alveolar trill [r]
                         },
                         # Moderate vowel reduction (between European and Brazilian)
                         DEFAULT_CHAR2PHONEMES={
                             **AO1990.DEFAULT_CHAR2PHONEMES,
                             "a": "a",  # DIVERGENCE: Less reduction
                             "e": "e",  # DIVERGENCE: Less reduction than European [ɨ]
                             "o": "o",  # DIVERGENCE: Less reduction than European [u]
                             "r": "ɾ",  # DIVERGENCE: Strong R is [r], not [ʁ]
                         },
                         IRREGULAR_WORDS=LEXICON.get_ipa_map(region="dli") # Dili
         )

