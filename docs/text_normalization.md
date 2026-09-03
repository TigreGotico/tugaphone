# Text normalization

`tugaphone.text_normalization` rewrites written conventions — number ranges,
clock times, European thousands/decimal separators, honorific abbreviations,
regnal Roman numerals, letter-spelled acronyms — into plain words or plain
digit tokens, so [`normalize_numbers`](numbers.md) can read the result out
loud. It runs at the text level, before any lattice or phoneme work, wired
into the engine's `normalize` stage ahead of `normalize_numbers`. Number
words themselves follow standard European Portuguese ("vinte e cinco").

```python
from tugaphone.text_normalization import normalize_orthography
from tugaphone.number_utils import normalize_numbers

text = "A reunião é às 16:00 com 25 pessoas."
normalize_orthography(text)
# 'A reunião é às 16 horas com 25 pessoas.'
normalize_numbers(normalize_orthography(text), "pt-PT")
# 'A reunião é às dezasseis horas com vinte e cinco pessoas.'
```

`normalize_orthography(text)` runs every rule below, in an order chosen so
they don't interfere with each other.

---

## Number ranges

A dash directly between two digits is a numeric range, read " a ". A word
hyphen (`chamo-me`, `guarda-chuva`) has a letter on at least one side and is
left alone.

```python
from tugaphone.text_normalization import split_number_ranges

split_number_ranges("As páginas 1139-1185 falam disso.")
# 'As páginas 1139 a 1185 falam disso.'
```

## Clock times

`HH:00` is read as the hour plus "hora"/"horas"; the digit token is left for
`normalize_numbers`, which already picks the feminine form ("uma", "duas",
"vinte e uma", …) from the following noun. Any other `HH:MM` is read "H e MM"
— the leading zero of the minutes is dropped, so "9:05" reads "9 e 5", not
"9 e 05". Whole hours additionally accept `24:00` ("24 horas"); non-whole
times keep the ordinary 0-23 hour range.

```python
from tugaphone.text_normalization import expand_clock_times

expand_clock_times("A reunião é às 16:00")
# 'A reunião é às 16 horas'
expand_clock_times("O comboio parte às 16:54")
# 'O comboio parte às 16 e 54'
expand_clock_times("Combinámos para a 1:00")
# 'Combinámos para a 1 hora'
expand_clock_times("O despertador tocou às 9:05")
# 'O despertador tocou às 9 e 5'
expand_clock_times("A loja fecha às 24:00")
# 'A loja fecha às 24 horas'
```

## European separators

A `.` between two digits groups thousands and is dropped; a `,` between two
digits is the decimal mark, read "vírgula". Both only fire between two
digits, so a sentence-final period, a list comma, or an ordinal mark like
`3.º` are untouched.

```python
from tugaphone.text_normalization import normalize_number_separators

normalize_number_separators("O total foi 92.073 euros.")
# 'O total foi 92073 euros.'
normalize_number_separators("A nota foi 10,4 valores.")
# 'A nota foi 10 vírgula 4 valores.'
normalize_number_separators("Ele ficou em 3.º lugar.")
# 'Ele ficou em 3.º lugar.'
```

## Abbreviations

Two groups, matched independently. Unconditional abbreviations expand
wherever they appear, with no regard to what follows: section/reference
markers (`vs.`, `pág.`/`págs.`, `tel.`, `art.`, `fig.`, `cap.`, `séc.`) and
place-name abbreviations (`Av.`, `R.`, `Lx.`, `n.º`/`nº`, `N.º`/`Nº`) that
stand for the same word whether followed by a capitalised name, a lowercase
word, or the end of a sentence. Personal honorifics (`D.`, `Sr.`, `Sra.`,
`Dr.`, `Dra.`, `Eng.`, `Prof.`) expand only when followed by a capitalised
word — the name they introduce — since a standalone "Dr." or "Sr." at a
sentence's end is more often the plain abbreviation than a title.

```python
from tugaphone.text_normalization import expand_abbreviations

expand_abbreviations("O Sr. Silva chegou.")
# 'O Senhor Silva chegou.'
expand_abbreviations("Isto é o n.º 4 da lista.")
# 'Isto é o número 4 da lista.'
expand_abbreviations("Ver o vs. anterior.")
# 'Ver o versus anterior.'
```

## Regnal Roman numerals

A multi-letter regnal numeral (`II`..`XX`) always converts to its masculine
ordinal. A single `I`, `V` or `X` converts only right after a capitalised
name-like word, so "eu vi X pessoas" is left alone.

```python
from tugaphone.text_normalization import expand_regnal_numerals

expand_regnal_numerals("D. Afonso I fundou o reino.")
# 'D. Afonso Primeiro fundou o reino.'
expand_regnal_numerals("D. João VI regressou.")
# 'D. João Sexto regressou.'
expand_regnal_numerals("Eu vi X pessoas.")
# 'Eu vi X pessoas.'
```

## Acronyms

Acronyms are matched case-sensitively against an explicit table, so ordinary
lowercase words (`ia`, `eu`) are never touched. Matched acronyms are spelled
out with Portuguese letter names (`IA` → "i á", `GPS` → "gê pê ésse").
Acronyms that are read as words in Portuguese (NASA, UNESCO, FIFA, NATO/OTAN,
SIDA, OVNI) simply aren't in the table, so they pass through unspelled.

```python
from tugaphone.text_normalization import expand_acronyms

expand_acronyms("A IA venceu o jogo.")
# 'A i á venceu o jogo.'
expand_acronyms("Fui à ONU falar de IA.")
# 'Fui à ONU falar de i á.'
expand_acronyms("ia ao mercado")
# 'ia ao mercado'
```

---

## Where next

- [numbers.md](numbers.md), `normalize_numbers` and gender agreement
- [quickstart.md](quickstart.md), the pipeline in context


---
[← Numbers](numbers.md) · [Home](../README.md) · [API →](api.md)
