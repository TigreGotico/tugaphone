"""Word-level language detection for code-switch routing.

The code-switch stage needs one decision per token: is this word Portuguese, or
is it embedded contact-language material to route through the ``es``/``fr``/``en``
lattice and nativize? The orthographic heuristic in :mod:`tugaphone.codeswitch`
answers that from spelling alone — it flags a word only when it carries a letter
or digraph Portuguese does not use natively or is a known function word. That
misses the loans and internationalisms spelled with Portuguese-legal letters
(``site``, ``feedback``, ``general``) and, on the border, cannot tell a Spanish
embed from a Portuguese word.

This module adds a statistical detector: four character-level Markov models —
one each for Portuguese, Spanish, French and English — trained on Wikipedia and
serialized as small JSON artifacts under ``tugaphone/data/langdetect/``. A word
is scored under all four models; the model that assigns it the lowest perplexity
wins.

In-language default (null beats wrong)
--------------------------------------
Portuguese is the surrounding language, so it is the default: a word is only
routed out of Portuguese when a foreign model beats the Portuguese model by at
least :data:`DEFAULT_MARGIN` nats-per-character. Below that margin the word stays
``pt`` — a weak, ambiguous signal never misroutes a native word. The genuinely
ambiguous shared-alphabet internationalisms (``hotel``, ``radio``, ``general``)
sit inside that margin band and therefore stay Portuguese, which is exactly the
conservative behaviour a TTS frontend wants.

Known limit: an open-class native word typed without its diacritic and not on
:data:`PORTUGUESE_KEEP` can still be routed out. ``como esta a tua mae`` is
handled because every token is on the keep-list; an unaccented open-class word
is scored by the models as written, and the models are trained on accented text.

The detector is optional. It is used only when :mod:`markovonnx` is importable
and the bundled models are present; otherwise the caller falls back to the
orthographic heuristic. Loading is lazy and cached, so importing tugaphone never
pays the cost unless code-switching actually runs.
"""
from __future__ import annotations

import functools
import math
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

#: Languages the detector scores. ``pt`` is the in-language default.
LANGS: List[str] = ["pt", "es", "fr", "en"]

#: Boundary sentinels wrapping each word, matching the training pipeline so
#: word-initial and word-final character statistics are modelled.
_BOS, _EOS = "\x02", "\x03"

#: A foreign model must beat the Portuguese model by at least this many
#: nats-per-character (log-perplexity units) before a word is routed out of
#: Portuguese. Tuned on held-out Wikipedia words to favour never misrouting a
#: native word over catching every contact word (null beats wrong): a higher
#: margin keeps more words Portuguese. This is set well above the Basque
#: frontend's 0.25 because Portuguese, Spanish and French share the Romance
#: character-shape so tightly that a small margin misroutes common native words
#: (``noite``, ``carne``); 0.5 keeps native retention high at a modest recall
#: cost (see ``docs/codeswitch.md``).
DEFAULT_MARGIN: float = 0.5

