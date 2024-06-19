import base64
import gzip


def encode_bytes(string: bytes | str) -> bytes:
    encoded_bytes = base64.b64encode(string)
    return encoded_bytes


def decode_bytes(string: bytes | str) -> bytes:
    decoded_bytes = base64.b64decode(string)
    return decoded_bytes


def compress_bytes(bytecontent: bytes) -> bytes:
    compressed_bytes: bytes = gzip.compress(bytecontent)
    return compressed_bytes


def decompress_bytes(bytecontent: bytes) -> bytes:
    decompressed_bytes: bytes = gzip.decompress(bytecontent)
    return decompressed_bytes

