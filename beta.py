#! /usr/bin/env python3

import socket
import argparse
from typing import Iterator, Callable, Any
import cryptography
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as crypto_padding
import threading
import time
import os
import shutil
from typing import cast

import util
from util import Symetric_key, SYMETRIC_KEY_SIZE_BYTES, SYMETRIC_BLOCKSIZE_BYTES, Addr, Private_key, Public_key, Node

from alpha import create_send_entry

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_RECEIVED_UNPROCESSED = f'{HERE}/_received_unprocessed'
FOLDER_RECEIVED_UNPROCESSED_TMP = f'{FOLDER_RECEIVED_UNPROCESSED}_tmp'

FILE_PUBLIC_KEY = f'{HERE}/_public_key'
FILE_PRIVATE_KEY = f'{HERE}/_private_key'

Socket = socket.socket

######
###### basic fnc
######

def cut_until(msg:bytes, until:bytes) -> tuple[bytes, bytes]:
    idx = msg.index(until)
    return msg[:idx], msg[idx+len(until):]

######
###### asymetric encryption
######

ASYMETRIC_KEY_SIZE_BYTES = 256
# actually this is also the size in bits of the encrypted message

def generate_asymetric_keys() -> tuple[Private_key,Public_key]:
    private = cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
        public_exponent=65537,
        key_size=ASYMETRIC_KEY_SIZE_BYTES * 8,
    )

    public = private.public_key()

    return private, public

