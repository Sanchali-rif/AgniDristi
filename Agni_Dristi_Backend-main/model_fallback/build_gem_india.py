from __future__ import annotations

from pathlib import Path
import csv
import json
import math
import re
import zipfile
import xml.etree.ElementTree as ET

# ============================================================
# CONFIG
# ============================================================
# Put this script in your Agni_Dristi_Backend main/root folder.
# Put the seven GEM files inside: Agni_Dristi_Backend/gem_dataset/
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "gem_dataset"
OUTPUT = ROOT / "GEM_INDIA_COMBINED_ALL.csv"

# Keep ALL Indian GEM records. Runtime matching should filter by status as needed.

OUTPUT_COLUMNS = [
    "gem_id",
    "facility_name",
    "category",
    "exact_type",
    "subtype",
    "status",
    "latitude",
    "longitude",
    "location_accuracy",
    "state",
    "owner",
    "operator",
    "capacity",
    "capacity_unit",
    "gem_tracker",
    "source_url",
]

# ============================================================
# SMALL XLSX READER (stdlib only)
# ============================================================
# XLSX is a ZIP of XML files. This avoids requiring pandas/openpyxl.
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


def _col_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    n = 0
    for ch in letters.upper():
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def read_xlsx_sheet(path: Path, sheet_name: str) -> list[dict]:
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall(f"{{{NS_MAIN}}}si"):
                text = "".join(t.text or "" for t in si.iter(f"{{{NS_MAIN}}}t"))
                shared.append(text)

        wb_root = ET.fromstring(z.read("xl/workbook.xml"))
        rel_root = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rels = {
            r.attrib["Id"]: r.attrib["Target"]
            for r in rel_root.findall(f"{{{NS_REL_PKG}}}Relationship")
        }

        target = None
        sheets_el = wb_root.find(f"{{{NS_MAIN}}}sheets")
        for s in sheets_el:
            if s.attrib.get("name") == sheet_name:
                rid = s.attrib.get(f"{{{NS_REL_DOC}}}id")
                target = rels[rid]
                break
        if target is None:
            raise KeyError(f"Sheet '{sheet_name}' not found in {path.name}")

        if target.startswith("/"):
            sheet_path = target.lstrip("/")
        elif target.startswith("xl/"):
            sheet_path = target
        else:
            sheet_path = "xl/" + target

        sheet_root = ET.fromstring(z.read(sheet_path))
        sheet_data = sheet_root.find(f"{{{NS_MAIN}}}sheetData")

        raw_rows = []
        max_col = -1
        for row in sheet_data.findall(f"{{{NS_MAIN}}}row"):
            vals = {}
            for c in row.findall(f"{{{NS_MAIN}}}c"):
                ref = c.attrib.get("r", "A1")
                idx = _col_index(ref)
                max_col = max(max_col, idx)
                ctype = c.attrib.get("t")
                value = None

                if ctype == "inlineStr":
                    is_el = c.find(f"{{{NS_MAIN}}}is")
                    if is_el is not None:
                        value = "".join(t.text or "" for t in is_el.iter(f"{{{NS_MAIN}}}t"))
                else:
                    v = c.find(f"{{{NS_MAIN}}}v")
                    if v is not None and v.text is not None:
                        raw = v.text
                        if ctype == "s":
                            value = shared[int(raw)] if raw else ""
                        elif ctype == "b":
                            value = raw == "1"
                        elif ctype in ("str", "e"):
                            value = raw
                        else:
                            try:
                                num = float(raw)
                                value = int(num) if num.is_integer() else num
                            except ValueError:
                                value = raw
                vals[idx] = value
            raw_rows.append(vals)

    if not raw_rows:
        return []

    width = max_col + 1
    rows = [[r.get(i) for i in range(width)] for r in raw_rows]
    headers = [str(x).strip() if x is not None else "" for x in rows[0]]
    records = []
    for row in rows[1:]:
        if not any(v not in (None, "") for v in row):
            continue
        rec = {}
        for i, h in enumerate(headers):
            if h:
                rec[h] = row[i] if i < len(row) else None
        records.append(rec)
    return records


# ============================================================
# HELPERS
# ============================================================
def norm(value) -> str:
    return "" if value is None else str(value).strip()


def lower(value) -> str:
    return norm(value).casefold()


def is_india(record: dict, country_col: str) -> bool:
    return lower(record.get(country_col)) == "india"


def as_float(value):
    if value is None or value == "":
        return None
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def split_coords(value):
    if value is None:
        return None, None
    parts = str(value).split(",", 1)
    if len(parts) != 2:
        return None, None
    return as_float(parts[0].strip()), as_float(parts[1].strip())


def join_unique(values):
    cleaned = sorted({norm(v) for v in values if norm(v)})
    return "; ".join(cleaned) if cleaned else ""


