#! /usr/bin/env python3

from beta import bytes_to_public_key
from gamma import send_circular

pub_bytes = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAomCXisuPGxlOPSoznZ6R\nQIdw2EDaj+OAQufnRMQDv9ploJioyUVKoTCF4qfhX1iG6xPB9uTWIA0gVwY0j92t\n0f5UIrtJztAZHhfC60Jd8Ar72d/cfgc4LYvSO40QDiJTNi0fiK76n0IMxH7jHr7z\n/OAuM77yceMsjj/EU+uRZUa1WGAVx1XZOxCge6tgqcLa6VOzR9jj4ZIi92MB1H0C\nekI85OaxxT7/2//EyFBx+o4YaokuQRlsJvb9VwEb4bXU2bcD62E1sDb9LTMHiWJg\nxT5wybeu7Lz43cwUaiOBF+vG7MwH8w5wA8Vro3n3XDj5XDMNgw+Of7+5m2WrO8m/\n3QIDAQAB\n-----END PUBLIC KEY-----\n'
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
