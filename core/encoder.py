import base64
import gzip


class TSpEncoder:
    def __init__(self, encoding: str = 'utf-8'):
        self._ENCODING = encoding

    def encode_bytes(self, bytecontent: bytes) -> bytes:
        encoded_bytes = base64.b64encode(bytecontent)
        return encoded_bytes
    
    def encode_string(self, string: str) -> str:
        byte_string = bytes(string, self._ENCODING)
        encoded_string = self.encode_bytes(byte_string)
        return str(encoded_string, self._ENCODING)
    
    def decode_bytes(self, bytecontent: bytes) -> bytes:
        decoded_bytes = base64.b64decode(bytecontent)
        return decoded_bytes
    
    def decode_string(self, string: str) -> str:
        byte_string: bytes = base64.b64decode(string)
        decoded_string: bytes = self.decode_bytes(byte_string)
        return str(decoded_string, self._ENCODING)

    def compress_bytes(self, bytecontent: bytes) -> bytes:
        compressed_bytes: bytes = gzip.compress(bytecontent)
        return compressed_bytes

    def decompress_bytes(self, bytecontent: bytes) -> bytes:
        decompressed_bytes: bytes = gzip.decompress(bytecontent)
        return decompressed_bytes
    
    def compress_string(self, string: str) -> str:
        byte_string = string.encode(self._ENCODING)
        compressed_bytes = self.compress_bytes(byte_string)
        encoded_compressed_bytes = self.encode_bytes(compressed_bytes)
        return str(encoded_compressed_bytes, self._ENCODING)
    
    def decompress_string(self, string: str) -> str:
        decoded_compressed_bytes = self.decode_bytes(string)
        decompressed_string = self.decompress_bytes(decoded_compressed_bytes)
        return str(decompressed_string, self._ENCODING)

full_encoder = TSpEncoder()
