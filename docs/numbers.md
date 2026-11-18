# Numbers, dates and times

tugaphone reads numbers, dates, clock times, money, measures and the
abbreviations of its tables with
[text2spoken](https://github.com/TigreGotico/text2spoken). `phonemize` does
this for you. This page shows how to call the reading step alone and what it
gives.

---

## Read a sentence

1. Import `normalize_numbers`.
2. Give it the text and the lect.

```python
from tugaphone.number_utils import normalize_numbers

normalize_numbers("Nasceu a 25/12/2023.")
# 'Nasceu a vinte e cinco de dezembro de dois mil e vinte e três.'
normalize_numbers("A reunião é às 19h30.")
# 'A reunião é às dezanove horas e trinta minutos.'
normalize_numbers("A reunião é às 19h30.", "pt-BR")
# 'A reunião é às dezenove horas e trinta minutos.'
normalize_numbers("O Dr. Silva pagou 2,50 € às 14:30.")
# 'O Doutor Silva pagou dois euros e cinquenta cêntimos às catorze e trinta.'
```

A number agrees with the noun that it counts:

```python
normalize_numbers("vou comprar 1 casa")   # 'vou comprar uma casa'
normalize_numbers("vou adotar 1 cão")     # 'vou adotar um cão'
normalize_numbers("comprei 2 casas")      # 'comprei duas casas'
```

The rest of the text stays as written. Text that is already spelled out
comes back unchanged, so a caller can normalise the text first and pass the
result to tugaphone.

---

## The variety of each lect

text2spoken reads two varieties, `pt-PT` and `pt-BR`. Each lect reads the
variety of its AO1990 spelling norm, which `tugaphone.registry.spelling_norm`
gives. `tugaphone.number_utils.text2spoken_tag` gives the variety:

| Lects | Variety | 19 reads |
| --- | --- | --- |
| `pt-PT` and its sub-lects, `pt-AO`, `pt-CV`, `pt-GW`, `pt-MO`, `pt-MZ`, `pt-ST`, `pt-TL` | `pt-PT` | dezanove |
| `pt-BR` and its sub-lects, `pt-UY` | `pt-BR` | dezenove |

```python
from tugaphone.number_utils import text2spoken_tag

text2spoken_tag("pt-AO")   # 'pt-PT'
text2spoken_tag("pt-UY")   # 'pt-BR'
```

---

## Number scale

`pt-PT` reads the long scale (`10^12` is "um bilião"). `pt-BR` reads the
short scale (`10^12` is "um trilhão"). The `scale` argument overrides the
scale and keeps the spelling of the variety:

```python
normalize_numbers("1000000000000", "pt-PT")                 # 'um bilião'
normalize_numbers("1000000000000", "pt-BR")                 # 'um trilhão'
normalize_numbers("1000000000000", "pt-PT", scale="short")  # 'um trilião'
normalize_numbers("1000000000000", "pt-BR", scale="long")   # 'um bilhão'
```

---

## A form with no reading

text2spoken leaves some forms as written. tugaphone reads most of them with
its [fallback rewrites](text_normalization.md#fallback-rewrites). A form that
is still unread stays as written. The phoneme lattice drops digits, so a form
with digits gives a `tugaphone.number_utils.UnreadFormWarning` that names the
form and the text:

```python
normalize_numbers("um filme 3D")
# UnreadFormWarning: pt-PT: no reading for '3D' in 'um filme 3D'; its digits are dropped
```

With `strict=True`, the default, an error in text2spoken raises. With
`strict=False`, the text comes back as written.

---

## Where the readings come from

text2spoken owns every reading rule and cites a source for each. Its
[Portuguese page](https://github.com/TigreGotico/text2spoken/blob/dev/docs/languages/pt.md)
lists the forms, the options and the limits. To report a wrong reading, open
an issue in text2spoken with the written form, the reading that you expect
and its source.

---

## Where next

- [text_normalization.md](text_normalization.md), the rewrites that run around text2spoken
- [quickstart.md](quickstart.md), `normalize_numbers` in context
- [api.md](api.md), the function reference


---
[← Code-switch](codeswitch.md) · [Home](../README.md) · [Text normalization →](text_normalization.md)
