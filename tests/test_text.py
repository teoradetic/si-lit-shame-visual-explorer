from emotion_explorer.text import has_dialogue, sentences, words

TEXT = "»Kaj pa ti, Janez?« je vprašala Marija. Sram ga je bilo … Potem je šel."


def test_words_are_lower_case_letters():
    assert words("Šel je 3x domov.") == ["šel", "je", "x", "domov"]


def test_sentences():
    assert sentences(TEXT) == [
        "»Kaj pa ti, Janez?« je vprašala Marija.",
        "Sram ga je bilo …",
        "Potem je šel.",
    ]


def test_dialogue():
    assert has_dialogue(TEXT)
    assert has_dialogue("– Ne vem.")
    assert not has_dialogue("Šel je domov.")
