#! /usr/bin/env python3

import argparse
import time
import os
import shutil
import random

import util
from util import Node

from alpha import ITER_SLEEP_SEC
from gamma import FOLDER_RESPONSES, FILENAME_PRIVATE_DATA, FILENAME_RESPONSE, send_circular, FILENAME_SENDER_ADDR

def send_query(query_type:bytes, query_args:bytes, private_data:bytes, dest:Node, me:Node, extra_hops:int) -> None:

    assert len(query_type) == 1

    query = query_type + query_args

    private_data = query_type + private_data

    # TODO we need to save some statistics for each of the peers' reliability
    # a simple counter for "queries sent to peer" and "successully completed queries"
    # and I'm no sure if this logic should be here, or in `send_circular`, or even somewhere on a higher level
    # (we could include the peers on the path in the `private_data`)
    # (actually, the more I think about it, the better of an idea seems that this peer evaluation thing should be in `send_circular` and the path selection too)

    path:list[Node] = []
    for _ in range(extra_hops):
        path.append(util.get_random_peer())

    split_idx = random.randint(0, len(path)-1)

    path_to_dest = path[:split_idx] + [dest]
    path_way_back = path[split_idx:] + [me]

    send_circular(
        query,
        private_data,
        path_to_dest,
        path_way_back,
    )

def handle_folder(path:str) -> None:

    sender_addr = util.file_read_addr(f'{path}/{FILENAME_SENDER_ADDR}')
    private_data = util.file_read_bytes(f'{path}/{FILENAME_PRIVATE_DATA}')
    response = util.file_read_bytes(f'{path}/{FILENAME_RESPONSE}')

    assert len(private_data) > 0

    query_type = private_data[0:1]
    private_data = private_data[1:]

    print('epsilon:')
    print(f'epsilon: {sender_addr=}')
    print(f'epsilon: {query_type=}')
    print(f'epsilon: {response=}')
    print(f'epsilon: {private_data=}')

def main() -> None:

    while True:

        time.sleep(ITER_SLEEP_SEC)

        for _path, response_folders, _files in os.walk(FOLDER_RESPONSES):

            for response_folder in response_folders:

                path = f'{FOLDER_RESPONSES}/{response_folder}'

                util.try_finally(
                    lambda: handle_folder(path),
                    lambda: shutil.rmtree(path),
                )

            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: query response evaluator')
    args = parser.parse_args()
    main()
