import string
from typing import Optional

from unicode_rbnf import RbnfEngine, FormatPurpose


class NumberParser:
    """
    A utility class to convert digits into their spelled-out Portuguese equivalent.

    In Portuguese, numbers must agree in gender (masculine/feminine) and
    type (cardinal/ordinal) with the nouns they modify.
    Example: '1' can be 'um' (masc.), 'uma' (fem.), 'primeiro' (1st masc.), or 'primeira' (1st fem.).

    NOTE: RbnfEngine defaults to short-scale for pt-BR and long-scale for pt-PT.
          https://en.wikipedia.org/wiki/Long_and_short_scales
          https://pt.wikipedia.org/wiki/Escalas_curta_e_longa

    Limitations:
        - Can not set number scale independently of language
        - Can not handle very large numbers  TODO: document max value
    """
    engine_pt = RbnfEngine.for_language("pt_PT")
    engine_br = RbnfEngine.for_language("pt")

    # Symbols used in PT to denote ordinals (like the English 'st', 'nd', 'rd')
    ORDINAL_MALE = "º"  # e.g., 1º (primeiro)
    ORDINAL_FEMALE = "ª"  # e.g., 1ª (primeira)
    ORDINAL_TOKENS = [ORDINAL_MALE, ORDINAL_FEMALE]

    @classmethod
    def pronounce_number_word(cls, word: str,
                              prev_word: Optional[str] = None,
                              next_word: Optional[str] = None,
                              gender: Optional[str] = None,
                              as_ordinal: Optional[bool] = None,
                              is_brazilian=False) -> str:
        """
        Convert a numeric token into its spelled-out Portuguese form using surrounding context.

        Parameters:
            word (str): Numeric string to convert (e.g., "1", "2.5", "1e9").
            prev_word (Optional[str]): Word immediately before `word`, used to infer gender.
            next_word (Optional[str]): Word immediately after `word`, used to infer ordinality and gender.
            gender (Optional[str]): Explicit gender override ("masculine" or "feminine"); if omitted a heuristic is applied.
            as_ordinal (Optional[bool]): If provided, forces ordinal (`True`) or cardinal (`False`) interpretation; otherwise context is used.
            is_brazilian (bool): If True, use Brazilian Portuguese formatting rules (pt-BR); otherwise use pt-PT.

        Returns:
            Optional[str]: The spelled-out form of the number in Portuguese, or `None` if a textual form cannot be produced.
        """
        # TODO: allow scale independent from language code
        #       ie. enable pt-PT+short-scale and pt-BR+long-scale
        if cls.is_scientific_notation(word):
            return cls.pronounce_scientific(word, is_brazilian=is_brazilian)

        # 1. Determine if the number is an ordinal (1st, 2nd) or cardinal (1, 2)
        is_ord = cls.is_ordinal(word, next_word) if as_ordinal is None else as_ordinal

        # 2. Determine grammatical gender (numbers 1, 2, and hundreds change in PT)
        gender = gender or cls.get_number_gender(word, prev_word, next_word)
        fmt = FormatPurpose.ORDINAL if is_ord else FormatPurpose.CARDINAL

        # 3. Generate the base text using RBNF (Rule-Based Number Format)
        word = word.replace(" º", "º").replace(" ª", "ª").strip()
        spelled = cls.engine_br.format_number(word, fmt) if is_brazilian else cls.engine_pt.format_number(word, fmt)

        # Select the specific ruleset based on grammar results
        if is_ord:
            key = f'spellout-ordinal-{gender}'
        else:
            key = f'spellout-cardinal-{gender}'

        text = spelled.text_by_ruleset[key]
        return text

    # digit/string conversion
    @classmethod
    def to_int(cls, word: str) -> Optional[int]:
        """
        Parse a numeric token into an integer after stripping ordinal markers and surrounding punctuation/whitespace.

        Parameters:
            word (str): Input token which may contain ordinal symbols (º, ª), punctuation, or surrounding whitespace.

        Returns:
            int: The parsed integer value on success.
            None: If the token contains a decimal point (treated as a non-integer) or cannot be parsed as an integer after cleaning.
        """
        if "." in word:
            return None  # may be a decimal
        try:
            # Remove ordinal markers and standard punctuation
            word = word.strip(cls.ORDINAL_MALE +
                              cls.ORDINAL_FEMALE +
                              string.whitespace)
            return int(word)
        except (ValueError, TypeError):
            return None

    @classmethod
    def is_int(cls, word: str) -> bool:
        """
        Determine whether a token represents an integer (no decimal point).

        Parameters:
            word (str): Input token; ordinal markers (º, ª), punctuation and spaces are ignored during validation.

        Returns:
            bool: `True` if the token can be parsed to an integer after cleaning, `False` otherwise.
        """
        return cls.to_int(word) is not None

    @classmethod
    def to_float(cls, word: str) -> Optional[float]:
        """
        Convert a numeric string (possibly containing ordinal markers, punctuation, or surrounding whitespace) into a float.

        Parameters:
            word (str): The input string to parse; may include ordinal symbols (º, ª), punctuation, or whitespace.

        Returns:
            float: The parsed numeric value if conversion succeeds, `None` if the input cannot be converted to a float.
        """
        try:
            # Remove ordinal markers and standard punctuation
            word = word.strip(cls.ORDINAL_MALE +
                              cls.ORDINAL_FEMALE +
                              string.whitespace)
            return float(word)
        except (ValueError, TypeError):
            return None

    @classmethod
    def is_float(cls, word: str) -> bool:
        """
        Determine whether a string represents a decimal/floating point number.

        TODO: differentiate float and decimal , float also handles scientific notation
        Returns:
            `true` if the string can be parsed as a float, `false` otherwise.
        """
        return cls.to_float(word) is not None

    @classmethod
    def is_scientific_notation(cls, word: str) -> bool:
        """
        Check whether a token uses scientific notation with a decimal mantissa and an integer exponent separated by 'e' (case-insensitive).

        Parameters:
            word (str): Token to test; the mantissa may include a decimal point, and the exponent must consist of digits.

        Returns:
            `true` if the token is scientific notation (e.g., "1.5e10"), `false` otherwise.
        """
        nums = word.lower().split("e")
        if len(nums) != 2:
            return False
        # NOTE: cant use .isdigit() in order to allow decimals and negative numbers
        return cls.is_float(nums[0]) and cls.is_int(nums[1])

    @classmethod
    def pronounce_scientific(cls, word: str, is_brazilian=False) -> str:
        """
        Convert a number in scientific notation into its Portuguese spoken form.

        Parameters:
        	word (str): A numeric string in scientific notation (e.g., "1.5e10").
        	is_brazilian (bool): If True, use Brazilian Portuguese variants; otherwise use Portugal variants.

        Returns:
        	spoken (str): The spelled-out Portuguese phrase for the notation, combining mantissa and exponent (e.g., "um vírgula cinco vezes dez elevado a dez").

        Raises:
        	ValueError: If `word` is not valid scientific notation.
        """
        if not cls.is_scientific_notation(word):
            raise ValueError(f"word is not scientific notation: '{word}'")
        a, b = word.lower().split("e")
        a_str = cls.pronounce_number_word(a, is_brazilian=is_brazilian)
        b_str = cls.pronounce_number_word(b, is_brazilian=is_brazilian)
        return f"{a_str} vezes dez elevado a {b_str}"

    # contextual rules
    @classmethod
    def is_ordinal(cls, word: str, next_word: Optional[str] = None) -> bool:
        """
        Determine whether a token represents an ordinal number.

        Parameters:
            word (str): The token to check.
            next_word (Optional[str]): The following token; used to detect a separated ordinal marker (e.g., "º", "ª").

        Returns:
            `true` if the word contains an ordinal marker or the next_token is an ordinal marker, `false` otherwise.
        """
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
        Determine the grammatical gender (masculine or feminine) that a numeric token should take in Portuguese.

        Parameters:
            word (str): The numeric token (may include ordinal symbols like 'º' or 'ª').
            prev_word (Optional[str]): The preceding word in context, used for heuristic cues (e.g., articles).
            next_word (Optional[str]): The following word in context, used to infer the gender of the counted noun.

        Returns:
            str: "feminine" if the number should agree as feminine, "masculine" otherwise.
        """
        # Rule A: Ordinal symbols explicitly dictate gender (º = masc, ª = fem)
        if (next_word and next_word == cls.ORDINAL_FEMALE) or cls.ORDINAL_FEMALE in word:
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
            elif next_word.rstrip("sm").lower().endswith("e"):
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


def normalize_numbers(text: str, lang: str = "pt-PT", strict=True) -> str:
    """
    Replace numeric tokens in a sentence with their contextually correct Portuguese written forms.

    This function normalizes the language tag (treating any variant of "pt-br" as "pt-BR"), collapses spaced ordinal markers (e.g., "1 º" -> "1º") for parsing, and converts integer, float and scientific-notation tokens into their spelled-out Portuguese equivalents, preserving other tokens and surrounding context.

    Parameters:
        text (str): Input sentence containing numeric and non-numeric tokens.
        lang (str): Language variant to use for spelling rules (defaults to "pt-PT"; any "pt-br" variant is treated as "pt-BR").
        strict (bool): raise or ignore exceptions in RbnfEngine

    Returns:
        str: The input sentence with numeric tokens replaced by their spelled-out Portuguese forms.
    """
    if "pt-br" in lang.lower():
        lang = "pt-BR"

    # Pre-process: ensure symbols like 1 º become 1º for easier parsing
    words = text.replace(" º", "º").replace(" ª", "ª").split()
    normalized_words = []

    for idx, word in enumerate(words):
        # is this word a number?
        is_num = NumberParser.is_int(word) or NumberParser.is_float(word)
        if is_num:
            # Lookahead and Lookbehind for grammatical context
            next_word = words[idx + 1] if idx + 1 < len(words) else None
            prev_word = words[idx - 1] if idx - 1 >= 0 else None
            # spell out the number
            try:
                spelled = NumberParser.pronounce_number_word(
                    word, prev_word, next_word, is_brazilian=lang == "pt-BR"
                )
                normalized_words.append(spelled)
            except Exception as e:
                if strict:
                    raise e
                normalized_words.append(word)
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


    print(normalize_numbers("897654356789098", "pt-PT")) # long-scale
    # oitocentos e noventa e sete biliões seiscentos e cinquenta e quatro mil milhões trezentos e cinquenta e seis milhões setecentos e oitenta e nove mil e noventa e oito
    print(normalize_numbers("897654356789098", "pt-BR")) # short-scale
    # oitocentos e noventa e sete trilhões seiscentos e cinquenta e quatro bilhões trezentos e cinquenta e seis milhões setecentos e oitenta e nove mil e noventa e oito

    print(normalize_numbers("1e-3")) # um vezes dez elevado a nove
    print(normalize_numbers("1e9")) # um vezes dez elevado a nove
    print(normalize_numbers("1.5e10"))  # um vírgula cinco vezes dez elevado a dez
    print(normalize_numbers("1.5e10000000")) # um vírgula cinco vezes dez elevado a dez milhões
