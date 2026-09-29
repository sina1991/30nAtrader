def calculate(closes, period):

    if len(closes) < period:
        return None

    return sum(closes[-period:]) / period
