#! /usr/bin/env python3

import util

from beta import bytes_to_public_key, FILE_PUBLIC_KEY
from gamma import send_circular
from delta import QUERY_TYPE_PING, QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY, QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW

pub_bytes = util.file_read_bytes(FILE_PUBLIC_KEY)
pub = bytes_to_public_key(pub_bytes)

q = QUERY_TYPE_PING + b'hiace4tcwet4wat4w'
# q = QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY
# q = QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW

q_id = b'12345'

path_to_dest = [
    (('127.0.0.1', 6969), pub),
    (('127.0.0.1', 6969), pub),
    (('127.0.0.1', 6969), pub),
    (('127.0.0.1', 6969), pub),
]

path_way_back = [
    (('127.0.0.1', 6969), pub),
    (('127.0.0.1', 6969), pub),
    (('127.0.0.1', 6969), pub),
    (('127.0.0.1', 6969), pub),
]

q_sym_key = send_circular(q, q_id, path_to_dest, path_way_back)
