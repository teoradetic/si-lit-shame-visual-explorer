import pandas as pd
import pytest

from emotion_explorer.emotion import SHAME

HIGH = {"0_1": 0.95, "0_10": 8, "0_100": 85}
BROAD_ONLY = {"0_1": 0.85, "0_10": 8, "0_100": 85}
LOW = {"0_1": 0.0, "0_10": 0, "0_100": 0}


def paragraph(text: str, scores: dict[str, float], stem: bool = False) -> dict:
    return {
        "text": text,
        SHAME.stem_key: stem,
        **{SHAME.score_key.format(scale=s): v for s, v in scores.items()},
    }


def keyed(paragraphs: list[dict]) -> dict[str, dict]:
    """Paragraph ids are string keys in the raw JSON."""
    return {str(i): p for i, p in enumerate(paragraphs)}


@pytest.fixture
def annotations() -> dict:
    """Two small novels; A has a core paragraph at 2 and a broad one at 5."""
    novel_a = [paragraph(f"A{i} " * (i + 1), LOW) for i in range(10)]
    novel_a[2] = paragraph("Sram ga je bilo.", HIGH, stem=True)
    novel_a[5] = paragraph("Zardel je.", BROAD_ONLY)
    novel_b = [paragraph(f"B{i} " * 3, LOW) for i in range(4)]
    return {
        "N1": {"author": "X", "title": "A", "paragraphs": keyed(novel_a)},
        "N2": {"author": "Y", "title": "B", "paragraphs": keyed(novel_b)},
    }


@pytest.fixture
def metadata() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "novel_id": ["N1", "N2"],
            "author": ["X", "Y"],
            "title": ["A", "B"],
            "year": [1900, 1910],
            "period": ["Realism", "Modernism"],
            "gender": ["M", "F"],
            "word_count": [100, 50],
            "source_corpus": ["KDSP", "KDSP"],
            "doc_link": ["", ""],
        }
    )
