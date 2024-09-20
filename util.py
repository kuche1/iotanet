#! /usr/bin/env python3

from typing import Callable, cast, Any
import os
import cryptography
import cryptography.hazmat.primitives.asymmetric.rsa as cryptography_rsa
import cryptography.hazmat.primitives.serialization as cryptography_serialization
import random
import traceback
import datetime
import io
import inspect
import argparse
import time
import shutil

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_TMP = f'{HERE}/_tmp'

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
###### atomic operation enablers
######

def gen_rnd_filename() -> str:
    return f'{time.time()}_{random.random()}'

def gen_tmp_file_path() -> str:
    return f'{FOLDER_TMP}/{gen_rnd_filename()}'

def move(src:str, dst:str) -> None:
    shutil.move(src, dst)

def rmtree(path:str) -> None:
    tmp = gen_tmp_file_path()
    move(path, tmp)
    shutil.rmtree(tmp)

def copy(src:str, dst:str) -> None:
    tmp = gen_tmp_file_path()
    shutil.copy(src, tmp)
    move(tmp, dst)

######
###### conversion of things to rawbytes
###### 
# NOTE:
# for when they are going to be used by themselves
# for example, a conversion of an int would just be
# str(123).encode(), so no len info, so it must not
# be concatinated with other data

def public_key_to_rawbytes(key:Public_key) -> bytes:
    return key.public_bytes(
        encoding=cryptography_serialization.Encoding.PEM,
        format=cryptography_serialization.PublicFormat.SubjectPublicKeyInfo,
    )

def rawbytes_to_public_key(data:bytes) -> Public_key:
    key = cryptography_serialization.load_pem_public_key(
        data,
    )
    return cast(Public_key, key)

######
###### conversion of things to bytes
###### 
# NOTE: all of these are supposed to be "choppable", so information about the length or a separator is included if unknown

def int_to_bytes(num:int) -> bytes:
    sep = b';'
    return str(num).encode() + sep

# no need to include len info here, since it's fixed
def symetric_key_to_bytes(key:Symetric_key) -> bytes:
    k, i = key
    return k + i

def public_key_to_bytes(key:Public_key) -> bytes:
    data = public_key_to_rawbytes(key)

    return int_to_bytes(len(data)) + data

def addr_to_bytes(addr:Addr) -> bytes:
    sep = b';'
    ip, port = addr
    return ip.encode() + sep + str(port).encode() + sep

def list_of_nodes_to_bytes_of_node_addrs(nodes:list[Node]) -> bytes:
    data = b''
    data += int_to_bytes(len(nodes))
    for addr, _pub in nodes:
        data += addr_to_bytes(addr)
    return data

######
###### serialisation: bytes
######

def file_read_bytes(file:str) -> bytes:
    with open(file, 'rb') as f:
        return f.read()

def file_write_bytes(file:str, data:bytes) -> None:
    tmp = gen_tmp_file_path()

    with open(tmp, 'wb') as f:
        f.write(data)
    
    move(tmp, file)

######
###### serialisation: str
######

def file_read_str(file:str) -> str:
    return file_read_bytes(file).decode()

def file_write_str(file:str, data:str) -> None:
    return file_write_bytes(file, data.encode())

######
###### serialisation: int
######

def file_read_int(file:str) -> int:
    return int(file_read_str(file))

def file_write_int(file:str, num:int) -> None:
    return file_write_str(file, str(num))

def file_increase(file:str) -> None:
    num = file_read_int(file)
    file_write_int(file, num + 1)

def chop_int(data:bytes) -> tuple[int, bytes]:
    sep = b';'
    idx = data.index(sep)
    num_bytes = data[:idx]
    data = data[idx + len(sep):]
    num = int(num_bytes)
    return num, data

######
###### control flow
######

