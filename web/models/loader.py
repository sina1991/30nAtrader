from typing import Iterable, Sequence

from web.models.candle import Candle


def candle_from_row(row: Sequence) -> Candle:
    return Candle(
        time=int(row[0]),
        open=float(row[1]),
        high=float(row[2]),
        low=float(row[3]),
        close=float(row[4]),
    )


def candles_from_rows(rows: Iterable[Sequence]) -> list[Candle]:
    return [
        candle_from_row(row)
        for row in rows
    ]
