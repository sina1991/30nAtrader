from datetime import datetime, timedelta, timezone

import requests


BASE_URL = "https://biquote.io/api"


class BiquoteClient:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def get_ohlc(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 100,
        to: str | None = None,
    ):
        url = f"{BASE_URL}/{symbol}/ohlc"

        params = {
            "interval": interval,
            "limit": limit,
        }

        if to is not None:
            params["to"] = to

        response = requests.get(
            url,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Invalid API response: expected object")

        bars = data.get("bars")

        if not isinstance(bars, list):
            raise ValueError("Invalid API response: missing bars")

        return bars

    def get_latest_candles(
        self,
        symbol: str,
        count: int = 3000,
        interval: str = "1m",
    ) -> list[dict]:
        if count <= 0:
            return []

        collected = {}
        to = None

        while len(collected) < count:
            bars = self.get_ohlc(
                symbol=symbol,
                interval=interval,
                limit=301,
                to=to,
            )

            if not bars:
                break

            previous_count = len(collected)

            for bar in bars:
                collected[bar["openTime"]] = bar

                if len(collected) >= count:
                    break

            if len(collected) == previous_count:
                break

            oldest_time = min(collected)

            oldest_dt = datetime.fromisoformat(
                oldest_time.replace("Z", "+00:00")
            )

            to = (
                oldest_dt - timedelta(minutes=1)
            ).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

        bars = sorted(
            collected.values(),
            key=lambda bar: bar["openTime"],
        )

        return bars[-count:]


def bar_to_candle(bar: dict) -> dict:
    required_fields = (
        "openTime",
        "open",
        "high",
        "low",
        "close",
        "tickVolume",
    )

    for field in required_fields:
        if field not in bar:
            raise ValueError(f"Invalid bar: missing {field}")

    timestamp = int(
        datetime.fromisoformat(
            bar["openTime"].replace("Z", "+00:00")
        ).timestamp()
    )

    return {
        "time": timestamp,
        "open": float(bar["open"]),
        "high": float(bar["high"]),
        "low": float(bar["low"]),
        "close": float(bar["close"]),
        "tick_volume": int(bar["tickVolume"]),
    }
