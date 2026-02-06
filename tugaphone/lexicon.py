import os
from typing import Dict, List, Tuple, Optional


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
        self.dictionary_path = dictionary_path or os.path.join(
            os.path.dirname(__file__), "regional_dict.csv"
        )
        self.ipa, self.syllables = self._load_lang_map(self.dictionary_path)

    @staticmethod
    def _load_lang_map(path: str) -> Tuple[Dict[str, Dict[str, Dict[str, str]]], List[str]]:
        """Load region/language phoneme mappings from a CSV file.

        Expected CSV columns:
            _, word, pos, _, phonemes, _, region
        """
        ipa: Dict[str, Dict[str, Dict[str, str]]] = {}
        syllables: Dict[str, List[str]] = {}

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
        """Convert ISO dialect code (pt-PT, pt-BR, etc.) to dataset region code."""
        try:
            return self._DIALECT_REGIONS[lang]
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {lang}") from e

    def get_phonemes(self, word: str, pos: str = "NOUN", region: str = "lbx") -> Optional[str]:
        return self.ipa[region].get(word, {}).get(pos)

    def get_syllables(self, word: str, region: str = "lbx") -> Optional[str]:
        return self.syllables[region].get(word, {})

    def get(self, word: str, pos: str = "NOUN", region: str = "lbx") -> Dict[str, str]:
        return {
            "syllables": self.get_syllables(word, region),
            "phonemes": self.get_phonemes(word, pos, region),
        }

    def get_wordlist(self, region: str = "lbx") -> List[str]:
        return sorted(self.syllables[region].keys())

if __name__ == "__main__":
    ph = TugaLexicon()

    for w in ph.get_wordlist():
        gold_pho = ph.get_phonemes(w)
        if gold_pho:
            print(w, gold_pho)
