from types import SimpleNamespace

import pytest

from emotion_explorer.corpora import tei_path
from emotion_explorer.paths import CORPORA_DIR
from emotion_explorer.tokens import (
    assign_paragraphs,
    entity_of,
    paragraph_of_tokens,
    read_tei,
    split_msd,
    tagged_rows,
    to_table,
)

KDSP = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><p><s>
<name type="PER"><w msd="UPosTag=PROPN|Case=Nom|Gender=Masc|Number=Sing"
  lemma="Janez">Janez</w></name>
<w msd="UPosTag=VERB|Number=Sing" lemma="zardeti">zardi</w>
<pc msd="UPosTag=PUNCT">.</pc></s>
<s><w msd="UPosTag=ADV" lemma="zdaj">Zdaj</w></s></p></text></TEI>"""
# ELTeC keeps the part of speech apart, and punctuation may have no msd.
ELTEC = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><p><s>
<w pos="NOUN" msd="Case=Loc|Gender=Fem|Number=Sing|SpaceAfter=No|XPOS=Ncfsl"
  lemma="vas">vasi</w><pc pos="PUNCT">.</pc></s></p></text></TEI>"""


def test_split_msd_drops_what_is_no_morphology():
    assert split_msd("UPosTag=NOUN|Case=Nom|Gender=Fem") == (
        "NOUN",
        "Case=Nom|Gender=Fem",
    )
    assert split_msd("UposTag=ADV") == ("ADV", None)
    assert split_msd("Case=Loc|SpaceAfter=No|XPOS=Sl") == (None, "Case=Loc")
    assert split_msd("") == (None, None)


def test_read_tei_keeps_sentences_entities_and_punctuation(tmp_path):
    path = tmp_path / "novel.xml"
    path.write_text(KDSP, encoding="utf-8")
    rows = read_tei(path)
    assert [r[1:3] for r in rows] == [
        (0, "Janez"),
        (0, "zardi"),
        (0, "."),
        (1, "Zdaj"),
    ]
    assert rows[0][3:] == ("Janez", "PROPN", "Case=Nom|Gender=Masc|Number=Sing", "PER")
    assert rows[1][6] is None
    assert rows[2][3:5] == (".", "PUNCT")


def test_read_tei_takes_the_eltec_part_of_speech(tmp_path):
    path = tmp_path / "novel.xml"
    path.write_text(ELTEC, encoding="utf-8")
    assert [r[4:6] for r in read_tei(path)] == [
        ("NOUN", "Case=Loc|Gender=Fem|Number=Sing"),
        ("PUNCT", None),
    ]


def test_paragraphs_follow_the_text_not_the_markup():
    forms = ["Sram", "ga", "je", ".", "Zardel", "je", ".", "Konec"]
    texts = ["Sram ga\nje.", "", "Zardel je.", "Konec"]
    assert paragraph_of_tokens(forms, texts).tolist() == [0, 0, 0, 0, 2, 2, 2, 3]


def test_tokens_past_the_end_are_dropped():
    rows = [(None, 0, f, f, "X", None, None) for f in ["Sram", "ga", "je"]]
    assert [r[0] for r in assign_paragraphs(rows, ["Sram", "ga"])] == [0, 1]


def test_different_text_is_an_error():
    with pytest.raises(ValueError, match="do not hold the text"):
        paragraph_of_tokens(["Sram"], ["Strah"])


def test_entity_of():
    assert entity_of("B-PER") == "PER"
    assert entity_of("I-DERIV-PER") == "DERIV-PER"
    assert entity_of("O") is None
    assert entity_of(None) is None


def word(text, upos, ner="O"):
    tagged = SimpleNamespace(text=text, lemma=text.lower(), upos=upos, feats=None)
    return SimpleNamespace(words=[tagged], ner=ner)


def test_tagged_rows_number_paragraphs_and_sentences():
    docs = {
        "Janez zardi.": [[word("Janez", "PROPN", "B-PER"), word(".", "PUNCT")]],
        "Sram. Zdaj.": [[word("Sram", "NOUN")], [word("Zdaj", "ADV")]],
    }

    def tagger(text):
        return SimpleNamespace(
            sentences=[SimpleNamespace(tokens=s) for s in docs[text]]
        )

    table = to_table(tagged_rows(tagger, ["Janez zardi.", " ", "Sram. Zdaj."]))
    assert table["para_id"].tolist() == [0, 0, 2, 2]
    assert table["sentence"].tolist() == [0, 0, 1, 2]
    assert table["entity"].iloc[0] == "PER"
    assert table["entity"].iloc[1:].isna().all()


def test_tei_path():
    assert tei_path("ELTeC", "SLV1") == CORPORA_DIR / "ELTeC.l2" / "SLV1-L2.xml"
    assert tei_path("KDSP", "KDSP1") == (CORPORA_DIR / "KDSP.TEI.ana" / "KDSP1.ana.xml")
