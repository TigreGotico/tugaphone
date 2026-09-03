# Number normalization

`tugaphone.number_utils` spells out numeric tokens before phonemization, with
gender agreement and a long/short scale that defaults to the dialect and can
be overridden independently.

---

## `normalize_numbers`

```python
normalize_numbers(text: str, lang: str = "pt-PT", strict: bool = True, scale: str | None = None) -> str
```

Replaces every numeric token in `text` with its Portuguese written form.
Gender and ordinality are inferred from the surrounding words.

```python
from tugaphone.number_utils import normalize_numbers

normalize_numbers("vou comprar 1 casa")    # 'vou comprar uma casa'
normalize_numbers("vou adotar 1 cão")     # 'vou adotar um cão'
normalize_numbers("comprei 2 casas")      # 'comprei duas casas'
normalize_numbers("tem 19 anos")          # 'tem dezanove anos'
```

Pass `strict=False` to leave tokens that fail to format in place instead of
raising:

```python
normalize_numbers("abc 1 xyz", strict=False)
```

---

## Number scale

`pt-PT` (and `pt-AO`/`pt-MZ`/`pt-TL`) default to the **long scale** (thousand
million = *mil milhões*, billion = *bilião*); `pt-BR` defaults to the **short
scale** (billion = *bilhão*).

```python
normalize_numbers("tem 19 anos", lang="pt-BR")   # 'tem dezenove anos'
normalize_numbers("tem 19 anos", lang="pt-PT")   # 'tem dezanove anos'

normalize_numbers("1000000000000", lang="pt-PT")               # 'um bilião'  (long)
normalize_numbers("1000000000000", lang="pt-BR")               # 'um trilhão' (short)
```

Pass `scale="long"` or `scale="short"` to override the scale the language
would otherwise pick:

```python
normalize_numbers("1000000000000", lang="pt-PT", scale="short")  # 'um trilhão'
normalize_numbers("1000000000000", lang="pt-BR", scale="long")   # 'um bilião'
```

`unicode-rbnf` bundles scale and dialect spelling into a single ruleset per
language, so overriding `scale` also switches which ruleset spells the rest
of the number (e.g. `pt-PT` forced to `scale="short"` is spelled entirely
with the `pt-BR` ruleset). There is no way to mix a pt-PT dialect with
short-scale words in the underlying library.

---

## Decimals and scientific notation

Decimals may use either a comma or a dot as the separator; both read out with
*vírgula*:

```python
normalize_numbers("tem 10,4 graus")   # 'tem dez vírgula quatro graus'
normalize_numbers("tem 10.4 graus")   # 'tem dez vírgula quatro graus'
```

Scientific notation (`<mantissa>e<exponent>`, mantissa may itself be a comma
or dot decimal) reads out as "... vezes dez elevado a ...":

```python
normalize_numbers("1e6")     # 'um vezes dez elevado a seis'
normalize_numbers("2,5e3")   # 'dois vírgula cinco vezes dez elevado a três'
normalize_numbers("1.5e10")  # 'um vírgula cinco vezes dez elevado a dez'
```

`NumberParser.is_decimal(word)` tells a plain decimal apart from scientific
notation; `NumberParser.is_scientific_notation(word)` detects the latter.

---

## Number ceiling

`NumberParser.MAX_SAFE_INTEGER` (`2**53 - 1 = 9007199254740991`) is the
largest integer part `normalize_numbers` and `NumberParser.pronounce_number_word`
will spell out. The limit comes from `unicode-rbnf`'s `RbnfEngine`, which
casts numbers through a Python `float` internally: IEEE-754 doubles only
represent every integer exactly up to `2**53 - 1`, and beyond that some
values silently round to a *different* integer before being spelled out
(e.g. `9007199254741103` gets read as if it were `9007199254741104`).

Past the ceiling, `normalize_numbers` and `pronounce_number_word` raise
`ValueError` instead of producing a wrong reading:

```python
NumberParser.MAX_SAFE_INTEGER          # 9007199254740991
normalize_numbers("9007199254740992")  # raises ValueError
normalize_numbers("9007199254740992", strict=False)  # '9007199254740992' (left untouched)
```

The ceiling applies equally to both scales; the largest value each dialect
can still spell correctly is:

```python
NumberParser.pronounce_number_word("9007199254740991")
# 'nove mil biliões sete biliões cento e noventa e nove mil milhões
#  duzentos e cinquenta e quatro milhões setecentos e quarenta mil
#  novecentos e noventa e um'
NumberParser.pronounce_number_word("9007199254740991", is_brazilian=True)
# 'nove quatrilhões sete trilhões cento e noventa e nove bilhões
#  duzentos e cinquenta e quatro milhões setecentos e quarenta mil
#  novecentos e noventa e um'
```

---

## Ordinal forms

Ordinals are detected from attached ordinal markers (`1º`, `1ª`) or by forcing
them via `NumberParser`:

```python
from tugaphone.number_utils import NumberParser

NumberParser.pronounce_number_word("1", as_ordinal=True, gender="masculine")  # 'primeiro'
NumberParser.pronounce_number_word("1", as_ordinal=True, gender="feminine")   # 'primeira'
```

---

## `NumberParser` API

`NumberParser` is the classmethod-based helper underneath `normalize_numbers`.
Use it for single-token control.

| Method | Returns |
|--------|---------|
| `pronounce_number_word(word, prev_word=None, next_word=None, gender=None, as_ordinal=None, is_brazilian=False, scale=None)` | Spelled-out form of one numeric token; raises `ValueError` past `MAX_SAFE_INTEGER`. |
| `to_int(word)` / `is_int(word)` | Integer value (ordinal markers, comma/dot decimals stripped out) / membership test. |
| `to_float(word)` / `is_float(word)` | Float value (comma or dot decimal, scientific notation) / membership test. |
| `is_decimal(word)` | `True` for a non-scientific decimal like `"10,4"` or `"10.4"`. |
| `is_scientific_notation(word)` | `True` for forms like `"1.5e10"` or `"2,5e3"`. |
| `pronounce_scientific(word, is_brazilian=False, scale=None)` | Spoken form of scientific notation. |
| `is_ordinal(word, next_word=None)` | Detects `º`/`ª` markers, attached or separate. |
| `get_number_gender(word, prev_word=None, next_word=None)` | `"feminine"` or `"masculine"`. |
| `MAX_SAFE_INTEGER` | `9007199254740991` (`2**53 - 1`), the largest integer part guaranteed to spell out correctly. |

```python
from tugaphone.number_utils import NumberParser

NumberParser.pronounce_number_word("19", is_brazilian=True)   # 'dezenove'
NumberParser.pronounce_number_word("19", is_brazilian=False)  # 'dezanove'
NumberParser.get_number_gender("1", next_word="casa")         # 'feminine'
```

---

## Gender inference

Gender is inferred from:
- The preceding word (articles `a`, `as`, `da`, `das` → feminine)
- The following word's ending (`-a`, `-dade`, `-agem` → feminine, default masculine)
- An explicit `gender` override passed to `pronounce_number_word`

Only numbers 1, 2, and the hundreds (100 to 900) change form with gender in
Portuguese.

---

## Where next

- [quickstart.md](quickstart.md), normalize_numbers in context
- [text_normalization.md](text_normalization.md), the orthographic rewrites that run before `normalize_numbers`
- [api.md](api.md), full `NumberParser` reference


---
[← Code-switch](codeswitch.md) · [Home](../README.md) · [Text normalization →](text_normalization.md)
