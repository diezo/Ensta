import time


def time_id() -> str:
    return str(int(time.time() * 1000))


def fb_uploader(time_identifier: str = None) -> str:
    time_identifier = time_identifier if time_identifier else time_id()
    return f'fb_uploader_{time_identifier}'
