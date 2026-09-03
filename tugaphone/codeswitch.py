"""Code-switch handling: embedded Spanish / French / English routed and nativized.

Real Portuguese text is bilingual, and in the modern register trilingual. The
Brazilian tech/media register embeds **English** heavily (``download``, ``app``,
``site``, ``feedback``, ``streaming``, product and band names); European and
African writing embeds English loans too, and on the Uruguayan border
(``pt-UY``, *portunhol*) Portuguese embeds **Spanish**; quoted French fragments
and Gallicisms turn up throughout. A TTS frontend that hands such a word to the
Portuguese lattice mispronounces it, and one that hands it to the raw
Spanish/French/English lattice can emit phones outside the Portuguese inventory
the voice was trained on.

tugaphone takes arbtok's **total-nativization** stance — *never drop a segment,
always project it onto the target inventory* — but keeps the machinery simple: a
word-level decision (the char-Markov detector in :mod:`tugaphone.langdetect`,
with an orthographic heuristic as fallback) decides whether a token is Portuguese
or contact-language and, if contact, which of es/fr/en; a detected contact word
is transcribed through the orthography2ipa ``es-ES`` / ``fr-FR`` / ``en-US``
lattice, and every phone in that result is projected onto the target Portuguese
lect's phoneme inventory. There is no sub-word alignment.

Because Portuguese already has ``/v z ʃ ʒ ʁ/``, the palatal ``/ɲ ʎ/``, the glides
``/w j/`` and a full set of **nasal vowels**, the projections are far gentler than
Basque's — most contact phones are already Portuguese phones and pass through
unchanged. Only the genuinely non-Portuguese segments move: the interdentals
``/θ ð/``, French ``/y ø œ/``, the English rhotic ``/ɹ/`` and velar nasal ``/ŋ/``.

The contact language is chosen by the ``contact`` parameter:

* ``"none"`` (default) — disable code-switching; every token is transcribed as
  Portuguese. This is the default because Portuguese shares the Romance
  character-shape with Spanish and French too tightly for statistical routing to
  be safe unattended, so code-switching is opt-in and the out-of-the-box output
  is unchanged by this feature;
* ``"auto"`` — detect contact words and, *per word*, classify them as English,
  French or Spanish; an unclassified contact word falls to the dialect's default
  side (Uruguayan border → Spanish, everywhere else → English; see
  :func:`tugaphone.registry.default_contact`);
* ``"es"`` / ``"fr"`` / ``"en"`` — force that contact lattice for detected
  contact words.

Loanword-adaptation conventions
-------------------------------
Where the phonological-adaptation literature on Portuguese anglicisms and
borrowings documents a substitution it is followed (interdental stopping to
``/t d/``, English rhotic to the Portuguese tap ``/ɾ/``, five-/seven-vowel
mapping, denasalised-then-renasalised French vowels onto Portuguese nasals);
where the literature is silent the mapping is stated as a **convention**, not a
claim. The per-table comments mark which is which.
"""
from __future__ import annotations