def valid_india_coords(lat, lon):
    return lat is not None and lon is not None and 6 <= lat <= 38 and 68 <= lon <= 98


def find_one(*patterns: str) -> Path:
    for pattern in patterns:
        hits = sorted(DATA_DIR.glob(pattern))
        if hits:
            return hits[0]
    raise FileNotFoundError(
        "Could not find any file matching: " + ", ".join(patterns) +
        f"\nExpected folder: {DATA_DIR}"
    )


def make_row(**kwargs):
    row = {c: "" for c in OUTPUT_COLUMNS}
    row.update(kwargs)
    row["latitude"] = as_float(row["latitude"])
    row["longitude"] = as_float(row["longitude"])
    row["capacity"] = as_float(row["capacity"])
    return row


# ============================================================
# 1) GLOBAL IRON & STEEL TRACKER
# ============================================================
def extract_steel(path: Path):
    plants = read_xlsx_sheet(path, "Plant data")
    caps = read_xlsx_sheet(path, "Plant capacities and status")

    all_caps = {}
    for r in caps:
        if not is_india(r, "Country/area"):
            continue
        status = lower(r.get("Status"))
        gid = norm(r.get("GEM plant ID"))
        if not gid:
            continue
        d = all_caps.setdefault(gid, {"statuses": [], "equipment": [], "capacity": []})
        d["statuses"].append(status)
        d["equipment"].append(r.get("Main production equipment"))
        cap = as_float(r.get("Nominal crude steel capacity (ttpa)"))
        if cap is not None:
            d["capacity"].append(cap)

    out = []
    for r in plants:
        if not is_india(r, "Country/area"):
            continue
        gid = norm(r.get("GEM plant ID"))
        lat, lon = split_coords(r.get("Coordinates"))
        d = all_caps.get(gid, {"statuses": [], "equipment": [], "capacity": []})
        out.append(make_row(
            gem_id=gid,
            facility_name=norm(r.get("Plant name (English)")),
            category="Metallurgical",
            exact_type="Steel Plant",
            subtype=join_unique(d["equipment"]),
            status=join_unique(d["statuses"]),
            latitude=lat,
            longitude=lon,
            location_accuracy=norm(r.get("Coordinate accuracy")),
            state=norm(r.get("Subnational unit")),
            owner=norm(r.get("Owner")),
            operator="",
            capacity=max(d["capacity"]) if d["capacity"] else None,
            capacity_unit="ttpa",
            gem_tracker="GIST",
            source_url=norm(r.get("GEM wiki page")),
        ))
    return out


# ============================================================
# 2) GLOBAL COAL MINE TRACKER
# ============================================================
def extract_coal_mines(path: Path):
    # Keep both current/non-closed and historical closed Indian mines.
    rows = []
    for sheet_name in ("Non-closed mines", "Closed mines"):
        try:
            sheet_rows = read_xlsx_sheet(path, sheet_name)
            rows.extend(sheet_rows)
        except KeyError:
            pass

    out = []
    for r in rows:
        # GEM uses the same country field in both mine sheets.
        country_col = "Country / Area" if "Country / Area" in r else "Country/Area"
        if not is_india(r, country_col):
            continue
        status = lower(r.get("Status")) or ("closed" if "Closure Year" in r or "Closing Year" in r else "")
        lat, lon = as_float(r.get("Latitude")), as_float(r.get("Longitude"))
        subtype = " | ".join(x for x in [norm(r.get("Mine Type")), norm(r.get("Mining Method"))] if x)
        out.append(make_row(
            gem_id=norm(r.get("GEM Mine ID")),
            facility_name=norm(r.get("Mine Name")),
            category="Mining_Extraction",
            exact_type="Coal Mine",
            subtype=subtype,
            status=status,
            latitude=lat,
            longitude=lon,
            location_accuracy=norm(r.get("Location Accuracy")),
            state=norm(r.get("State, Province")) or norm(r.get("State / Province")),
            owner=norm(r.get("Owners")),
            operator="",
            capacity=r.get("Capacity (Mtpa)"),
            capacity_unit="Mtpa",
            gem_tracker="GCMT",
            source_url=norm(r.get("GEM Wiki Page (ENG)")),
        ))
    return out


# ============================================================
# 3) GLOBAL IRON ORE MINES TRACKER
# ============================================================
def extract_iron_ore(path: Path):
    rows = read_xlsx_sheet(path, "Main Data")
    out = []
    for r in rows:
        if not is_india(r, "Country/Area"):
            continue
        status = lower(r.get("Operating status"))
        lat, lon = split_coords(r.get("Coordinates"))
        out.append(make_row(
            gem_id=norm(r.get("GEM Asset ID")),
            facility_name=norm(r.get("Asset name (English)")),
            category="Mining_Extraction",
            exact_type="Iron Ore Mine",
            subtype="Iron Ore",
            status=status,
            latitude=lat,
            longitude=lon,
            location_accuracy=norm(r.get("Coordinate accuracy")),
            state=norm(r.get("Subnational unit")),
            owner=norm(r.get("Owner")),
            operator="",
            capacity=r.get("Design capacity (ttpa)"),
            capacity_unit="ttpa",
            gem_tracker="GIOMT",
            source_url=norm(r.get("GEM wiki page URL")),
        ))
    return out


