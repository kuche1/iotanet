#! /usr/bin/env python3

import argparse
import os
import random
import time

import util
from util import echo as print
from util import Addr, Public_key, Node

from a_send_1way import ITER_SLEEP_SEC
from c_circular import send_circular
from d_lib_peer import peer_addr_to_node, peer_get_random_nodes_based_on_reliability, peer_me, peer_increase_queries_sent, peer_create_or_update

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_SEND_MEASURE = f'{HERE}/_send_measure'
FOLDER_SEND_MEASURE_TMP = f'{FOLDER_SEND_MEASURE}_tmp'

SEND_MEASURE_FILENAME_QUERY = 'query'
SEND_MEASURE_FILENAME_PRIVATE_DATA = 'private_data'
SEND_MEASURE_FILENAME_DEST = 'dest_addr'
SEND_MEASURE_FILENAME_EXTRA_HOPS = 'extra_hops'

### create entry for sending a message

def send_measure(query:bytes, private_data:bytes, dest_addr:Addr, extra_hops:int) -> None:
    root = f'{FOLDER_SEND_MEASURE_TMP}/{time.time()}_{random.random()}'
    save_loc = f'{FOLDER_SEND_MEASURE}/{time.time()}_{random.random()}'

    os.mkdir(root)

    util.file_write_bytes(f'{root}/{SEND_MEASURE_FILENAME_QUERY}', query)
    util.file_write_bytes(f'{root}/{SEND_MEASURE_FILENAME_PRIVATE_DATA}', private_data)
    util.file_write_addr(f'{root}/{SEND_MEASURE_FILENAME_DEST}', dest_addr)
    util.file_write_int(f'{root}/{SEND_MEASURE_FILENAME_EXTRA_HOPS}', extra_hops)

    util.move(root, save_loc)

### deal with entry for sending a message

def handle_folder(root:str) -> None:
    query = util.file_read_bytes(f'{root}/{SEND_MEASURE_FILENAME_QUERY}')
    private_data = util.file_read_bytes(f'{root}/{SEND_MEASURE_FILENAME_PRIVATE_DATA}')
    dest_addr = util.file_read_addr(f'{root}/{SEND_MEASURE_FILENAME_DEST}')
    extra_hops = util.file_read_int(f'{root}/{SEND_MEASURE_FILENAME_EXTRA_HOPS}')

    dest = peer_addr_to_node(dest_addr)

    path:list[Node] = peer_get_random_nodes_based_on_reliability(extra_hops)
    split_idx = random.randint(0, len(path)-1)
    path_to_dest = path[:split_idx] + [dest]
    path_way_back = path[split_idx:] + [peer_me()]

    path_without_me = path_to_dest + path_way_back[:-1]
    private_data = util.list_of_nodes_to_bytes_of_node_addrs(path_without_me) + private_data

    send_circular(query, private_data, path_to_dest, path_way_back)

    for addr, _pub in path_without_me:
        peer_increase_queries_sent(addr)

### main

def main() -> None:

    os.makedirs(FOLDER_SEND_MEASURE, exist_ok=True)
    os.makedirs(FOLDER_SEND_MEASURE_TMP, exist_ok=True)

    me_addr, me_pub = peer_me()
    peer_create_or_update(me_addr, me_pub)

    # TODO there should probably be another thread that does things like check if the peers are currently alive,
    # ask for more peers, ...

    while True:

        time.sleep(ITER_SLEEP_SEC)

        for folders_path, folders, _files in os.walk(FOLDER_SEND_MEASURE):
            for folder in folders:
                path = f'{folders_path}/{folder}'
                util.try_finally(
                    lambda: handle_folder(path),
                    lambda: util.rmtree(path),
                )
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: peer send')
    args = parser.parse_args()
    main()
