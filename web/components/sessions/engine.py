from datetime import datetime
from zoneinfo import ZoneInfo


DISPLAY_TIMEZONE = "Asia/Tehran"


SESSIONS = [
    {
        "name": "Sydney",
        "timezone": "Australia/Sydney",
        "start_hour": 8,
        "start_minute": 0,
        "end_hour": 17,
        "end_minute": 0,
    },
    {
        "name": "Tokyo",
        "timezone": "Asia/Tokyo",
        "start_hour": 9,
        "start_minute": 0,
        "end_hour": 18,
        "end_minute": 0,
    },
    {
        "name": "London",
        "timezone": "Europe/London",
        "start_hour": 8,
        "start_minute": 0,
        "end_hour": 17,
        "end_minute": 0,
    },
    {
        "name": "New York",
        "timezone": "America/New_York",
        "start_hour": 8,
        "start_minute": 0,
        "end_hour": 17,
        "end_minute": 0,
    },
]


def _minutes_since_midnight(value):
    return value.hour * 60 + value.minute


def _format_minutes(total_minutes):
    total_minutes %= 1440

    hour = total_minutes // 60
    minute = total_minutes % 60

    return f"{hour:02d}:{minute:02d}"


def _session_window(session, now_utc):
    timezone = ZoneInfo(session["timezone"])

    local_now = now_utc.astimezone(timezone)

    start = local_now.replace(
        hour=session["start_hour"],
        minute=session["start_minute"],
        second=0,
        microsecond=0,
    )

    end = local_now.replace(
        hour=session["end_hour"],
        minute=session["end_minute"],
        second=0,
        microsecond=0,
    )

    if end <= start:
        if local_now < end:
            start = start.replace(day=start.day - 1)

        else:
            end = end.replace(day=end.day + 1)

    return local_now, start, end


def _build_session(session, now_utc):
    local_now, start, end = _session_window(
        session,
        now_utc,
    )

    is_open = start <= local_now < end

    local_start_minutes = (
        session["start_hour"] * 60
        + session["start_minute"]
    )

    local_end_minutes = (
        session["end_hour"] * 60
        + session["end_minute"]
    )

    display_start = start.astimezone(
        ZoneInfo(DISPLAY_TIMEZONE)
    )

    display_end = end.astimezone(
        ZoneInfo(DISPLAY_TIMEZONE)
    )

    display_start_minutes = _minutes_since_midnight(
        display_start
    )

    display_end_minutes = _minutes_since_midnight(
        display_end
    )

    if display_end_minutes <= display_start_minutes:
        display_end_minutes += 1440

    duration = display_end_minutes - display_start_minutes

    current_display = now_utc.astimezone(
        ZoneInfo(DISPLAY_TIMEZONE)
    )

    current_minutes = _minutes_since_midnight(
        current_display
    )

    timeline_start = display_start_minutes
    timeline_end = display_end_minutes

    if timeline_end > 1440:
        current_for_session = current_minutes

        if current_for_session < timeline_start:
            current_for_session += 1440

    else:
        current_for_session = current_minutes

    progress = (
        (current_for_session - timeline_start)
        / duration
        * 100
    )

    progress = max(
        0,
        min(100, progress),
    )

    return {
        "name": session["name"],
        "timezone": session["timezone"],
        "status": "OPEN" if is_open else "CLOSED",
        "is_open": is_open,
        "start": f"{display_start:%H:%M}",
        "end": f"{display_end:%H:%M}",
        "label": (
            f"{display_start:%H:%M} — "
            f"{display_end:%H:%M}"
        ),
        "timeline_start": display_start_minutes % 1440,
        "timeline_end": display_end_minutes % 1440,
        "timeline_end_extended": display_end_minutes,
        "duration": duration,
        "progress": round(progress, 2),
        "local_time": f"{local_now:%H:%M:%S}",
    }


def build_sessions(now_utc=None):
    if now_utc is None:
        now_utc = datetime.now(ZoneInfo("UTC"))

    sessions = [
        _build_session(
            session,
            now_utc,
        )
        for session in SESSIONS
    ]

    display_now = now_utc.astimezone(
        ZoneInfo(DISPLAY_TIMEZONE)
    )

    current_minutes = (
        display_now.hour * 60
        + display_now.minute
        + display_now.second / 60
    )

    return {
        "timezone": DISPLAY_TIMEZONE,
        "timezone_label": "Tehran Time",
        "live_time": f"{display_now:%H:%M:%S}",
        "current_minutes": current_minutes,
        "sessions": sessions,
    }