# ============================================================
# 4) GLOBAL OIL & GAS EXTRACTION TRACKER
# ============================================================
def extract_oil_gas(path: Path):
    rows = read_xlsx_sheet(path, "Field-level main data")
    out = []
    for r in rows:
        if not is_india(r, "Country/Area"):
            continue
        status = lower(r.get("Status"))
        lat, lon = as_float(r.get("Latitude")), as_float(r.get("Longitude"))
        fuel = lower(r.get("Fuel type"))
        exact = {
            "oil": "Oil Field",
            "gas": "Gas Field",
            "oil and gas": "Oil and Gas Field",
        }.get(fuel, "Oil/Gas Field")
        subtype = " | ".join(x for x in [norm(r.get("Production Type")), norm(r.get("Onshore/Offshore"))] if x)
        out.append(make_row(
            gem_id=norm(r.get("Unit ID")),
            facility_name=norm(r.get("Unit Name")),
            category="Oil_Gas",
            exact_type=exact,
            subtype=subtype,
            status=status,
            latitude=lat,
            longitude=lon,
            location_accuracy=norm(r.get("Location accuracy")),
            state=norm(r.get("Subnational unit")),
            owner=norm(r.get("Owner(s)")),
            operator=norm(r.get("Operator")),
            capacity=None,
            capacity_unit="",
            gem_tracker="GOGET",
            source_url=norm(r.get("Wiki URL (field)")),
        ))
    return out


