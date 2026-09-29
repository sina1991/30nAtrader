import json
from datetime import datetime
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


CALENDAR_URL = (
    "https://nfs.faireconomy.media/"
    "ff_calendar_thisweek.json"
)

DISPLAY_TIMEZONE = "Asia/Tehran"

CACHE_SECONDS = 300

_cache = {
    "timestamp": 0,
    "events": [],
}


def _fetch_events():
    request = Request(
        CALENDAR_URL,
        headers={
            "User-Agent": "Mozilla/5.0 XAUUSD-Dashboard"
        },
    )

    with urlopen(request, timeout=15) as response:
        return json.load(response)


def _format_event(event):
    event_time = datetime.fromisoformat(
        event["date"]
    )

    tehran_time = event_time.astimezone(
        ZoneInfo(DISPLAY_TIMEZONE)
    )

    return {
        "date": tehran_time.strftime("%Y-%m-%d"),
        "time": tehran_time.strftime("%H:%M"),
        "datetime": tehran_time,
        "currency": event.get("country", ""),
        "impact": event.get("impact", ""),
        "title": event.get("title", ""),
        "forecast": event.get("forecast", ""),
        "previous": event.get("previous", ""),
    }


def build_calendar():
    now = datetime.now(ZoneInfo(DISPLAY_TIMEZONE))
    now_timestamp = now.timestamp()

    if (
        _cache["events"]
        and now_timestamp - _cache["timestamp"]
        < CACHE_SECONDS
    ):
        events = _cache["events"]
    else:
        try:
            raw_events = _fetch_events()
        except Exception:
            raw_events = []

        events = [
            _format_event(event)
            for event in raw_events
            if event.get("country") == "USD"
            and event.get("impact") in {"High", "Medium"}
        ]

        events.sort(
            key=lambda event: event["datetime"]
        )

        _cache["events"] = events
        _cache["timestamp"] = now_timestamp

    return {
        "timezone": DISPLAY_TIMEZONE,
        "timezone_label": "Tehran Time",
        "events": events,
        "count": len(events),
    }
