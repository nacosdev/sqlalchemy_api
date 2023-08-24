from datetime import datetime, date


def datetostr(date) -> str:
    return date.strftime("%Y-%m-%d")


def strtodate(str) -> date:
    return datetime.strptime(str, "%Y-%m-%d").date()


def datetimetostr(dt: datetime) -> str:
    return dt.isoformat()


def strtodatetime(str) -> datetime:
    return datetime.strptime(str, "%Y-%m-%dT%H:%M:%S.%f")
