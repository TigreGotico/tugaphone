from typing import List, Tuple


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
            "spacy": self.tag_spacy
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
        for method in [self.tag_spacy, self.tag_brill]:
            try:
                return method(sentence)
            except:
                continue
        return self.tag_dummy(sentence)

    @staticmethod
    def tag_dummy(sentence: str) -> List[Tuple[str, str]]:
        """
        Split the sentence on whitespace and tag each token as the noun "NOUN".

        Returns:
            List[Tuple[str, str]]: A list of (word, tag) tuples where each whitespace-separated token from the input is paired with the tag "NOUN".
        """
        words = sentence.split()
        return [(word, "NOUN") for word in words]

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



if __name__ == "__main__":
    # Initialize with 'auto' to use the best available engine
    tagger = TugaTagger(engine="brill")

    text = "O gato preto pulou o muro."

    print(f"Using engine: {tagger.engine}")
    tags = tagger.tag(text)

    for word, pos in tags:
        print(f"{word:10} -> {pos}")