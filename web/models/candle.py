from dataclasses import dataclass


@dataclass(frozen=True)
class Candle:
    time: int
    open: float
    high: float
    low: float
    close: float

    @property
    def range(self) -> float:
        return self.high - self.low

    @property
    def body(self) -> float:
        return abs(self.close - self.open)

    @property
    def upper_wick(self) -> float:
        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> float:
        return min(self.open, self.close) - self.low

    @property
    def body_ratio(self) -> float:
        if self.range == 0:
            return 0.0

        return self.body / self.range

    @property
    def wick_ratio(self) -> float:
        if self.range == 0:
            return 0.0

        return (
            self.upper_wick + self.lower_wick
        ) / self.range

    @property
    def close_position(self) -> float:
        if self.range == 0:
            return 0.0

        return (
            self.close - self.low
        ) / self.range

    @property
    def change_percent(self) -> float:
        if self.open == 0:
            return 0.0

        return (
            (self.close - self.open)
            / self.open
        ) * 100
