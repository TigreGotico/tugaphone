"""The spelling step reads old Portuguese spellings in the AO1990 spelling of the lect.

The step runs desacordo_ortografico before G2P, as the first stage of the pipeline's
``expand``. Each expected value below comes from the source quoted next to it, not from
tugaphone output.
"""
import csv
from pathlib import Path

import pytest

from tugaphone import lattice_core, list_dialects, registry

SENTENCES = Path(__file__).parent / "data" / "sentences"
LECTS = {"pt": ["pt-PT", "pt-PT-x-porto", "pt-AO"], "br": ["pt-BR", "pt-BR-x-sp", "pt-UY"]}

# Old spellings and their AO1990 forms, the same in both norms.
OLD_WORDS = [
    # desacordo spelling.json row "pharmacia" -> "farmácia", source "Reforma Ortográfica
    # de 1911 (Portaria de 1 de setembro de 1911), comissão de Gonçalves Viana (digraphs)",
    # group digraphs: "ph->f, th->t, rh->r, y->i. Modern values carry the accent the 1911
    # systematic accentuation introduced."
    ("pharmacia", "farmácia"),
    ("Pharmacia", "Farmácia"),
    # The same source and group, row "lyrio" -> "lírio".
    ("lyrio", "lírio"),
    # AO1990 Base IV 1.º b): "Eliminam-se nos casos em que são invariavelmente mudos nas
    # pronúncias cultas da língua: ação, acionar, afetivo, aflição, aflito, ato, coleção,
    # coletivo, direção, diretor, exato, objeção; adoção, adotar, batizar, Egito, ótimo."
    ("acção", "ação"),
]

# AO1990 Base XV 1.º Obs.: "Certos compostos, em relação aos quais se perdeu, em certa
# medida, a noção de composição, grafam-se aglutinadamente: girassol, madressilva,
# mandachuva, pontapé, paraquedas, paraquedista, etc."
BR_OLD_WORDS = [("manda-chuva", "mandachuva")]

# Text valid in the AO1990 spelling of the norm, so the step leaves it as written.
MODERN_WORDS = {
    "pt": [
        # VOP lemma 47603: "sector - nome masculino ... variante AO de : setor"
        "sector",
        # VOP lemma 48215: "carácter - nome masculino ... Portugal ... variante AO de : caráter"
        "carácter",
        # VOP lemma 106786: "acupunctura - nome feminino ... variante AO de : acupuntura"
        "acupunctura",
    ],
    "br": [
        # VOLP: "fato s.m. | facto s.m."
        "facto",
        # VOLP: "contato s.m. | contacto s.m."
        "contacto",
        # VOLP: "corruto adj. s.m. | corrupto adj. s.m."
        "corrupto",
    ],
}

OLD_SENTENCES = [
    "A acção da pharmacia foi rápida.",
    "O lyrio do theatro murchou.",
    "A Pharmacia Central abriu, e a acção começou.",
]


def _battery(lang):
    with open(SENTENCES / f"{lang}.tsv", encoding="utf-8", newline="") as f:
        rows = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        return [row["text"] for row in rows if not any(c.isdigit() for c in row["text"])]


def _cases(words, groups=("pt", "br")):
    return [pytest.param(lect, old, new, id=f"{lect}-{old}")
            for group in groups for lect in LECTS[group] for old, new in words]


@pytest.mark.parametrize("lect, old, new", _cases(OLD_WORDS))
def test_old_spelling_reads_as_ao1990(lect, old, new):
    assert lattice_core._expander(lect)(old) == new


@pytest.mark.parametrize("lect, old, new", _cases(BR_OLD_WORDS, groups=("br",)))
def test_br_group_joins_a_base_xv_compound(lect, old, new):
    assert lattice_core._expander(lect)(old) == new


@pytest.mark.parametrize("lect", LECTS["pt"] + LECTS["br"])
def test_step_runs_before_the_other_stages(lect):
    expand = lattice_core._expander(lect)
    assert expand(" A acção da pharmacia. ") == " A ação da farmácia. "


@pytest.mark.parametrize("lect, word", [
    pytest.param(lect, word, id=f"{lect}-{word}")
    for group, words in MODERN_WORDS.items() for lect in LECTS[group] for word in words])
def test_modern_dual_form_stays(lect, word):
    assert lattice_core.normalize_spelling(word, lect) == word
    assert lattice_core.normalize_spelling(f"O {word}, disse.", lect) == f"O {word}, disse."


# VOLP: ótica s.f. "ciência da audição"; cf. óptica | óptica s.f. "ciência da visão";
# cf. ótica. The two are different words, so pt-BR óptica stays. desacordo's base-iv
# map drops the p, and its own test marks the same row (p04-013) as a strict xfail.
@pytest.mark.xfail(strict=True, reason="desacordo base_iv.json drops the p of óptica")
@pytest.mark.parametrize("lect", LECTS["br"])
def test_br_group_keeps_optica(lect):
    assert lattice_core.normalize_spelling("A fibra óptica.", lect) == "A fibra óptica."


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
def test_step_keeps_the_word_count(lang):
    texts = _battery(lang) + OLD_SENTENCES
    assert len(texts) > 150
    changed = 0
    for text in texts:
        out = lattice_core.normalize_spelling(text, lang)
        changed += out != text
        assert len(out.split()) == len(text.split()), (text, out)
    assert changed >= len(OLD_SENTENCES)


@pytest.mark.parametrize("lang", ["pt-PT", "pt-BR"])
def test_step_is_idempotent(lang):
    texts = _battery(lang) + OLD_SENTENCES + [old for old, _ in OLD_WORDS + BR_OLD_WORDS]
    for text in texts:
        once = lattice_core.normalize_spelling(text, lang)
        assert lattice_core.normalize_spelling(once, lang) == once, (text, once)


def test_every_lect_follows_one_norm():
    norms = {lect: registry.spelling_norm(lect) for lect in list_dialects()}
    assert set(norms.values()) == {"ao1990-pt", "ao1990-br"}
    for group, norm in (("pt", "ao1990-pt"), ("br", "ao1990-br")):
        for lect in LECTS[group]:
            assert norms[lect] == norm, lect
    assert all(norm == "ao1990-br" for lect, norm in norms.items() if lect.startswith("pt-BR"))
