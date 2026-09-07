import hashlib
import os
import re
from datetime import datetime, timezone

DEVICE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
RATE_LIMITS = {
    "parse": int(os.getenv("PARSE_DAILY_LIMIT", "5")),
    "analyze_jd": int(os.getenv("JD_DAILY_LIMIT", "5")),
    "tailor": int(os.getenv("TAILOR_DAILY_LIMIT", "3")),
}


def validate_device_id(device_id: str) -> str:
    if not DEVICE_ID_RE.fullmatch(device_id or ""):
        raise ValueError("x-device-id must contain 1-128 letters, numbers, '_' or '-'")
    return device_id


def check_limit(ip: str, device_id: str, action: str) -> bool:
    if os.getenv("APP_ENV", "development") != "production":
        return True
    if action not in RATE_LIMITS:
        raise ValueError("unknown rate-limit action")
    validate_device_id(device_id)
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required in production")
    try:
        import psycopg
    except ImportError as e:
        raise RuntimeError("psycopg is required in production") from e

    key_hash = hashlib.sha256(f"{ip}|{device_id}".encode()).hexdigest()
    day = datetime.now(timezone.utc).date()
    try:
        with psycopg.connect(database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO rate_limit_counters
                        (key_hash, action, window_date, count)
                    VALUES (%s, %s, %s, 1)
                    ON CONFLICT (key_hash, action, window_date)
                    DO UPDATE SET count = rate_limit_counters.count + 1
                    WHERE rate_limit_counters.count < %s
                    RETURNING count
                    """,
                    (key_hash, action, day, RATE_LIMITS[action]),
                )
                return cursor.fetchone() is not None
    except psycopg.Error as e:
        raise RuntimeError("rate limiter database is unavailable") from e


def check_tailor_limit(ip: str, device_id: str, action: str = "tailor") -> bool:
    return check_limit(ip, device_id, action)
