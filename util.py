
from typing import Callable

# TODO we could add `file_read_port`, `file_read_ip` and so on

def file_read_bytes(file:str) -> bytes:
    with open(file, 'rb') as f:
        return f.read()

def file_read_str(file:str) -> str:
    with open(file, 'r') as f:
        return f.read()

def file_read_int(file:str) -> int:
    return int(file_read_str(file))

def file_read_int_positive_or_0(file:str) -> int:
    num = file_read_int(file)
    assert num >= 0
    return num

def file_read_int_positive(file:str) -> int:
    num = file_read_int(file)
    assert num > 0
    return num

def try_finally(fnc:Callable[[],None], cleanup:Callable[[],None]) -> None:
    # TODO we could add some fancy formating, along with timestamp in case of errors
    try:
        fnc()
    finally:
        cleanup()
