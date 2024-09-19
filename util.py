
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
###### generic: serialisation
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

# TODO delete
def file_read_int_positive(file:str) -> int:
    num = file_read_int(file)
    assert num > 0
    return num

def int_to_bytes(num:int) -> bytes:
    sep = b';'
    return str(num).encode() + sep

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

def file_read_public_key(file:str) -> Public_key:
    key_bytes = file_read_bytes(file)
    return bytes_to_public_key(key_bytes)

######
###### addr: serialisation
######

def addr_to_bytes(addr:Addr) -> bytes:
    sep = b';'
    ip, port = addr
    return ip.encode() + sep + str(port).encode() + sep

# TODO rename tp `chop_addr_from_bytes`
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

######
###### peer operations + serialisation
######

# TODO allow for peers other than the default ones
FOLDER_PEERS_DEFAULT = f'{HERE}/_peers_default'

FILENAME_PEER_PUBLIC_KEY = 'public_key'

def folder_read_peer(path:str) -> Node:

    peer_addr_str = os.path.basename(path)

    peer_addr, nothing = chop_addr_from_str(peer_addr_str)
    assert len(nothing) == 0

    peer_pub = file_read_public_key(f'{path}/{FILENAME_PEER_PUBLIC_KEY}')

    return (peer_addr, peer_pub)

def get_peer_folders() -> list[str]:
    files:list[str] = []
    for path, folders, _files in os.walk(FOLDER_PEERS_DEFAULT):
        files = [f'{path}/{folder}' for folder in folders]
        break
    return files

def get_peers() -> list[Node]:
    result:list[Node] = []

    for peer_folder_path in get_peer_folders():
        result.append(folder_read_peer(peer_folder_path))

    return result

# TODO this should also include us
def get_random_peer() -> Node:
    folders = get_peer_folders()
    folder = random.choice(folders)
    peer = folder_read_peer(folder)
    return peer
