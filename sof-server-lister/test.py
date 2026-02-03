from code.SofServers import cl_server,cl_gamespy

if __name__ == '__main__':
    #fetch the data    
    gamespy=cl_gamespy()

    if gamespy.GetIpList() is None:
        #['gamemode', 'violence', 'hostname', 'numplayers', 'maxplayers', 'mapname', 'queryid', 'gametype', 'hostport', 'final']
        
        # raw tableData, in Raw Value Form, Rows Columns
       
        s = gamespy.retServers()
        print(len(s));

