# Text normalization

Written text holds forms that the phoneme rules cannot read: numbers, dates, clock times, money, abbreviations, Roman numerals and acronyms. The engine's `expand` step rewrites them as words before any lattice or phoneme work. `tugaphone.text_normalization.normalize_text` is that step after the spelling step:

```python
from tugaphone.text_normalization import normalize_text

normalize_text("A reunião é às 16:00 com 25 pessoas.")
# 'A reunião é às dezasseis horas com vinte e cinco pessoas.'
normalize_text("O Sr. presidente falou com o Dr.")
# 'O Senhor presidente falou com o Doutor'
```

`normalize_text` runs four steps:

1. It expands the [abbreviations](#abbreviations), [acronyms](#acronyms) and [letter-digit codes](#letter-digit-codes), which text2spoken leaves as written.
2. [text2spoken](numbers.md) reads numbers, dates, clock times, ranges, money, measures, percentages and Roman numerals, in the `pt-PT` or `pt-BR` variety of the lect.
3. The [fallback rewrites](#fallback-rewrites) read the forms that text2spoken leaves as written, and text2spoken reads the digits that they leave.
4. The [Roman numeral rules](#roman-numerals) read the numerals that text2spoken leaves.

`normalize_orthography(text, lang)` runs the rewrites alone, in the order of
tugaphone 1.7, and leaves the digits for
[`normalize_numbers`](numbers.md).

## Old spellings

Before these rules run, the spelling step rewrites spellings from before the
1990 Orthographic Agreement (AO1990), so the phoneme rules read the modern
form. It calls [desacordo_ortografico](https://github.com/TigreGotico/desacordo_ortografico)
with the AO1990 norm of the lect: `ao1990-br` for the Brazilian lects and
`pt-UY`, `ao1990-pt` for every other lect.

```python
from tugaphone.lattice_core import normalize_spelling

normalize_spelling("A acção da pharmacia foi rápida.", "pt-PT")
# 'A ação da farmácia foi rápida.'
normalize_spelling("O manda-chuva chegou.", "pt-BR")
# 'O mandachuva chegou.'
normalize_spelling("Tive uma ideia.", "pt-BR")
# 'Tive uma idéia.'
```

Text that is already in the AO1990 spelling stays as written. That includes
the forms the agreement keeps in two spellings, such as *sector* in Portugal
and *facto* in Brazil:

```python
normalize_spelling("O facto e o contacto ficam.", "pt-BR")
# 'O facto e o contacto ficam.'
```

Case and punctuation stay. Modern text changes in three ways:

- A name in an old spelling takes the AO1990 spelling (*Sophia* → *Sofia*,
  *Rachel* → *Raquel*), although AO1990 Base XXI lets a name keep its spelling.
- For the Brazilian lects and `pt-UY`, the hyphen rules of AO1990 change the word count
  (*há-de* → *há de*, *manda-chuva* → *mandachuva*).
- For the Brazilian lects and `pt-UY`, a paroxytone that lost the accent of an open *éi*
  (AO1990 Base IX 3.º) takes the accent back, so it reads with the open
  vowel (*ideia* → *idéia*, *estreia* → *estréia*). Michaelis marks these
  words with an open *e*, "(éi)". A closed *ei* stays (*areia*, *baleia*).

The Brazilian lects keep the trema (*freqüente*), because in a text from
before AO1990 it is the only mark of a pronounced *u*. They also keep both
forms of a VOLP dual as written (*epilético* and *epiléptico*), because the
form carries the pronunciation of the writer. *Óptica* also stays, because the
VOLP lists *óptica* and *ótica* as two different words:

```python
normalize_spelling("A fibra óptica.", "pt-BR")
# 'A fibra óptica.'
```

---

## Forms that text2spoken reads

text2spoken reads most unit symbols, percentages, money, ranges with "a" or
an en dash, clock times after a time word, European separators and Roman
numerals after a title, a century or a ruler. Its
[Portuguese page](https://github.com/TigreGotico/text2spoken/blob/dev/docs/languages/pt.md)
gives the rules and their sources.

```python
normalize_text("Pesa 7kg e custa €20.")
# 'Pesa sete quilogramas e custa vinte euros.'
normalize_text("Viveu de 1139-1185.")
# 'Viveu de mil cento e trinta e nove a mil cento e oitenta e cinco.'
normalize_text("Abre das 12:00 às 14:00.")
# 'Abre do meio-dia às catorze horas.'
normalize_text("No século XIX, Luís XIV já era história.")
# 'No século dezanove, Luís Catorze já era história.'
normalize_text("o século XIX", "pt-BR")
# 'o século dezenove'
```

## Fallback rewrites

text2spoken reads first, and its reading stands. The rewrites below read only
the forms that text2spoken leaves as written: a range with an em dash or a
hyphen ("3-2"), a clock time with no time word ("São 16:30."), `24:00`, a
glued litre symbol with a capital L ("2L", "10mL"), a unit symbol such as `m2` or `L` after a number in digits, a
multiplication sign, a decimal with a dot, scientific notation, a number
between two marks, and a pair of numbers whose noun may give the first number
another gender ("de 1 a 2 casas"). The first number of such a pair reads in the
masculine, and the second agrees with its noun. When a comma, a semicolon, a
stop, a question mark or an exclamation mark follows the second number or its
closing bracket, no noun counts the pair, and both numbers read in the
masculine. In "Escreve-se com dois L."
the `L` is a letter and stays. Each fallback names its text2spoken issue in
the code, and it goes when text2spoken reads its form.

```python
normalize_text("O jogo é 3-2.")
# 'O jogo é três a dois.'
normalize_text("São 16:30.")
# 'São dezasseis e trinta.'
normalize_text("Bebi 2L de água.")
# 'Bebi dois litros de água.'
normalize_text("Mede 15x8 metros.")
# 'Mede quinze vezes oito metros.'
normalize_text("1e6")
# 'um vezes dez elevado a seis'
normalize_text("de 1 a 2 casas")
# 'de um a duas casas'
normalize_text("de 1 a 2, casas")
# 'de um a dois, casas'
```

The rewrites that 1.7 made public stay public. Each one leaves its digits for
a number reader.

### Unit symbols, percent, euros and multiplication

The SI puts a space between a number and its unit symbol, and between a
number and `%`. A symbol glued to the digits (`7kg`, `20%`) gets that space
back, and a leading euro sign moves after the number (`€20` → `20 €`), so
that a number reader reads the unit name with number agreement. A symbol
counts only right after digits, so the letter `m` in running text is left
alone. An amount in euros with one or two decimals is read as euros and
cents. A `x` or `×` between two numbers is read *vezes*; a hex literal such
as `0x1F` and the word in "o x da questão" are left alone. Only a product in
digits reads *vezes*: a product that the author wrote in words keeps its `x`
(`normalize_text("dois x três e 2 x 3")` gives "dois x três e dois vezes três").

```python
from tugaphone.text_normalization import separate_unit_symbols

separate_unit_symbols("Pesa 7kg e custa €20.")
# 'Pesa 7 kg e custa 20 €.'
separate_unit_symbols("Custa 2,50 €.")
# 'Custa 2 € e 50 cêntimos.'
separate_unit_symbols("15x8")
# '15 vezes 8'
```

### Number ranges

A dash directly between two digits is a numeric range, read " a ". A word
hyphen (`chamo-me`, `guarda-chuva`) has a letter on at least one side and is
left alone.

```python
from tugaphone.text_normalization import split_number_ranges

split_number_ranges("As páginas 1139-1185 falam disso.")
# 'As páginas 1139 a 1185 falam disso.'
```

### Clock times

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

### European separators

A `.` between two digits groups thousands and is dropped; a `,` between two
digits is the decimal mark, read "vírgula". Both only fire between two
digits, so a sentence-final period, a list comma, or an ordinal mark like
`3.º` are untouched. text2spoken reads both separators, so `normalize_text`
does not run this rewrite; `normalize_orthography` does.

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
word, or the end of a sentence. The personal titles (`Sr.`, `Sra.`, `Srs.`,
`Sras.`, `Dr.`, `Dra.`, `Eng.`, `Prof.`) also expand wherever they appear:
"os Srs. deputados" and "falei com o Dr." read the title. `D.` expands only
when a capitalised word follows, the name it introduces, and not after a
noun that labels a letter ("a vitamina D."). It is the abbreviation of both
"Dom" and "Dona" (Priberam): it reads "Dona" before a feminine given name and
"Dom" before any other name, so "D. Maria" is "Dona Maria" and "D. Sebastião"
is "Dom Sebastião". A name of both genders, or one that is not in the
given-name list, reads "Dom".

A reference marker (`cap.`, `art.`, `fig.`, `pág.`, `págs.`, `séc.`, `tel.`)
is capitalised at the start of a sentence or a reference. Capitalised, it
expands only before its number, in digits or Roman numerals: `Cap. 3` is
"Capítulo 3" and `Art. 5.º` is "Artigo 5.º". Before a name, `Cap.` is also
the military rank and `Art.` is a name, so "O Cap. Salgueiro Maia" stays as
written.

Forms with a superscript ending match no ordinary word, so they expand
unconditionally: `Sr.ª`, `Sr.as`, `Dr.ª`, `Eng.ª`, `Prof.ª`, `n.os`/`N.os`
("números"), `Ex.mo`/`Ex.ma` and their plurals, and the "Excelência" forms
`Ex.ª`, `Ex.as`, `Exa.`, `Exas.`. Before an "Excelência" form, `V.` reads
"Vossa", `VV.` or `Vv.` reads "Vossas" and `S.` reads "Sua"; alone, `V.` and
`S.` are left for the other rules. The expansions follow the *Vocabulário Ortográfico*
of the Academia das Ciências de Lisboa and the vocabularies quoted by
Ciberdúvidas (answers 33650 and 15826). An opening bracket or quotation mark
before the abbreviation stays in place, and so does a comma, colon, closing
bracket or similar mark after its own period: "(art. 5.º)" is "(artigo
5.º)".

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

text2spoken reads a Roman numeral after a title, a century, a ruler or a
part of a work. `expand_regnal_numerals` reads the numerals that it leaves,
such as "Afonso I" and "a II Guerra Mundial", by these rules.

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
quinta". After a word that is not a given name, the ordinal takes the gender
of that noun in tugalex (`TugaLexicon.get_noun_gender`): "a figura II" is "a
figura segunda". A cardinal above ten is a label and stays masculine. A name
of both genders, or a word that tugalex does not know, reads as masculine.

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
both genders reads as masculine.

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

A code of one to three capitals or one or two lowercase letters followed by
digits reads as the letter names and then the number as a masculine
cardinal: "T2" is "tê dois", "A3" is "á três", "RTP2" is "érre tê pê dois",
"mp3" is "éme pê três". A number that labels something is invariable, so
"o T2 na cidade" reads "tê dois", not "duas". text2spoken reads the digits
alone, in the variety of the lect, so they take the masculine. Right after a
number in digits the letters are a unit symbol, so "10 m2" is left for the
unit rule.

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

- [numbers.md](numbers.md), `normalize_numbers` and the variety of each lect
- [quickstart.md](quickstart.md), the pipeline in context


---
[← Numbers](numbers.md) · [Home](../README.md) · [API →](api.md)
