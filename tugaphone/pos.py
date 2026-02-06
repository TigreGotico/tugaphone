from typing import List, Tuple
from tugaphone.dialects import LEXICON


class TugaTagger:
    """
    A unified interface for Portuguese Part-of-Speech (POS) tagging.

    Supports multiple backends including spaCy and Brill-style taggers.
    The 'auto' mode provides a fallback mechanism to ensure tagging works
    even if specific dependencies are missing.
    """

    def __init__(self, engine: str = "auto", spacy_model: str = "pt_core_news_lg"):
        """
        Create a TugaTagger configured for the chosen tagging engine and optionally preload backend models.

        Parameters:
            engine (str): Tagging engine to use: "spacy", "brill", "dummy", or "auto".
                - "spacy": preload the spaCy model in strict mode.
                - "brill": preload the Brill tagger in strict mode.
                - "auto": attempt to preload both spaCy and Brill (not strict).
            spacy_model (str): Name of the spaCy Portuguese model to load when using spaCy (default "pt_core_news_lg").

        Notes:
            Load failures for a backend will be propagated when that backend is loaded in strict mode.
        """
        self.engine = engine
        self._spacy = self._brill = None

        if engine in ["spacy", "auto"]:
            self.load_spacy(spacy_model, strict=(engine == "spacy"))
        if engine in ["brill", "auto"]:
            self.load_brill(strict=(engine == "brill"))

    def load_spacy(self, spacy_model: str = "pt_core_news_lg", strict: bool = True):
        """
        Load and cache a spaCy Portuguese NLP model on the instance.

        Parameters:
            spacy_model (str): Name of the spaCy model to load (e.g., "pt_core_news_lg").
            strict (bool): If True, re-raise any exception encountered while loading; if False, suppress the exception and leave `self._spacy` as None.

        Side effects:
            Assigns the loaded spaCy model to `self._spacy`.
        """
        try:
            import spacy
            self._spacy = spacy.load(spacy_model, disable=["ner", "parser"])
        except Exception as e:
            if strict:
                raise e

    def load_brill(self, strict: bool = True):
        """
        Load and cache a Brill-style Portuguese POS tagger on the instance.

        Parameters:
            strict (bool): If True, re-raise any exception encountered while importing or loading the tagger;
                if False, suppress load errors and leave `self._brill` unset when loading fails.
        """
        try:
            from brill_postaggers import BrillPostagger
            self._brill = BrillPostagger.from_pretrained("pt")
        except Exception as e:
            if strict:
                raise e

    def tag(self, sentence: str) -> List[Tuple[str, str]]:
        """
        Tags a sentence using the configured engine.

        Args:
            sentence (str): The Portuguese text to tag.

        Returns:
            List[Tuple[str, str]]: A list of (word, tag) tuples.
        """
        engines = {
            "auto": self.tag_auto,
            "dummy": self.tag_dummy,
            "brill": self.tag_brill,
            "spacy": self.tag_spacy,
            "lexicon": self.tag_lexicon
        }
        handler = engines.get(self.engine)
        if not handler:
            raise ValueError(f"Invalid engine: '{self.engine}'")
        return handler(sentence)

    def tag_auto(self, sentence: str) -> List[Tuple[str, str]]:
        """
        Tag a sentence by trying spaCy then Brill and using the dummy tagger if both fail.

        Returns:
            List[Tuple[str, str]]: A list of (word, POS-tag) tuples produced by the first successful tagger; if both spaCy and Brill raise exceptions, returns the dummy tagger's output.
        """
        for method in [self.tag_brill, self.tag_spacy, self.tag_lexicon]:
            try:
                return method(sentence)
            except:
                continue
        return self.tag_dummy(sentence)

    def tag_brill(self, sentence: str) -> List[Tuple[str, str]]:
        """
        Tag a sentence using the Brill-style POS tagger.

        If the Brill tagger is not yet loaded, it will be initialized automatically.

        Parameters:
            sentence (str): Raw text sentence to be tagged.

        Returns:
            List[Tuple[str, str]]: List of (token, POS-tag) pairs for the input sentence.
        """
        if self._brill is None:
            self.load_brill(strict=True)
        return self._brill.tag(sentence)

    def tag_spacy(self, sentence: str) -> List[Tuple[str, str]]:
        """
        Tag a sentence using the configured spaCy Portuguese model.

        Returns:
            List[Tuple[str, str]]: A list of (token_text, POS_tag) tuples, one per token. `POS_tag` is spaCy's coarse-grained part-of-speech label.
        """
        if self._spacy is None:
            self.load_spacy(strict=True)
        doc = self._spacy(sentence)
        return [(tok.text, tok.pos_) for tok in doc]

    @classmethod
    def tag_lexicon(cls, sentence: str) -> List[Tuple[str, str]]:
        tagged = []
        for word in sentence.lower().split():
            if word in LEXICON.possible_postags:
                possibilities = LEXICON.possible_postags[word]
                # TODO: how to choose postag? use surrounding context
                tagged.append((word, possibilities[0]))
            else:
                tagged.append((word, cls._guess_pos(word)))
        return tagged

    @classmethod
    def tag_dummy(cls, sentence: str) -> List[Tuple[str, str]]:
        """
        Split the sentence on whitespace and tag each token as the noun "NOUN".

        Returns:
            List[Tuple[str, str]]: A list of (word, tag) tuples where each whitespace-separated token from the input is paired with the tag "NOUN".
        """
        return [(word, cls._guess_pos(word)) for word in sentence.split()]

    @staticmethod
    def _guess_pos(word: str) -> str:
        """Applies heuristic rules to guess the POS tag."""
        lower_word = word.lower()

        # Rule 0: Punctuation
        if not word.isalnum():
            return "PUNCT"

        # Rule 0.5: Numbers
        if word.isdigit():
            return "NUM"

        # 1. Closed-class words (Functional words that rarely change category)
        COMMON_WORDS = {
            # Articles
            "o": "DET", "a": "DET", "os": "DET", "as": "DET", "um": "DET", "uma": "DET",
            # Prepositions
            "de": "ADP", "do": "ADP", "da": "ADP", "em": "ADP", "no": "ADP", "na": "ADP",
            "por": "ADP", "para": "ADP", "com": "ADP", "sem": "ADP", #"a": "ADP",
            # Conjunctions
            "e": "CCONJ", "mas": "CCONJ", "ou": "CCONJ", "que": "SCONJ", "se": "SCONJ",
            # Pronouns
            "eu": "PRON", "ele": "PRON", "ela": "PRON", "nós": "PRON", "eles": "PRON",
            "isso": "PRON", "aquilo": "PRON",
            # Common Verbs (Auxiliary/Copula)
            "é": "AUX", "foi": "AUX", "são": "AUX", "está": "AUX", "ser": "AUX", "ter": "AUX",
            # Adverbs
            "não": "ADV", "sim": "ADV", "muito": "ADV", "mais": "ADV"
        }

        # 2. Suffix Rules (Order matters: check longer suffixes first)
        SUFFIX_RULES = [
            ("mente", "ADV"),   # rapidamente
            ("ando", "VERB"),   # cantando
            ("endo", "VERB"),   # correndo
            ("indo", "VERB"),   # partindo
            ("aram", "VERB"),   # cantaram
            ("eram", "VERB"),   # correram
            ("iram", "VERB"),   # partiram
            ("ava", "VERB"),    # cantava
            ("ria", "VERB"),    # cantaria
            ("dor", "NOUN"),    # jogador
            ("ção", "NOUN"),    # ação
            ("são", "NOUN"),    # tensão
            ("dade", "NOUN"),   # cidade
            ("ismo", "NOUN"),   # realismo
            ("ista", "NOUN"),   # realista
            ("oso", "ADJ"),     # formoso
            ("osa", "ADJ"),     # formosa
            ("vel", "ADJ"),     # amável
            ("al", "ADJ"),      # nacional
            ("ar", "VERB"),     # amar
            ("er", "VERB"),     # comer
            ("ir", "VERB"),     # partir (careful with 'ir' the verb itself)
        ]

        # Rule 1: Dictionary Lookup (O(1) speed)
        if lower_word in COMMON_WORDS:
            return COMMON_WORDS[lower_word]

        # Rule 2: Suffix Morphology
        for suffix, tag in SUFFIX_RULES:
            if lower_word.endswith(suffix):
                # Exception: prevent very short words triggering rules (e.g. "lar" ending in "ar")
                if len(lower_word) > len(suffix):
                    return tag

        # Rule 3: Capitalization (Proper Noun heuristic)
        # If it's not the start of the sentence (hard to know context-free here) but matches Title case
        if word[0].isupper() and word[1:].islower():
            return "PROPN"

        # Rule 4: Fallback
        return "NOUN"

if __name__ == "__main__":
    # Initialize with 'auto' to use the best available engine
    tagger = TugaTagger(engine="brill")

    text = "O gato preto pulou o muro."

    print(f"Using engine: {tagger.engine}")
    tags = tagger.tag(text)

    for word, pos in tags:
        print(f"{word:10} -> {pos}")