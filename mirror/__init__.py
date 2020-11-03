import pathlib

MIRROR_DATA = pathlib.Path(__file__).parent
MIRROR_DATA = MIRROR_DATA / ".." / "data" / "mirror-data.yaml"

MIRROR_LOCK = MIRROR_DATA.parent / "mirror-data.lock"

if not MIRROR_DATA.parent.exists():
    MIRROR_DATA.parent.mkdir(parents=True)
