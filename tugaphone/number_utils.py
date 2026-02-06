import string
from typing import Optional

from unicode_rbnf import RbnfEngine, FormatPurpose


class NumberParser:
    """
    A utility class to convert digits into their spelled-out Portuguese equivalent.

    In Portuguese, numbers must agree in gender (masculine/feminine) and
    type (cardinal/ordinal) with the nouns they modify.
    Example: '1' can be 'um' (masc.), 'uma' (fem.), 'primeiro' (1st masc.), or 'primeira' (1st fem.).

    Limitations:
        - after one billion results may be incorrect for pt-PT, long-scale vs short-scale is not modelled!
          https://en.wikipedia.org/wiki/Long_and_short_scales
          https://pt.wikipedia.org/wiki/Escalas_curta_e_longa
        NOTE: RbnfEngine defaults to pt-BR and short scale. output will be "bilhões" not "biliões"
    """

    engine = RbnfEngine.for_language("pt")

    # Symbols used in PT to denote ordinals (like the English 'st', 'nd', 'rd')
    ORDINAL_MALE = "º"  # e.g., 1º (primeiro)
    ORDINAL_FEMALE = "ª"  # e.g., 1ª (primeira)
    ORDINAL_TOKENS = [ORDINAL_MALE, ORDINAL_FEMALE]

    # Regional differences: numbers 16, 17, and 19 use 'e' in Brazil and 'a' in Portugal.
    # pt-BR: dez-e-sseis | pt-PT: dez-a-sseis
    # NOTE: RbnfEngine defaults to pt-BR
    BR2PT = {
        "dezesseis": "dezasseis",
        "dezessete": "dezassete",
        "dezenove": "dezanove"
    }

    @classmethod
    def pronounce_number_word(cls, word: str,
                              prev_word: Optional[str] = None,
                              next_word: Optional[str] = None,
                              gender: Optional[str] = None,
                              as_ordinal: Optional[bool] = None,
                              is_brazilian=False) -> Optional[str]:
        """
        Converts a numeric string into spelled-out text based on surrounding context.

        Args:
            word: The digit string (e.g., "1").
            prev_word: The word appearing before the digit.
            next_word: The word appearing after the digit.
            gender: Explicit override for gender ('masculine'/'feminine').
            as_ordinal: Explicit override to treat number as an ordinal.
            is_brazilian: If True, uses Brazil's spelling (pt-BR).
        """
        # TODO: account for short/long scale
        scale = "short" if is_brazilian else "long"
        # TODO: if scientific notation, pronounce explicitly
        if cls.is_scientific_notation(word):
            pass

        # 1. Determine if the number is an ordinal (1st, 2nd) or cardinal (1, 2)
        is_ord = cls.is_ordinal(word, next_word) if as_ordinal is None else as_ordinal

        # 2. Determine grammatical gender (numbers 1, 2, and hundreds change in PT)
        gender = gender or cls.get_number_gender(word, prev_word, next_word)
        fmt = FormatPurpose.ORDINAL if is_ord else FormatPurpose.CARDINAL

        # 3. Generate the base text using RBNF (Rule-Based Number Format)
        spelled = cls.engine.format_number(word, fmt)

        # Select the specific ruleset based on grammar results
        if is_ord:
            key = f'spellout-ordinal-{gender}'
        else:
            key = f'spellout-cardinal-{gender}'

        text = spelled.text_by_ruleset[key]

        # 4. Handle European Portuguese (pt-PT) variations if necessary
        return cls.BR2PT.get(text, text) if not is_brazilian else text

    # digit/string conversion
    @classmethod
    def pronounce_int(cls, number: int, as_ordinal=False, gender: str = "m"):
        """Directly spells out an integer given specific parameters."""
        gender = 'masculine' if "f" not in gender else "feminine"
        fmt = FormatPurpose.ORDINAL if as_ordinal else FormatPurpose.CARDINAL
        spelled = cls.engine.format_number(number, fmt)

        ord_key = f'spellout-ordinal-{gender}' if as_ordinal else f'spellout-cardinal-{gender}'
        return spelled.text_by_ruleset[ord_key]

    @classmethod
    def to_int(cls, word: str) -> Optional[int]:
        """Cleans a string of punctuation/symbols and converts to integer."""
        if "." in word:
            return False  # may be a decimal
        try:
            # Remove ordinal markers and standard punctuation
            word = word.strip(cls.ORDINAL_MALE +
                              cls.ORDINAL_FEMALE +
                              string.punctuation + string.whitespace)
            return int(word)
        except (ValueError, TypeError):
            return None

    @classmethod
    def is_int(cls, word: str) -> bool:
        return cls.to_int(word) is not None

    @classmethod
    def to_float(cls, word: str) -> Optional[float]:
        """Cleans a string of punctuation/symbols and converts to a float."""
        try:
            # Remove ordinal markers and standard punctuation
            word = word.strip(cls.ORDINAL_MALE +
                              cls.ORDINAL_FEMALE +
                              string.punctuation + string.whitespace)
            return float(word)
        except (ValueError, TypeError):
            return None

    @classmethod
    def is_float(cls, word: str) -> bool:
        return cls.to_int(word) is not None

    @classmethod
    def is_scientific_notation(cls, word: str) -> bool:
        nums = word.lower().split("e")
        if len(nums) != 2:
            return False
        return nums[0].isdigit() and nums[1].isdigit()

    # contextual rules
    @classmethod
    def is_ordinal(cls, word: str, next_word: Optional[str] = None) -> bool:
        """Checks if the number is meant to be an ordinal (1st, 2nd, etc)."""
        # Check if the symbol is a separate token or attached to the number
        if next_word in cls.ORDINAL_TOKENS:
            return True
        elif any(t in word for t in cls.ORDINAL_TOKENS):
            return True
        return False

    @classmethod
    def get_number_gender(cls, word: str,
                          prev_word: Optional[str] = None,
                          next_word: Optional[str] = None) -> str:
        """
        Linguistic Heuristics to determine if the number should be Male or Female.
        Defaults to Masculine as it is the 'neutral' gender in Portuguese.
        """
        # Rule A: Ordinal symbols explicitly dictate gender (º = masc, ª = fem)
        if next_word and next_word == cls.ORDINAL_FEMALE or cls.ORDINAL_FEMALE in word:
            return "feminine"

        # Rule B: Check preceding articles/prepositions (a, as, da, das are feminine)
        if prev_word and prev_word in ["a", "as", "da", "das"]:
            return "feminine"

        # Rule C: Check the following noun (the object being counted)
        if next_word:
            # Simple check: Words ending in 'a' are usually feminine (e.g., 'casa')
            # We strip 's' to account for plural nouns.
            if next_word.strip("s").lower().endswith("a"):
                # 1 casa (house) -> uma casa (female)
                # 1 cão (dog) -> um cão (male)
                return "feminine"

            # Rule D: Handle tricky '-e' endings
            # Words ending in -dade, -age, or -agem are consistently feminine.
            elif next_word.strip("sm").lower().endswith("e"):
                # words ending with "e" may be either male, female or both
                # a wordlist is needed to be sure
                # 1 ponte (bridge) -> uma ponte  (female)
                # 1 dente (tooth) -> um dente  (male)
                # 1 cliente -> um(a) cliente
                female_endings = ["dade", "age", "agem"]
                # -dade (Feminine): Words like felicidade (happiness), cidade (city), and liberdade (freedom) are always feminine.
                # -age / -agem (Feminine): Words like viagem (trip) or coragem (courage) are feminine.
                if any(next_word.endswith(f) for f in female_endings):
                    return "feminine"
        # by default numbers are male in portuguese
        return "masculine"


