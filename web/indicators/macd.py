def calculate(closes, fast_period=12, slow_period=26, signal_period=9):

    if len(closes) < slow_period + signal_period:
        return None

    def ema(values, period):
        multiplier = 2 / (period + 1)

        result = sum(values[:period]) / period

        for value in values[period:]:
            result = ((value - result) * multiplier) + result

        return result

    macd_values = []

    for i in range(slow_period, len(closes) + 1):
        window = closes[:i]

        fast_ema = ema(
            window,
            fast_period,
        )

        slow_ema = ema(
            window,
            slow_period,
        )

        macd_values.append(
            fast_ema - slow_ema
        )

    if len(macd_values) < signal_period:
        return None

    signal = ema(
        macd_values,
        signal_period,
    )

    return {
        "macd": macd_values[-1],
        "signal": signal,
        "histogram": macd_values[-1] - signal,
    }