# ============================================================
# 5) GGIT LNG TERMINALS GEOJSON
# ============================================================
def extract_lng(path: Path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    out = []
    for feature in data.get("features", []):
        r = feature.get("properties") or {}
        if lower(r.get("Country/Area")) != "india":
            continue
        status = lower(r.get("Status"))
        lat, lon = as_float(r.get("Latitude")), as_float(r.get("Longitude"))
        if (lat is None or lon is None):
            geom = feature.get("geometry") or {}
            coords = geom.get("coordinates")
            if geom.get("type") == "Point" and isinstance(coords, list) and len(coords) >= 2:
                lon, lat = as_float(coords[0]), as_float(coords[1])
        out.append(make_row(
            gem_id=norm(r.get("UnitID")) or norm(r.get("ProjectID")),
            facility_name=norm(r.get("TerminalName")),
            category="Oil_Gas",
            exact_type="LNG Terminal",
            subtype=norm(r.get("FacilityType")),
            status=status,
            latitude=lat,
            longitude=lon,
            location_accuracy=norm(r.get("Accuracy")),
            state=norm(r.get("State/Province")),
            owner=norm(r.get("Owner")),
            operator=norm(r.get("Operator")),
            capacity=r.get("Capacity"),
            capacity_unit=norm(r.get("CapacityUnits")),
            gem_tracker="GGIT",
            source_url=norm(r.get("Wiki")),
        ))
    return out


# ============================================================
# 6) GLOBAL CEMENT & CONCRETE TRACKER
# ============================================================
def extract_cement(path: Path):
    rows = read_xlsx_sheet(path, "Final data")
    out = []
    for r in rows:
        if not is_india(r, "Country/area"):
            continue
        status = lower(r.get("Operating status"))
        lat, lon = split_coords(r.get("Coordinates"))
        out.append(make_row(
            gem_id=norm(r.get("GEM plant ID")),
            facility_name=norm(r.get("Plant name (English)")),
            category="Other_Industrial",
            exact_type="Cement Plant",
            subtype=norm(r.get("Plant type")),
            status=status,
            latitude=lat,
            longitude=lon,
            location_accuracy=norm(r.get("Coordinate accuracy")),
            state=norm(r.get("Subnational unit")),
            owner=norm(r.get("Owner (English)")),
            operator="",
            capacity=r.get("Cement capacity (million metric tonnes per annum)"),
            capacity_unit="Mtpa",
            gem_tracker="GCCT",
            source_url=norm(r.get("GEM wiki page")),
        ))
    return out


# ============================================================
# 7) GLOBAL COAL PLANT TRACKER
# ============================================================
def extract_coal_power(path: Path):
    rows = read_xlsx_sheet(path, "Units")

    # Aggregate all Indian units to one row per physical plant/location.
    plants = {}
    for r in rows:
        if not is_india(r, "Country/Area"):
            continue
        status = lower(r.get("Status"))
        gid = norm(r.get("GEM location ID"))
        if not gid:
            continue
        lat, lon = as_float(r.get("Latitude")), as_float(r.get("Longitude"))

        p = plants.setdefault(gid, {
            "gem_id": gid,
            "facility_name": norm(r.get("Plant name")),
            "category": "Other_Industrial",
            "exact_type": "Coal Power Plant",
            "subtypes": [],
            "statuses": [],
            "latitude": lat,
            "longitude": lon,
            "location_accuracy": norm(r.get("Location accuracy")),
            "state": norm(r.get("Subnational unit (province, state)")),
            "owners": [],
            "capacity": 0.0,
            "has_capacity": False,
            "gem_tracker": "GCPT",
            "source_url": norm(r.get("Wiki URL")),
        })
        p["subtypes"].append(r.get("Combustion technology"))
        p["statuses"].append(status)
        p["owners"].append(r.get("Owner"))
        cap = as_float(r.get("Capacity (MW)"))
        if cap is not None:
            p["capacity"] += cap
            p["has_capacity"] = True

    out = []
    for p in plants.values():
        out.append(make_row(
            gem_id=p["gem_id"],
            facility_name=p["facility_name"],
            category=p["category"],
            exact_type=p["exact_type"],
            subtype=join_unique(p["subtypes"]),
            status=join_unique(p["statuses"]),
            latitude=p["latitude"],
            longitude=p["longitude"],
            location_accuracy=p["location_accuracy"],
            state=p["state"],
            owner=join_unique(p["owners"]),
            operator="",
            capacity=p["capacity"] if p["has_capacity"] else None,
            capacity_unit="MW",
            gem_tracker=p["gem_tracker"],
            source_url=p["source_url"],
        ))
    return out


# ============================================================
# MAIN
# ============================================================
def main():
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Folder not found: {DATA_DIR}\n"
            "Create a folder named 'gem_dataset' beside this script and put the GEM files inside it."
        )

    steel_file = find_one("*Iron*Steel*Tracker*.xlsx", "*Steel*Tracker*.xlsx")
    coal_mine_file = find_one("*Coal Mine Tracker*.xlsx", "*Coal*Mine*Tracker*.xlsx")
    iron_ore_file = find_one("*Iron-Ore-Mines-Tracker*.xlsx", "*Iron*Ore*Mines*Tracker*.xlsx")
    oil_gas_file = find_one("*Oil-and-Gas-Extraction-Tracker*.xlsx", "*Oil*Gas*Extraction*Tracker*.xlsx")
    lng_file = find_one("*LNG-Terminals*.geojson", "*LNG*Terminal*.geojson")
    cement_file = find_one("*Cement*Concrete*Tracker*.xlsx", "*Cement*Tracker*.xlsx")
    coal_power_file = find_one("*Coal-Plant-Tracker*.xlsx", "*Coal*Plant*Tracker*.xlsx")

    extractors = [
        ("GIST steel", extract_steel, steel_file),
        ("GCMT coal mines", extract_coal_mines, coal_mine_file),
        ("GIOMT iron ore", extract_iron_ore, iron_ore_file),
        ("GOGET oil/gas", extract_oil_gas, oil_gas_file),
        ("GGIT LNG", extract_lng, lng_file),
        ("GCCT cement", extract_cement, cement_file),
        ("GCPT coal power", extract_coal_power, coal_power_file),
    ]

    combined = []
    print("\nGEM India preprocessing")
    print("=" * 72)
    for label, func, path in extractors:
        rows = func(path)
        combined.extend(rows)
        print(f"{label:<22} {len(rows):>5} rows   <- {path.name}")

    # Remove exact duplicate tracker + GEM ID pairs.
    unique = {}
    fallback_n = 0
    for r in combined:
        gid = norm(r.get("gem_id"))
        if gid:
            key = (r["gem_tracker"], gid)
        else:
            # preserve rows lacking an ID without accidentally collapsing unrelated facilities
            fallback_n += 1
            key = (r["gem_tracker"], f"NOID::{fallback_n}")
        unique[key] = r
    combined = list(unique.values())

    # Stable order for easy inspection/upload.
    combined.sort(key=lambda r: (
        r["category"], r["exact_type"], r["state"], r["facility_name"]
    ))

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(combined)

    print("=" * 72)
    print(f"TOTAL: {len(combined)} rows")
    print(f"OUTPUT: {OUTPUT}")

    # Simple summary by category/exact type.
    counts = {}
    for r in combined:
        k = (r["category"], r["exact_type"])
        counts[k] = counts.get(k, 0) + 1
    print("\nBreakdown:")
    for (cat, typ), n in sorted(counts.items()):
        print(f"  {cat:<20} | {typ:<22} | {n:>5}")


if __name__ == "__main__":
    main()