import functools
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Detection (orthographic fallback — used only when the Markov detector,
# tugaphone.langdetect, is unavailable).
# ---------------------------------------------------------------------------

#: Letters not used natively in Portuguese orthography (loans/proper names only).
#: Portuguese uses ``ç`` and the accented vowels ``á é í ó ú â ê ô à ã õ``
#: natively, so — unlike Basque — those are *not* contact signals. ``k w y`` are.
_NON_PT_LETTERS = set("kwyñ")

#: Letters that point specifically at Spanish.
_SPANISH_LETTERS = set("ñ")

#: Letters/accents that point specifically at French (excluding ``ç``, ``ê``,
#: ``ô``, ``â``, ``à`` which Portuguese also uses).
_FRENCH_LETTERS = set("èëïîûùœæ")

#: English orthographic digraphs absent from native Portuguese spelling.
#: Deliberately excludes sequences that occur natively in Portuguese — ``nh``
#: ``lh`` (native digraphs), ``oo`` (``voo``, ``coordenar``) — so the signal
#: never fires on a Portuguese word.
_ENGLISH_DIGRAPHS = ("th", "sh", "wh", "ck", "gh", "ght", "ph", "ww", "yy")

#: Very common Spanish function words (no non-Portuguese letter of their own).
_SPANISH_STOPWORDS = {
    "el", "los", "las", "del", "por", "para", "con", "una", "unos", "unas",
    "más", "muy", "pero", "como", "este", "esta", "esto", "y", "su", "sus",
}

#: Very common French function words.
_FRENCH_STOPWORDS = {
    "le", "les", "des", "du", "et", "un", "une", "dans", "pour", "avec",
    "sur", "pas", "plus", "très", "mais", "cette", "au", "aux", "je", "vous",
}

#: Very common English function/register words (tech, music, media).
_ENGLISH_STOPWORDS = {
    "the", "of", "and", "to", "in", "is", "it", "for", "with", "this",
    "that", "on", "at", "as", "by", "live", "new", "best", "feat", "remix",
    "online", "web", "app", "software", "hardware", "streaming", "stream",
    "download", "upload", "email", "startup", "feedback", "password",
    "weekend", "rock", "pop", "jazz", "band", "single", "album", "site",
    "link", "post", "story", "stories", "reels", "gamer", "gaming", "player",
    "smartphone", "notebook", "mouse", "print", "screenshot", "deadline",
}

#: Union of all contact stopwords, for the language-agnostic contact test.
_CONTACT_STOPWORDS = _SPANISH_STOPWORDS | _FRENCH_STOPWORDS | _ENGLISH_STOPWORDS


def _strip(token: str) -> str:
    """Lower-case a token and strip surrounding punctuation for testing."""
    return token.strip("".join(
        c for c in token if not (c.isalpha() or c == "-"))).lower()


def _has_english_signal(core: str) -> bool:
    """Whether *core* (a stripped lower-case token) looks English.

    ``w`` and ``y`` are not native Portuguese letters and point at English/
    Germanic material; the English digraphs (``th sh wh ck gh ph …``) never occur
    in native Portuguese spelling. ``k`` alone is a weaker signal (it also appears
    in Greco-Latin and other loans), so it is not treated as English on its own.
    """
    if core in _ENGLISH_STOPWORDS:
        return True
    if any(dg in core for dg in _ENGLISH_DIGRAPHS):
        return True
    return ("w" in core or core.endswith("y")) and not any(
        ch in _FRENCH_LETTERS for ch in core)


def is_contact_word(token: str) -> bool:
    """Heuristically decide whether *token* is embedded contact-language text."""
    core = _strip(token)
    if not core:
        return False
    if any(ch in _NON_PT_LETTERS or ch in _FRENCH_LETTERS for ch in core):
        return True
    if _has_english_signal(core):
        return True
    return core in _CONTACT_STOPWORDS


def contact_language(token: str, default_side: str = "en") -> str:
    """Classify a *contact* token as ``"en"``, ``"fr"`` or ``"es"``.

    Only meaningful for a token that :func:`is_contact_word` already flagged.
    English is checked first (its digraph/function-word signals are the most
    specific), then the Spanish/French accent split; a token with no
    language-specific signal falls back to ``default_side`` (the dialect's
    contact side — English for most lects, Spanish for the Uruguayan border).
    """
    core = _strip(token)
    if _has_english_signal(core):
        return "en"
    if any(ch in _FRENCH_LETTERS for ch in core) or core in _FRENCH_STOPWORDS:
        return "fr"
    if any(ch in _SPANISH_LETTERS for ch in core) or core in _SPANISH_STOPWORDS:
        return "es"
    return default_side


# ---------------------------------------------------------------------------
# Nativization: project a contact-language IPA string onto Portuguese phones.
# ---------------------------------------------------------------------------

#: Combining/length marks dropped before projection (stress, liaison, length).
#: The nasal tilde is *kept* — Portuguese has nasal vowels, so a French nasal
#: vowel projects onto a Portuguese nasal vowel rather than being denasalised.
_DROP = ("ˈ", "ˌ", "‿", "ː", "ˑ")

#: Phones shared by every contact language that Portuguese lacks. Small, because
#: Portuguese already has ``/v z ʃ ʒ/`` and the glides.
_NATIVIZE_COMMON = {
    "ɥ": "j",    # labial-palatal glide → palatal glide
    "ə": "ɐ",    # mid-central vowel → Portuguese /ɐ/
    "ɑ": "a",    # back open → /a/
    "ɜ": "ɛ", "ɐ": "ɐ",
}

#: Romance-specific projection (Spanish + French). Portuguese keeps ``/ʁ/``,
#: ``/ʎ/`` and the nasal vowels, so this is short.
_NATIVIZE_ROMANCE = {
    **_NATIVIZE_COMMON,
    "θ": "s",    # Castilian interdental → seseo /s/ (Portuguese has no /θ/)
    "β": "b", "ð": "d", "ɣ": "ɡ",   # Spanish approximants → their stops
    "ʝ": "ʒ",    # Spanish yeísmo fricative → Portuguese /ʒ/ (convention)
    "ɟʝ": "dʒ",  # affricated /ʝ/ → /dʒ/
    "x": "ʁ",    # Spanish jota / velar fricative → Portuguese uvular
    "ʀ": "ʁ", "r": "ʁ",   # trills → Portuguese uvular /ʁ/ (tap /ɾ/ kept)
    "y": "i",    # French /y/ → /i/
    "ø": "e", "œ": "ɛ",   # French rounded front → /e ɛ/
    # French nasal vowels → Portuguese nasal vowels (gentle: both exist)
    "ɑ̃": "ɐ̃", "ɛ̃": "ẽ", "ɔ̃": "õ", "œ̃": "ẽ", "æ̃": "ẽ",
}

#: English-specific projection. See the module docstring for the convention/
#: literature split.
_NATIVIZE_ENGLISH = {
    **_NATIVIZE_COMMON,
    # diphthongs first (longest-first matching also handles this)
    "eɪ": "ej", "aɪ": "aj", "ɔɪ": "ɔj", "aʊ": "aw", "oʊ": "ow", "əʊ": "ow",
    # interdentals → stops (TH-stopping, the common Portuguese adaptation)
    "θ": "t", "ð": "d",
    # rhotic / velar-nasal / dark-l substitutions
    "ɹ": "ɾ", "ɻ": "ɾ", "ɫ": "l", "ŋ": "n", "ʍ": "w",
    # /w j v z dʒ tʃ ʃ ʒ/ are all native Portuguese — kept, not remapped.
    # vowels to the Portuguese inventory (gentle: /ɔ ɛ/ already exist)
    "æ": "a", "ʌ": "a", "ɒ": "ɔ",
    "ɪ": "i", "ʊ": "u", "ɝ": "ɛ",
}


def _nativize(ipa: str, english: bool = False) -> str:
    """Project a contact-language IPA string onto the Portuguese inventory.

    ``english`` selects the English projection table; otherwise the Romance
    (Spanish/French) table is used.
    """
    table = _NATIVIZE_ENGLISH if english else _NATIVIZE_ROMANCE
    for d in _DROP:
        ipa = ipa.replace(d, "")
    for src in sorted(table, key=len, reverse=True):
        ipa = ipa.replace(src, table[src])
    return ipa


# ---------------------------------------------------------------------------
# The contact transcriber.
# ---------------------------------------------------------------------------

_CONTACT_CODE = {"es": "es-ES", "fr": "fr-FR", "en": "en-US"}


@functools.lru_cache(maxsize=None)
def _contact_engine(contact: str):
    """A cached orthography2ipa engine for the contact lattice."""
    from orthography2ipa import G2P
    return G2P(_CONTACT_CODE[contact])


def transcribe_contact(word: str, contact: str) -> str:
    """Transcribe a contact *word* and nativize it onto the Portuguese inventory."""
    ipa = _contact_engine(contact).transcribe(word)
    return _nativize(ipa, english=(contact == "en"))


# ---------------------------------------------------------------------------
# Per-token routing.
# ---------------------------------------------------------------------------

def _classify(token: str, default_side: str) -> Optional[str]:
    """Route *token*: ``None`` for Portuguese, else the contact language.

    Prefers the char-Markov detector (:mod:`tugaphone.langdetect`), which returns
    the contact language directly; falls back to the orthographic heuristic when
    the detector's models are unavailable.
    """
    from tugaphone.langdetect import get_detector

    detector = get_detector()
    if detector is not None:
        lang, _ = detector.detect(token, default_side=default_side)
        return None if lang == "pt" else lang
    if not is_contact_word(token):
        return None
    return contact_language(token, default_side)


def _is_contact(token: str) -> bool:
    """Whether *token* is contact-language material (detector, else heuristic)."""
    from tugaphone.langdetect import get_detector

    detector = get_detector()
    if detector is not None:
        return detector.is_contact(token)
    return is_contact_word(token)


def split_runs(text: str, contact: str,
               default_side: str = "en") -> List[Tuple[Optional[str], str]]:
    """Split *text* into ``(contact_lang, token)`` pairs by the word decision.

    ``contact_lang`` is ``None`` for a Portuguese token, or the contact language
    (``"es"`` / ``"fr"`` / ``"en"``) to route the token through. For
    ``contact == "auto"`` each token is classified individually; for a forced
    ``"es"`` / ``"fr"`` / ``"en"`` every detected contact token routes through
    that language. ``contact == "none"`` marks every token as Portuguese.
    """
    runs: List[Tuple[Optional[str], str]] = []
    for token in text.split():
        if contact == "none":
            runs.append((None, token))
        elif contact == "auto":
            runs.append((_classify(token, default_side), token))
        else:
            runs.append(((contact if _is_contact(token) else None), token))
    return runs
