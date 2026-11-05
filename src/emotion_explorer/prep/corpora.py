"""The source corpora with ready-made lemmas and tags.

They hold 262 of the 305 novels and go to data/corpora, which is not committed.
Only the annotated editions are fetched. The other 43 novels (Wikisource and
Wikivir) have no annotation, and their text is already in the annotated corpus.
"""

import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from emotion_explorer.paths import CORPORA_DIR

CLARIN_URL = "https://www.clarin.si/repository/xmlui/bitstream/handle"
ELTEC_URL = "https://raw.githubusercontent.com/COST-ELTeC/ELTeC-slv/v2.0.0/level2"


@dataclass(frozen=True)
class Source:
    # Where one novel's file ends up, under CORPORA_DIR.
    folder: str
    suffix: str
    # The zip holding the whole corpus; without one, novels come one by one.
    archive: str | None = None


SOURCES = {
    "KDSP": Source(
        "KDSP.TEI.ana", ".ana.xml", f"{CLARIN_URL}/11356/1823/KDSP.TEI.ana.zip"
    ),
    "PriLit": Source(
        "PriLit.ana", ".ana.xml", f"{CLARIN_URL}/11356/1319/PriLit.ana.zip"
    ),
    "ELTeC": Source("ELTeC.l2", "-L2.xml"),
}


def tei_path(source_corpus: str, original_id: str) -> Path:
    source = SOURCES[source_corpus]
    return CORPORA_DIR / source.folder / f"{original_id}{source.suffix}"


def download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {url}")
    with urllib.request.urlopen(url) as response, path.open("wb") as out:
        shutil.copyfileobj(response, out)


def download_archive(source: Source) -> None:
    if (CORPORA_DIR / source.folder).exists():
        return
    path = CORPORA_DIR / Path(source.archive).name
    download(source.archive, path)
    with zipfile.ZipFile(path) as archive:
        archive.extractall(CORPORA_DIR)
    path.unlink()


def download_corpora(metadata: pd.DataFrame) -> None:
    """Fetch whatever is missing; a finished download is never repeated."""
    for source in SOURCES.values():
        if source.archive:
            download_archive(source)
    for row in metadata[metadata["source_corpus"] == "ELTeC"].itertuples():
        path = tei_path("ELTeC", row.original_id)
        if not path.exists():
            download(f"{ELTEC_URL}/{path.name}", path)
