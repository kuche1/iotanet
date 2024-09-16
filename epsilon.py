
import socket
import argparse
from typing import Iterator

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey

NOT_FOR_YOU = '0'.encode()
YES_FOR_YOU = '1'.encode()

Private_key = RSAPrivateKey
Public_key = RSAPublicKey
Ip = str
Port = int
Addr = tuple[Ip,Port]
Node = tuple[Addr,Public_key]

def cut_until(msg:bytes, until:bytes) -> tuple[bytes, bytes]:
    idx = msg.index(until)
    return msg[:idx], msg[idx+len(until):]

def generate_keys() -> tuple[Private_key,Public_key]:
    private = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
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

# TODO ne mi haresva tova kak se poluchava
# ideally, tova e otdelen thread i drugite procesi prosto si govorqt s nego
def handle_incoming(port:int, private_key:Private_key) -> Iterator[bytes]:

    sock = socket.socket()

    sock.bind(('', port))

    sock.listen()

    while True:

        client_sock, _client_addr = sock.accept()

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
            yield actual_data

    sock.close()

def send_directly(payload:bytes, to:Addr) -> None:
    # TODO we should do the "wait for some time before sending then send all in mixed order" trick
    sock = socket.socket()
    sock.connect(to)
    sock.sendall(payload)
    sock.close()

def send(payload:bytes, path:list[Node]) -> None:

    is_receiver = True

    assert len(path)

    for [ip, port], public_key in reversed(path):

        if is_receiver:
            is_receiver = False
            payload = YES_FOR_YOU + payload
        else:
            payload = NOT_FOR_YOU + ip.encode() + ':'.encode() + str(port).encode() + ':'.encode() + payload

        payload = encrypt(payload, public_key)

    send_directly(payload, (ip, port))

def handle_msg(payload:bytes, private_key:Private_key) -> tuple[bool, bytes]:

    payload = decrypt(payload, private_key)

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

        payload = decrypt(payload, private_key)

        return True, payload

    else:

        assert False

def main() -> None:

    print('dicks')

    # handle_requests(6969)

    private_key, public_key = generate_keys()

    data = encrypt(b'hui 123', public_key)

    print(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Epsilon Node')
    args = parser.parse_args()

    main()
