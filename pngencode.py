import io
import struct
import sys
import zlib

PNG_HEADER = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'

# Chunk encoding
# Length (4B) + Chunk Type (4B) + Chunk data (length B) + CRC (4B)
# CRC is computed over the chunk type and chunk data, but not length
CHUNK_HEADER    = '!IBBBB'
CHUNK_TRAILER   = '!I'

# Critial chunks: IHDR, IDAT, IEND

# IHDR
# Width:              4 bytes
# Height:             4 bytes
# Bit depth:          1 byte
# Color type:         1 byte
# Compression method: 1 byte
# Filter method:      1 byte
# Interlace method:   1 byte
IHDR_CHUNK      = '!IIBBBBB'

_WIDTH          = 1
_HEIGHT         = 1
_BIT_DEPTH      = 8
_COLOR_TYPE     = 6
_COMPRESSION    = 0
_FILTER         = 0
_INTERLACE      = 0

_SIZE_OF_PIXEL  = 4

def _crc32(data):
    """Packable CRC32."""
    return zlib.crc32(data) & 0xFFFFFFFF

def PNGEncode(data):
    """Encode arbitrary data into a PNG file."""
    if not type(data) is bytes:
        raise TypeError('data not of type \'bytes\'')

    png = io.BytesIO()
    png.write(PNG_HEADER)

    # IHDR
    IHDR = struct.pack(CHUNK_HEADER, struct.calcsize(IHDR_CHUNK), ord('I'), ord('H'), ord('D'), ord('R'))
    IHDR += struct.pack(IHDR_CHUNK, _WIDTH, _HEIGHT, _BIT_DEPTH, _COLOR_TYPE, _COMPRESSION, _FILTER, _INTERLACE)
    IHDR += struct.pack(CHUNK_TRAILER, _crc32(IHDR))
    png.write(IHDR)

    # IDAT
    IDAT = struct.pack(CHUNK_HEADER, len(data) , ord('I'), ord('D'), ord('A'), ord('T'))
    IDAT += data 
    IDAT += struct.pack(CHUNK_TRAILER, _crc32(IDAT))
    png.write(IDAT)

    # IEND (Empty data)
    IEND = struct.pack(CHUNK_HEADER, 0, ord('I'), ord('E'), ord('N'), ord('D'))
    IEND += struct.pack(CHUNK_TRAILER, _crc32(IEND))
    png.write(IEND)

    return png.getvalue()

def PNGDecode(png):
    """Decode arbitrary data from a PNG file."""
    if not type(png) is bytes:
        raise TypeError('png not of type \'bytes\'')

    # Header
    png = io.BytesIO(png)
    header = png.read(len(PNG_HEADER))
    if header != PNG_HEADER:
        return None

    # Read IHDR
    IHDR = struct.unpack(CHUNK_HEADER, png.read(struct.calcsize(CHUNK_HEADER)))
    png.read(IHDR[0] + 4)

    # Process IDAT
    IDAT_header = png.read(struct.calcsize(CHUNK_HEADER))
    IDAT        = struct.unpack(CHUNK_HEADER, IDAT_header)
    data        = png.read(IDAT[0])
    crc32       = png.read(struct.calcsize(CHUNK_TRAILER))
    local_crc32 = struct.pack(CHUNK_TRAILER, _crc32(IDAT_header + data))

    if crc32 == local_crc32:
        return data
    else:
        return None

def _cli_error():
    print('usage: {0} --decode|--encode INFILE OUTFILE'.format(sys.argv[0]))
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        _cli_error()

    if sys.argv[1] == '--encode':
        with open(sys.argv[3], 'wb') as output:
            with open(sys.argv[2], 'rb') as input:
                output.write(PNGEncode(input.read()))
    elif sys.argv[1] == '--decode':
        with open(sys.argv[3], 'wb') as output:
            with open(sys.argv[2], 'rb') as input:
                output.write(PNGDecode(input.read()))
    else:
        _cli_error()
