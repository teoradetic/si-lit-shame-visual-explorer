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
