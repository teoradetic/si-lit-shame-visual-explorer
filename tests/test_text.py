import pandas as pd

from emotion_explorer.analysis.text import sentences, speech_flags, split_speech, words

TEXT = "»Kaj pa ti, Janez?« je vprašala Marija. Sram ga je bilo … Potem je šel."


def test_words_are_lower_case_letters():
    assert words("Šel je 3x domov.") == ["šel", "je", "x", "domov"]


def test_sentences():
    assert sentences(TEXT) == [
        "»Kaj pa ti, Janez?« je vprašala Marija.",
        "Sram ga je bilo …",
        "Potem je šel.",
    ]


def test_split_speech():
    texts = pd.Series([TEXT, "– Ne vem.", "Šel je domov."])
    parts = split_speech(texts)
    assert parts.loc[0, "dialogue"] == "» Kaj pa ti, Janez? «"
    assert parts.loc[0, "narration"].startswith("je vprašala Marija.")
    assert parts["dialogue"].tolist()[1:] == ["– Ne vem.", ""]
    assert parts.loc[2, "all"] == "Šel je domov."


def test_speech_flags_on_tokens():
    tokens = pd.Series(
        ["«", "Ne", "«", "je", "rekel", "–", "Da"], index=[1] * 5 + [2] * 2
    )
    assert speech_flags(tokens).tolist() == [True] * 3 + [False] * 2 + [True] * 2
