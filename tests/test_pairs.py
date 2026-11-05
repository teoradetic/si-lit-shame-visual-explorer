import pandas as pd

from emotion_explorer.analysis.pairs import ANY, count_pairs, keep_strong, pmi


def test_count_pairs_counts_sentences_once():
    words = pd.DataFrame(
        {
            "novel_id": "N1",
            "para_id": [0, 0, 0, 0, 1],
            "sentence": [0, 0, 0, 1, 2],
            "word": ["sram", "lice", "sram", "lice", "biti"],
        }
    )
    pairs = count_pairs(words, keep={"sram", "lice"})
    counts = {(a, b): n for a, b, n in pairs[["a", "b", "n"]].itertuples(index=False)}
    assert counts == {
        (ANY, ANY): 3,
        (ANY, "lice"): 2,
        (ANY, "sram"): 1,
        ("lice", "sram"): 1,
    }


def test_pmi_is_one_at_twice_chance():
    assert pmi(n_ab=2, n_a=4, n_b=5, n=20) == 1


def test_keep_strong_keeps_the_sentence_counts_of_its_words():
    pairs = pd.DataFrame(
        {"a": [ANY, ANY, ANY, ANY, "a", "b"], "b": [ANY, "a", "b", "c", "b", "c"]}
    )
    kept = pd.MultiIndex.from_tuples([("a", "b")])
    assert keep_strong(pairs, kept).index.tolist() == [0, 1, 2, 4]
