# Number normalization

`tugaphone.number_utils` spells out numeric tokens before phonemization, with
gender agreement and long/short scale per dialect.

---

## `normalize_numbers`

```python
normalize_numbers(text: str, lang: str = "pt-PT", strict: bool = True) -> str
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

`pt-PT` uses the **long scale** (thousand million = *mil milhões*);
`pt-BR` uses the **short scale** (billion = *bilhão*).

```python
normalize_numbers("tem 19 anos", lang="pt-BR")   # 'tem dezenove anos'
normalize_numbers("tem 19 anos", lang="pt-PT")   # 'tem dezanove anos'
```

Scale is tied to the language code via `RbnfEngine` (`unicode-rbnf`). Setting
scale independently of language is not supported.

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
| `pronounce_number_word(word, prev_word=None, next_word=None, gender=None, as_ordinal=None, is_brazilian=False)` | Spelled-out form of one numeric token. |
| `to_int(word)` / `is_int(word)` | Integer value (ordinal markers stripped) / membership test. |
| `to_float(word)` / `is_float(word)` | Float value / membership test. |
| `is_scientific_notation(word)` | `True` for forms like `"1.5e10"`. |
| `pronounce_scientific(word, is_brazilian=False)` | Spoken form of scientific notation. |
| `is_ordinal(word, next_word=None)` | Detects `º`/`ª` markers, attached or separate. |
| `get_number_gender(word, prev_word=None, next_word=None)` | `"feminine"` or `"masculine"`. |

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
- The following word's ending (`-a`, `-dade`, `-agem` → feminine; default masculine)
- An explicit `gender` override passed to `pronounce_number_word`

Only numbers 1, 2, and the hundreds (100–900) change form with gender in
Portuguese.

---

## Where next

- [quickstart.md](quickstart.md) — normalize_numbers in context
- [api.md](api.md) — full `NumberParser` reference
