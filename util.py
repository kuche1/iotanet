
from typing import Callable, cast
import os
import cryptography
import cryptography.hazmat.primitives.asymmetric.rsa as cryptography_rsa
import cryptography.hazmat.primitives.serialization as cryptography_serialization
import random

HERE = os.path.dirname(os.path.realpath(__file__))

SYMETRIC_KEY_SIZE_BYTES = 32 # 32 bytes, for AES-256
SYMETRIC_BLOCKSIZE_BYTES = 16
SYMETRIC_KEY_IV_SIZE_BYTES = SYMETRIC_BLOCKSIZE_BYTES

Ip = str
Port = int
Addr = tuple[Ip,Port]

Private_key = cryptography_rsa.RSAPrivateKey
Public_key = cryptography_rsa.RSAPublicKey
Symetric_key = tuple[bytes, bytes]

Node = tuple[Addr,Public_key]

######
###### int: serialisation
######

def file_read_int(file:str) -> int:
    return int(file_read_str(file))

def file_write_int(file:str, num:int) -> None:
    with open(file, 'w') as f:
        f.write(str(num))

def int_to_bytes(num:int) -> bytes:
    sep = b';'
    return str(num).encode() + sep

######
###### generic: serialisation
######

def file_read_bytes(file:str) -> bytes:
    with open(file, 'rb') as f:
        return f.read()

def file_read_str(file:str) -> str:
    with open(file, 'r') as f:
        return f.read()

def chop_int(data:bytes) -> tuple[int, bytes]:
    sep = b';'
    idx = data.index(sep)
    num_bytes = data[:idx]
    data = data[idx + len(sep):]
    num = int(num_bytes)
    return num, data

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
###### key: serialisation
######

def bytes_to_public_key(data:bytes) -> Public_key:
    key = cryptography_serialization.load_pem_public_key(
        data,
    )
    return cast(Public_key, key)

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

def public_key_to_bytes(key:Public_key) -> bytes:
    return key.public_bytes(
        encoding=cryptography_serialization.Encoding.PEM,
        format=cryptography_serialization.PublicFormat.SubjectPublicKeyInfo,
    )

def file_read_public_key(file:str) -> Public_key:
    key_bytes = file_read_bytes(file)
    return bytes_to_public_key(key_bytes)

def file_write_public_key(file:str, pub:Public_key) -> None:
    key_bytes = public_key_to_bytes(pub)
    with open(file, 'wb') as f:
        f.write(key_bytes)

######
###### port: serialisation
######

def file_write_port(file:str, port:Port) -> None:
    return file_write_int(file, port)

def file_read_port(file:str) -> Port:
    port = file_read_int(file)
    assert port > 0
    return port

######
###### addr: serialisation
######

def addr_to_bytes(addr:Addr) -> bytes:
    sep = b';'
    ip, port = addr
    return ip.encode() + sep + str(port).encode() + sep

def addr_to_str(addr:Addr) -> str:
    return addr_to_bytes(addr).decode()

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
    assert port > 0

    return (ip, port), data

def chop_addr_from_str(data:str) -> tuple[Addr, str]:
    addr, data_bytes = chop_addr(data.encode())
    return addr, data_bytes.decode()

def file_write_addr(file:str, addr:Addr) -> None:
    with open(file, 'wb') as f:
        f.write(addr_to_bytes(addr))

def file_read_addr(file:str) -> Addr:

    with open(file, 'rb') as f:
        data = f.read()

    addr, data = chop_addr(data)
    assert len(data) == 0

    return addr

def list_of_nodes_to_bytes_of_node_addrs(nodes:list[Node]) -> bytes:
    data = b''
    data += int_to_bytes(len(nodes))
    for addr, _pub in nodes:
        data += addr_to_bytes(addr)
    return data

def chop_list_of_addrs(data:bytes) -> tuple[list[Addr], bytes]:
    addrs:list[Addr] = []
    size, data = chop_int(data)
    for _ in range(size):
        addr, data = chop_addr(data)
        addrs.append(addr)
    return addrs, data
