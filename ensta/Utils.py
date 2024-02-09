import time


def time_id() -> str:
    return str(int(time.time() * 1000))
