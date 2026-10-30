# Text normalization

Written text contains conventions that the phoneme rules cannot read: unit symbols, number ranges, clock times, European thousands and decimal separators, honorific abbreviations, regnal Roman numerals and acronyms. `tugaphone.text_normalization` rewrites them into plain words or plain digit tokens so that [`normalize_numbers`](numbers.md) can read the result. It runs on the text before any lattice or phoneme work, in the engine's `normalize` stage, ahead of `normalize_numbers`. Number words follow standard European Portuguese ("vinte e cinco").

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

## Unit symbols, percent, euros and multiplication

The SI puts a space between a number and its unit symbol, and between a
number and `%`. A symbol glued to the digits (`7kg`, `20%`) gets that space
back, and a leading euro sign moves after the number (`€20` → `20 €`), so
that `normalize_numbers` reads the unit name with number agreement (see
[Units, percent and euros](numbers.md#units-percent-and-euros)). A symbol
counts only right after digits, so the letter `m` in running text is left
alone. An amount in euros with one or two decimals is read as euros and
cents. A `x` or `×` between two numbers is read *vezes*; a hex literal such
as `0x1F` and the word in "o x da questão" are left alone.

```python
from tugaphone.text_normalization import separate_unit_symbols

separate_unit_symbols("Pesa 7kg e custa €20.")
# 'Pesa 7 kg e custa 20 €.'
separate_unit_symbols("Custa 2,50 €.")
# 'Custa 2 € e 50 cêntimos.'
separate_unit_symbols("15x8")
# '15 vezes 8'
```

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
"9 e 05". Whole hours also accept `24:00` ("24 horas"); non-whole
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
sentence's end is more often the plain abbreviation than a title. `D.` is
the abbreviation of both "Dom" and "Dona" (Priberam): it reads "Dona" before
a feminine given name and "Dom" before any other name, so "D. Maria" is
"Dona Maria" and "D. Sebastião" is "Dom Sebastião". A name of both genders,
or one that is not in the given-name list, reads "Dom".

Forms with a superscript ending match no ordinary word, so they expand
unconditionally: `Sr.ª`, `Sr.as`, `Dr.ª`, `Eng.ª`, `Prof.ª`, `n.os`/`N.os`
("números"), `Ex.mo`/`Ex.ma` and their plurals, and the "Excelência" forms
`Ex.ª`, `Ex.as`, `Exa.`, `Exas.`. Before an "Excelência" form, `V.` reads
"Vossa", `VV.` or `Vv.` reads "Vossas" and `S.` reads "Sua"; alone, `V.` and
`S.` are left for the other rules. The plurals `Srs.` and `Sras.` follow the
personal-honorific rule. The expansions follow the *Vocabulário Ortográfico*
of the Academia das Ciências de Lisboa and the vocabularies quoted by
Ciberdúvidas (answers 33650 and 15826). A comma, colon or similar mark after
the abbreviation's own period stays in place.

```python
from tugaphone.text_normalization import expand_abbreviations

expand_abbreviations("Obrigado, V. Ex.ª, pela visita.")
# 'Obrigado, Vossa Excelência, pela visita.'
expand_abbreviations("Vv. Ex.as sabem que a Sr.ª Ana chegou.")
# 'Vossas Excelências sabem que a Senhora Ana chegou.'
expand_abbreviations("O Sr. Silva chegou.")
# 'O Senhor Silva chegou.'
expand_abbreviations("Isto é o n.º 4 da lista.")
# 'Isto é o número 4 da lista.'
expand_abbreviations("Ver o vs. anterior.")
# 'Ver o versus anterior.'
expand_abbreviations("D. Maria I")
# 'Dona Maria I'
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

An ordinal agrees in gender with its name or noun: "Isabel II" is "Isabel
Segunda", "D. Maria I" is "Dona Maria Primeira", "a parte V" is "a parte
quinta". A cardinal above ten is a label and stays masculine. A name of both
genders, or one that is not in the given-name list, reads as masculine.

These rules decide when a capital letter is a numeral:

- After a part-of-work noun (`século`, `capítulo`, `livro`, `parte`, ...),
  matched case-insensitively, a numeral always converts: "O SÉCULO XIX"
  converts.
- Inside a run of all-caps words, as in a headline, a numeral does not
  convert: in "EU VI O FILME", "VI" is the verb.
- After the word of a fixed expression in `tugaphone/data/letter_expressions.json`,
  the letter stays: "Raio X", "Geração X", "Malcolm X", "vitamina C".
  The word is matched case-insensitively.
- A multi-letter numeral of `I`, `V` and `X` converts anywhere else.
- A single `I`, `V` or `X` converts only after a given name, so "eu vi X
  pessoas", "a Sala V" and "o Anexo I" are left alone.
- A numeral with `L`, `C`, `D` or `M` converts only after a part-of-work
  noun, so "tamanho XL", "o CD" and "o MDC" are left alone.

tugaphone converts only tokens written wholly in capitals, so lowercase
words such as "vi", "li" and "mix" are never numerals.

The rules take a given name and its gender from tugalex
(`TugaLexicon.get_given_name_gender`). A name before a Roman numeral reads the
numeral as regnal, and a feminine name after `D.` reads `Dona`. A name borne by
both genders, or a word that is not a name, reads as masculine.

```python
from tugaphone.text_normalization import expand_regnal_numerals

expand_regnal_numerals("D. Afonso I fundou o reino.")
# 'D. Afonso Primeiro fundou o reino.'
expand_regnal_numerals("No século XIX, Luís XIV já era história.")
# 'No século dezanove, Luís Catorze já era história.'
expand_regnal_numerals("o século XIX", lang="pt-BR")
# 'o século dezenove'
expand_regnal_numerals("Isabel II")
# 'Isabel Segunda'
expand_regnal_numerals("Eu vi X pessoas.")
# 'Eu vi X pessoas.'
expand_regnal_numerals("Fez um raio X.")
# 'Fez um raio X.'
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
