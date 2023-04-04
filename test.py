def copy_bits(src, dst,ss, dd, n):
    """
    Copy n bits from bit position ss in src bytearray to bit position dd in dst bytearray.
    The bit position inputs start at 0, just like byte indexes do.
    The dst bytearray must only have those bits changed, the others preserved.
    """
    for i in range(n):
        # Get the source bit
        sbyte = ss // 8
        sbit = ss % 8
        sbitval = (src[sbyte] >> (7 - sbit)) & 1
        
        # Get the destination byte and bit
        dbyte = dd // 8
        dbit = dd % 8
        
        # Modify the destination byte
        if sbitval:
            dst[dbyte] |= (1 << (7 - dbit))
        else:
            dst[dbyte] &= ~(1 << (7 - dbit))
        
        # Advance the bit positions
        ss += 1
        dd += 1

def visualizeBits(byte_array):
    for byte in byte_array:
        for i in range(8):
            bit = (byte >> (7-i)) & 1
            print(bit, end="")
        print(" ", end="")
    print()



source = bytearray(b"\xFF\xFF\xFF")
visualizeBits(source)
dest = bytearray(b"\x01\x01\x01")
visualizeBits(dest)
copy_bits(source,dest,3,3,9)

visualizeBits(dest)