#: High-frequency Portuguese wordforms that are always kept Portuguese,
#: regardless of the models. Encyclopedic training text underrepresents
#: conversational grammar, so a char-model can rate a short function word like
#: ``de`` or ``que`` as Spanish/French on its letter shape alone — and these
#: shared-Romance function words are exactly the ones a Spanish or French model
#: also fits well. They are unambiguously native here and must never be routed to
#: a contact lattice, so the statistical decision is bypassed for them entirely.
#: Both code-switch classifiers consult this set: the orthographic fallback in
#: :mod:`tugaphone.codeswitch` checks it before its own contact stopword lists,
#: so the invariant holds whether or not the detector is installed.
#:
#: Membership criterion: a Portuguese closed-class form — article, preposition,
#: conjunction, pronoun, determiner — or a finite form of a high-frequency
#: irregular verb belongs here regardless of what a model scores it. Open-class
#: vocabulary goes through the models. The finite forms of *ser, ir, ter, estar,
#: haver, fazer, ver, vir, dar, poder, querer, saber* are listed by paradigm
#: cell: a whole tense goes in as soon as any of its forms is one a foreign
#: model outscores Portuguese on (the future subjunctive of *ser* — ``for``,
#: ``fores``, ``formos``, ``forem`` — is the motivating case). A tense no
#: foreign model claims anywhere is left out rather than padding the set.
#:
#: The kinship and address words at the end are admitted as high-frequency
#: native vocabulary rather than as grammar: their only foreign-looking property
#: is a diacritic, and lookup is diacritic-folded (:func:`is_keep_word`) so the
#: unaccented spellings Portuguese speakers actually type — ``mae``, ``nao``,
#: ``voce`` — resolve to the accented entry.
PORTUGUESE_KEEP = frozenset("""
o a os as um uma uns umas de do da dos das em no na nos nas por pra pro
para com sem sob sobre entre ate até desde após trás e ou nem mas porém
que se como quando onde quem qual quais cujo cuja quanto porque porquê
não sim já ainda também só apenas muito pouco mais menos bem mal assim
tão tanto cada todo toda todos todas algum alguma nenhum nenhuma outro outra
este esta estes estas esse essa esses essas aquele aquela aqueles aquelas
isto isso aquilo meu minha teu tua seu sua nosso nossa vosso vossa
eu tu ele ela nós vós eles elas me te lhe nos vos lhes mim ti si
é foi era são somos sou está estão estava estou tem têm tinha há havia
ser estar ter haver fazer ir vir dar ver dizer poder querer saber
aqui ali aí lá cá agora hoje ontem amanhã sempre nunca depois antes então
olá oi bom boa obrigado obrigada por favor tchau adeus
és sois éramos fui fomos seremos fosses fôssemos fôsseis for fores fordes
vais vai vamos ides íeis irás irá iremos iríamos ide tens tendes tive
tiveste tivestes teremos tiver tiveres tiverdes estás estamos estarás
estaremos estaria estarias estaríamos estiveres hás havemos havíamos houve
houveste haverei haveremos houvesse houver houveres faço farás faremos
faríamos faça fizer vejo vedes víamos vi viste vistes verás veremos vejas
visse vires virdes vens vindes vieste viemos virei virás virá viremos viria
virias viesse viessem vier vieres viermos vierem dais dávamos deste demos
destes darei daremos daria deem desse der deres derem podíamos pude pudemos
possa pudesses pudéssemos puder puderes puderem quero queres quer queremos
querias quis quiseste quererá quereremos quereria quisesse quiser quiseres
quiserem sei sabes sabe sabias sabíamos soube soubeste saberemos saiba
saibas saibamos saibam soubesse soubessem souber souberes
eras éreis eram foste fostes foram serei serás será sereis serão fosse
fossem formos forem vou vão ia ias íamos iam irei ireis irão iria irias
iríeis iriam vá vás vades tenho temos teve tivemos tiveram terei terás terá
tereis terão tivermos tiverem estais estarei estará estareis estarão
estaríeis estariam estiver estivermos estiverdes estiverem hei heis hão
havias havieis haviam houvemos houvestes houveram haverás haverá havereis
haverão houvesses houvéssemos houvessem houvermos houverdes houverem fazes
faz fazemos fazeis fazem farei fará fareis farão faria farias faríeis fariam
faças façamos façais façam fizeres fizermos fizerdes fizerem vês vê vemos
veem via vias víeis viam viu vimos viram verei verá vereis verão veja
vejamos vejais vejam visses víssemos vissem virmos virem venho vem vêm vim
veio viestes vieram vireis virão viríamos viriam viesses viéssemos vierdes
dou dás dá damos dão dava davas davam dei deu deram darás dará dareis darão
darias daríamos dariam dê dês dêmos desses déssemos dessem dermos derdes
podia podias podiam pudeste pôde pudestes puderam possas possamos possais
possam pudesse pudessem pudermos puderdes quereis querem queria queríamos
queriam quisemos quisestes quiseram quererei quererás quererão quereríamos
quereriam quisesses quiséssemos quisessem quisermos quiserdes sabemos sabeis
sabem sabia sabiam soubemos soubestes souberam saberei saberás saberá
sabereis saberão saibais soubesses soubéssemos soubermos souberdes souberem
mãe mães pai pais pão pães mão mãos irmã irmãs irmão irmãos avó avô avós
você vocês coração
""".split())

#: Where the bundled JSON models live.
_MODEL_DIR = Path(__file__).parent / "data" / "langdetect"


