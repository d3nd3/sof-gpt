chunks = []
def interact(msg):
	if s == "stop":
		chunks = []
	elif s == "+attack":
		buttonsPressed |= BUTTON_ATTACK
	elif s == "-attack":
		buttonsPressed &= ~BUTTON_ATTACK
	elif s == "+altattack":
		buttonsPressed |= BUTTON_ALTATTACK
	elif s == "-altattack":
		buttonsPressed &= ~BUTTON_ALTATTACK
	elif s == "+use":
		buttonsPressed |= BUTTON_ACTION
	elif s == "-use":
		buttonsPressed &= ~BUTTON_ACTION
	elif s == "+forward":
		moveForward = True
	elif s == "-forward":
		moveForward = False
	elif s == "+back":
		moveBack = True
	elif s == "-back":
		moveBack = False
	elif s == "+moveright":
		moveRight = True
	elif s == "-moveright":
		moveRight = False
	elif s == "+moveleft":
		moveLeft = True
	elif s == "-moveleft":
		moveLeft = False
	elif not len(chunks):
		print(s)
		answer = gpt_ask(s,heartbeat)

		generate_chunks_gpt()
		print(answer)


def generate_chunks_gpt():
	global chunks, last_gpt_stamp, answer
	last_gpt_stamp = time.time()
	flood_msgs = 4
	flood_persecond = 1
	max_chunk_size = 150

	# Split the message by words and newlines
	segments = answer.split('\n')
	
	for segment in segments:
		words = segment.split()
		chunk = ''
		for word in words:
			if len(chunk) + len(word) + 1 <= max_chunk_size:
				if chunk:
					chunk += ' '
				chunk += word
			else:
				chunks.append(chunk)
				chunk = word
		if chunk:
			chunks.append(chunk)

	# Send each chunk while preserving whole words and newlines
	for i, chunk in enumerate(chunks):
		# Add a newline character to the end of all chunks except the last one
		if i < len(chunks) - 1:
			chunk += '\n'

len_prev=0
def output_gpt(conn):
	global chunks, last_gpt_stamp, len_prev
	
	# larger delay if the text length is larger because takes time to read
	if len(chunks) and False:
		if not len_prev :
			len_prev = 0
		if time.time() - last_gpt_stamp > 3+6*len_prev/150:
			last_gpt_stamp = time.time()
			conn.send(True, (f"\x04say {chunks[0]}\x00").encode('ISO 8859-1'))
	
			len_prev = len(chunks[0])
			if len(chunks) == 1:
				chunks = []
				len_prev = 0
			else:
				chunks = chunks[1:]
