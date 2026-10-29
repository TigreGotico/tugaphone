# Text normalization

Written text contains conventions that the phoneme rules cannot read: number ranges, clock times, European thousands and decimal separators, honorific abbreviations, regnal Roman numerals and acronyms. `tugaphone.text_normalization` rewrites them into plain words or plain digit tokens so that [`normalize_numbers`](numbers.md) can read the result. It runs on the text before any lattice or phoneme work, in the engine's `normalize` stage, ahead of `normalize_numbers`. Number words follow standard European Portuguese ("vinte e cinco").

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
expand_clock_times("O comboio parte às 16:54.")
# 'O comboio parte às 16 e 54.'
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

## Roman numerals

A Roman numeral after a century, a ruler, a pope or a part of a work reads
as an ordinal up to ten and as a cardinal above ten: "D. João V" is "Dom
João Quinto", "o século XIX" is "o século dezanove", "Pio XII" is "Pio
Doze". A numeral before its noun keeps the ordinal, with the gender of the
article: "a II Guerra Mundial" is "a Segunda Guerra Mundial". The rule is
Cunha & Cintra's, as quoted by Ciberdúvidas (answers 14284, 14167 and
11716). The numeral takes the case of the name it belongs to and is
lowercase after a common noun such as "século". The cardinals follow `lang`
("dezanove" in pt-PT, "dezenove" in pt-BR).

A multi-letter numeral of `I`, `V` and `X` always converts. A single `I`,
`V` or `X` converts only after a capitalised name-like word or a
part-of-work noun (`século`, `capítulo`, `livro`, ...), so "eu vi X pessoas"
is left alone. A numeral with `L` or `C` converts only after a part-of-work
noun, so "Pizza Grande XL" is left alone.

```python
from tugaphone.text_normalization import expand_regnal_numerals

expand_regnal_numerals("D. Afonso I fundou o reino.")
# 'D. Afonso Primeiro fundou o reino.'
expand_regnal_numerals("No século XIX, Luís XIV já era história.")
# 'No século dezanove, Luís Catorze já era história.'
expand_regnal_numerals("o século XIX", lang="pt-BR")
# 'o século dezenove'
expand_regnal_numerals("Eu vi X pessoas.")
# 'Eu vi X pessoas.'
```

## Letter-digit codes

`normalize_orthography(text, lang)` passes `lang` to the Roman-numeral and
letter-digit rules, so the numbers they read follow pt-PT or pt-BR spelling.

A code of one to three capitals or one or two lowercase letters followed by
digits reads as the letter names and then the number as a masculine
cardinal: "T2" is "tê dois", "A3" is "á três", "RTP2" is "érre tê pê dois",
"mp3" is "éme pê três". A number that labels something is invariable, so
"o T2 na cidade" reads "tê dois", not "duas". The reading does not depend on
what the code stands for, so no context is needed. Right after a number the
letters are a unit symbol, so "10 m2" is left alone.

```python
from tugaphone.text_normalization import expand_letter_digit_codes

expand_letter_digit_codes("Vendo um T2 perto da A3.")
# 'Vendo um tê dois perto da á três.'
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
