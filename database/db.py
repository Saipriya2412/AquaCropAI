
import sqlite3

def get_db_connection():
    connection = sqlite3.connect("aquacrop.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_name TEXT NOT NULL,
            phone TEXT,
            location TEXT NOT NULL,
            farm_area REAL NOT NULL,
            crop TEXT NOT NULL,
            soil_type TEXT NOT NULL,
            crop_stage TEXT NOT NULL,
            irrigation_source TEXT NOT NULL,
            irrigation_method TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS groundwater_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            water_level REAL NOT NULL,
            recorded_on TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (farmer_id) REFERENCES farmers(id)
        )
    """)

    connection.commit()
    connection.close()
