"""Filesystem locations shared by the CLI and the app."""

from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_DIR / "data"
# Entry points from the first project; never edited.
RAW_DIR = DATA_DIR / "raw"
# Everything derived from RAW_DIR; small enough to deploy.
PROCESSED_DIR = DATA_DIR / "processed"

CORPUS_METADATA_CSV = RAW_DIR / "corpus_metadata.csv"
ANNOTATIONS_JSON_ZST = RAW_DIR / "main_shame_annotations.json.zst"

# Outputs, in build order. The app reads only these.
META_JSON = PROCESSED_DIR / "meta.json"
PARAGRAPHS = PROCESSED_DIR / "paragraphs.parquet"
COMPARISON = PROCESSED_DIR / "comparison.parquet"
EXCERPTS = PROCESSED_DIR / "excerpts.parquet"
TEXTS = PROCESSED_DIR / "texts.parquet"
NOVELS = PROCESSED_DIR / "novels.parquet"
POSITION_BINS = PROCESSED_DIR / "position_bins.parquet"
WORD_COUNTS = PROCESSED_DIR / "word_counts.parquet"
WORD_PRIOR = PROCESSED_DIR / "word_prior.parquet"
STYLE_PARAGRAPHS = PROCESSED_DIR / "style_paragraphs.parquet"
STYLE_NOVELS = PROCESSED_DIR / "style_novels.parquet"
