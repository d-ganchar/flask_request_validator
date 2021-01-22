from datetime import datetime


def dt_from_iso(value: str) -> datetime:
    if len(value) == 10:
        return datetime.strptime(value, '%Y-%m-%d')
    if len(value) == 13:
        return datetime.strptime(value, '%Y-%m-%dT%H')
    if len(value) == 16:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M')
    if len(value) == 19:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    if len(value) == 26:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
    if len(value) == 32 and ':' == value[-3]:
        value = value[:-3] + value[-2:]
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
