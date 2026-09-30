import time

from collector.biquote import BiquoteClient, bar_to_candle
from collector.database import get_candle, initialize, upsert_candle


SYMBOL = "XAUUSD"
INTERVAL = "1m"
INITIAL_FETCH_LIMIT = 301
RECOVERY_FETCH_LIMIT = 301
POLL_FETCH_LIMIT = 1
POLL_INTERVAL = 5


def initial_collect(client: BiquoteClient):
    bars = client.get_ohlc(
        symbol=SYMBOL,
        interval=INTERVAL,
        limit=INITIAL_FETCH_LIMIT,
    )

    for bar in bars:
        candle = bar_to_candle(bar)
        upsert_candle(candle)


    return len(bars)


def recovery_collect(client: BiquoteClient):
    bars = client.get_ohlc(
        symbol=SYMBOL,
        interval=INTERVAL,
        limit=RECOVERY_FETCH_LIMIT,
    )

    if not bars:
        return 0

    for bar in bars:
        candle = bar_to_candle(bar)
        upsert_candle(candle)


    return len(bars)


def candles_match(api_candle: dict, db_candle: dict) -> bool:
    if db_candle is None:
        return False

    fields = (
        "time",
        "open",
        "high",
        "low",
        "close",
        "tick_volume",
    )

    return all(
        api_candle[field] == db_candle[field]
        for field in fields
    )


def update_latest(client: BiquoteClient):
    bars = client.get_ohlc(
        symbol=SYMBOL,
        interval=INTERVAL,
        limit=POLL_FETCH_LIMIT,
    )

    if not bars:
        return None, False

    latest_candle = bar_to_candle(bars[0])

    if len(bars) < 2:
        upsert_candle(latest_candle)
        return latest_candle, False

    previous_closed_candle = bar_to_candle(bars[1])
    db_previous_candle = get_candle(previous_closed_candle["time"])

    if not candles_match(
        previous_closed_candle,
        db_previous_candle,
    ):
        count = recovery_collect(client)

        if count == 0:
            raise RuntimeError("Recovery failed: no candles received")

        latest_candle = bar_to_candle(
            client.get_ohlc(
                symbol=SYMBOL,
                interval=INTERVAL,
                limit=POLL_FETCH_LIMIT,
            )[0]
        )

        upsert_candle(latest_candle)

        return latest_candle, True

    upsert_candle(latest_candle)

    return latest_candle, False


def main():
    initialize()

    client = BiquoteClient()

    print(f"Collector started: {SYMBOL} {INTERVAL}")

    try:
        count = initial_collect(client)
        print(f"Initial collection: {count} candles")

        while True:
            try:
                candle, recovered = update_latest(client)

                if candle is not None:
                    if recovered:
                        print(
                            f"Recovery completed: {RECOVERY_FETCH_LIMIT} candles"
                        )

                    print(
                        f"Latest candle: {candle['time']} "
                        f"close={candle['close']}"
                    )
                else:
                    print("No latest candle received")

            except Exception as exc:
                print(f"Collector error: {exc}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("Collector stopped")


if __name__ == "__main__":
    main()
