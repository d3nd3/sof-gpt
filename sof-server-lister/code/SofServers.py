import socket
headerlookup = {
    "numplayers" : "online",
    "mapname" : "map"
}
class cl_server():
    di_props=None
    def __init__(self,addr,port):
        self.tu_addr=(addr,port)
    def QueryInfo(self,sock):
        sock.sendto(b"\\info\\",self.tu_addr)
        print(f"Attempting : {self.tu_addr}")
        try:
            data=sock.recv(1400)
            # print(data)
            li_data=data.split(b'\\')
            # print(li_data)
            # print(len(li_data))
            if data[0] == ord(b'\\'):
                li_data = li_data[1:]
                # print("Ye nwo legnth is " + ("odd" if len(li_data) % 2 != 0 else "even"))

            self.di_props={ headerlookup[li_data[i]] if headerlookup.get(li_data[i]) else li_data[i].decode('iso-8859-1')  : {"val":li_data[i+1]} for i in range(0, len(li_data), 2) }# -8 query/final/violence/gamemode
            
            for key,val in self.di_props.items():
                self.di_props[key]['val'] = self.di_props[key]['val'].decode('iso-8859-1') 
                self.di_props[key]['plainval'] = self.getPlainVal(self.di_props[key]['val'])
            # print(self.di_props['hostname']['plainval'].strip("\x00\x20"))
            # print("port is %s" % self.tu_addr[1])

        except socket.timeout:
            print(f"{self.tu_addr} Server timed out!")
            return 1

    def getPlainVal(self,in_str):
        out_str = ''.join(c for c in in_str if ord(c) >= 32)
        # print(":".join("{:02x}".format(ord(c)) for c in in_str) )   
        # print(":".join("{:02x}".format(ord(c)) for c in out_str))
        return out_str

class cl_gamespy():
    def __init__(self):
        self.HOST = 'sof1master.megalag.org'
        self.PORT = 28900       
        self.li_cl_servers=[]

    def retServers(self):
        return self.li_cl_servers
    def GetIpList(self):
        filt=''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        print("STEP 1 : CONNECT TO MASTER");
        s.connect((self.HOST, self.PORT))
        data = s.recv(1400)
        print("STEP 2 : RECEIVE A KEY FROM MASTER")
        key_secure = self.ExtractKey(data)
        key_secure = key_secure[:-1]
        # print(key_secure)
        key_valid = self.ValidateKey('iVn3a3',key_secure)
        print("STEP 3 : HASH THE KEY WITH FIXED KEY")
        #print('valid key is : '+key_valid)
        print(key_valid)
        print("STEP 4 : SEND HASH ALONG WITH GAMENAME")
        pkt_valid = b'\\gamename\\sofretail\\gamever\\1.6\\location\\0\\validate\\'+key_valid + b'\\final\\\\queryid\\1.1\\'
        s.sendall(pkt_valid)
        # data = s.recv(2048)
        s.sendall(b"\\list\\cmp\\gamename\\sofretail\\final\\")
        print("STEP 5 : ALSO SEND LIST CMP")
        

        try:
            data = b""
            while True:
                r = s.recv(1400)
                if len(r) == 0:
                    break
                data = data + r
            
        except socket.timeout:
            print("GameSpy timed out!")

        print("STEP 6: RECEIVE THE DATA")
        print(data)
        print(f"Length before remove 7 == {len(data)}")
        data = data[:-7] # \final\ removed
        print(f"Length after remove 7 == {len(data)}")
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        
        print(len(data))
        i=0   
        while i < len(data):
            self.li_cl_servers.append(cl_server(str(data[i])+'.'+str(data[i+1])+'.'+str(data[i+2])+'.'+str(data[i+3]),data[i+4]*256+data[i+5]))
            print(f"i is : {i+5}")
            i+=6;
        self.li_cl_servers=[x for x in self.li_cl_servers if x.QueryInfo(s) is None]
        #print('%d servers found' % len(self.li_cl_servers)
        s.close()
    def ExtractKey(self,data):
        key=data[-7:]
        return key
    def AddChar(self,x):
        if x<26:
            return chr(x+65).encode('ascii')
        elif x<52:
            return chr(x+71).encode('ascii')
        elif x<62:
            return chr(x-4).encode('ascii')
        elif x==62:
            return b'+'
        elif x==63:
            return b'/'
    def ValidateKey(self,handoff,in_key):
        handofflen=len(handoff)
        in_keylen=len(in_key)
        a=b=c=d= 0
        table=[]    
        for i in range(0,256):
            table.append(i)
        if handofflen>6:
            print("invalid handoff\n")
            sys.exit()
        for i in range(0,256):
            a=(a+table[i]+ord(handoff[i%len(handoff)]))&255
            b=table[a]
            table[a]=table[i]
            table[i]=b
        a=0
        key=[]
        for i in range(0,in_keylen):
            key.append(in_key[i])
            a=(a+key[i]+1)&255
            b=table[a]
            c=(c+b)&255
            d=table[c]
            table[c]=b
            table[a]=d
            key[i]^=table[(b+d)&255]
        in_keylen/=3
        i=0
        out_key=b''
        # indexing a bytes array becomes an int
        while in_keylen>0:
            in_keylen-=1
            b=key[i]
            i+=1
            d=key[i]
            i+=1
            out_key+=self.AddChar(b>>2)
            out_key+=self.AddChar(((b&3)<<4)|(d>>4))
            b=key[i]
            i+=1
            out_key+=self.AddChar(((d&15)<<2)|(b>>6))
            out_key+=self.AddChar(b&63)
        return out_key
