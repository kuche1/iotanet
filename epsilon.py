
import socket
import argparse
from typing import Iterator, Callable, Any
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
import threading
import time

NOT_FOR_YOU = '0'.encode()
YES_FOR_YOU = '1'.encode()

Private_key = RSAPrivateKey
Public_key = RSAPublicKey
Ip = str
Port = int
Addr = tuple[Ip,Port]
Node = tuple[Addr,Public_key]
Socket = socket.socket

class Bucket:
    def __init__(s, data:Any) -> None:
        s.set(data)
    def set(s, data:Any) -> None:
        s.data = data
    def get(s) -> Any:
        return s.data

def cut_until(msg:bytes, until:bytes) -> tuple[bytes, bytes]:
    idx = msg.index(until)
    return msg[:idx], msg[idx+len(until):]

def generate_keys(key_size:int=2048) -> tuple[Private_key,Public_key]:
    private = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size, # actually this is the size in bits of the encrypted message
    )

    public = private.public_key()

    return private, public

def encrypt(msg:bytes, key:Public_key) -> bytes:
    return key.encrypt(
        msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt(msg:bytes, key:Private_key) -> bytes:
    return key.decrypt(
        msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

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

        payload = encrypt(payload, public_key)

        # print(f'encrypted {payload!r}')

    send_directly(payload, (ip, port))

def handle_msg(payload:bytes, private_key:Private_key) -> tuple[bool, bytes]:

    # print(f'got {payload!r}')

    payload = decrypt(payload, private_key)

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
    #### just testing something out
    ####

    msg = '1234567890'
    msg_as_bytes = msg.encode()
    priv, pub = generate_keys(256*8)
    msg_as_bytes = encrypt(msg_as_bytes, pub)
    print(f'original={len(msg)} encrypted={len(msg_as_bytes)}')
    priv, pub = generate_keys((256+32*2+2)*8)
    msg_as_bytes = encrypt(msg_as_bytes, pub)
    print(f'original={len(msg)} encrypted={len(msg_as_bytes)}')

    ####
    #### enc/dec
    ####

    msg = 'fxewagv4reytgesrfdgvfy5ey645r'
    msg_as_bytes = msg.encode()
    priv, pub = generate_keys()
    msg_as_bytes = encrypt(msg_as_bytes, pub)
    priv2, pub2 = generate_keys()
    msg_as_bytes = encrypt(msg_as_bytes, pub2)
    assert decrypt(msg_as_bytes, priv).decode() == msg

    ####
    #### send/recv self
    ####

    priv, pub = generate_keys()

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
