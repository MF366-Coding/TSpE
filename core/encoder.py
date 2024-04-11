import base64


class Base64Encoder:
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


b64_encoder = Base64Encoder()