def try_finally(fnc:Callable[[],None], cleanup:Callable[[],None]) -> None:
    try:
        fnc()
    except:
         err_info = traceback.format_exc()
         print()
         print(f'ERROR ({datetime.date.today()}):')
         print(err_info)
         print()
    finally:
        cleanup()

######
###### serialisation: key
######

def chop_symetric_key(data:bytes) -> tuple[Symetric_key, bytes]:

    sym_key = data[:SYMETRIC_KEY_SIZE_BYTES]
    data = data[SYMETRIC_KEY_SIZE_BYTES:]
    assert len(sym_key) == SYMETRIC_KEY_SIZE_BYTES

    sym_iv = data[:SYMETRIC_KEY_IV_SIZE_BYTES]
    data = data[SYMETRIC_KEY_IV_SIZE_BYTES:]
    assert len(sym_iv) == SYMETRIC_KEY_IV_SIZE_BYTES

    return (sym_key, sym_iv), data

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
    data = symetric_key_to_bytes(key)
    file_write_bytes(file, data)

def file_read_public_key(file:str) -> Public_key:
    key_bytes = file_read_bytes(file)
    return rawbytes_to_public_key(key_bytes)

def file_write_public_key(file:str, pub:Public_key) -> None:
    data = public_key_to_rawbytes(pub)
    file_write_bytes(file, data)

######
###### serialisation: port
######

def file_write_port(file:str, port:Port) -> None:
    return file_write_int(file, port)

def file_read_port(file:str) -> Port:
    port = file_read_int(file)
    assert port > 0
    return port

######
###### serialisation: addr
######

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
    data = addr_to_bytes(addr)
    file_write_bytes(file, data)

def file_read_addr(file:str) -> Addr:

    with open(file, 'rb') as f:
        data = f.read()

    addr, data = chop_addr(data)
    assert len(data) == 0

    return addr

def chop_list_of_addrs(data:bytes) -> tuple[list[Addr], bytes]:
    addrs:list[Addr] = []
    size, data = chop_int(data)
    for _ in range(size):
        addr, data = chop_addr(data)
        addrs.append(addr)
    return addrs, data

######
###### dynamic (de)serialisation [seems like a cool idea but needs refinement]
######

def file_serialise_addr(file:str, addr:Addr) -> None:
    filename = os.path.basename(file)
    directory = os.path.dirname(file)
    file_write_addr(f'{directory}/addr_{filename}', addr)

def file_serialise_bytes(file:str, data:bytes) -> None:
    filename = os.path.basename(file)
    directory = os.path.dirname(file)
    file_write_bytes(f'{directory}/bytes_{filename}', data)

def file_deserialise(file:str) -> Any:
    filename = os.path.basename(file)

    assert '_' in filename
    typ = filename.split('_')[0]

    if typ == 'addr':
        return file_read_addr(file)
    elif typ == 'bytes':
        return file_read_bytes(file)
    else:
        assert False, f'unknown type `{typ}` for file `{file}`'

def folder_deserialise(root:str) -> list[Any]:
    ret = []
    for files_path, _folders, files in os.walk(root):
        files.sort() # sorted alphabetically
        for file in files:
            file_path = f'{files_path}/{file}'
            ret.append(file_deserialise(file_path))
        break
    return ret

######
###### echo
######

def echo(*a:Any, **kw:Any) -> None:
    file = io.StringIO()
    print(*a, **kw, file=file)
    buf = file.getvalue()

    frame = inspect.stack()[1]
    filename = frame[0].f_code.co_filename
    filename = os.path.basename(filename)

    if filename.endswith('.py'):
        filename = filename[:-3]

    buf = '\n'.join([f'{filename}: {line}' for line in buf.splitlines()])

    print(buf)

######
###### main (init)
######

def main() -> None:

    try:
        shutil.rmtree(FOLDER_TMP)
    except FileNotFoundError:
        pass

    os.mkdir(FOLDER_TMP)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('utilities')
    args = parser.parse_args()
    main()