def encrypt_asymetric(msg:bytes, key:Public_key) -> bytes:
    return key.encrypt(
        msg,
        cryptography.hazmat.primitives.asymmetric.padding.OAEP( # this padding adds (32*2+2) additional bytes to the message (sha256 is 32bits)
            mgf=cryptography.hazmat.primitives.asymmetric.padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_asymetric(msg:bytes, key:Private_key) -> bytes:
    return key.decrypt(
        msg,
        cryptography.hazmat.primitives.asymmetric.padding.OAEP(
            mgf=cryptography.hazmat.primitives.asymmetric.padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def private_key_to_bytes(key:Private_key) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

def bytes_to_private_key(data:bytes) -> Private_key:
    key = serialization.load_pem_private_key(
        data,
        password=None,
    )

    return cast(Private_key, key)

def public_key_to_bytes(key:Public_key) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

######
###### symetric encryption
######

def generate_symetric_key() -> Symetric_key:
    key = os.urandom(SYMETRIC_KEY_SIZE_BYTES)
    iv = os.urandom(SYMETRIC_BLOCKSIZE_BYTES)
    return key, iv

def encrypt_symetric(msg:bytes, key_iv:Symetric_key) -> bytes:
    key, iv = key_iv

    padder = crypto_padding.PKCS7(SYMETRIC_BLOCKSIZE_BYTES * 8).padder()
    padded = padder.update(msg) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded) + encryptor.finalize()

    return encrypted

def decrypt_symetric(msg:bytes, key_iv:Symetric_key) -> bytes:
    key, iv = key_iv

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(msg) + decryptor.finalize()

    unpadder = crypto_padding.PKCS7(SYMETRIC_BLOCKSIZE_BYTES * 8).unpadder()
    decrypted = unpadder.update(decrypted) + unpadder.finalize()

    return decrypted

######
###### handle incoming messages
######

RECEIVE_MSG_MAX_SIZE = 1024 * 1024 * 50 # in bytes

CMD_SEND = b'0'
CMD_PUSH = b'1'

def handle_incoming_connections(port:int, private_key:Private_key) -> None:

    sock = socket.socket()

    sock.bind(('', port))

    sock.listen()

    while True:

        client_sock, _client_addr = sock.accept()

        connection_time = time.time()

        threading.Thread(target=handle_client, args=(private_key, client_sock, connection_time)).start()

    sock.close()

def handle_client(private_key:Private_key, client:Socket, connection_time:float) -> None:

    payload = b''

    while True:

        data = client.recv(4096)

        if not data:
            break
        
        payload += data

        if len(payload) > RECEIVE_MSG_MAX_SIZE:
            print(f'message too big')
            client.close()
            return

    client.close()
    
    handle_msg(payload, private_key, connection_time)

def handle_msg(payload:bytes, private_key:Private_key, connection_time:float) -> None:

    # print()
    # print(f'received message {payload!r}')
    # print()

    if len(payload) < ASYMETRIC_KEY_SIZE_BYTES:
        print(f'message too short')
        return
    
    req = payload[:ASYMETRIC_KEY_SIZE_BYTES]
    payload = payload[ASYMETRIC_KEY_SIZE_BYTES:]

    req = decrypt_asymetric(req, private_key)
    # print()
    # print(f'got request: {req!r}')
    # print()

    cmd = req[0:1] # this really is just req[0] but in a way that makes mypy happy
    args = req[1:]

    if cmd == CMD_SEND:

        addr, args = util.chop_addr(args)
        assert len(args) == 0

        create_send_entry(addr, payload)

        print(f'beta: sending data to {addr}')

    elif cmd == CMD_PUSH:

        sym_key, args = util.chop_symetric_key(args)
        assert len(args) == 0

        payload = decrypt_symetric(payload, sym_key)

        data_tmp = f'{FOLDER_RECEIVED_UNPROCESSED_TMP}/{connection_time}'
        data_saved = f'{FOLDER_RECEIVED_UNPROCESSED}/{connection_time}'

        with open(data_tmp, 'wb') as f: # this cannot fail since the incoming connection handler is single-threaded
            f.write(payload)
        
        shutil.move(data_tmp, data_saved)

        print(f'beta: pushing')

    else:

        print(f'got unknown command {cmd!r}')

######
###### send
######

def generate_send_1way_header(path:list[Node]) -> tuple[Addr, bytes, Symetric_key]:

    assert len(path) >= 0

    target_addr = None

    data = b''

    while True:

        addr_cur, public_key_cur = path[0]
        path = path[1:]

        if target_addr == None:
            target_addr = addr_cur

        if len(path) <= 0:

            sym_key, sym_iv = generate_symetric_key()

            data += encrypt_asymetric(CMD_PUSH + sym_key + sym_iv, public_key_cur)

            assert target_addr != None
            return cast(Addr, target_addr), data, (sym_key, sym_iv)

        else:

            addr_next, public_key_next = path[0]

            data += \
                encrypt_asymetric(
                    CMD_SEND + util.addr_to_bytes(addr_next)
                    ,
                    public_key_next
                )

def generate_send_1way_payload(payload:bytes, path:list[Node]) -> tuple[Addr, bytes]:

    addr, header, sym_key = generate_send_1way_header(path)

    payload = encrypt_symetric(payload, sym_key)

    payload = header + payload
    
    return addr, payload

def send_1way(payload:bytes, path:list[Node]) -> None:

    addr, payload = generate_send_1way_payload(payload, path)

    create_send_entry(addr, payload)

######
###### main
######

def main(port:int, private_key:Private_key) -> None:

    os.makedirs(FOLDER_RECEIVED_UNPROCESSED, exist_ok=True)
    os.makedirs(FOLDER_RECEIVED_UNPROCESSED_TMP, exist_ok=True)

    handle_incoming_connections(port, private_key)

if __name__ == '__main__':

    parser = argparse.ArgumentParser('daemon: receiver')
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    if os.path.isfile(FILE_PUBLIC_KEY) and os.path.isfile(FILE_PRIVATE_KEY):

        with open(FILE_PRIVATE_KEY, 'rb') as fr:
            priv_bytes = fr.read()

        with open(FILE_PUBLIC_KEY, 'rb') as fr:
            pub_bytes = fr.read()

        priv = bytes_to_private_key(priv_bytes)

        pub = util.bytes_to_public_key(pub_bytes)

        print('loaded existing keys')

    else:

        priv, pub = generate_asymetric_keys()

        priv_bytes = private_key_to_bytes(priv)

        pub_bytes = public_key_to_bytes(pub)

        with open(FILE_PRIVATE_KEY, 'wb') as fw:
            fw.write(priv_bytes)

        with open(FILE_PUBLIC_KEY, 'wb') as fw:
            fw.write(pub_bytes)

        print('generated new keys')

    main(args.port, priv)
