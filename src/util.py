import binascii

def pretty_dump(data):
    # Generate hex dump
    hex_dump = ' '.join([f'{byte:02x}' for byte in data])

    # Print hex dump and ASCII representation side-by-side
    print('Hexdump:                  ASCII:')
    for i in range(0, len(data), 16):
        line = data[i:i+16]
        hex_line = hex_dump[i*3:i*3+48]
        ascii_line = ''.join(chr(byte) if 32 <= byte < 127 else '.' for byte in line)
        ascii_line = ascii_line.ljust(16, ' ') if len(ascii_line) <= 16 else ascii_line[:16]

        print(f'{hex_line.ljust(48)} {ascii_line}')


def say(player,msg):
	player.conn.send(True, (f"\x04say {msg}\x00").encode('latin_1'))

