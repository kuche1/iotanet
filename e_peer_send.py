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
from c_circular import send_circular

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_PEERS = f'{HERE}/_peers'
FOLDER_SEND_MEASURE = f'{HERE}/_send_measure'
FOLDER_SEND_MEASURE_TMP = f'{FOLDER_SEND_MEASURE}_tmp'

PEER_FILENAME_PUBLIC_KEY = 'public_key'
PEER_FILENAME_QUERIES_SENT = 'queries_sent'
PEER_FILENAME_QUERIES_ANSWERED = 'queries_answered'

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

### main

def main() -> None:

    os.makedirs(FOLDER_PEERS, exist_ok=True)
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
