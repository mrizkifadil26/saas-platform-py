# TODO: later should be introduce the hash secret
# def hash_identifier(
#     value: str,
#     *,
#     secret: bytes,
# ) -> str:
#     return hmac.new(
#         secret,
#         value.encode(),
#         hashlib.sha256,
#     ).hexdigest()


import hashlib


def hash_identifier(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8"),
    ).hexdigest()
