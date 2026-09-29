def calculate(closes, period=14):

    if len(closes) <= period:
        return None

    gains = []
    losses = []

    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]

        if change > 0:
            gains.append(change)
            losses.append(0)

        else:
            gains.append(0)
            losses.append(abs(change))

    recent_gains = gains[-period:]
    recent_losses = losses[-period:]

    average_gain = sum(recent_gains) / period
    average_loss = sum(recent_losses) / period

    if average_loss == 0:
        return 100

    rs = average_gain / average_loss

    return 100 - (100 / (1 + rs))
