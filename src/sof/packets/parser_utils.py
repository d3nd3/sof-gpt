def string(buf):
	"""
	parse a null terminated string
	returns a tuple containing the string parsed
	and the remaining of buffer without the string
	"""
	startstr = buf
	count = 0
	while buf:
		if buf[0] == 0x00: #or view is none
			buf = buf[1:]
			break;
		buf = buf[1:]
		count += 1
	return (startstr[:count],buf)
