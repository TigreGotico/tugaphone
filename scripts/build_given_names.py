"""Build tugaphone/data/given_names.json, the given names that the text
normaliser needs, with their gender.

The list holds only the names that can stand before a Roman numeral or
after "D.":

* Regnal names. The Portuguese label of every pope and monarch on Wikidata
  ("Pio XII", "Isabel II", "Afonso I") gives the word before the numeral,
  and the person's sex (P21) gives its gender.
* Brazilian given names. The first names of the IBGE 2010 census, as
  published by datasets-br/prenomes (ODC-PDDL), are matched without accents
  to the Portuguese and multilingual labels of Wikidata given-name items
  ("JOAO" -> "João"). The census list has no accents and no gender, so only
  the names that match a Wikidata given name enter the list.
* Portuguese given names. The Wikidata given-name items whose language of
  work or name (P407) is Portuguese.

Gender, in order of precedence: the sexes of the rulers who bore the name,
then the Wikidata items marked Portuguese, then every Wikidata item with the
label. One gender gives "masculine" or "feminine"; a name borne by both, or
a unisex item, gives "both". tugaphone reads a "both" name as masculine.

A name is one capitalised word of three or more letters. Shorter labels
("Do", "Da", "Vi") are function words or verb forms in Portuguese text far
more often than names. No other word is left out: a name that is also a
common word stays in the list.

The queries run on the QLever Wikidata endpoint, which returns the full
result sets; the Wikidata Query Service times out on the given-name query.

    python scripts/build_given_names.py [--endpoint URL] [--common N] [--out PATH]
"""
from __future__ import annotations

import argparse
import csv
import datetime
import io
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ENDPOINT = "https://qlever.dev/api/wikidata"
IBGE_CSV = ("https://raw.githubusercontent.com/datasets-br/prenomes/"
            "b745134c1cb710bad2b0e4800dce7a1cbb9b478a/data/nomes-censos-ibge.csv")
OUT = Path(__file__).resolve().parent.parent / "tugaphone" / "data" / "given_names.json"
USER_AGENT = "tugaphone-build-given-names (https://github.com/TigreGotico/tugaphone)"

PREFIXES = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""
# Popes (Q19546) and holders of a position or noble title under monarch (Q116).
RULERS_QUERY = PREFIXES + """
SELECT DISTINCT ?person ?label ?sex WHERE {
  { ?person wdt:P39 wd:Q19546 }
  UNION { ?person wdt:P39 ?position . ?position wdt:P279* wd:Q116 }
  UNION { ?person wdt:P97 ?title . ?title wdt:P279* wd:Q116 }
  ?person rdfs:label ?label . FILTER(LANG(?label) = "pt")
  OPTIONAL { ?person wdt:P21 ?sex }
}
"""
GIVEN_NAMES_QUERY = PREFIXES + """
SELECT ?item ?cls ?label ?pt WHERE {
  VALUES ?cls { wd:Q12308941 wd:Q11879590 wd:Q3409032 }
  ?item wdt:P31 ?cls ; rdfs:label ?label .
  FILTER(LANG(?label) = "pt" || LANG(?label) = "mul")
  OPTIONAL { ?item wdt:P407 ?pt . FILTER(?pt = wd:Q5146) }
}
"""
CLASSES = {"Q12308941": "masculine", "Q11879590": "feminine", "Q3409032": "both"}
SEXES = {"Q6581097": "masculine", "Q6581072": "feminine"}

NAME = re.compile(r"[A-ZÀ-Ý][a-zà-ÿ]{2,}")
REGNAL = re.compile(r"(?:^|\s)([A-ZÀ-Ý][a-zà-ÿ]+) [IVXLC]+(?=$|[\s,])")


def get(url: str, accept: str, tries: int = 5) -> str:
    request = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": USER_AGENT})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == tries - 1:
                raise
            time.sleep(int(error.headers.get("Retry-After") or 30))
    raise AssertionError("unreachable")


