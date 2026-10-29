# Portuguese noun genders

`noun_gender.tsv.gz` lists Portuguese common nouns, singular and plural, with
their grammatical gender: `m`, `f`, or `mf` for a noun of both genders. The
number reader uses it to make a number agree with the noun it counts
(`1 lei` → `uma lei`, `1 dia` → `um dia`).

## Licence

This data file is licensed under the Creative Commons Attribution-ShareAlike
4.0 International licence (CC BY-SA 4.0,
https://creativecommons.org/licenses/by-sa/4.0/). It is not covered by the
Apache-2.0 licence of the tugaphone code. Copies and changes of this file must
keep this licence and the attribution below.

## Source and attribution

The data is derived from the English Wiktionary
(https://en.wiktionary.org/), by the Wiktionary contributors, as extracted by
wiktextract and published by kaikki.org
(https://kaikki.org/dictionary/Portuguese/). kaikki.org states that its data
is available under the same licences as Wiktionary, CC BY-SA and GFDL. The
`#` header lines of `noun_gender.tsv.gz` record the dump URL and its date.

## Changes from the source

`scripts/build_noun_gender.py` keeps the gender of each noun entry and the
plural and gendered forms that the entry lists. It joins the genders of all
entries of one spelling, drops genders and entries labelled obsolete,
nonstandard or similar when a standard one exists, and drops words that are
also articles, pronouns, determiners, conjunctions, contractions or letters.
The script docstring gives the full rules. To rebuild the file:

```bash
python scripts/build_noun_gender.py
```
