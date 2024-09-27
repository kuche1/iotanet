#! /usr/bin/env python3

import util

from b_recv_1way import FILE_PUBLIC_KEY
from d_lib_peer import peer_create_or_update
from m_query_send import send_query
from j_lib_query import QUERY_TYPE_PING, QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY, QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW, QUERY_TYPE_CHECK_ALIVE

# add peers

# peer_create_or_update(
#     ('127.0.0.1', 6970),
#     util.file_read_public_key('/var/tmp/iotanet-testing/default-peer-0/_public_key'),
# )
# peer_create_or_update(
#     ('127.0.0.1', 6971),
#     util.file_read_public_key('/var/tmp/iotanet-testing/default-peer-1/_public_key'),
# )
# peer_create_or_update(
#     ('127.0.0.1', 6972),
#     util.file_read_public_key('/var/tmp/iotanet-testing/default-peer-2/_public_key'),
# )

# test

pub = util.file_read_public_key(FILE_PUBLIC_KEY)

# query_type = QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY
# query_args = b''

# query_type = QUERY_TYPE_PING
# query_args = b'gacergcaregr'

query_type = QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW
query_args = b''

# query_type = QUERY_TYPE_CHECK_ALIVE
# query_args = b''

private_data = b'12345'

dest_addr = ('127.0.0.1', 6969)

extra_hops = 4

send_query(query_type, query_args, private_data, dest_addr, extra_hops)
