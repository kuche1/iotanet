#! /usr/bin/env python3

import os
import random
import argparse
import shutil

import util
from util import Addr, Public_key, Node

from b_recv_1way import FILE_PUBLIC_KEY, FILE_PORT

HERE = os.path.dirname(os.path.realpath(__file__))

FOLDER_PEERS_KNOWN = f'{HERE}/_peers_known'
FOLDER_PEERS_ALIVE = f'{HERE}/_peers_alive'

PEER_FILENAME_PUBLIC_KEY = 'public_key'
PEER_FILENAME_QUERIES_SENT = 'queries_sent'
PEER_FILENAME_QUERIES_ANSWERED = 'queries_answered'

### creation / update

# TODO check if addr is valid (addr might be 127.0.0.1, port might be invalid)
def peer_create_or_update(addr:Addr, pub:Public_key) -> None:
    peer_folder = peer_get_known_folder_by_addr(addr)

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
    peer_folder = peer_get_known_folder_by_addr(addr)
    file = f'{peer_folder}/{PEER_FILENAME_QUERIES_SENT}'
    util.file_increase(file)

# TODO what is the query itself is invalid?
# should we really expect the server to return an answer
# regardless?
def peer_increase_queries_answered(addr:Addr) -> None:
    peer_folder = peer_get_known_folder_by_addr(addr)

    file = f'{peer_folder}/{PEER_FILENAME_QUERIES_ANSWERED}'
    util.file_increase(file)

### FS

def peer_get_known_node_folders() -> list[str]:
    folders:list[str] = []
    for path, folders, _files in os.walk(FOLDER_PEERS_KNOWN):
        folders = [f'{path}/{folder}' for folder in folders]
        break
    return folders

def peer_get_alive_node_folders() -> list[str]:
    folders:list[str] = []
    for path, _folders, files in os.walk(FOLDER_PEERS_ALIVE):
        files = [f'{path}/{file}' for file in files]
        break
    return files

def peer_get_known_addrs() -> list[Addr]:
    ret = []
    for folder in peer_get_known_node_folders():
        addr = util.str_to_addr(os.path.basename(folder))
        ret.append(addr)
    return ret

def peer_get_alive_addrs() -> list[Addr]:
    ret = []
    for folder in peer_get_alive_node_folders():
        addr = util.str_to_addr(os.path.basename(folder))
        ret.append(addr)
    return ret

def peer_all_known_nodes_to_bytes() -> bytes:

    all_peer_folders = peer_get_known_node_folders()

    ret = util.int_to_bytes(len(all_peer_folders))

    for peer_folder in all_peer_folders:

        addr = util.str_to_addr(os.path.basename(peer_folder))

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
    peer_folder = peer_get_known_folder_by_addr(addr)

    file_pub = f'{peer_folder}/{PEER_FILENAME_PUBLIC_KEY}'
    pub = util.file_read_public_key(file_pub)
    return addr, pub

def peer_me() -> Node:
    # TODO wrong address
    pub = util.file_read_public_key(FILE_PUBLIC_KEY)
    port = util.file_read_port(FILE_PORT)
    return ('127.0.0.1', port), pub

### alive/dead status

def peer_mark_alive(addr:Addr) -> None:
    file = f'{FOLDER_PEERS_ALIVE}/{util.addr_to_str(addr)}'

    with open(file, 'w'):
        pass

# untested
def peer_mark_dead(addr:Addr) -> None:
    file = f'{FOLDER_PEERS_ALIVE}/{util.addr_to_str(addr)}'
    util.rmtree(file)

### util

def peer_get_random_alive_nodes(num:int) -> list[Node]:
    assert num >= 0

    if num == 0:
        return []

    node_folders = peer_get_alive_node_folders()
    assert len(node_folders) > 0

    ret = []
    for _ in range(num):
        folder = random.choice(node_folders)
        ret.append(peer_get_node_by_folder(folder))
    return ret

def peer_get_known_folder_by_addr(addr:Addr) -> str:
    folder_name = util.addr_to_str(addr)
    peer_folder = f'{FOLDER_PEERS_KNOWN}/{folder_name}'
    return peer_folder

def peer_get_node_by_folder(folder:str) -> Node:
    addr_str = os.path.basename(folder)
    addr = util.str_to_addr(addr_str)
    return peer_addr_to_node(addr)

######
###### main (init)
######

def main() -> None:
    os.makedirs(FOLDER_PEERS_KNOWN, exist_ok=True)

    try:
        shutil.rmtree(FOLDER_PEERS_ALIVE)
    except FileNotFoundError:
        pass
    
    os.mkdir(FOLDER_PEERS_ALIVE)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('lib: peer')
    args = parser.parse_args()
    main()
