"""Numbers, dates and abbreviations read through text2spoken.

The expand stage of the pipeline reads numbers, dates, times, money, measures
and abbreviations with text2spoken, in the ``pt-PT`` or ``pt-BR`` variety of
the lect. Each expected value comes from the source named next to it, not from
tugaphone output. "t2s pt-NNN" names a row of text2spoken
``tests/data/pt.tsv`` at 0.0.2a69, or at the release that the comment names,
and the row names its own source.
"""
import csv
from pathlib import Path

import pytest

from tugaphone import lattice_core, list_dialects, phonemize, pipeline

SENTENCES = Path(__file__).parent / "data" / "sentences"

# Plan row 2.4: the readings of text2spoken 0.0.2a61 for 25/12/2023 and 19h30.
# t2s pt-080 and pt-090. Ciberdúvidas 32700 quotes Cunha & Cintra p. 374:
# "nas referências aos dias do mês usam-se os cardinais [...] Também na
# indicação dos anos e das horas se empregam os cardinais."
PLAN_ROWS = [
    ("pt-PT", "Nasceu a 25/12/2023.",
     "Nasceu a vinte e cinco de dezembro de dois mil e vinte e três."),
    ("pt-PT", "A reunião é às 19h30.", "A reunião é às dezanove horas e trinta minutos."),
    ("pt-BR", "Nasceu a 25/12/2023.",
     "Nasceu a vinte e cinco de dezembro de dois mil e vinte e três."),
    ("pt-BR", "A reunião é às 19h30.", "A reunião é às dezenove horas e trinta minutos."),
]

FORMS = [
    # cardinal, t2s pt-001 and pt-002 (Priberam: uma, duas)
    ("pt-PT", "Comprei 1 casa e 2 casas.", "Comprei uma casa e duas casas."),
    ("pt-BR", "Comprei 1 casa e 2 casas.", "Comprei uma casa e duas casas."),
    # ordinal, t2s pt-057 (Priberam: primeiro, segundo) and pt-127 (Dicio: 1.ª primeira)
    ("pt-PT", "A 1.ª vez e o 2.º lugar.", "A primeira vez e o segundo lugar."),
    ("pt-BR", "A 1ª vez.", "A primeira vez."),
    # decimal with a comma, t2s pt-016 (Priberam: vírgula)
    ("pt-PT", "O valor é 3,5 hoje.", "O valor é três vírgula cinco hoje."),
    ("pt-BR", "O valor é 3,5 hoje.", "O valor é três vírgula cinco hoje."),
    # year, tests/data/sentences/*.spec.tsv "Foi em 1974." (Cunha & Cintra p. 387)
    ("pt-PT", "Foi em 1974.", "Foi em mil novecentos e setenta e quatro."),
    ("pt-BR", "Foi em 1974.", "Foi em mil novecentos e setenta e quatro."),
    # range, t2s pt-076 (design section 4.2: the range word "a")
    ("pt-PT", "Idades 18-25 anos.", "Idades dezoito a vinte e cinco anos."),
    ("pt-BR", "Idades 18-25 anos.", "Idades dezoito a vinte e cinco anos."),
    # clock time, t2s pt-036 (Priberam: hora feminine) and pt-126 (Manual de Redação, p. 71)
    ("pt-PT", "Fecha às 21:00 hoje.", "Fecha às vinte e uma horas hoje."),
    ("pt-BR", "Chego às 2h.", "Chego às duas horas."),
    # clock time with a full stop after "às", t2s pt-800, pt-801, pt-804 and
    # pt-810 at 0.0.2a114 (Ciberdúvidas 14648: "Há quem prefira a notação 17.30 h")
    ("pt-PT", "Chego às 10.30 horas.", "Chego às dez e trinta horas."),
    ("pt-BR", "Chego às 16.30 horas.", "Chego às dezesseis e trinta horas."),
    ("pt-PT", "O comboio parte às 9.30h.", "O comboio parte às nove horas e trinta minutos."),
    ("pt-PT", "O bar fecha às 24.00.", "O bar fecha à meia-noite."),
    # year before a comma, t2s pt-856 and pt-857 at 0.0.2a113 (Ciberdúvidas
    # 10879: "de dois mil e um a dois mil e cem"; Priberam, ano: "nome masculino")
    ("pt-PT", "Foi fundada em 1763, cidade de Minas.",
     "Foi fundada em mil setecentos e sessenta e três, cidade de Minas."),
    ("pt-BR", "Foi fundada em 1763, cidade de Minas.",
     "Foi fundada em mil setecentos e sessenta e três, cidade de Minas."),
    # percentage, t2s pt-021 and pt-022 (Priberam: por cento, símbolo %)
    ("pt-PT", "hoje 20% está", "hoje vinte por cento está"),
    ("pt-BR", "hoje 20%.", "hoje vinte por cento."),
    # currency, t2s pt-023 (Priberam: euro, cêntimo) and pt-026 (Priberam: real)
    ("pt-PT", "Pagou 2,50 € ontem.", "Pagou dois euros e cinquenta cêntimos ontem."),
    ("pt-BR", "Custou R$ 10,50 hoje.", "Custou dez reais e cinquenta centavos hoje."),
]

