import pandas as pd

from emotion_explorer.analysis import themes


def test_fit_themes_separates_two_vocabularies(monkeypatch):
    monkeypatch.setattr(themes, "N_THEMES", 2)
    monkeypatch.setattr(themes, "MIN_PARAGRAPHS", 1)
    monkeypatch.setattr(themes, "MAX_SHARE", 1.0)
    family, church = ["oče", "mati", "sin"], ["cerkev", "greh", "vera"]
    words = pd.DataFrame(
        [
            ("N1", p, w)
            for p in range(6)
            for w in (family if p < 3 else church)[: 2 + p % 2]
        ],
        columns=["novel_id", "para_id", "word"],
    )
    _, main = themes.fit_themes(words)
    by_paragraph = main.set_index("para_id")["theme"]
    assert by_paragraph[0] == by_paragraph[2] != by_paragraph[3] == by_paragraph[5]
