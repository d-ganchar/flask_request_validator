from datetime import datetime


def datetime_from_iso_format(value: str) -> datetime:
    if len(value) == 10:
        return datetime.strptime(value, '%Y-%m-%d')
    if len(value) == 19:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    if len(value) == 26:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
    if len(value) == 32 and ':' == value[-3]:
        value = value[:-3] + value[-2:]
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
