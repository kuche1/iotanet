#! /usr/bin/env python3

import socket
import os
import time
import argparse
import shutil
import random

import util

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_TO_SEND = f'{HERE}/_to_send'
FOLDER_TO_SEND_TMP = f'{FOLDER_TO_SEND}_tmp'

FILE_IP = 'ip'
FILE_PORT = 'port'
FILE_DATA = 'data'

GRACE_PERIOD_BEFORE_SENDING_SEC = 0.5

ITER_SLEEP_SEC = 0.1

def create_send_entry(ip:str, port:int, data:bytes) -> None:

    now = time.time()

    root = f'{FOLDER_TO_SEND_TMP}/{now}'
    target_root = f'{FOLDER_TO_SEND}/{now}'

    os.mkdir(root)
    # if this fails: (the parent folder doesn't exist) or (someone else already tried to send a message at the exact same time)

    with open(f'{root}/{FILE_IP}', 'w') as f:
        f.write(ip)

    with open(f'{root}/{FILE_PORT}', 'w') as f:
        f.write(str(port))

    with open(f'{root}/{FILE_DATA}', 'wb') as f:
        f.write(data)

    shutil.move(root, target_root)

def handle_folder(root:str) -> None:

    ip = util.file_read_str(f'{root}/{FILE_IP}')
    port = util.file_read_int_positive(f'{root}/{FILE_PORT}')
    data = util.file_read_bytes(f'{root}/{FILE_DATA}')

    # print()
    # print(f'sending to {ip}:{port} message {data!r}')
    # print()

    sock = socket.socket()

    sock.connect((ip, port))

    sock.sendall(data)

    sock.close()

def main() -> None:

    os.makedirs(FOLDER_TO_SEND, exist_ok=True)
    os.makedirs(FOLDER_TO_SEND_TMP, exist_ok=True)

    while True:

        time.sleep(ITER_SLEEP_SEC)

        folders:list[str] = []
        for _path, folders, _files in os.walk(FOLDER_TO_SEND):
            break
        
        timestamps = []

        for folder in folders:
            folder_path = f'{FOLDER_TO_SEND}/{folder}'

            try:
                timestamp = float(folder)
            except ValueError:
                print(f'bad folder, invalid name: {folder}')
                shutil.rmtree(folder_path)
                continue

            timestamps.append(timestamp)

        if len(timestamps) == 0:
            continue

        send_them_all = False

        now = time.time()

        oldest = min(timestamps)

        if oldest + GRACE_PERIOD_BEFORE_SENDING_SEC > now:
            # the precise time COULD be calculated
            continue
        
        timestamps.sort(key=lambda i: random.random())

        for entry in timestamps:

            root = f'{FOLDER_TO_SEND}/{entry}'

            util.try_finally(
                lambda: handle_folder(root),
                lambda: shutil.rmtree(root),
            )

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: sender')
    args = parser.parse_args()

    main()
