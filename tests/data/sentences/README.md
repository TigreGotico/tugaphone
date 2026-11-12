# Sentence sets for the scriptconv gate

The gate in `scriptconv.testing.compare` scores tugaphone against standalone
orthography2ipa. Then it switches off one tugaphone stage at a time and scores
again. A stage stays when it removes more error in its own category than one
sentence carries, and loses at most one segment in every other category.

`pt-PT.tsv` and `pt-BR.tsv` are the sets. They are test data, and the wheel
does not include them. Each row has the columns
`id lang category text expected_ipa source tier`, with one of the categories
`plain number date abbreviation homograph contact`.

## Run the gate

Install tugaphone and the scriptconv `test` extra, then run this command from
the repository root:

```
uv pip install --prerelease=allow -e . "scriptconv[test]"
python -m scriptconv.testing.compare --lang pt-PT \
    --tsv tests/data/sentences/pt-PT.tsv \
    --backend tests.gate_backend:TugaphoneBackend \
    --stages lexicon:plain,expand:number,expand:date,expand:abbreviation,mark:homograph
```

`tests/gate_backend.py` is the backend. Its stages are the three fields of the
orthography2ipa `Pipeline` that `tugaphone.pipeline(lect)` fills: `lexicon`,
`expand` and `mark`. The `expand` stage reads numbers, dates and abbreviations,
so the gate judges it in each of the three categories. The scriptconv
phonemizer named `tugaphone` cannot switch a stage off, so the gate names the
backend as `module:attribute`.

## Build the sets

Each `<lang>.spec.tsv` gives a sentence and the words that a reader says for
it. `build.py` looks up the IPA of each spoken word and writes `<lang>.tsv`.
Edit the spec, never the TSV, and run this command:

```
python tests/data/sentences/build.py pt-PT pt-BR
```

The script needs `huggingface_hub` and network access. It downloads the
lexicon at a fixed revision and bifonia's sense table at a fixed commit.

## Sources

No `expected_ipa` comes from tugaphone or orthography2ipa output.

**Word readings.** Every word comes from a human row of
`TigreGotico/portuguese-unified-pronunciation-lexicon`, revision
`23898e1437dc77e84681bb7ce5580a9b3e2d04ba`. A human row has an Infopédia,
Michaelis or Wiktionary URL. The Portal da Língua Portuguesa (LUPo) rows are
rule output, so the script does not read them. The `source` column gives the
letter of each word: `I` Infopédia, `M` Michaelis, `W` Wiktionary. pt-PT reads
Infopédia first, then Wiktionary. pt-BR reads Michaelis first, then Wiktionary.
A Wiktionary row with no region (`pt`) comes last.

**Homograph senses.** `B:<sense>` is the Infopédia reading of one sense in
bifonia's `bifonia/data/infopedia_pt.csv`, commit `4bf96de`. A pt-BR homograph
takes the Michaelis or Wiktionary row whose stressed vowel matches the sense.

**Function words.** Infopédia gives the article and preposition `a` only as
[a], the name of the letter. pt-PT takes [ɐ] from Cruz-Ferreira (1999),
*Handbook of the IPA*, p. 130 (`CF130`). For `o` and `e`, the other reading in
the lexicon is the name of the letter, so the sets take [u] and [i].

**Spoken readings.** A number, date or abbreviation row cites the reading of
its written form after `reading:`:

| Short form | Source |
| --- | --- |
| C&C p.385 to p.391 | Cunha & Cintra, *Nova Gramática do Português Contemporâneo*, 7th ed.: gender of cardinals (p. 385), cem and cento (p. 386), the conjunction e and the forms catorze, dezasseis, dezassete, dezanove (p. 387), ordinals and cardinals after a noun (p. 388), the table of cardinals and ordinals (pp. 390-391) |
| C&C p.374 via Ciberdúvidas 32700 | cardinals for the day and the year, the ordinal for the first day of the month; a numeric date reads as day, month name and year |
| AO1990 Base XIX 1.º b) | month names in lowercase |
| Priberam DLPO 'Sr.' and others | the dictionary entry of the abbreviation: Sr., Dr., Dra., Prof., Eng., av., pág., séc., cap. |
| VOLP-ACL | the abbreviation list of the Vocabulário Ortográfico da Língua Portuguesa, as `tests/test_honorific_abbreviations.py` quotes it |

A surname that is also a noun, such as Costa or Rocha, takes the reading of
the noun.

## Rules

**Composition.** A sentence is the isolation form of each word, in order,
separated by spaces. The sets write no cross-word process: no sibilant
sandhi and no vowel elision. The gate therefore scores sentences against
isolation forms. A backend that writes sandhi loses on it, and its baseline
loses the same, so the gain of a stage does not change.

**Notation.** The script changes symbols only, never a sound:

- `ə` is `ɨ` in pt-PT and `ɐ` in pt-BR, and `ʀ` is `ʁ`.
- A bare `r` becomes `ʁ` for a written ⟨rr⟩, a word-initial ⟨r⟩, or ⟨r⟩ after
  ⟨n l s⟩, and `ɾ` elsewhere.
- Both elements of a nasal diphthong carry the tilde. pt-BR writes nasal `ã`
  as `ɐ̃`.
- `i̯ u̯` are `j w`, `ɪ ʊ` are `i u`, `g` is `ɡ`, and syllable dots go.

Michaelis transcribes pt-BR in broad notation, so pt-BR gold writes [ti di]
where a narrow transcription writes the affricates. Absolute PER therefore
does not compare across sources. The gain of a stage does.

**Choices.** Infopédia writes an optional vowel as `(ə)`, and the lexicon
keeps the forms with and without it. The script takes the full form. For
⟨ou⟩ Infopédia gives [o] and [ow], and the script takes [o]. A word with two
readings and no rule takes the reading that the spec names after `@`.

**pt-PT norm.** pt-PT gold follows the official norm, so it must not carry a
Lisbon trait. Infopédia writes two of them: ⟨ei⟩ as [ɐj], and a stressed
⟨e⟩ as [ɐ] before a palatal. The script refuses a gold row with either trait.
A row that needs such a word, for example `primeiro` or `engenheiro`, is
silver, with the [ej] reading written by hand.

**Silver.** A word with no human reading in these sources is written by hand
after `~`, and its row is silver. The `source` column says why. The gate
scores gold and silver apart, and only gold sets the verdict.

**The lexicon stage.** The pt-PT packaged lexicon of o2i-lexicons holds
Infopédia rows of the same dataset. The gain of the `lexicon` stage on pt-PT
`plain` rows therefore measures, in part, agreement of Infopédia with itself.
