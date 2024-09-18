#! /usr/bin/env python3

import threading
import time

from beta import generate_symetric_key, encrypt_symetric, decrypt_symetric, generate_asymetric_keys, encrypt_asymetric, decrypt_asymetric, private_key_to_bytes, bytes_to_private_key, handle_incoming_connections, send_1way, bytes_to_public_key

def main() -> None:

    ####
    #### sym enc/dec
    ####

    original = b'This is a secret message.'

    messeeg = original

    key1, iv1 = generate_symetric_key()
    key2, iv2 = generate_symetric_key()

    messeeg = encrypt_symetric(messeeg, key1, iv1)

    # print("Single Encrypted Message:", messeeg)

    messeeg = encrypt_symetric(messeeg, key2, iv2)

    # print("Double Encrypted Message:", messeeg)

    messeeg = decrypt_symetric(messeeg, key2, iv2)

    # print("Single Decrypted Message:", messeeg)

    messeeg = decrypt_symetric(messeeg, key1, iv1)

    # print("Double Decrypted Message:", messeeg)

    assert messeeg == original

    ####
    #### asym enc/dec
    ####

    msg = 'fxewagv4reytgesrfdgvfy5ey645r'
    msg_as_bytes = msg.encode()
    priv, pub = generate_asymetric_keys()
    msg_as_bytes = encrypt_asymetric(msg_as_bytes, pub)
    assert decrypt_asymetric(msg_as_bytes, priv).decode() == msg

    ####
    #### saving/loading keys
    ####

    priv, pub = generate_asymetric_keys()

    msg_as_bytes = b'wa4egx4egecg'

    encrypted = encrypt_asymetric(msg_as_bytes, pub)

    priv_bytes = private_key_to_bytes(priv)

    priv = bytes_to_private_key(priv_bytes)

    decrypted = decrypt_asymetric(encrypted, priv)

    assert msg_as_bytes == decrypted

    ####
    #### send/recv self
    ####

    # those were copy-pasted from the receiving daemon
    priv_bytes = b'-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDKIXOepZC4IU0d\nNx0Lc6A2hQ7c0F5K7YkWZBctDmH7IaNIbIq0DC4uq6IcNq/g5ALMyWHVpXsok7Sx\nvjbD+D0P9EwPuv5LuFr2OLjcJR2JhyPUZc5nfciGzuFMUwWDanWt1nnHxC7Y5r/l\n76020zLm+M1+EBRuKgNor34bEV8KwIUxHNHVT5SqPEe0nqfAW/deQkxxB1Hka89H\njYFGYXbMtW96HM4UKw1o2vSTCpz9pIbF41pdUgmipY9BObflGryb7bSgzFxVf4p5\n7f6MmqYGFUWKh2vd+2RzJe88b2e2d0yLNauhfYvdzu79oB4fSxbrWlbUHJoIk7/a\nDKbDgeCfAgMBAAECggEADCs2ZDswer1agKNERt+3qgCZs/aBbr5dLfFpqcc/Y9iT\nFXWfZhaDo0Cm+k7aiM4BUyXek3eqcfduffLnJiYoOvEosRu/WnynUUJ58prza8es\ngwl8AyQB8ge7bZZj8xTyL7yFSV8IuPsvW17yDSZq3pfk+y1ppXY3DVLfYy7JC4MP\nPYV5tNBhWfjPSFVJ6n/Kh56NehayzsuIwuF8QdwIQ18xJe2Pum1H+uZ5ZpyaR7Me\nnloHoHXqmMe4tVGjzbQ+GLkf5FjjRwmS6OUJMjrLJFmxQ1CmnMq/PjtjYhMj0V74\n9G0jXq8DLmAEUCntVY0RkqdvdSvNNDoj2hG49HSiPQKBgQDl8a74n6IvHszjr5wT\nsrgKP1SnNHkinSJU9o4ddI2Xnzywyh1C3Yt9Ahyep7md3ttoySJWluI0cwP8R8Cl\ndKO1fAnHbojoPz40GM2GlvhEbGi80yMALpmID99sTVOmVKIfOL2js3gntQmoIJxZ\nYv7SkEOT5+UAIyUNwKjWC/UXlQKBgQDhCPHnuZS64HSIUBvVoeMOeh4TPP+LODY0\nHgwyEErL2TCwmZEyxvUOCZr8mcoTxCYsMuPb30CPnhunealF3rt+UZwPXBAnj6Fm\n1F1KnurddGBaUuR5WM26dG3CQ2QsRyWDyWUyBMVDG68CZiGuH/dTZPuykKYjpKfi\nx/Siilo6YwKBgQDVN/BJNq0LCIJwtkwBr/0b83Gpwex5fj9xjVZmVcddyxhZznCn\nqgtIFYc4Tsq9awME/UzMAgkrHWOasWYfhjKvfJ8MwKBOyyYA5ObfYGpB+Ex+m0Gf\nT5aqJh3ErUdduqjCTrj6bNaD60lTDzorYLJtybwAEE22fOBFClsEb/4KqQKBgE3q\n7vexRlI+jZr1Qe4Ck7/bgLZglIr796isDsT25y8WEMnVInVWdltZ8BQum82kSSNc\nq5DiCFSyBhlDAt1ydbETSNn4oo9QKC6WsYa459GuDf64XOu3V+SLk8WD2BeMuuya\nuzNKe5L07vABtP+5icWSXaRCeYQ16vuXCJmPFhbJAoGBAIRzvZ3msLEIBP7FVla6\nbzI0zCHkuDC2cJ5/M6vo87yO2oJ8sgdG5F5rykbQWXvfNeJiIrfl5AGwlDo25kKp\nfEoq22o2MHlSogiKA9ITkSZWj3h6E/Bb1gCuNRTOF5rNvN98egzcd9NNpHG5u+nD\nGfo5mQsNi1r7GTG94Q3Ap3fO\n-----END PRIVATE KEY-----\n'
    pub_bytes = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyiFznqWQuCFNHTcdC3Og\nNoUO3NBeSu2JFmQXLQ5h+yGjSGyKtAwuLquiHDav4OQCzMlh1aV7KJO0sb42w/g9\nD/RMD7r+S7ha9ji43CUdiYcj1GXOZ33Ihs7hTFMFg2p1rdZ5x8Qu2Oa/5e+tNtMy\n5vjNfhAUbioDaK9+GxFfCsCFMRzR1U+UqjxHtJ6nwFv3XkJMcQdR5GvPR42BRmF2\nzLVvehzOFCsNaNr0kwqc/aSGxeNaXVIJoqWPQTm35Rq8m+20oMxcVX+Kee3+jJqm\nBhVFiodr3ftkcyXvPG9ntndMizWroX2L3c7u/aAeH0sW61pW1ByaCJO/2gymw4Hg\nnwIDAQAB\n-----END PUBLIC KEY-----\n'

    priv = bytes_to_private_key(priv_bytes)
    pub = bytes_to_public_key(pub_bytes)

    msg = 'sex sex SEEEXXXX $###33333XXXXXXHHHHHHs'

    msg_as_bytes = msg.encode()

    path = [
        (('127.0.0.1', 6969), pub),
        (('127.0.0.1', 6969), pub),
        (('127.0.0.1', 6969), pub),
        (('127.0.0.1', 6969), pub),
    ]

    send_1way(msg_as_bytes, path)

main()
