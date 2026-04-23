import csv
import sqlite3
from pathlib import Path

CSV_DIR = Path(__file__).parent / "csvs"

PRIMARY_DB = "/tmp/space_logistics.db"
ALT_DB = "/tmp/space_logistics_alt.db"


SCHEMAS_PRIMARY = {
    "planets": """
        CREATE TABLE IF NOT EXISTS planets (
            planet_id INTEGER PRIMARY KEY,
            planet_name TEXT,
            planet_type TEXT,
            distance_from_sun_au REAL,
            orbital_period_days REAL,
            is_habitable TEXT,
            has_orbital_station TEXT,
            has_surface_hub TEXT
        )""",
    "moons": """
        CREATE TABLE IF NOT EXISTS moons (
            moon_id INTEGER PRIMARY KEY,
            moon_name TEXT,
            planet_id INTEGER,
            orbital_radius_km REAL,
            is_habitable TEXT,
            has_orbital_station TEXT,
            has_surface_hub TEXT
        )""",
    "asteroids": """
        CREATE TABLE IF NOT EXISTS asteroids (
            asteroid_id INTEGER PRIMARY KEY,
            asteroid_name TEXT,
            asteroid_belt TEXT,
            designation TEXT,
            diameter_km REAL,
            is_mining_colony TEXT,
            has_station TEXT
        )""",
    "spacecraft": """
        CREATE TABLE IF NOT EXISTS spacecraft (
            spacecraft_id INTEGER PRIMARY KEY,
            spacecraft_name TEXT,
            registration_number TEXT,
            spacecraft_type TEXT,
            manufacturer TEXT,
            capacity_tonnes REAL,
            max_speed_kmps REAL,
            fuel_type TEXT,
            home_station_id INTEGER,
            current_status TEXT,
            commissioned_date TEXT
        )""",
    "space_stations": """
        CREATE TABLE IF NOT EXISTS space_stations (
            station_id INTEGER PRIMARY KEY,
            station_name TEXT,
            station_type TEXT,
            planet_id INTEGER,
            moon_id INTEGER,
            asteroid_id INTEGER,
            orbital_altitude_km REAL,
            capacity_tonnes REAL,
            is_operational TEXT,
            commissioned_date TEXT
        )""",
    "pilots": """
        CREATE TABLE IF NOT EXISTS pilots (
            pilot_id INTEGER PRIMARY KEY,
            pilot_name TEXT,
            license_number TEXT,
            license_class TEXT,
            species TEXT,
            home_planet_id INTEGER,
            hire_date TEXT,
            rating REAL,
            total_missions INTEGER,
            is_active TEXT
        )""",
    "shipping_routes": """
        CREATE TABLE IF NOT EXISTS shipping_routes (
            route_id INTEGER PRIMARY KEY,
            route_name TEXT,
            origin_station_id INTEGER,
            origin_hub_id INTEGER,
            destination_station_id INTEGER,
            destination_hub_id INTEGER,
            distance_million_km REAL,
            avg_transit_days REAL,
            fuel_cost_credits REAL,
            risk_level TEXT,
            is_active TEXT
        )""",
}


SCHEMA_ALT_SPACECRAFT = """
    CREATE TABLE IF NOT EXISTS spacecraft (
        id INTEGER PRIMARY KEY,
        name TEXT,
        reg_no TEXT,
        craft_type TEXT,
        maker TEXT,
        capacity_kg REAL,
        top_speed_kps REAL,
        propulsion TEXT,
        base_station INTEGER,
        status TEXT,
        in_service_since TEXT
    )
"""


def _load_csv(conn: sqlite3.Connection, table: str, csv_name: str | None = None) -> int:
    path = CSV_DIR / f"{csv_name or table}.csv"
    if not path.exists():
        return 0
    with path.open() as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    if not rows:
        return 0
    cols = reader.fieldnames
    placeholders = ",".join("?" for _ in cols)
    colnames = ",".join(cols)
    conn.execute(f"DELETE FROM {table}")
    conn.executemany(
        f"INSERT INTO {table} ({colnames}) VALUES ({placeholders})",
        [tuple(r[c] for c in cols) for r in rows],
    )
    conn.commit()
    return len(rows)


def seed_primary(db_path: str = PRIMARY_DB) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    counts: dict[str, int] = {}
    try:
        for table, ddl in SCHEMAS_PRIMARY.items():
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            conn.execute(ddl)
            counts[table] = _load_csv(conn, table)
    finally:
        conn.close()
    return counts


def seed_alt_with_drift(db_path: str = ALT_DB) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DROP TABLE IF EXISTS spacecraft")
        conn.execute(SCHEMA_ALT_SPACECRAFT)
        src = CSV_DIR / "spacecraft.csv"
        rows_inserted = 0
        if src.exists():
            with src.open() as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)
            payload = [
                (
                    int(r["spacecraft_id"]),
                    r["spacecraft_name"],
                    r["registration_number"],
                    r["spacecraft_type"],
                    r["manufacturer"],
                    float(r["capacity_tonnes"]) * 1000.0,
                    float(r["max_speed_kmps"]),
                    r["fuel_type"],
                    int(r["home_station_id"]),
                    r["current_status"],
                    r["commissioned_date"],
                )
                for r in rows
            ]
            conn.executemany(
                "INSERT INTO spacecraft VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                payload,
            )
            rows_inserted = len(payload)
        conn.commit()
        return {"spacecraft": rows_inserted}
    finally:
        conn.close()
