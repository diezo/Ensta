import time


def time_id() -> str:
    return str(int(time.time() * 1000))


def fb_uploader(id: str | None) -> str:
    id = id if id else time_id()
    return f'fb_uploader_{id}'