# The scriptconv contract: raw text with "Dr." and "20%" reads through tugaphone
# alone. t2s pt-021 (Priberam: por cento); "Dr." is "Doutor" (Priberam DLPO
# "Dr.": "Abreviatura de doutor").
RAW = [
    ("pt-PT", "O Dr. Silva subiu 20%.", "O Doutor Silva subiu vinte por cento."),
    ("pt-BR", "O Dr. Silva subiu 20%.", "O Doutor Silva subiu vinte por cento."),
    ("pt-PT", "Falei com o Dr.", "Falei com o Doutor"),
]


def _digit_free(lang):
    with open(SENTENCES / f"{lang}.spec.tsv", encoding="utf-8", newline="") as f:
        rows = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        return [row["text"] for row in rows if not any(c.isdigit() for c in row["text"])]


@pytest.mark.parametrize("lang,text,spoken", PLAN_ROWS + FORMS + RAW)
def test_text_step_reads_the_form(lang, text, spoken):
    assert pipeline(lang).expand(text) == spoken
    assert phonemize(text, lang) == phonemize(spoken, lang)


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
def test_text_normalised_by_text2spoken_reads_as_raw_text(lang):
    # phoonnx sets the text2spoken normaliser hook, so text can reach tugaphone
    # already normalised. text2spoken is idempotent (its design section 11).
    from text2spoken import normalize
    for _, text, _ in [row for row in PLAN_ROWS + FORMS + RAW if row[0] == lang]:
        normalised = normalize(text, lang)
        assert pipeline(lang).expand(normalised) == pipeline(lang).expand(text), text
        assert phonemize(normalised, lang) == phonemize(text, lang), text


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
def test_spelled_out_text_stays_unchanged(lang):
    spelled = [spoken for row_lang, _, spoken in PLAN_ROWS + FORMS + RAW if row_lang == lang]
    for text in spelled:
        assert pipeline(lang).expand(text) == text


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
def test_digit_free_text_keeps_its_token_count(lang):
    # Plan row 2.3: on text with no digits, the output has one IPA token per
    # input word.
    texts = _digit_free(lang)
    assert len(texts) > 140
    for text in texts:
        assert len(pipeline(lang).expand(text).split()) == len(text.split()), text
        assert len(phonemize(text, lang).split()) == len(text.split()), text


@pytest.mark.parametrize("lect", list_dialects())
def test_each_lect_reads_the_variety_of_its_norm(lect):
    # t2s pt-084 and pt-085: 19 is "dezenove" in pt-BR and "dezanove" in pt-PT.
    nineteen = {"ao1990-pt": "dezanove", "ao1990-br": "dezenove"}[lattice_core.spelling_norm(lect)]
    assert pipeline(lect).expand("Tem 19 anos.") == f"Tem {nineteen} anos."
