from web.config.signals import SIGNALS
from web.indicators.engine import calculate


def build_signals(closes):

    results = []

    for slot in range(1, 10):

        config = SIGNALS.get(
            slot,
            {
                "indicator": None,
                "params": {},
            },
        )

        indicator = config["indicator"]
        params = config["params"]

        # Empty signal
        if indicator is None:

            results.append({
                "slot": slot,
                "indicator": None,
                "params": {},
                "value": None,
                "status": "EMPTY",
                "color": "gray",
            })

            continue

        # Calculate indicator
        value = calculate(
            indicator,
            closes,
            params,
        )

        results.append({
            "slot": slot,
            "indicator": indicator,
            "params": params,
            "value": value,
            "status": "READY" if value is not None else "N/A",
            "color": "gray",
        })

    return results
