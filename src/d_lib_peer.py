#! /usr/bin/env python3

import os
import random
import argparse

import util
from util import Addr, Public_key, Node

from b_recv_1way import FILE_PUBLIC_KEY, FILE_PORT

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_PEERS = f'{HERE}/_peers'

PEER_FILENAME_PUBLIC_KEY = 'public_key'
PEER_FILENAME_QUERIES_SENT = 'queries_sent'
PEER_FILENAME_QUERIES_ANSWERED = 'queries_answered'

### creation / update

def peer_create_or_update(addr:Addr, pub:Public_key) -> None:
    peer_folder = peer_get_folder_by_addr(addr)

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
    peer_folder = peer_get_folder_by_addr(addr)
    file = f'{peer_folder}/{PEER_FILENAME_QUERIES_SENT}'
    util.file_increase(file)

# TODO what is the query itself is invalid?
# should we really expect the server to return an answer
# regardless?
def peer_increase_queries_answered(addr:Addr) -> None:
    peer_folder = peer_get_folder_by_addr(addr)

    file = f'{peer_folder}/{PEER_FILENAME_QUERIES_ANSWERED}'
    util.file_increase(file)

### FS

def peer_get_node_folders() -> list[str]:
    folders:list[str] = []
    for path, folders, _files in os.walk(FOLDER_PEERS):
        folders = [f'{path}/{folder}' for folder in folders]
        break
    return folders

# TODO rename to get_nodeS_and_reliabilitIES
def peer_get_node_and_reliability() -> list[tuple[Node, int, int]]:

    folders = peer_get_node_folders()
    
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

def peer_all_nodes_to_bytes() -> bytes:

    all_peer_folders = peer_get_node_folders()

    ret = util.int_to_bytes(len(all_peer_folders))

    for peer_folder in all_peer_folders:

        addr_str = os.path.basename(peer_folder)

        addr, nothing = util.chop_addr_from_str(addr_str)
        assert len(nothing) == 0

        pub = util.file_read_public_key(f'{peer_folder}/{PEER_FILENAME_PUBLIC_KEY}')

        ret += util.addr_to_bytes(addr)
        ret += util.public_key_to_bytes(pub)
    
    return ret

def peer_bytes_to_list_of_nodes(data:bytes) -> list[Node]:

    ret = []

    length, data = util.chop_len(data)

    for _ in range(length):
        addr, data = util.chop_addr(data)
        pub, data = util.chop_public_key(data)

        ret.append((addr, pub))
    
    assert len(data) == 0
    
    return ret

def peer_addr_to_node(addr:Addr) -> Node:
    peer_folder = peer_get_folder_by_addr(addr)

    file_pub = f'{peer_folder}/{PEER_FILENAME_PUBLIC_KEY}'
    pub = util.file_read_public_key(file_pub)
    return addr, pub

def peer_me() -> Node:
    # TODO wrong address
    pub = util.file_read_public_key(FILE_PUBLIC_KEY)
    port = util.file_read_port(FILE_PORT)
    return ('127.0.0.1', port), pub

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

def peer_get_folder_by_addr(addr:Addr) -> str:
    folder_name = util.addr_to_str(addr)
    peer_folder = f'{FOLDER_PEERS}/{folder_name}'
    return peer_folder

######
###### main (init)
######

def main() -> None:
    os.makedirs(FOLDER_PEERS, exist_ok=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('lib: peer')
    args = parser.parse_args()
    main()
