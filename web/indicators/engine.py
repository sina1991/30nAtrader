from web.indicators.ma import calculate as calculate_ma
from web.indicators.rsi import calculate as calculate_rsi
from web.indicators.macd import calculate as calculate_macd


INDICATORS = {
    "MA": calculate_ma,
    "RSI": calculate_rsi,
    "MACD": calculate_macd,
}


def calculate(indicator, closes, params):
    if indicator not in INDICATORS:
        return None

    function = INDICATORS[indicator]

    return function(
        closes,
        **params,
    )