def normalize_numbers(text: str) -> str:
    """
    Iterates through a sentence and replaces digits with their
    contextually correct Portuguese written form.
    """
    # Pre-process: ensure symbols like 1 º become 1º for easier parsing
    words = text.replace(" º", "º").replace(" ª", "ª").split()
    normalized_words = []

    for idx, word in enumerate(words):
        # is this word a number?
        int_word = NumberParser.to_int(word)
        if int_word is not None:
            # Lookahead and Lookbehind for grammatical context
            next_word = words[idx + 1] if idx + 1 < len(words) else None
            prev_word = words[idx - 1] if idx - 1 >= 0 else None
            # spell out the number
            normalized_words.append(
                NumberParser.pronounce_number_word(word, prev_word, next_word)
            )
        else:
            normalized_words.append(word)

    return " ".join(normalized_words)


if __name__ == "__main__":
    # Test regional spelling (19)
    print(f"BR: {NumberParser.pronounce_number_word('19', is_brazilian=True)}")
    print(f"PT: {NumberParser.pronounce_number_word('19', is_brazilian=False)}")

    # Test gender agreement
    print(normalize_numbers("vou comprar 1 casa"))  # uma (fem)
    print(normalize_numbers("vou comprar 2 casas"))  # duas (fem)
    print(normalize_numbers("vou adotar 1 cão"))  # um (masc)
    print(normalize_numbers("vou adotar 2 cães"))  # dois (masc)

    # Test -e suffix rule (cidade = fem)
    print(normalize_numbers("visitei 1 cidade"))  # uma (fem)


    print(normalize_numbers("897654356789098"))
    print(normalize_numbers("1e9"))  # uma (fem)
