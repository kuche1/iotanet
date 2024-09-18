#! /usr/bin/env python3

import util

from beta import bytes_to_public_key, FILE_PUBLIC_KEY
from delta import QUERY_TYPE_PING, QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY, QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW
from epsilon import send_query

pub_bytes = util.file_read_bytes(FILE_PUBLIC_KEY)
pub = bytes_to_public_key(pub_bytes)

query_type = QUERY_TYPE_PING

query_args = b'gacergcaregr'

private_data = b'12345'

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

send_query(query_type, query_args, private_data, path_to_dest, path_way_back)
