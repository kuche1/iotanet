#! /usr/bin/env python3

import util

from beta import FILE_PUBLIC_KEY
from delta import QUERY_TYPE_PING, QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY, QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW
from epsilon import send_query

pub = util.file_read_public_key(FILE_PUBLIC_KEY)

query_type = QUERY_TYPE_PING

query_args = b'gacergcaregr'

private_data = b'12345'

me = (('127.0.0.1', 6969), pub)

path_to_dest = [
    util.get_random_peer(),
    util.get_random_peer(),
    me,
]

path_way_back = [
    util.get_random_peer(),
    util.get_random_peer(),
    me,
]

send_query(query_type, query_args, private_data, path_to_dest, path_way_back)
