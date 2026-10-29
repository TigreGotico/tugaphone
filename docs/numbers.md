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
would otherwise pick, while keeping the dialect's own spelling:

```python
normalize_numbers("1000000000000", lang="pt-PT", scale="short")  # 'um trilião'
normalize_numbers("1000000000000", lang="pt-BR", scale="long")   # 'um bilhão'
```

The long-scale words (pt-PT, pt-AO, pt-MZ, pt-TL) are: *milhão* (10⁶), *mil
milhões* (10⁹), *bilião* (10¹²), *mil biliões* (10¹⁵), *trilião* (10¹⁸),
*quatrilião* (10²⁴). The short-scale words (pt-BR) are: *milhão* (10⁶),
*bilhão* (10⁹), *trilhão* (10¹²), *quatrilhão* (10¹⁵), *quintilhão* (10¹⁸),
*sextilhão* (10²¹), *septilhão* (10²⁴).

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

When the decimal comes from [`normalize_orthography`](text_normalization.md),
the comma is already the word *vírgula* and the fractional digits are a token
of their own. Their leading zeros are read one by one, and the integer part
agrees with the noun after the whole decimal, not with *vírgula*:

```python
normalize_numbers("0 vírgula 02")      # 'zero vírgula zero dois'
normalize_numbers("2 vírgula 5 anos")  # 'dois vírgula cinco anos'
```

---

## Units, percent and euros

A number followed by a unit symbol in `NumberParser.UNIT_NAMES` reads the
symbol as its name: `%` (*por cento*), `€`, `mm`, `cm`, `m`, `km`, `km/h`,
square and cubic metres (`m2`, `m²`, `m3`, `m³`, and the `cm`/`km` forms),
`mg`, `g`, `kg`, `ml`, `cl`, `dl`, `l`, `L`. Symbols and names follow the SI
brochure (*Tradução luso-brasileira de 2021 do SI*, IPQ/Inmetro, §5.2-5.3).
Every unit name is masculine (*o grama*, *duzentos gramas*), so the number
takes the masculine form.

The name is plural after every number except one. In European Portuguese
this includes zero and every decimal (*zero quilómetros*, *um vírgula cinco
quilómetros*). In Brazilian Portuguese the name stays singular up to one
(*zero quilômetro*). A round million takes *de* (*um milhão de euros*).

```python
normalize_numbers("pesa 200 g")          # 'pesa duzentos gramas'
normalize_numbers("1 km")                # 'um quilómetro'
normalize_numbers("3 vírgula 5 km")      # 'três vírgula cinco quilómetros'
normalize_numbers("subiu 20 %")          # 'subiu vinte por cento'
normalize_numbers("0 km", lang="pt-BR")  # 'zero quilômetro'
```

`normalize_orthography` separates glued symbols (`7kg`, `20%`), moves a
leading euro sign after the number (`€20`), reads euro cents
(`2,50 €` → *dois euros e cinquenta cêntimos*) and reads `x` or `×` between
two numbers as *vezes*.

---

## Large numbers

Cardinal and ordinal reading is delegated to
[`ovos-number-parser`](https://github.com/OpenVoiceOS/ovos-number-parser),
which spells out arbitrarily large Python integers correctly in either
scale, grouping each magnitude by its scale word instead of by every three
digits. There is no ceiling on the integer part.

```python
NumberParser.pronounce_number_word("9007199254740991")
# 'nove mil e sete biliões cento e noventa e nove mil duzentos e
#  cinquenta e quatro milhões setecentos e quarenta mil novecentos
#  e noventa e um'
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
| `pronounce_number_word(word, prev_word=None, next_word=None, gender=None, as_ordinal=None, is_brazilian=False, scale=None)` | Spelled-out form of one numeric token. |
| `to_int(word)` / `is_int(word)` | Integer value (ordinal markers, comma/dot decimals stripped out) / membership test. |
| `to_float(word)` / `is_float(word)` | Float value (comma or dot decimal, scientific notation) / membership test. |
| `is_decimal(word)` | `True` for a non-scientific decimal like `"10,4"` or `"10.4"`. |
| `is_scientific_notation(word)` | `True` for forms like `"1.5e10"` or `"2,5e3"`. |
| `pronounce_scientific(word, is_brazilian=False, scale=None)` | Spoken form of scientific notation. |
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
- An ordinal marker on the number: `º` is masculine, `ª` is feminine.
- A singular label head before the number (`artigo`, `número`, `página`,
  `capítulo`, `alínea` and others in `NumberParser.LABEL_HEADS`). A cardinal
  that labels a noun is invariable, so it takes the masculine form:
  `"o artigo 1 da lei"` → `"o artigo um da lei"`, `"na página 2"` →
  `"na página dois"`. A plural word after the number other than `das`/`dos`
  and similar is the noun it counts, and the rules below apply
  (`"na sala 2 pessoas"` → `"duas pessoas"`).
- The preceding word, when it is an article (`a`/`as`/`da`/`das` feminine,
  `o`/`os`/`do`/`dos` masculine) AND a word follows the number:
  `"as 2 artistas"` → `"duas"`, `"os 2 artistas"` → `"dois"`. A bare `a`
  with nothing after the number is the preposition "to", not the article, as
  in a score reading like `"3 a 2"`, and does not force feminine. Before a
  masculine noun, `a` is the preposition too: `"a 2 dias do fim"` → `"dois"`.
- The gender of the following word in the bundled noun list
  (`NumberParser.noun_gender`): `"1 lei"` → `"uma lei"`, `"1 dia"` →
  `"um dia"`, `"2 vezes"` → `"duas vezes"`. The list holds singular and plural
  forms. A noun of both genders (`artista`, `estudante`, `capital`, `rádio`)
  is marked `mf` and does not decide. The list is derived from the English
  Wiktionary and is licensed under CC BY-SA 4.0, see
  `tugaphone/data/noun_gender/README.md`.
- For a word that is not in the list, or a noun of both genders, the word's
  ending (`-a`, `-dade`, `-agem` → feminine, default masculine)
- A unit symbol after the number (`2 m`, `2 g`): always masculine
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
