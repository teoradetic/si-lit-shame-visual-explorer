import pandas as pd

from emotion_explorer.analysis.words import (
    count_words,
    lemma_stats,
    lexicon,
    read_words,
    vocabulary,
    word_forms,
)


def test_read_words_lowercases_lemmas_and_drops_what_is_no_word(tmp_path):
    path = tmp_path / "N1.parquet"
    pd.DataFrame(
        {
            "para_id": [0, 0, 0, 1, 1, 1],
            "form": ["Sram", "ga", ".", "Janez", "1848", "Očí"],
            "lemma": ["Sram", "on", ".", "Janez", "1848", "očí"],
            "upos": ["NOUN", "PRON", "PUNCT", "PROPN", "NUM", "NOUN"],
            "feats": ["Case=Nom", "Case=Acc", None, "Case=Nom", None, "Case=Gen"],
            "entity": [None, None, None, "PER", None, None],
        }
    ).to_parquet(path)
    words = read_words(path)
    assert words["word"].tolist() == ["sram", "on", "janez", "oči"]
    assert words["form"].tolist() == ["sram", "ga", "janez", "očí"]
    assert words["name"].tolist() == [False, False, True, False]
    assert words["case"].tolist() == ["Nom", "Acc", "Nom", "Gen"]


def test_lexicon_takes_the_commonest_pos_and_finds_names():
    words = pd.DataFrame(
        {
            "word": ["sram"] * 3 + ["janez"] * 2 + ["zora"] * 3,
            "pos": ["NOUN", "NOUN", "ADV", "PROPN", "PROPN", "NOUN", "NOUN", "PROPN"],
            "name": [False] * 3 + [True] * 2 + [False, False, True],
        }
    )
    halves = [lemma_stats(words.iloc[:4]), lemma_stats(words.iloc[4:])]
    lex = lexicon(pd.concat(halves))
    assert lex.loc["sram", "pos"] == "NOUN"
    assert lex.loc["sram", "n_corpus"] == 3
    assert lex.loc["janez", "name"]
    # A name in a minority of uses is not a name.
    assert not lex.loc["zora", "name"]


def test_vocabulary_drops_names_and_rare_lemmas():
    counts = pd.Series({"sram": 12, "janez": 30, "redko": 2})
    assert vocabulary(counts, names={"janez"}) == {"sram"}


def test_count_words_per_novel_and_case():
    words = pd.DataFrame(
        {
            "novel_id": ["N1", "N1", "N1", "N2"],
            "word": ["sram", "sram", "sram", "biti"],
            "case": ["Nom", "Nom", None, None],
        }
    )
    counts = count_words(words, keep={"sram"})
    assert counts.fillna("-").to_dict("records") == [
        {"novel_id": "N1", "word": "sram", "case": "Nom", "n": 2},
        {"novel_id": "N1", "word": "sram", "case": "-", "n": 1},
    ]


def test_each_form_finds_one_lemma():
    words = pd.DataFrame(
        {
            "form": ["je", "je", "je", "sramu", "ga"],
            "word": ["biti", "biti", "on", "sram", "on"],
        }
    )
    forms = word_forms(words, keep={"biti", "on", "sram"})
    assert forms.to_dict("records") == [
        {"word": "biti", "form": "je"},
        {"word": "on", "form": "ga"},
        {"word": "sram", "form": "sramu"},
    ]
