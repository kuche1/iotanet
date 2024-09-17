
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

######
###### symetric encryption
######

SYMETRIC_BLOCKSIZE_BYTES = 16

SYMETRIC_KEY_SIZE_BYTES = 32
# 32 bytes, for AES-256

SYMETRIC_KEY_IV_SIZE_BYTES = SYMETRIC_BLOCKSIZE_BYTES

def generate_symetric_key() -> tuple[bytes, bytes]:
    key = os.urandom(SYMETRIC_KEY_SIZE_BYTES)
    iv = os.urandom(SYMETRIC_BLOCKSIZE_BYTES)
    return key, iv

def encrypt_symetric(msg:bytes, key:bytes, iv:bytes) -> bytes:
    padder = crypto_padding.PKCS7(SYMETRIC_BLOCKSIZE_BYTES * 8).padder()
    padded = padder.update(msg) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded) + encryptor.finalize()

    return encrypted

def decrypt_symetric(msg:bytes, key:bytes, iv:bytes) -> bytes:
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
CMD_SEND_SEP = b':'

CMD_PUSH = b'1'

# TODO all messages that are meant for us should go to a folder instead of using a callback
def handle_incoming_connections(buck_sock:Bucket, port:int, private_key:Private_key, on_recv:Callable[[bytes],None]) -> None:

    sock = socket.socket()

    sock.bind(('', port))

    sock.listen()

    buck_sock.set(sock)

    while True:

        try:
            client_sock, _client_addr = sock.accept()
        except OSError:
            # thread owner has closed the socket
            break
        
        connection_time = time.time()

        threading.Thread(target=handle_client, args=(private_key, on_recv, client_sock, connection_time)).start()

    sock.close()

    buck_sock.set(None)

def handle_client(private_key:Private_key, on_recv:Callable[[bytes],None], client:Socket, connection_time:float) -> None:

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
    
    for_us, actual_data = handle_msg(payload, private_key)
    if for_us:
        on_recv(actual_data)

def handle_msg(payload:bytes, private_key:Private_key) -> tuple[bool, bytes]:

    print()
    print(f'received message {payload!r}')
    print()

    if len(payload) < ASYMETRIC_KEY_SIZE_BYTES:
        print(f'someone is fucking with us')
        return False, b''
    
    req = payload[:ASYMETRIC_KEY_SIZE_BYTES]
    payload = payload[ASYMETRIC_KEY_SIZE_BYTES:]

    req = decrypt_asymetric(req, private_key)
    print(f'got request: {req!r}')

    cmd = req[0:1] # this really is req[0] but in a way that makes mypy happy
    args = req[1:]

    if cmd == CMD_SEND:

        ip_as_bytes, port_as_bytes = args.split(CMD_SEND_SEP)

        ip = ip_as_bytes.decode()

        port = int(port_as_bytes)

        send_directly(payload, (ip, port))

    elif cmd == CMD_PUSH:

        asym_key = args[:SYMETRIC_KEY_SIZE_BYTES]
        asym_iv = args[SYMETRIC_KEY_SIZE_BYTES:]

        assert len(asym_key) == SYMETRIC_KEY_SIZE_BYTES
        assert len(asym_iv) == SYMETRIC_KEY_IV_SIZE_BYTES

        payload = decrypt_symetric(payload, asym_key, asym_iv)

        return True, payload

    else:

        print(f'got unknown command `{cmd!r}`')

    return False, b''

######
###### send
######

def send(payload:bytes, path:list[Node]) -> None:

    assert len(path)

    is_receiver = True

    for [ip, port], public_key in reversed(path):

        if is_receiver:

            is_receiver = False

            sym_key, sym_iv = generate_symetric_key()

            payload = encrypt_symetric(payload, sym_key, sym_iv)

            payload = \
                encrypt_asymetric(CMD_PUSH + sym_key + sym_iv, public_key) + \
                payload

        else:

            payload = \
                encrypt_asymetric(CMD_SEND + ip.encode() + CMD_SEND_SEP + str(port).encode(), public_key) + \
                payload

    send_directly(payload, (ip, port))

def send_directly(payload:bytes, to:Addr) -> None:
    # TODO we should do the "wait for some time before sending then send all in mixed order" trick

    print()
    print(f'sending to {to} message {payload!r}')
    print()

    sock = socket.socket()

    try:
        sock.connect(to)
    except ConnectionRefusedError:
        print(f'connection refused to {to}')
        return

    sock.sendall(payload)

    sock.close()

######
###### test
######

def test() -> None:

    ####
    #### sym enc/dec
    ####

    original = b'This is a secret message.'

    messeeg = original

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

    assert messeeg == original

    ####
    #### asym enc/dec
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
    thr = threading.Thread(target=handle_incoming_connections, args=(buck_sock, 6969, priv, on_recv))
    thr.start()

    print('waiting')

    while buck_sock.get() != None:
        time.sleep(0.1)
    
    print('ready')

    msg = 'sex sex SEEEXXXX $###33333XXXXXXHHHHHHs'

    msg_as_bytes = msg.encode()

    path = [
        (('127.0.0.1', 6969), pub),
        (('127.0.0.1', 6969), pub),
        (('127.0.0.1', 6969), pub),
        (('127.0.0.1', 6969), pub),
    ]

    send(msg_as_bytes, path)

    time.sleep(5)

    buck_sock.get().close() # a bit forced

    thr.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Epsilon Node; call directly to run tests')
    args = parser.parse_args()
    test()
