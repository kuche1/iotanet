#! /usr/bin/env python3

import util

from gamma import send_circular
from d_recv_query import QUERY_TYPE_PING

pub_bytes = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs5DSV+PzM5uzE/ETLTnK\nu8JmLH/wIzVh7fRS8P1EsADeJgKq6uDKPUMeHuyIpLB1ldoGjEogrShdxLu1HVRG\nm8KNFTxEc64CkE79toZ0AN5IpGVSflZBSp+D2liAIt5PQdUL6p/tHm8ZA56rdWbu\nJYUc3PUTaUsuit9CdqHM0SP1ZXxV8e8rvjhrJznfEa73+ZCEJc5IQEk6hHTQDLoo\nXDdRJYNnUfNIJ7rjPMuDW4vtwypw/G7gNAAk3+y4PZ5inCfMQy4OzKkoZz3JnFSi\n/GSzYpuSzhpyoAZ0mPuQ54zF3pz6RPhAt/YB9e7VDJDRf+KerZcMi1OZ4QyHhfj/\nHQIDAQAB\n-----END PUBLIC KEY-----\n'
pub = util.bytes_to_public_key(pub_bytes)

q = QUERY_TYPE_PING + b'hi'
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

send_circular(q, q_id, path_to_dest, path_way_back)
