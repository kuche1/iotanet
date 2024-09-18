#! /usr/bin/env python3

from beta import bytes_to_public_key
from gamma import send_circular

pub_bytes = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtHGGwUOqRzAkWfXx2xCl\n4bCuJn6PmONrtzG8CiMkH5P+fvvpRDMwr8IPmFT5sYhDbCD3qjSv/b3nyPfpTgr9\nN9Cx6qOyPbaGUue15R5/uYb6IR9rcdJ71yZ4/vhsbcRM0iHmM1Wp/ASr+QCa9mN7\nAfG7LkwMFxEg4955Llj65vWrdPnImmYjLlTw0XOK2QHVAi9pvPvfrq9EI3owaUZq\n2ct5ZVIMiSbFTbkpCrCvmP/rca/kS362DCWeHVMs32A5qcgiJ5s0LiKhh9MK+nWF\nMg22U3nSiMrtMGz6711coEdIXMyOu0XTzXjVoY3fwT2N2DxwMBcDmJnFU1UccQcK\n+wIDAQAB\n-----END PUBLIC KEY-----\n'
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
