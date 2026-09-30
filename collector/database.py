import sqlite3
from pathlib import Path


DATABASE = Path("/root/metatrader/xauusd.db")


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS candles (
    time INTEGER PRIMARY KEY,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    tick_volume INTEGER,
    spread INTEGER,
    real_volume INTEGER
)
"""


def connect():
    return sqlite3.connect(DATABASE)


def initialize():
    conn = connect()
    try:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()


def get_candle(time: int):
    conn = connect()
    try:
        row = conn.execute(
            """
            SELECT
                time,
                open,
                high,
                low,
                close,
                tick_volume
            FROM candles
            WHERE time = ?
            """,
            (time,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    return {
        "time": row[0],
        "open": row[1],
        "high": row[2],
        "low": row[3],
        "close": row[4],
        "tick_volume": row[5],
    }


def upsert_candle(candle: dict):
    conn = connect()
    try:
        conn.execute(
            """
            INSERT INTO candles (
                time,
                open,
                high,
                low,
                close,
                tick_volume,
                spread,
                real_volume
            )
            VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)
            ON CONFLICT(time) DO UPDATE SET
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                tick_volume = excluded.tick_volume
            """,
            (
                candle["time"],
                candle["open"],
                candle["high"],
                candle["low"],
                candle["close"],
                candle["tick_volume"],
            ),
        )
        conn.commit()
    finally:
        conn.close()


