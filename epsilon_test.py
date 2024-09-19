#! /usr/bin/env python3

import util

from beta import FILE_PUBLIC_KEY
from delta import QUERY_TYPE_PING, QUERY_TYPE_GIVE_ME_YOUR_PUBLIC_KEY, QUERY_TYPE_GIVE_ME_THE_PEERS_YOU_KNOW
from epsilon import send_query, peer_update

# add peers

peer_update(
    ('127.0.0.1', 6970),
    util.file_read_public_key('/var/tmp/iotanet-testing/default-peer-0/_public_key'),
)
peer_update(
    ('127.0.0.1', 6971),
    util.file_read_public_key('/var/tmp/iotanet-testing/default-peer-1/_public_key'),
)
peer_update(
    ('127.0.0.1', 6972),
    util.file_read_public_key('/var/tmp/iotanet-testing/default-peer-2/_public_key'),
)

# test

pub = util.file_read_public_key(FILE_PUBLIC_KEY)

query_type = QUERY_TYPE_PING

query_args = b'gacergcaregr'

private_data = b'12345'

me = (('127.0.0.1', 6969), pub)

dest = me

extra_hops = 4

send_query(query_type, query_args, private_data, dest, me, extra_hops)
