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

    def __init__(self, dialect_code=None, IRREGULAR_WORDS=None, **kwargs):
        super().__init__(
            dialect_code=dialect_code or "pt-PT",
            FALLING_NASAL_DIPHTHONGS={
                **AO1990.FALLING_NASAL_DIPHTHONGS,
                "ũj": "ui",  # muito (special nasalized case)
            },
            TRIPHTHONG2IPA={
                **AO1990.TRIPHTHONG2IPA,
                # [j-e-j] sequence
                "iei": "jej",  # chieira, macieira, pardieiro
                # Alternative Lisbon realization:
                # "iei": "jɐj",  # with vowel reduction
                # [j-a-w] sequence
                "iau": "jaw",  # miau
            },
            IRREGULAR_WORDS=IRREGULAR_WORDS or LEXICON.get_ipa_map(region="lbx"), # Lisbon
            **kwargs
        )


class LisbonPortuguese(EuropeanPortuguese):
    def __init__(self):
        super().__init__(
            dialect_code="pt-PT-x-lisbon",
        )


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

    def __init__(self, dialect_code=None, IRREGULAR_WORDS=None, **kwargs):
        super().__init__(
            dialect_code=dialect_code or "pt-BR",
            DIGRAPH2IPA = {
                **AO1990.DIGRAPH2IPA,
                "rr": "h"  # DIVERGENCE: Brazilian uses [h] or [x] instead of [ʁ]
            },
            DEFAULT_CHAR2PHONEMES = {
                **AO1990.DEFAULT_CHAR2PHONEMES,
                # VOWELS - LESS REDUCTION IN BRAZILIAN
                "a": "a",  # DIVERGENCE: stays [a], not [ɐ]
                "â": "a",  # DIVERGENCE: stays [a], not [ɐ]
                "e": "e",  # DIVERGENCE: stays [e], not [ɨ]
                "o": "o",  # DIVERGENCE: stays [o], not [u]
                # CONSONANTS
                "r": "ɾ",  # DIVERGENCE: tap, strong R is [h]
            },
            IRREGULAR_WORDS=IRREGULAR_WORDS or LEXICON.get_ipa_map(region="rjx"),
            **kwargs
        )


class RioJaneiroPortuguese(BrazilianPortuguese):
    def __init__(self):
        super().__init__(
            dialect_code="pt-BR-x-rio-janeiro",
        )


class SaoPauloPortuguese(BrazilianPortuguese):
    def __init__(self):
        super().__init__(
            dialect_code="pt-BR-x-sao-paulo",
            IRREGULAR_WORDS=LEXICON.get_ipa_map(region="spx")
        )


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

