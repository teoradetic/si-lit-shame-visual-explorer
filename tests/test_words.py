from collections import Counter

import pandas as pd

from emotion_explorer.words import count_words, function_words, vocabulary


def test_vocabulary_drops_names_rare_and_short_words():
    counts = Counter({"sram": 12, "janez": 30, "redko": 2, "v": 50})
    assert vocabulary(counts, names={"janez"}) == {"sram"}


def test_count_words_per_novel():
    paragraphs = pd.DataFrame(
        {"novel_id": ["N1", "N1", "N2"], "words": [["sram", "je"], ["sram"], ["je"]]}
    )
    counts = count_words(paragraphs, keep={"sram"})
    assert counts.to_dict("records") == [{"novel_id": "N1", "word": "sram", "n": 2}]


def test_function_words():
    assert {"je", "in", "ti"} <= function_words()
    assert "sram" not in function_words()
