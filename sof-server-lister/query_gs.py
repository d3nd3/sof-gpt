#!/usr/bin/python
# -*- coding: utf-8 -*-
# Echo client program
import socket
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class MyWindow(QMainWindow):
    
    def __init__(self,servers):
        super(MyWindow, self).__init__()
        
        self.initUI(servers)
        
    def initUI(self,servers):               
        self.lbl = QLabel("Ubuntu",self)

        combo = QComboBox(self)


        for server in servers:
            # item=QStandardItem()            
            combo.setStyleSheet('QComboBox {color: blue}')
            combo.addItem(server.di_props['hostname'])
            #print server.di_props['hostname']
        #combo.addItem("Ubuntu")
        #combo.addItem("Ubuntu2")
        #combo.addItem("Ubuntu3")
        combo.move(50, 50)
        self.lbl.move(50, 150)

        combo.activated[str].connect(self.onActivated)        
         
        self.resize(800, 200)
        self.center()
        self.setWindowTitle('SoF Multi-Tool by d3nd3')
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    def onActivated(self, text):
      
        self.lbl.setText(text)
        self.lbl.adjustSize()  


def main(servers):
    app = QApplication([])
    ex = MyWindow(servers)
    sys.exit(app.exec_())

class cl_server():
    def __init__(self,addr,port):
        self.tu_addr=(addr,port)
    def QueryInfo(self,sock):
        sock.sendto("\\info\\",self.tu_addr)
        data=sock.recv(2048)
        li_data=data.split('\\')
        self.di_props={li_data[i]:li_data[i+1] for i in range(1, len(li_data)-2, 2)}
        print self.di_props
       

def ExtractKey(data):
    print data
    key=data[-6:]
    return key
def AddChar(x):
    if x<26:
        return chr(x+65)
    elif x<52:
        return chr(x+71)
    elif x<62:
        return chr(x-4)
    elif x==62:
        return '+'
    elif x==63:
        return '/'
def ValidateKey(handoff,in_key):
    handofflen=len(handoff)
    in_keylen=len(in_key)
    a=b=c=d= 0
    table=[]    
    for i in range(0,256):
        table.append(i)
    if handofflen>6:
        print "invalid handoff\n"
        sys.exit()
    for i in range(0,256):
        a=(a+table[i]+ord(handoff[i%len(handoff)]))&255
        b=table[a]
        table[a]=table[i]
        table[i]=b
    a=0
    key=[]
    for i in range(0,in_keylen):
        key.append(ord(in_key[i]))
        a=(a+key[i]+1)&255
        b=table[a]
        c=(c+b)&255
        d=table[c]
        table[c]=b
        table[a]=d
        key[i]^=table[(b+d)&255]
    in_keylen/=3
    i=0
    out_key=''
    while in_keylen>0:
        in_keylen-=1
        b=key[i]
        i+=1
        d=key[i]
        i+=1
        out_key+=AddChar(b>>2)
        out_key+=AddChar(((b&3)<<4)|(d>>4))
        b=key[i]
        i+=1
        out_key+=AddChar(((d&15)<<2)|(b>>6))
        out_key+=AddChar(b&63)
    return out_key
HOST = 'sof1master.megalag.org'    # The remote host
PORT = 28900              # The same port as used by the server
filt=''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
data = s.recv(1024)
print 'data is %r' % data
key_secure = ExtractKey(data)
print 'secure key is : %r'% key_secure
key_valid = ValidateKey('iVn3a3',key_secure)
print 'valid key is : '+key_valid
pkt_valid = '\\gamename\\sofretail\\gamever\\1.6\\location\\0\\validate\\'+key_valid +'\\final\\\\queryid\\1.1\\'
s.sendall(pkt_valid)
# data = s.recv(2048)
s.sendall("\\list\\cmp\\gamename\\sofretail\\final\\")
# data = s.recv(1024)
# data = data + s.recv(1024)

data = ""
while True:
    r = s.recv(1024)
    if len(r) == 0:
        break
    data = data + r
data = data[:-7]

s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print 'data is %s' % data
li_cl_servers=[]
if len(data)%6 ==0:
    i=0   
    while i < len(data):
        li_cl_servers.append(cl_server(str(ord(data[i]))+'.'+str(ord(data[i+1]))+'.'+str(ord(data[i+2]))+'.'+str(ord(data[i+3])),ord(data[i+4])*256+ord(data[i+5])))
        i+=6;
    x=0
    for server in li_cl_servers:
        print "%s : %d" % server.tu_addr
        server.QueryInfo(s)
    print '%d servers found' % len(li_cl_servers)
else:
    print 'no servers found'

if __name__ == '__main__':
    main(li_cl_servers)
