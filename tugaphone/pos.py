from typing import List, Tuple


class TugaTagger:
    """
    A unified interface for Portuguese Part-of-Speech (POS) tagging.

    Supports multiple backends including spaCy, NLTK, and Brill-style taggers.
    The 'auto' mode provides a fallback mechanism to ensure tagging works
    even if specific dependencies are missing.
    """

    def __init__(self, engine: str = "auto", spacy_model: str = "pt_core_news_lg"):
        """
        Initializes the TugaTagger with a specific engine.

        Args:
            engine (str): The tagging engine to use ('spacy', 'brill', 'nltk', 'dummy', or 'auto').
            spacy_model (str): The spaCy model name to load if using the spaCy engine.
        """
        self.engine = engine
        self._spacy = self._brill = None

        if engine in ["spacy", "auto"]:
            self.load_spacy(spacy_model, strict=(engine == "spacy"))
        if engine in ["brill", "auto"]:
            self.load_brill(strict=(engine == "brill"))

    def load_spacy(self, spacy_model: str = "pt_core_news_lg", strict: bool = True):
        """Loads the spaCy NLP model for Portuguese."""
        try:
            import spacy
            self._spacy = spacy.load(spacy_model, disable=["ner", "parser"])
        except Exception as e:
            if strict:
                raise e

    def load_brill(self, strict: bool = True):
        """Loads the Brill-style POS tagger."""
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
            "spacy": self.tag_spacy
        }
        handler = engines.get(self.engine)
        if not handler:
            raise ValueError(f"Invalid engine: '{self.engine}'")
        return handler(sentence)

    def tag_auto(self, sentence: str) -> List[Tuple[str, str]]:
        """Attempts tagging via Spacy, then Brill, falling back to Dummy."""
        for method in [self.tag_spacy, self.tag_brill]:
            try:
                return method(sentence)
            except:
                continue
        return self.tag_dummy(sentence)

    @staticmethod
    def tag_dummy(sentence: str) -> List[Tuple[str, str]]:
        """Simple fallback: splits by whitespace and tags everything as NOUN."""
        words = sentence.split()
        return [(word, "NOUN") for word in words]

    def tag_brill(self, sentence: str) -> List[Tuple[str, str]]:
        """Tags text using the BrillPostagger."""
        if self._brill is None:
            self.load_brill()
        return self._brill.tag(sentence)

    def tag_spacy(self, sentence: str) -> List[Tuple[str, str]]:
        """Tags text using spaCy's POS model."""
        if self._spacy is None:
            self.load_spacy()
        doc = self._spacy(sentence)
        return [(tok.text, tok.pos_) for tok in doc]



if __name__ == "__main__":
    # Initialize with 'auto' to use the best available engine
    tagger = TugaTagger(engine="brill")

    text = "O gato preto pulou o muro."

    print(f"Using engine: {tagger.engine}")
    tags = tagger.tag(text)

    for word, pos in tags:
        print(f"{word:10} -> {pos}")