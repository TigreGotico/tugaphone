import os
from typing import Dict, List, Tuple, Optional

# Typing helpers
IPA_MAP = Dict[str, Dict[str, Dict[str, str]]]
SYLLABLE_MAP = Dict[str, List[str]]


class TugaLexicon:
    """
    Supports:
        - pt-PT (Portugal)
        - pt-BR (Brazil)
        - pt-AO (Angola)
        - pt-MZ (Mozambique)
        - pt-TL (Timor-Leste)
    """
    _DIALECT_REGIONS = {
        "pt-PT": "lbx",
        "pt-BR": "rjx",
        "pt-AO": "lda",
        "pt-MZ": "mpx",
        "pt-TL": "dli",
    }

    def __init__(self, dictionary_path: str = None):
        """
        Initialize the TugaLexicon and load regional phoneme and syllable data.

        Parameters:
            dictionary_path (str, optional): Path to the CSV file containing regional phoneme and syllable mappings.
                If not provided, defaults to "regional_dict.csv" located in the same directory as this module.

        Description:
            Loads the dataset at `dictionary_path` and populates `self.ipa` and `self.syllables` with region-specific
            phoneme and syllable mappings.
        """
        self.dictionary_path = dictionary_path or os.path.join(
            os.path.dirname(__file__), "regional_dict.csv"
        )
        self.ipa, self.syllables = self._load_lang_map(self.dictionary_path)

    @staticmethod
    def _load_lang_map(path: str) -> Tuple[IPA_MAP, SYLLABLE_MAP]:
        """
        Load phoneme and syllable mappings from a CSV into region-indexed lookup structures.

        The CSV is expected to have columns in this order (header is skipped): _, word, pos, _, phonemes, _, region.
        - `phonemes` entries use `|` as an internal separator in the file and will be represented using the middle dot `·` in the returned data.
        - `word` and `region` values are normalized to lowercase.

        Parameters:
            path (str): Path to the CSV file.

        Returns:
            Tuple[Dict[str, Dict[str, Dict[str, str]]], Dict[str, List[str]]]:
                - ipa: mapping region -> word -> POS -> phoneme string (POS keys are uppercase).
                - syllables: mapping region -> word -> list of syllable segments.
        """
        ipa: IPA_MAP = {}
        syllables: SYLLABLE_MAP = {}

        with open(path, "r", encoding="utf-8") as f:
            for line in f.read().splitlines()[1:]:  # skip header
                _, word, pos, _, phonemes, syl, region = line.lower().split(",", 6)
                phonemes = phonemes.replace("|", "·").strip()
                word = word.strip().lower()
                region = region.strip()
                if region not in syllables:
                    syllables[region] = {}
                if region not in ipa:
                    ipa[region] = {}
                if word not in ipa[region]:
                    ipa[region][word] = {}
                syllables[region][word] = syl.strip().replace(" ", "|").split("|")
                ipa[region][word][pos.upper()] = phonemes

        return ipa, syllables

    def lang_to_region(self, lang: str) -> str:
        """
        Map an ISO Portuguese dialect code to the internal dataset region code.

        Parameters:
            lang (str): ISO dialect code (e.g., "pt-PT", "pt-BR").

        Returns:
            region (str): Corresponding dataset region code (e.g., "lbx", "rjx").

        Raises:
            ValueError: If the provided dialect code is not supported.
        """
        try:
            return self._DIALECT_REGIONS[lang]
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {lang}") from e

    def get_phonemes(self, word: str, pos: str = "NOUN", region: str = "lbx") -> Optional[str]:
        """
        Retrieve the phoneme transcription for a word in a specific region and part of speech.

        Parameters:
            word: The word to look up; matching is case-insensitive because entries are normalized to lowercase.
            pos: Part-of-speech tag to select the transcription variant (default: "NOUN").
            region: Region code identifying the dialect dataset (e.g., "lbx").

        Returns:
            The phoneme string for the specified word and POS in the region, or None if no entry exists.
        """
        return self.ipa[region].get(word, {}).get(pos)

    def get_syllables(self, word: str, region: str = "lbx") -> Optional[str]:
        """
        Retrieve the syllable segments for a word in the given region.

        Parameters:
            word (str): The target word, normalized to lowercase.
            region (str): Dataset region code (e.g. 'lbx', 'rjx', 'lda', 'mpx', 'dli').

        Returns:
            list[str]: List of syllable strings for the word if present.
            {}: An empty mapping if the word is not found for the region.
        """
        try:
            return self.syllables[region].get(word, {})
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {region}") from e

    def get(self, word: str, pos: str = "NOUN", region: str = "lbx") -> Dict[str, str]:
        """
        Retrieve both syllable segmentation and phoneme transcription for a word in a given region and part of speech.

        Parameters:
            word (str): The lookup word (case-insensitive).
            pos (str): Part-of-speech tag to select the phoneme variant (default: "NOUN").
            region (str): Region code to query (e.g. "lbx") (default: "lbx").

        Returns:
            dict: A mapping with keys:
                - "syllables": list of syllable segments for the word in the region, or `None` if not found.
                - "phonemes": phoneme transcription for the given POS and region, or `None` if not found.
        """
        return {
            "syllables": self.get_syllables(word, region),
            "phonemes": self.get_phonemes(word, pos, region),
        }

    def get_wordlist(self, region: str = "lbx") -> List[str]:
        """
        Return a sorted list of words available for the given region.

        Parameters:
            region (str): Region code (e.g., "lbx") identifying the dataset to query.

        Returns:
            List[str]: Words available in the lexicon for the region, sorted alphabetically.
        """
        try:
            return sorted(self.syllables[region].keys())
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {region}") from e

if __name__ == "__main__":
    ph = TugaLexicon()

    for w in ph.get_wordlist():
        gold_pho = ph.get_phonemes(w)
        if gold_pho:
            print(w, gold_pho)
