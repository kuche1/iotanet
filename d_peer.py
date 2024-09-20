#! /usr/bin/env python3

import argparse
import os
import random
import time

import util
from util import echo as print
from util import Addr, Public_key, Node

from a_send_1way import ITER_SLEEP_SEC
from b_recv_1way import FILE_PUBLIC_KEY, FILE_PORT

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_PEERS = f'{HERE}/_peers'

PEER_FILENAME_PUBLIC_KEY = 'public_key'
PEER_FILENAME_QUERIES_SENT = 'queries_sent'
PEER_FILENAME_QUERIES_ANSWERED = 'queries_answered'

### creation / update

def peer_create_or_update(addr:Addr, pub:Public_key) -> None:
    folder_name = util.addr_to_str(addr)
    peer_folder = f'{FOLDER_PEERS}/{folder_name}'

    os.makedirs(peer_folder, exist_ok=True)

    file_public_key = f'{peer_folder}/{PEER_FILENAME_PUBLIC_KEY}'
    util.file_write_public_key(file_public_key, pub)

    file_queries_sent = f'{peer_folder}/{PEER_FILENAME_QUERIES_SENT}'
    if not os.path.isfile(file_queries_sent):
        util.file_write_int(file_queries_sent, 0)
    
    file_queries_answered = f'{peer_folder}/{PEER_FILENAME_QUERIES_ANSWERED}'
    if not os.path.isfile(file_queries_answered):
        util.file_write_int(file_queries_answered, 0)

def peer_increase_queries_sent(addr:Addr) -> None:
    folder_name = util.addr_to_str(addr)
    peer_folder = f'{FOLDER_PEERS}/{folder_name}'

    file = f'{peer_folder}/{PEER_FILENAME_QUERIES_SENT}'
    util.file_increase(file)

def peer_increase_queries_answered(addr:Addr) -> None:
    folder_name = util.addr_to_str(addr)
    peer_folder = f'{FOLDER_PEERS}/{folder_name}'

    file = f'{peer_folder}/{PEER_FILENAME_QUERIES_ANSWERED}'
    util.file_increase(file)

### FS

def peer_get_node_and_reliability() -> list[tuple[Node, int, int]]:

    folders:list[str] = []
    for path, folders, _files in os.walk(FOLDER_PEERS):
        folders = [f'{path}/{folder}' for folder in folders]
        break
    
    ret = []

    for folder_path in folders:

        peer_addr_str = os.path.basename(folder_path)

        peer_addr, nothing = util.chop_addr_from_str(peer_addr_str)
        assert len(nothing) == 0

        peer_pub = util.file_read_public_key(f'{folder_path}/{PEER_FILENAME_PUBLIC_KEY}')

        node = (peer_addr, peer_pub)

        queries_sent = util.file_read_int(f'{folder_path}/{PEER_FILENAME_QUERIES_SENT}')

        queries_answered = util.file_read_int(f'{folder_path}/{PEER_FILENAME_QUERIES_ANSWERED}')

        ret.append((node, queries_answered, queries_sent))
    
    return ret

### util

# TODO keep in mind that your (real) reliability is going
# to be 100% so you might end up in a situation where you're
# routing all the traffic on your own node
def peer_get_random_nodes_based_on_reliability(num:int) -> list[Node]:

    node_succ_total = peer_get_node_and_reliability()

    ret = []

    for _ in range(num):

        # higher number means higher change to be picked
        # TODO I REALLY need to think about this formula, so that both (inactive nodes get ignored) and (you can't get exposed by the path you take)
        # also there need to be some sort of mechanism for getting rid of data that is too old
        node_succ_total.sort(
            key=lambda i: random.random() * ( (20 + i[1]) / (20 + i[2]) ),
            reverse=True,
        )

        node, _, _ = node_succ_total[0]

        ret.append(node)

    return ret

### main

def main() -> None:

    os.makedirs(FOLDER_PEERS, exist_ok=True)

    # TODO stupid, find another way to add yourself, or at least do not use the local ip
    peer_create_or_update(
        ('127.0.0.1', util.file_read_port(FILE_PORT)),
        util.file_read_public_key(FILE_PUBLIC_KEY),
    )

    while True:

        time.sleep(ITER_SLEEP_SEC)

        print('TODO nothing')

if __name__ == '__main__':
    parser = argparse.ArgumentParser('daemon: peer managament')
    args = parser.parse_args()
    main()