from sof.client import SofClient

import sys

if __name__ == "__main__":
	ip = sys.argv[1]
	port = sys.argv[2]
	name = sys.argv[3]
	print(f"ip : {ip}\nport : {port}\nname : {name}")

	client = SofClient()

	userinfo = {
		"predicting"			: "0",
		"spectator_password" 	: "specme",
		"password"				: "player",
		"cl_violence"			: "0",
		"spectator"				: "0",
		"skin"					: "widowmaker",
		"teamname"				: "Ministry of Sin",
		"fov"					: "95",
		"msg"					: "0",
		"rate"					: "15000",
		"allow_download_models" : "1",
		"team_red_blue"			: "0"
	}
	
	# endpoints store players
	# connection is just a class that stores socket and funcs for the socket
	# each player will create a connection class (socket)
	
	endpoint = client.addEndpoint(ip,port)
	# green visible font
	name += "\x03"
	client.addPlayerToEndpoint(endpoint,userinfo,name)

	# endpoint = client.addEndpoint("5.135.46.179","28916")
	# client.addPlayerToEndpoint(endpoint,userinfo,name)

	# endpoint = client.addEndpoint("5.135.46.179","28926")
	# client.addPlayerToEndpoint(endpoint,userinfo,name)


	# endpoint = client.addEndpoint("5.135.46.179","28920")
	# client.addPlayerToEndpoint(endpoint,userinfo,name)

	client.beginLoop()

