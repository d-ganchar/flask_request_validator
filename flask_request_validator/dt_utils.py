from datetime import datetime


def dt_from_iso(value: str) -> datetime:
    """
        for python versions < 3.7 get datetime from isoformat
        Source: https://github.com/fitoprincipe/ipygee/blob/master/ipygee/tasks.py#L80
    """
    try:
        return datetime.fromisoformat(value)
    except AttributeError:
        d, t = value.split('T')
        year, month, day = d.split('-')
        hours, minutes, seconds = t.split(':')
        seconds = float(seconds[0:-1])
        sec = int(seconds)
        microseconds = int((seconds - sec) * 1e6)

        return datetime(
            int(year), int(month), int(day), int(hours), int(minutes), int(seconds), microseconds
        )

