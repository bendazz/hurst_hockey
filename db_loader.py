from pathlib import Path
import csv
import time
from typing import List

from sqlmodel import SQLModel, create_engine, Session
from models import Bio, Stats


HERE = Path(__file__).parent


def _coerce_int(value: str):
    try:
        return int(value)
    except Exception:
        return None


def _coerce_float(value: str):
    try:
        return float(value)
    except Exception:
        return None


def make_bio_instances(csv_path: str = "bio.csv") -> List[Bio]:
    """Read `csv_path` and return a list of `Bio` instances (no DB operations)."""
    csv_file = HERE / csv_path
    bios: List[Bio] = []
    with csv_file.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            num = _coerce_int(row.get("Number", ""))
            bio = Bio(
                Number=num,
                Player=(row.get("Player") or "").strip(),
                FirstName=(row.get("FirstName") or "").strip(),
                LastName=(row.get("LastName") or "").strip(),
                Position=(row.get("Position") or "").strip(),
                Height=(row.get("Height") or "").strip(),
                Weight=(row.get("Weight") or "").strip(),
                Class=(row.get("Class") or "").strip(),
                Hometown=(row.get("Hometown") or "").strip(),
                HighSchool=(row.get("HighSchool") or "").strip(),
            )
            bios.append(bio)
    return bios


def make_stats_instances(csv_path: str = "stats.csv") -> List[Stats]:
    """Read `csv_path` and return a list of `Stats` instances (no DB operations)."""
    csv_file = HERE / csv_path
    rows: List[Stats] = []
    int_fields = {"GP", "G", "A", "PTS", "SH", "plus_minus", "PPG", "SHG", "FG", "GWG", "GTG", "OTG", "HTG", "UAG", "MIN", "MAJ", "OTH", "BLK", "Number"}

    with csv_file.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            kw = {}
            kw["Number"] = _coerce_int(row.get("Number", ""))
            kw["FirstName"] = (row.get("FirstName") or "").strip()
            kw["LastName"] = (row.get("LastName") or "").strip()

            for key, val in row.items():
                if key in ("Number", "FirstName", "LastName"):
                    continue
                if key == "PN-PIM":
                    kw["PN_PIM"] = (val or "").strip()
                    continue
                if key in int_fields:
                    kw[key] = _coerce_int(val)
                elif key == "SH_PCT":
                    kw[key] = _coerce_float(val)
                else:
                    kw[key] = (val or "").strip()

            stat = Stats(**kw)
            rows.append(stat)
    return rows


def load_bios(db_url: str = "sqlite:///hurst.db", csv_path: str = "bio.csv") -> List[Bio]:
    """Create DB/tables, load `csv_path` into `Bio` rows, return list of `Bio` instances."""
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)

    csv_file = HERE / csv_path
    bios: List[Bio] = []
    with csv_file.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            num = _coerce_int(row.get("Number", ""))
            bio = Bio(
                Number=num,
                Player=(row.get("Player") or "").strip(),
                FirstName=(row.get("FirstName") or "").strip(),
                LastName=(row.get("LastName") or "").strip(),
                Position=(row.get("Position") or "").strip(),
                Height=(row.get("Height") or "").strip(),
                Weight=(row.get("Weight") or "").strip(),
                Class=(row.get("Class") or "").strip(),
                Hometown=(row.get("Hometown") or "").strip(),
                HighSchool=(row.get("HighSchool") or "").strip(),
            )
            bios.append(bio)

    with Session(engine) as session:
        session.add_all(bios)
        session.commit()

    return bios


def load_stats(db_url: str = "sqlite:///hurst.db", csv_path: str = "stats.csv") -> List[Stats]:
    """Create DB/tables, load `csv_path` into `Stats` rows, return list of `Stats` instances.

    Note: maps header `PN-PIM` -> attribute `PN_PIM`.
    """
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)

    csv_file = HERE / csv_path
    rows: List[Stats] = []
    int_fields = {"GP", "G", "A", "PTS", "SH", "plus_minus", "PPG", "SHG", "FG", "GWG", "GTG", "OTG", "HTG", "UAG", "MIN", "MAJ", "OTH", "BLK", "Number"}

    with csv_file.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            kw = {}
            # direct mappings
            kw["Number"] = _coerce_int(row.get("Number", ""))
            kw["FirstName"] = (row.get("FirstName") or "").strip()
            kw["LastName"] = (row.get("LastName") or "").strip()

            for key, val in row.items():
                if key in ("Number", "FirstName", "LastName"):
                    continue
                if key == "PN-PIM":
                    kw["PN_PIM"] = (val or "").strip()
                    continue
                if key in int_fields:
                    kw[key] = _coerce_int(val)
                elif key == "SH_PCT":
                    kw[key] = _coerce_float(val)
                else:
                    # keep as string
                    kw[key] = (val or "").strip()

            stat = Stats(**kw)
            rows.append(stat)

    with Session(engine) as session:
        session.add_all(rows)
        session.commit()

    return rows
