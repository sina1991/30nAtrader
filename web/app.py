import sqlite3
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from web.models.loader import candles_from_rows

from web.components.signal.engine import build_signals
from web.indicators.engine import calculate
from web.components.sessions.engine import build_sessions
from web.components.calendar.engine import build_calendar


# =========================
# CONFIG
# =========================

BASE_DIR = Path("/root/metatrader")

DATABASE = BASE_DIR / "xauusd.db"

SYMBOL = "XAUUSD"
TIMEFRAME = "M1"
def get_public_ip():
    try:
        import requests
        return requests.get(
            "https://api.ipify.org",
            timeout=3,
        ).text.strip()
    except Exception:
        return "N/A"



# =========================
# APP
# =========================

app = FastAPI(
    title="XAUUSD Dashboard"
)


app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "web/static"
    ),
    name="static",
)


templates = Jinja2Templates(
    directory=BASE_DIR / "web/templates"
)


# =========================
# DATABASE
# =========================

def get_candles():

    conn = sqlite3.connect(DATABASE)

    try:

        rows = conn.execute(
            """
            SELECT
                time,
                open,
                high,
                low,
                close,
                tick_volume,
                spread,
                real_volume
            FROM candles
            ORDER BY time ASC
            """
        ).fetchall()

    finally:

        conn.close()

    return rows


# =========================
# MA
# =========================

def calculate_ma(closes, periods):

    if len(closes) < periods:
        return None

    return sum(
        closes[-periods:]
    ) / periods


def get_status(close, ma):

    if ma is None:

        return {
            "color": "gray",
            "light": "⚪",
            "status": "N/A",
        }


    difference = close - ma


    if difference > 0:

        return {
            "color": "green",
            "light": "🟢",
            "status": "ABOVE MA",
        }


    if difference == 0:

        return {
            "color": "yellow",
            "light": "🟡",
            "status": "AT MA",
        }


    return {
        "color": "red",
        "light": "🔴",
        "status": "BELOW MA",
    }


# =========================
# TIME
# =========================

def format_candle_time(timestamp):

    return datetime.fromtimestamp(
        timestamp
    ).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# =========================
# DASHBOARD
# =========================

@app.get(
    "/",
    response_class=HTMLResponse
)
def dashboard(request: Request):

    # -------------------------
    # Get raw database rows
    # -------------------------

    rows = get_candles()


    if not rows:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "No candle data found."
            },
        )


    # -------------------------
    # Candle Model
    # -------------------------

    candles = candles_from_rows(
        rows
    )


    # -------------------------
    # Latest candle
    # -------------------------

    latest = rows[-1]

    latest_candle = candles[-1]


    (
        timestamp,
        open_price,
        high_price,
        low_price,
        close_price,
        tick_volume,
        spread,
        real_volume,
    ) = latest


    # -------------------------
    # Candle derived fields
    # -------------------------

    candle_range = latest_candle.range

    candle_body = latest_candle.body

    upper_wick = latest_candle.upper_wick

    lower_wick = latest_candle.lower_wick

    body_ratio = latest_candle.body_ratio

    wick_ratio = latest_candle.wick_ratio

    close_position = latest_candle.close_position

    change_percent = latest_candle.change_percent


    # -------------------------
    # Close prices

    closes = [
        candle.close
        for candle in candles
    ]


    # -------------------------
    # MA
    # -------------------------

    ma60 = calculate(
        "MA",
        closes,
        {"period": 60},
    )

    ma100 = calculate(
        "MA",
        closes,
        {"period": 100},
    )

    ma300 = calculate(
        "MA",
        closes,
        {"period": 300},
    )

    macd = calculate(
        "MACD",
        closes,
        {},
    )

    rsi = calculate(
        "RSI",
        closes,
        {"period": 14},
    )


    # -------------------------
    # Signal Engine
    # -------------------------

    # -------------------------

    signals = build_signals(
        closes
    )


    # -------------------------
    # Trading Sessions
    # -------------------------

    sessions = build_sessions()

    calendar = build_calendar()


    # -------------------------
    # Chart Data
    # -------------------------

    chart_data = [

        {
            "time": candle.time,

            "open": candle.open,

            "high": candle.high,

            "low": candle.low,

            "close": candle.close,
        }

        for candle in candles
    ]


    # -------------------------
    # Template
    # -------------------------

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={

            # Market
            "symbol": SYMBOL,

            "timeframe": TIMEFRAME,
            "ma60": ma60,
            "ma100": ma100,
            "ma300": ma300,
            "macd": macd,
            "rsi": rsi,



            # Network
            "server_ip": get_public_ip(),
            "user_ip": request.client.host,



            # Trading Sessions
            "sessions": sessions,

            # Economic Calendar
            "calendar": calendar,


            # Latest raw candle
            "latest": latest,

            "timestamp": timestamp,

            "candle_time":
                format_candle_time(
                    timestamp
                ),


            # Latest Candle Model
            "candle":
                latest_candle,


            # OHLC
            "open_price":
                latest_candle.open,

            "high_price":
                latest_candle.high,

            "low_price":
                latest_candle.low,

            "close_price":
                latest_candle.close,


            # Candle Analysis
            "candle_range":
                candle_range,

            "candle_body":
                candle_body,

            "upper_wick":
                upper_wick,

            "lower_wick":
                lower_wick,

            "body_ratio":
                body_ratio,

            "wick_ratio":
                wick_ratio,

            "close_position":
                close_position,

            "change_percent":
                change_percent,


            # Volume / Spread
            "tick_volume":
                tick_volume,

            "spread":
                spread,

            "real_volume":
                real_volume,


            # Database
            "candle_count":
                len(candles),


            # Signals
            "signals":
                signals,


            # Chart
            "chart_data":
                chart_data,
        },
    )
