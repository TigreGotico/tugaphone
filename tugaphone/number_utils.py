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

    The `scale` parameter selects which of the two engines does the
    formatting, independently of the requested dialect (`is_brazilian`).
    Since each engine bundles a full ruleset (dialect spelling AND scale
    words together), forcing e.g. `scale="short"` on a pt-PT call means
    the number is spelled entirely with the pt-BR ruleset (e.g. "trilhão"
    instead of "bilião") -- unicode_rbnf does not expose scale and dialect
    as independent axes, so this is the closest available approximation.

    Limitations:
        - Numbers whose integer part exceeds `MAX_SAFE_INTEGER` are refused
          (see `MAX_SAFE_INTEGER` below) instead of being spelled out wrong.
    """
    engine_pt = RbnfEngine.for_language("pt_PT")
    engine_br = RbnfEngine.for_language("pt")

    # RbnfEngine.format_number() casts its argument through float() (see
    # unicode_rbnf/engine.py). IEEE-754 doubles represent every integer
    # exactly only up to 2**53 - 1; beyond that, some magnitudes are
    # silently rounded to a *different* integer before being spelled out
    # (verified by execution: 9007199254741103 gets spelled as if it were
    # 9007199254741104). This ceiling applies to both scales -- it comes
    # from float precision, not from the language rules.
    MAX_SAFE_INTEGER = 2 ** 53 - 1  # 9_007_199_254_740_991

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
                              is_brazilian=False,
                              scale: Optional[str] = None) -> str:
        """
        Convert a numeric token into its spelled-out Portuguese form using surrounding context.

        Parameters:
            word (str): Numeric string to convert (e.g., "1", "2.5", "10,4", "1e9").
            prev_word (Optional[str]): Word immediately before `word`, used to infer gender.
            next_word (Optional[str]): Word immediately after `word`, used to infer ordinality and gender.
            gender (Optional[str]): Explicit gender override ("masculine" or "feminine"); if omitted a heuristic is applied.
            as_ordinal (Optional[bool]): If provided, forces ordinal (`True`) or cardinal (`False`) interpretation; otherwise context is used.
            is_brazilian (bool): If True, use Brazilian Portuguese formatting rules (pt-BR); otherwise use pt-PT.
            scale (Optional[str]): "long" or "short", overriding the scale that `is_brazilian` would
                otherwise pick (long for pt-PT, short for pt-BR). See the class docstring for the
                caveat that this also switches the dialect, since scale and dialect share one engine.

        Returns:
            Optional[str]: The spelled-out form of the number in Portuguese, or `None` if a textual form cannot be produced.

        Raises:
            ValueError: If the integer part of `word` exceeds `MAX_SAFE_INTEGER`.
        """
        if cls.is_scientific_notation(word):
            return cls.pronounce_scientific(word, is_brazilian=is_brazilian, scale=scale)

        cls._check_ceiling(word)

        # 1. Determine if the number is an ordinal (1st, 2nd) or cardinal (1, 2)
        is_ord = cls.is_ordinal(word, next_word) if as_ordinal is None else as_ordinal

        # 2. Determine grammatical gender (numbers 1, 2, and hundreds change in PT)
        gender = gender or cls.get_number_gender(word, prev_word, next_word)
        fmt = FormatPurpose.ORDINAL if is_ord else FormatPurpose.CARDINAL

        # 3. Generate the base text using RBNF (Rule-Based Number Format)
        # The ordinal markers (º/ª) are only used to detect ordinality/gender above;
        # RbnfEngine expects a plain numeric string, so strip them before formatting.
        word = word.replace(" º", "º").replace(" ª", "ª").strip()
        word = word.rstrip(cls.ORDINAL_MALE + cls.ORDINAL_FEMALE)
        # RbnfEngine expects a dot as the decimal separator; PT/BR write decimals with a comma.
        word = word.replace(",", ".", 1)
        use_short_scale = scale == "short" if scale else is_brazilian
        spelled = cls.engine_br.format_number(word, fmt) if use_short_scale else cls.engine_pt.format_number(word, fmt)

        # Select the specific ruleset based on grammar results
        if is_ord:
            key = f'spellout-ordinal-{gender}'
        else:
            key = f'spellout-cardinal-{gender}'

        text = spelled.text_by_ruleset[key]
        return text

    @classmethod
    def _check_ceiling(cls, word: str) -> None:
        """
        Raise if the integer part of `word` exceeds `MAX_SAFE_INTEGER`.

        Parameters:
            word (str): Numeric token, possibly with ordinal markers, a sign, and a decimal part.

        Raises:
            ValueError: If the integer part is larger than `MAX_SAFE_INTEGER`.
        """
        core = word.strip(cls.ORDINAL_MALE + cls.ORDINAL_FEMALE + string.whitespace)
        core = core.lstrip("+-")
        int_part = core.split(",")[0].split(".")[0]
        if int_part.isdigit() and int(int_part) > cls.MAX_SAFE_INTEGER:
            raise ValueError(
                f"'{word}' exceeds the largest integer NumberParser can spell out "
                f"correctly (MAX_SAFE_INTEGER = {cls.MAX_SAFE_INTEGER})"
            )

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
        if "." in word or "," in word:
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
        Convert a numeric string (possibly containing ordinal markers, punctuation, PT/BR comma
        decimals, or surrounding whitespace) into a float.

        Parameters:
            word (str): The input string to parse; may include ordinal symbols (º, ª), punctuation,
                a comma or dot decimal separator, scientific notation, or whitespace.

        Returns:
            float: The parsed numeric value if conversion succeeds, `None` if the input cannot be converted to a float.
        """
        try:
            # Remove ordinal markers and standard punctuation
            word = word.strip(cls.ORDINAL_MALE +
                              cls.ORDINAL_FEMALE +
                              string.whitespace)
            # PT/BR write decimals with a comma; float() only accepts a dot
            word = word.replace(",", ".", 1)
            return float(word)
        except (ValueError, TypeError):
            return None

    @classmethod
    def is_float(cls, word: str) -> bool:
        """
        Determine whether a string represents any floating-point value: a plain integer, a
        decimal (comma or dot separator), or scientific notation.

        Returns:
            `true` if the string can be parsed as a float, `false` otherwise.
        """
        return cls.to_float(word) is not None

    @classmethod
    def is_decimal(cls, word: str) -> bool:
        """
        Determine whether a token is a plain decimal number -- an integer part plus a fractional
        part separated by a comma or dot -- as opposed to a bare integer or scientific notation.

        Parameters:
            word (str): Token to test.

        Returns:
            `true` if the token is a non-scientific decimal, `false` otherwise.
        """
        if cls.is_scientific_notation(word):
            return False
        return ("," in word or "." in word) and cls.is_float(word)

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
    def pronounce_scientific(cls, word: str, is_brazilian=False, scale: Optional[str] = None) -> str:
        """
        Convert a number in scientific notation into its Portuguese spoken form.

        Parameters:
        	word (str): A numeric string in scientific notation (e.g., "1.5e10", "2,5e3").
        	is_brazilian (bool): If True, use Brazilian Portuguese variants; otherwise use Portugal variants.
        	scale (Optional[str]): "long" or "short", overriding the scale `is_brazilian` would pick.

        Returns:
        	spoken (str): The spelled-out Portuguese phrase for the notation, combining mantissa and exponent (e.g., "um vírgula cinco vezes dez elevado a dez").

        Raises:
        	ValueError: If `word` is not valid scientific notation.
        """
        if not cls.is_scientific_notation(word):
            raise ValueError(f"word is not scientific notation: '{word}'")
        a, b = word.lower().split("e")
        a_str = cls.pronounce_number_word(a, is_brazilian=is_brazilian, scale=scale)
        b_str = cls.pronounce_number_word(b, is_brazilian=is_brazilian, scale=scale)
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


