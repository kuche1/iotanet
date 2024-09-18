
# TODO we could add `file_read_port`, `file_read_ip` and so on

from typing import Callable

SYMETRIC_KEY_SIZE_BYTES = 32 # 32 bytes, for AES-256
SYMETRIC_BLOCKSIZE_BYTES = 16
SYMETRIC_KEY_IV_SIZE_BYTES = SYMETRIC_BLOCKSIZE_BYTES

Ip = str
Port = int
Addr = tuple[Ip,Port]

Symetric_key = tuple[bytes, bytes]

######
###### generic: file IO
######

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

######
###### generic: control flow
######

# TODO this doesn't actually protect from shit
# there should be an except that turns the error into a string and prints it
def try_finally(fnc:Callable[[],None], cleanup:Callable[[],None]) -> None:
    # TODO we could add some fancy formating, along with timestamp in case of errors
    try:
        fnc()
    finally:
        cleanup()

######
###### key: string operation
######

def symetric_key_to_bytes(key:Symetric_key) -> bytes:
    k, i = key
    return k + i

def chop_symetric_key(data:bytes) -> tuple[Symetric_key, bytes]:

    sym_key = data[:SYMETRIC_KEY_SIZE_BYTES]
    data = data[SYMETRIC_KEY_SIZE_BYTES:]
    assert len(sym_key) == SYMETRIC_KEY_SIZE_BYTES

    sym_iv = data[:SYMETRIC_KEY_IV_SIZE_BYTES]
    data = data[SYMETRIC_KEY_IV_SIZE_BYTES:]
    assert len(sym_iv) == SYMETRIC_KEY_IV_SIZE_BYTES

    return (sym_key, sym_iv), data

######
###### key: file IO
######

def file_read_symetric_key(file:str) -> Symetric_key:

    data = file_read_bytes(file)

    ident_key = data[:SYMETRIC_KEY_SIZE_BYTES]
    data = data[SYMETRIC_KEY_SIZE_BYTES:]
    assert len(ident_key) == SYMETRIC_KEY_SIZE_BYTES

    ident_iv = data[:SYMETRIC_KEY_IV_SIZE_BYTES]
    data = data[SYMETRIC_KEY_IV_SIZE_BYTES:]
    assert len(ident_iv) == SYMETRIC_KEY_IV_SIZE_BYTES

    assert len(data) == 0

    return ident_key, ident_iv

def file_write_symetric_key(file:str, key:Symetric_key) -> None:
    with open(file, 'wb') as f:
        f.write(symetric_key_to_bytes(key))

######
###### addr: serialisation
######

def addr_to_bytes(addr:Addr) -> bytes:
    sep = b';'
    ip, port = addr
    return ip.encode() + sep + str(port).encode() + sep

def chop_addr(data:bytes) -> tuple[Addr, bytes]:
    sep = b';'

    idx = data.index(sep)
    ip_bytes = data[:idx]
    data = data[idx + len(sep):]

    ip = ip_bytes.decode()

    idx = data.index(sep)
    port_bytes = data[:idx]
    data = data[idx + len(sep):]

    port = int(port_bytes.decode())

    return (ip, port), data

def file_write_addr(file:str, addr:Addr) -> None:
    with open(file, 'wb') as f:
        f.write(addr_to_bytes(addr))

def file_read_addr(file:str) -> Addr:

    with open(file, 'rb') as f:
        data = f.read()

    addr, data = chop_addr(data)
    assert len(data) == 0

    return addr
