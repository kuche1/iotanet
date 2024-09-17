
import socket
import os

HERE = os.path.dirname(os.path.realpath(__file__))

def create_send_entry(ip:str, port:int, data:bytes) -> None:

    # TODO we should do the "wait for some time before sending then send all in mixed order" trick

    print()
    print(f'sending to {ip}:{port} message {data!r}')
    print()

    sock = socket.socket()

    try:
        sock.connect((ip, port))
    except ConnectionRefusedError:
        print(f'connection refused to {ip}:{port}')
        return

    sock.sendall(data)

    sock.close()