def normalize_numbers(text: str, lang: str = "pt-PT", strict=True,
                       scale: Optional[str] = None) -> str:
    """
    Replace numeric tokens in a sentence with their contextually correct Portuguese written forms.

    This function normalizes the language tag (treating any variant of "pt-br" as "pt-BR"), collapses spaced ordinal markers (e.g., "1 º" -> "1º") for parsing, and converts integer, decimal and scientific-notation tokens into their spelled-out Portuguese equivalents, preserving other tokens and surrounding context.

    Parameters:
        text (str): Input sentence containing numeric and non-numeric tokens.
        lang (str): Language variant to use for spelling rules (defaults to "pt-PT"; any "pt-br" variant is treated as "pt-BR").
        strict (bool): If True, a number that cannot be spelled out (e.g. past `NumberParser.MAX_SAFE_INTEGER`) raises `ValueError`; if False, its digits are left untouched.
        scale (Optional[str]): "long" or "short", overriding the numeric scale that `lang` would otherwise pick (long for pt-PT/pt-AO/pt-MZ/pt-TL, short for pt-BR).

    Returns:
        str: The input sentence with numeric tokens replaced by their spelled-out Portuguese forms.
    """
    if "pt-br" in lang.lower():
        lang = "pt-BR"
    is_brazilian = lang == "pt-BR"
    if scale is None:
        scale = "short" if is_brazilian else "long"

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
                    word, prev_word, next_word, is_brazilian=is_brazilian, scale=scale
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
