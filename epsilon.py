
import socket
import argparse
from typing import Iterator, Callable, Any
import cryptography
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as crypto_padding
import threading
import time
import os

Private_key = RSAPrivateKey
Public_key = RSAPublicKey
Ip = str
Port = int
Addr = tuple[Ip,Port]
Node = tuple[Addr,Public_key]
Socket = socket.socket

######
###### class
######

class Bucket:
    def __init__(s, data:Any) -> None:
        s.set(data)
    def set(s, data:Any) -> None:
        s.data = data
    def get(s) -> Any:
        return s.data

######
###### basic fnc
######

def cut_until(msg:bytes, until:bytes) -> tuple[bytes, bytes]:
    idx = msg.index(until)
    return msg[:idx], msg[idx+len(until):]

######
###### asymetric encryption
######

ASYMETRIC_KEY_SIZE = 2048
# actually this is the size in bits of the encrypted message

def generate_asymetric_keys() -> tuple[Private_key,Public_key]:
    private = cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
        public_exponent=65537,
        key_size=ASYMETRIC_KEY_SIZE,
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

######
###### symetric encryption
######

ASYMETRIC_BLOCKSIZE_BYTES = 16

def generate_symetric_key() -> tuple[bytes, bytes]:
    key = os.urandom(32) # 32 bytes, for AES-256
    iv = os.urandom(ASYMETRIC_BLOCKSIZE_BYTES)
    return key, iv

def encrypt_symetric(msg:bytes, key:bytes, iv:bytes) -> bytes:
    padder = crypto_padding.PKCS7(ASYMETRIC_BLOCKSIZE_BYTES * 8).padder()
    padded = padder.update(msg) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded) + encryptor.finalize()

    return encrypted

def decrypt_symetric(msg:bytes, key:bytes, iv:bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(msg) + decryptor.finalize()

    unpadder = crypto_padding.PKCS7(ASYMETRIC_BLOCKSIZE_BYTES * 8).unpadder()
    decrypted = unpadder.update(decrypted) + unpadder.finalize()

    return decrypted

######
###### ...
######

NOT_FOR_YOU = '0'.encode()
YES_FOR_YOU = '1'.encode()

# perhaps it's best if instead of a callback all the messages
# get written to a folder on the FS
def handle_incoming(buck_sock:Bucket, port:int, private_key:Private_key, on_recv:Callable[[bytes],None]) -> None:

    sock = socket.socket()

    sock.bind(('', port))

    sock.listen()

    buck_sock.set(sock)

    # print('handler listening')

    while True:

        try:
            client_sock, _client_addr = sock.accept()
        except OSError:
            # thread owner has closed the socket
            break

        # TODO everything from this point on should be in a new thread

        payload = b''

        while True:

            data = client_sock.recv(4096)

            if not data:
                break
            
            payload += data
        
        client_sock.close()
        
        succ, actual_data = handle_msg(payload, private_key)
        if succ:
            on_recv(actual_data)

    sock.close()

def send_directly(payload:bytes, to:Addr) -> None:
    # TODO we should do the "wait for some time before sending then send all in mixed order" trick

    print(f'request to send something to `{to}`')

    sock = socket.socket()

    try:
        sock.connect(to)
    except ConnectionRefusedError:
        print(f'connection refused to `{to}`')
        return

    sock.sendall(payload)

    sock.close()

def send(payload:bytes, path:list[Node]) -> None:

    is_receiver = True

    assert len(path)

    for [ip, port], public_key in reversed(path):

        # print(f'payload to send {payload!r}')

        if is_receiver:
            is_receiver = False
            payload = YES_FOR_YOU + payload
        else:
            payload = NOT_FOR_YOU + ip.encode() + ':'.encode() + str(port).encode() + ':'.encode() + payload

        # print(f'with prefix {payload!r}')

        payload = encrypt_asymetric(payload, public_key)

        # print(f'encrypted {payload!r}')

    send_directly(payload, (ip, port))

def handle_msg(payload:bytes, private_key:Private_key) -> tuple[bool, bytes]:

    # print(f'got {payload!r}')

    payload = decrypt_asymetric(payload, private_key)

    # print(f'decrypted {payload!r}')

    if payload.startswith(NOT_FOR_YOU):

        payload = payload[len(NOT_FOR_YOU):]

        ip_as_bytes, payload = cut_until(payload, ':'.encode())
        ip = ip_as_bytes.decode()

        port_as_bytes, payload = cut_until(payload, ':'.encode())
        port = int(port_as_bytes)

        send_directly(payload, (ip, port))

        return False, b''

    elif payload.startswith(YES_FOR_YOU):

        payload = payload[len(YES_FOR_YOU):]

        # print(f'without the prefix {payload!r}')

        return True, payload

    else:

        assert False

def test() -> None:

    ####
    #### test shit out
    ####

    messeeg = b'This is a secret message.'

    key1, iv1 = generate_symetric_key()
    key2, iv2 = generate_symetric_key()

    messeeg = encrypt_symetric(messeeg, key1, iv1)

    print("Single Encrypted Message:", messeeg)

    messeeg = encrypt_symetric(messeeg, key2, iv2)

    print("Double Encrypted Message:", messeeg)

    messeeg = decrypt_symetric(messeeg, key2, iv2)

    print("Single Decrypted Message:", messeeg)

    messeeg = decrypt_symetric(messeeg, key1, iv1)

    print("Double Decrypted Message:", messeeg)

    ####
    #### enc/dec
    ####

    msg = 'fxewagv4reytgesrfdgvfy5ey645r'
    msg_as_bytes = msg.encode()
    priv, pub = generate_asymetric_keys()
    msg_as_bytes = encrypt_asymetric(msg_as_bytes, pub)
    assert decrypt_asymetric(msg_as_bytes, priv).decode() == msg

    ####
    #### send/recv self
    ####

    priv, pub = generate_asymetric_keys()

    buck_sock = Bucket(None)
    on_recv = lambda data: print(f'received: {data!r}')
    thr = threading.Thread(target=handle_incoming, args=(buck_sock, 6969, priv, on_recv))
    thr.start()

    print('waiting')

    while buck_sock.get() != None:
        time.sleep(0.1)
    
    print('ready')

    msg = 'sex sex SEEEXXXX $###33333XXXXXXHHHHHHs'

    msg_as_bytes = msg.encode()

    path = [
        (('127.0.0.1', 6969), pub),
    ]

    send(msg_as_bytes, path)

    buck_sock.get().close() # a bit forced

    thr.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Epsilon Node; call directly to run tests')
    args = parser.parse_args()
    test()
