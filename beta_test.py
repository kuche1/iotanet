# #! /usr/bin/env python3

# import threading
# import time

# from beta import generate_symetric_key, encrypt_symetric, decrypt_symetric, generate_asymetric_keys, encrypt_asymetric, decrypt_asymetric, private_key_to_bytes, bytes_to_private_key, handle_incoming_connections, send_1way, bytes_to_public_key

# def main() -> None:

#     ####
#     #### sym enc/dec
#     ####

#     original = b'This is a secret message.'

#     messeeg = original

#     key1, iv1 = generate_symetric_key()
#     key2, iv2 = generate_symetric_key()

#     messeeg = encrypt_symetric(messeeg, key1, iv1)

#     # print("Single Encrypted Message:", messeeg)

#     messeeg = encrypt_symetric(messeeg, key2, iv2)

#     # print("Double Encrypted Message:", messeeg)

#     messeeg = decrypt_symetric(messeeg, key2, iv2)

#     # print("Single Decrypted Message:", messeeg)

#     messeeg = decrypt_symetric(messeeg, key1, iv1)

#     # print("Double Decrypted Message:", messeeg)

#     assert messeeg == original

#     ####
#     #### asym enc/dec
#     ####

#     msg = 'fxewagv4reytgesrfdgvfy5ey645r'
#     msg_as_bytes = msg.encode()
#     priv, pub = generate_asymetric_keys()
#     msg_as_bytes = encrypt_asymetric(msg_as_bytes, pub)
#     assert decrypt_asymetric(msg_as_bytes, priv).decode() == msg

#     ####
#     #### saving/loading keys
#     ####

#     priv, pub = generate_asymetric_keys()

#     msg_as_bytes = b'wa4egx4egecg'

#     encrypted = encrypt_asymetric(msg_as_bytes, pub)

#     priv_bytes = private_key_to_bytes(priv)

#     priv = bytes_to_private_key(priv_bytes)

#     decrypted = decrypt_asymetric(encrypted, priv)

#     assert msg_as_bytes == decrypted

#     ####
#     #### send/recv self
#     ####

#     # those were copy-pasted from the receiving
#     priv_bytes = b'-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC+g7DI13zV90xr\nAvpO8CHbJBBPjvv8aavBVoIIzEdv8zIAFvrUKuc2nmWBSJ94UFjwkK2q47yP07jg\nagP/q40EJQ2vKx9EHdQBVZXyVP73XDOcQandwVKHvEcgzVaaQUqoBInb8mih0p1k\nhYynyn+wlkyIEH0muKJ7s6VTA/cqtE7yi4ASAPClwTQ1PbHZOjWcw1Jjld8mlsBc\nJqu0WTMRfKTFAPOcW3ItjKoOyQKhNtH2Er/ZnqKA0A9ZnQ1kpwcQ/u8VFr5Z8R0U\nyFrHcC2SgcXHOqeRJLVjB1eZ0LIUOfZ85WcqwY7fQLTvklpXTdeQ/xnJpgb6E2/e\nVdIJvqxbAgMBAAECggEADHA+/xCT+HOhxszWIzLqFaDYUHFxQfdzkiG/8gDFsJP2\nvEBugPgKH4FI9vS9tgESRXvqCCG/9738MJQLYx/ECwoQ8ievw2aVJxR7lUD3t+u0\n/Os2mCFdQ4/HLxI+U2pBjGW7dc5GXDu1hfty2v5NcZiRMkMCq3Vbj8BYt2pSCAof\npHZw4+XPROaSQYPB8ssqdwVOjS/zpTO4VUosxDXuYhjjwfF3jKAbQEFHKlqr/LRB\nxdWfD5ebaqQrOPCMuYBhO8p4dBXMYQ17C2GiJTc63r+0hTlBzBkE6/mQobUrjmMS\nggI3rEdzum96yeVjN3G1wwPVNp60p7sqUUXO1cQQrQKBgQD3qHF0ZvqZCUOXw/2Z\n4uKJH0Ln7ohrUcQBJWkoinBYnhc1Tqy+H03f7W6SKc4Rfp/6kDzIbC4/42gZdNAZ\nTKlvfu0nU8oKKrFUlf//IKcvU/QOuZvkOtyfS1LvfK9VtKYRkFTZV58Btl5DonqO\neuGnI0N/4C3PcawdztN2GYACxwKBgQDE7n95pOZ2j3emEdyPRNyZZ0nloFlQ8Q0C\nON+r7KHo9St4KtxUyy5OLEMurnm1wHv9RjjpIB6RaBKzqoU89n1nTElEdMXSFAkA\n6aMkfORes1iUlfRq41IG2zzpOrAbonB4t8ByUDsSL+btJTxs1QSkX+BsKk8/S2Nr\nM94188z1zQKBgF4vdVZrg4qH92jUZLINk1HKzcse8ErAQeadr6x3WdqZ5QGk9hUo\nGpm61n5H39LPcU/9YuBmJACwH3ru7eVxPk7k2pRGTWQocGBW25DPfkWFjB+9fwgB\nSr5aCySBKr1RgobTeTFfHV2tWZQnSqy9FuxVgOo0+7cU5/w+GDWl5QUpAoGAekf1\nk50XFYtkKhRxNez2ZbLDKfh1PVNQVo7mJCUdLEAAK+/BPE2lhRjq5nOkU30gAFa4\nQ9mT4YoUAsfhT8dmetvdqsovg5C5Pn3UtXVvgHYwjKLIUA6zAlrj6ZZtf9tPp0XC\nE7lJ1LM12w8CBDoJVd/KxJ9I8e5n30snsayfGgkCgYEAkCtt6H8SFy6Kqjp0Uypm\nvZG+qm7IeD1y8vZXaqc5NWv07oTiru3uMxBTBct9cv92kvERHp/DIrt5xo27W1gv\na6xRutKQgy80+uGRe6ZIkJ4KAryiJpEeuIDKuTVu72+pVbKDc1+OtYz6u5ojd/XK\nV8iSjLhnRjkSho8lk1YIPTM=\n-----END PRIVATE KEY-----\n'
#     pub_bytes = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvoOwyNd81fdMawL6TvAh\n2yQQT477/GmrwVaCCMxHb/MyABb61CrnNp5lgUifeFBY8JCtquO8j9O44GoD/6uN\nBCUNrysfRB3UAVWV8lT+91wznEGp3cFSh7xHIM1WmkFKqASJ2/JoodKdZIWMp8p/\nsJZMiBB9Jriie7OlUwP3KrRO8ouAEgDwpcE0NT2x2To1nMNSY5XfJpbAXCartFkz\nEXykxQDznFtyLYyqDskCoTbR9hK/2Z6igNAPWZ0NZKcHEP7vFRa+WfEdFMhax3At\nkoHFxzqnkSS1YwdXmdCyFDn2fOVnKsGO30C075JaV03XkP8ZyaYG+hNv3lXSCb6s\nWwIDAQAB\n-----END PUBLIC KEY-----\n'

#     priv = bytes_to_private_key(priv_bytes)
#     pub = bytes_to_public_key(pub_bytes)

#     msg = 'sex sex SEEEXXXX $###33333XXXXXXHHHHHHs'

#     msg_as_bytes = msg.encode()

#     path = [
#         (('127.0.0.1', 6969), pub),
#         (('127.0.0.1', 6969), pub),
#         (('127.0.0.1', 6969), pub),
#         (('127.0.0.1', 6969), pub),
#     ]

#     send_1way(msg_as_bytes, path)

# main()

import sys
print('this file is too old')
sys.exit(1)
