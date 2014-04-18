from pngencode import *

def test_codec():
    src     = b'Hello, world!'
    encoded = PNGEncode(src)
    decoded = PNGDecode(encoded)
    assert(src == decoded)
