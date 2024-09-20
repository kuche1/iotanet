#! /usr/bin/env python3

import util

from b_recv_1way import FILE_PUBLIC_KEY
from d_peer_send import peer_create_or_update
from e_recv_query import QUERY_TYPE_PING, QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY, QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW
from f_send_process_query import send_query

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

query_type = QUERY_TYPE_PING

query_args = b'gacergcaregr'

private_data = b'12345'

dest_addr = ('127.0.0.1', 6969)

extra_hops = 4

send_query(query_type, query_args, private_data, dest_addr, extra_hops)
