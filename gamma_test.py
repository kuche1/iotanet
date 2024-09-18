#! /usr/bin/env python3

from beta import bytes_to_public_key
from gamma import send_circular

pub_bytes = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAy3aMyPFGEPbgrdyAD3Rb\n2+voVzISCuGG6awx7oFEaiwrhwdPLgLckyACF2lsazRZTzfVVDqbEEY+Jrt2I5wG\nQd15fGTnHdce+xKSUJNTXQSKKHdyRCOZt9caAbhSfXnhImQv3tamwKX7FbdroHAn\n0pCPvaIT89EAOEMPTtC2SX6iYvegfsMlDvf5sWw83/9hHzfFUZqnSezug6W7MHT4\n3AkFrAYAlLz/rY9eks+and6SunqE7mQhaU746iaIOck9ybBXKqVdLLkDfhmEDEv+\nmJJGoFdmqpqTiZQfxO6HDxckF6+zl18qa46TgyLucT11L3T7wjz9Ro7mKX+ypZsW\n/wIDAQAB\n-----END PUBLIC KEY-----\n'
pub = bytes_to_public_key(pub_bytes)

q = b'hi'
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