def _load_gz(markov_chain_cls, path: Path):
    """Load a gzip-compressed markovonnx JSON model via a temporary file."""
    import gzip
    import tempfile

    with gzip.open(path, "rb") as fh:
        data = fh.read()
    with tempfile.NamedTemporaryFile("wb", suffix=".json", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        return markov_chain_cls.load(tmp_path)
    finally:
        import os
        os.unlink(tmp_path)


def _normalize(word: str) -> str:
    """NFC + lowercase + keep only alphabetic characters (training parity)."""
    word = unicodedata.normalize("NFC", word).lower()
    return "".join(ch for ch in word if ch.isalpha())


#: Combining cedilla — kept by :func:`fold_diacritics` because ``ç`` is a native
#: Portuguese letter and :func:`_normalize` treats it as one.
_CEDILLA = "\u0327"


def fold_diacritics(word: str) -> str:
    """Strip diacritics from *word*, keeping the cedilla.

    Portuguese is written unaccented all the time — search boxes, chat, ASR
    output — and the models are trained on accented text, so an unaccented
    native spelling looks foreign by construction. Folding both sides of the
    keep-list lookup makes ``mae`` reach the entry for ``mãe``.
    """
    decomposed = unicodedata.normalize("NFD", word)
    kept = "".join(ch for ch in decomposed
                   if not unicodedata.combining(ch) or ch == _CEDILLA)
    return unicodedata.normalize("NFC", kept)


_KEEP_FOLDED = frozenset(fold_diacritics(w) for w in PORTUGUESE_KEEP)


def is_keep_word(word: str) -> bool:
    """Whether *word* is on :data:`PORTUGUESE_KEEP`, ignoring lost diacritics."""
    core = _normalize(word)
    return bool(core) and (core in PORTUGUESE_KEEP
                           or fold_diacritics(core) in _KEEP_FOLDED)


def _wrap(word: str) -> List[str]:
    return [_BOS] + list(word) + [_EOS]


class MarkovLangDetector:
    """Four char-Markov models scoring a word as pt / es / fr / en."""

    def __init__(self, models: Dict[str, "object"]):
        self._models = models

    # -- construction ---------------------------------------------------------

    @classmethod
    def from_dir(cls, model_dir: Path = _MODEL_DIR) -> Optional["MarkovLangDetector"]:
        """Load the bundled models, or return ``None`` if unavailable.

        Returns ``None`` when :mod:`markovonnx` is not installed or any of the
        four model files is missing — the caller then falls back to the
        orthographic heuristic. Models are shipped gzip-compressed
        (``<lang>.json.gz``, a few tens of KB each); a plain ``<lang>.json`` is
        also accepted.
        """
        try:
            from markovonnx import MarkovChain
        except Exception:
            return None
        models = {}
        for lang in LANGS:
            gz = model_dir / f"{lang}.json.gz"
            plain = model_dir / f"{lang}.json"
            try:
                if gz.is_file():
                    models[lang] = _load_gz(MarkovChain, gz)
                elif plain.is_file():
                    models[lang] = MarkovChain.load(str(plain))
                else:
                    return None
            except Exception:
                return None
        return cls(models)

    # -- scoring --------------------------------------------------------------

    def score(self, word: str) -> Dict[str, float]:
        """Length-normalized log-perplexity per language (lower = better fit)."""
        seq = _wrap(_normalize(word))
        out: Dict[str, float] = {}
        for lang, mc in self._models.items():
            ppx = mc.perplexity([seq])
            out[lang] = math.log(max(ppx, 1e-30))
        return out

    def detect(self, word: str, margin: float = DEFAULT_MARGIN,
               default_side: Optional[str] = None
               ) -> Tuple[str, Dict[str, float]]:
        """Return ``(lang, scores)`` with the in-language default applied.

        The best-fitting foreign language is returned only if it beats ``pt`` by
        at least ``margin``; otherwise the word stays ``pt``. When two foreign
        models sit within ``margin`` of each other (the shared-Romance overlap),
        ``default_side`` — the dialect's contact side — breaks the tie so a
        genuinely ambiguous embed routes to the expected language.
        """
        core = _normalize(word)
        if not core:
            return "pt", {}
        if is_keep_word(core):
            # Unambiguously native wordform: never route out of Portuguese.
            return "pt", {}
        scores = self.score(word)
        best = min(scores, key=scores.get)
        if best == "pt":
            return "pt", scores
        if (scores["pt"] - scores[best]) < margin:
            return "pt", scores
        # Tie-break among foreign models within a margin of the winner.
        if default_side is not None and default_side in scores:
            if (scores[default_side] - scores[best]) < margin:
                return default_side, scores
        return best, scores

    def is_contact(self, word: str, margin: float = DEFAULT_MARGIN) -> bool:
        """Whether *word* is embedded contact-language material (not Portuguese)."""
        return self.detect(word, margin)[0] != "pt"


@functools.lru_cache(maxsize=1)
def get_detector() -> Optional[MarkovLangDetector]:
    """The cached bundled detector, or ``None`` if unavailable."""
    return MarkovLangDetector.from_dir()
