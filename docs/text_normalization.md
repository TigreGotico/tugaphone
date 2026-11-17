# Text normalization

Written text holds forms that the phoneme rules cannot read: numbers, dates, clock times, money, abbreviations, Roman numerals and acronyms. The engine's `expand` step rewrites them as words before any lattice or phoneme work. `tugaphone.text_normalization.normalize_text` is that step after the spelling step:

```python
from tugaphone.text_normalization import normalize_text

normalize_text("A reunião é às 16:00 com 25 pessoas.")
# 'A reunião é às dezasseis horas com vinte e cinco pessoas.'
normalize_text("O Sr. presidente falou com o Dr.")
# 'O Senhor presidente falou com o Doutor'
```

`normalize_text` runs three steps:

1. `normalize_orthography` rewrites the forms that text2spoken leaves as written: the multiplication sign, the abbreviations of the tables below, acronyms and letter-digit codes.
2. [text2spoken](numbers.md) reads numbers, dates, clock times, ranges, money, measures, percentages, Roman numerals and its own abbreviations, in the `pt-PT` or `pt-BR` variety of the lect.
3. The titles that text2spoken reads only before a name (`Sr.`, `Dr.`, `D.` and others) expand where text2spoken leaves them, as in "o Sr. presidente".

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
- For the Brazilian lects, the hyphen rules of AO1990 change the word count
  (*há-de* → *há de*, *manda-chuva* → *mandachuva*).
- For the Brazilian lects, *óptica* becomes *ótica*, although the VOLP lists
  both as separate words.

The Brazilian lects keep the trema (*freqüente*), because in a text from
before AO1990 it is the only mark of a pronounced *u*. They also keep both
forms of a VOLP dual as written (*epilético* and *epiléptico*), because the
form carries the pronunciation of the writer.

---

## Forms that text2spoken reads

text2spoken reads unit symbols, percentages, money, ranges, clock times,
European separators and Roman numerals. Its
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

## Multiplication

A `x` or `×` between two numbers is read *vezes*: "dois vezes dois são
quatro" (Priberam DLPO, "vezes"). A hex literal such as `0x1F` and the word
in "o x da questão" are left alone.

```python
from tugaphone.text_normalization import read_multiplication_signs

read_multiplication_signs("Mede 15x8 metros.")
# 'Mede 15 vezes 8 metros.'
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

In `normalize_text`, the titles `Sr.`, `Sra.`, `Sr.ª`, `Dr.`, `Dra.`, `Dr.ª`,
`Eng.`, `Prof.`, `D.` and the address `Av.` wait until text2spoken has read
the text. Before a name, text2spoken reads them, and the title tells it the
gender of a Roman numeral after the name: "D. Maria I" is "Dona Maria
Primeira". Where text2spoken leaves them as written, tugaphone expands them.

## Letter-digit codes

A code of one to three capitals or one or two lowercase letters followed by
digits reads as the letter names and then the number as a masculine
cardinal: "T2" is "tê dois", "A3" is "á três", "RTP2" is "érre tê pê dois",
"mp3" is "éme pê três". A number that labels something is invariable, so
"o T2 na cidade" reads "tê dois", not "duas". text2spoken reads the digits
alone, in the variety of the lect, so they take the masculine. Right after a
number the letters are a unit symbol, so "10 m2" is left alone.

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
