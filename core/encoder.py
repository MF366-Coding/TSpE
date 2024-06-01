import base64
import gzip


class TSpEncoder:
    def __init__(self, encoding: str = 'utf-8'):
        self._ENCODING = encoding

    def encode_bytes(self, string: bytes, *args) -> bytes:
        return base64.b64encode(string, *args)
    
    def encode_string(self, string: str, *args) -> str:
        return str(self.encode_bytes(bytes(string, self._ENCODING), *args), self._ENCODING)
    
    def decode_bytes(self, string: bytes | str, *args, **kwargs) -> bytes:
        return base64.b64decode(string, *args, **kwargs)
    
    def decode_string(self, string: str, *args, **kwargs) -> str:
        return str(self.decode_bytes(bytes(string, self._ENCODING), *args, **kwargs), self._ENCODING)

    def compress_bytes(self, bytecontent: bytes, *args):
        return str(gzip.compress(bytecontent, *args), encoding=self._ENCODING)

    def decompress_bytes(self, bytecontent: bytes):
        return str(gzip.decompress(bytecontent), encoding=self._ENCODING)
    
    def compress_string(self, string: str, *args):
        return str(gzip.compress(string.encode(self._ENCODING), *args), encoding=self._ENCODING)

    def decompress_string(self, string: str):
        return str(gzip.decompress(string.encode(self._ENCODING)), encoding=self._ENCODING)
    
full_encoder = TSpEncoder()