def sparql(endpoint: str, query: str) -> list[dict[str, str]]:
    text = get(endpoint + "?" + urllib.parse.urlencode({"query": query}), "text/csv")
    return list(csv.DictReader(io.StringIO(text)))


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def fold(name: str) -> str:
    decomposed = unicodedata.normalize("NFD", name.upper())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def is_name(label: str) -> bool:
    return bool(NAME.fullmatch(label))


def regnal_names(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    genders: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        match = REGNAL.search(row["label"])
        sex = SEXES.get(qid(row["sex"])) if row["sex"] else None
        if match and sex and is_name(match.group(1)):
            genders[match.group(1)].add(sex)
    return genders


def wikidata_genders(rows: list[dict[str, str]]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """(genders from every item, genders from items marked Portuguese)."""
    every: dict[str, set[str]] = defaultdict(set)
    portuguese: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if is_name(row["label"]):
            gender = CLASSES[qid(row["cls"])]
            every[row["label"]].add(gender)
            if row["pt"]:
                portuguese[row["label"]].add(gender)
    return every, portuguese


def census_names(text: str, count: int | None) -> list[str]:
    """The first names of the census, most frequent first, accent-free."""
    totals = Counter()
    for row in csv.DictReader(io.StringIO(text)):
        totals[row["Nome"]] = sum(int(v or 0) for k, v in row.items() if k != "Nome")
    return [name for name, _ in totals.most_common(count)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--endpoint", default=ENDPOINT)
    parser.add_argument("--common", type=int, default=None,
                        help="match only the N most frequent census names")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    ruler_rows = sparql(args.endpoint, RULERS_QUERY)
    name_rows = sparql(args.endpoint, GIVEN_NAMES_QUERY)
    census = census_names(get(IBGE_CSV, "text/csv"), args.common)

    regnal = regnal_names(ruler_rows)
    every, portuguese = wikidata_genders(name_rows)
    by_fold: dict[str, list[str]] = defaultdict(list)
    for label in every:
        by_fold[fold(label)].append(label)
    matched = {label for folded in census for label in by_fold.get(folded, [])}
    wanted = set(regnal) | set(portuguese) | matched

    lists: dict[str, list[str]] = {"masculine": [], "feminine": [], "both": []}
    for name in wanted:
        found = regnal.get(name) or portuguese.get(name) or every[name]
        lists[next(iter(found)) if len(found) == 1 else "both"].append(name)
    lists = {gender: sorted(names) for gender, names in lists.items()}

    data = {
        "about": {
            "description": "Given names that can stand before a Roman numeral or "
                           "after 'D.', with their gender. Used by "
                           "tugaphone.text_normalization.",
            "sources": [
                ("Wikidata: Portuguese labels of popes and monarchs, and their "
                 "sex (P21); labels of given-name items (Q12308941, Q11879590, "
                 "Q3409032). Licence CC0 1.0 "
                 "(https://www.wikidata.org/wiki/Wikidata:Licensing)."),
                ("IBGE Censo 2010 first names"
                 + (f", the {args.common} most frequent," if args.common else "")
                 + f" as published by datasets-br/prenomes under ODC-PDDL-1.0 ({IBGE_CSV})."),
            ],
            "endpoint": args.endpoint,
            "retrieved": datetime.date.today().isoformat(),
            "build_script": "scripts/build_given_names.py",
            "gender_rule": "Rulers' sex first, then Wikidata items marked "
                           "Portuguese, then all Wikidata items. 'both' is read "
                           "as masculine.",
        },
        **lists,
    }
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    counts = {gender: len(names) for gender, names in lists.items()}
    print(f"in: {len(ruler_rows)} ruler rows ({len(regnal)} regnal names), "
          f"{len(name_rows)} given-name rows ({len(portuguese)} marked Portuguese), "
          f"{len(census)} census names ({len(matched)} labels matched)")
    print(f"out: {sum(counts.values())} names {counts} "
          f"(union of the three sets: {len(wanted)})")


if __name__ == "__main__":
    main()
