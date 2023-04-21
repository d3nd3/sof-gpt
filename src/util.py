import binascii
import sys
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
	player.conn.append_string_to_reliable(f"\x04say {msg}\x00")


# Normal for sofgpt to change userinfo when outputting gpt text (altenrating text color)
def changeTextColor(player,newColor):
	c = player.userinfo["name"]
	player.userinfo["name"] = c[:-1] + newColor


def str_to_byte(str):
	return str.encode("latin-1")

def byte_to_str(bytes):
	return bytes.decode("latin-1")

def mem_to_str(memview):
	return byte_to_str(memview.tobytes())


def print_bits(bytes_obj,nlen,bitpos,n_bits):
	if nlen != n_bits:
		print(f"bit not match , expected { nlen } , got { n_bits }")
		sys.exit(1)
	bytepos = bitpos // 8
	bytes_obj = bytes_obj[bytepos:]
	bits = ''.join(format(byte, '08b') for byte in bytes_obj)
	print(bits[:n_bits])
