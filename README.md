png-encode
==========

Encode arbitrary data as a PNG image. Works with both python2 and python3.

```python
>>> from pngencode import *
>>> encoded = PNGEncode(b'Hello, world!')
>>> decoded = PNGDecode(encoded)
>>> print(decoded)
b'Hello, world!'
```

Both the encoder and decoder functions input and output `bytes`.

In the case the decoder fails, it returns `None`.