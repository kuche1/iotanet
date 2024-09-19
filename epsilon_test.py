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

dest = me

extra_hops = 4

send_query(query_type, query_args, private_data, dest, me, extra_hops)
