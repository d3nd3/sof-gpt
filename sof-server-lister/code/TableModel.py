# from PyQt4.QtGui import QTableView,QColor,QSortFilterProxyModel,QItemDelegate,QTextDocument,QLabel,QBrush,QPushButton,QStyle,QApplication,QMouseEvent,QDialog,QPalette,QWidget,QHelpEvent,QCursor,QToolTip,QPainter
# from PyQt4.QtCore import Qt,QAbstractTableModel,QString,QModelIndex,QVariant,QRect,QEvent,QPoint
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

color = [None] * 32
color[0] = ""
color[1] = '<span style="color:#ffffff;">'
color[2] = '<span style="color:#ff0000;">'
color[3] = '<span style="color:#00ff00;">'
color[4] = '<span style="color:#ffff00;">'
color[5] = '<span style="color:#0000ff;">'
color[6] = '<span style="color:#ff00ff;">'
color[7] = '<span style="color:#00ffff;">'
color[8] = '<span style="color:#202020;">'
color[9] = '<span style="color:#7f7f7f;">'
color[10] = ""
color[11] = '<span style="color:#7f0000;">'
color[12] = '<span style="color:#007f00;">'
color[13] = ""
color[14] = '<span style="color:#7f7f00;">'
color[15] = '<span style="color:#00007f;">'
color[16] = '<span style="color:#564d28;">'
color[17] = '<span style="color:#4c5e36;">'
color[18] = '<span style="color:#376f65;">'
color[19] = '<span style="color:#005572;">'
color[20] = '<span style="color:#54647e;">'
color[21] = '<span style="color:#1e2a63;">'
color[22] = '<span style="color:#471353;">'
color[23] = '<span style="color:#705e61;">'
color[24] = '<span style="color:#980053;">'
color[25] = '<span style="color:#960018;">'
color[26] = '<span style="color:#702d07;">'
color[27] = '<span style="color:#54492a;">'
color[28] = '<span style="color:#61a997;">'
color[29] = '<span style="color:#cb8f39;">'
color[30] = '<span style="color:#cf8316;">'
color[31] = '<span style="color:#ff8020;">'
def replaceColour(onwho):
    return ''.join(c if ord(c) >= 32 else color[ord(c)] for c in onwho)

class MyTableView(QTableView):
    def __init__(self,servers,headers,parent=None):
        QAbstractItemView.__init__(self,parent)
        self.headers = headers
        self.servers = servers

    def sizeHintForRow(self,row):
        # s = QSize()
        # s.setHeight(super(ListWidget,self).sizeHint().height())
        # s.setWidth(self.sizeHintForColumn(0))
        # return s
        fm = self.fontMetrics()
        return fm.height()
    def sizeHintForColumn(self,col):
        fm = self.fontMetrics()
        if col < len(self.headers):
            longest = 0

            for server in self.servers:
                t = server.di_props[self.headers[col]]['plainval']
                # l = fm.boundingRect(t).width()
                # l = fm.size(Qt.AlignLeft, t).width()
                l = fm.width(t)
                if l > longest: #and l != 536
                    lol = server.di_props[self.headers[col]]['plainval']
                    longest = l
            if col == len(self.headers)-1:
                print lol
                print "longest_fm = " + str(longest)
                print "norm len = " + str(len(lol))
            
            return longest + 2#* 0.5#*0.5#*10
        return fm.width("a"*25)
"""
Models store data and communicate to the views that data through signals etc
"""
class MyTableModel(QAbstractTableModel):
	#colors is a list of lists
    def __init__(self, servers,entries = [[]], headers = [],parent = None):
        QAbstractTableModel.__init__(self, parent)
        self.__entries = entries
        self.__headers = headers
        self.__servers = servers

    def UpdateHeaders(self,index,data):
        # self.__headers.insert(index,data)
        pass

    def rowCount(self, parent=None):
        if self.__entries:
            return len(self.__entries)
        return 0

    def columnCount(self, parent=None):
        if self.__entries and self.__entries[0]:
            return len(self.__headers)
        return 0

    def flags(self, index):
        return Qt.NoItemFlags

    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return
        if role == Qt.EditRole:
            return QVariant(QVariant.Invalid)
        if role == Qt.ToolTipRole:
            return QVariant(QVariant.Invalid)
        #this is for the icon next to the data
        """if role == Qt.DecorationRole:
            row = index.row()
            column = index.column()
            value = self.__entries[row][column]
            pixmap = QtGui.QPixmap(26, 26)
            pixmap.fill(value)
            icon = QtGui.QIcon(pixmap)
            return icon"""
		#and this is the main display of data!
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.__entries[row][column]
            if column == 0 :
                return replaceColour(value)#.encode("iso-8859-1")
            return '<span>' + value + "</span>"#.encode("iso-8859-1")

	#this one is for updating data via Edit usually
    def setData(self, index, value, role = Qt.EditRole):       
        return False

	#this is for the name of the columns and rows
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.__headers[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)
        

    def setHeaderData(self, section, orientation, towhat, role = Qt.DisplayRole):
        return True
    def insertRows(self, position, quantity, parent = QModelIndex()):
        position-=1
		#inbetween these function calls because of signalling
        self.beginInsertRows(parent, position, position + quantity-1)
        for i in range(quantity):
            #slip a new list inside the outer list at position
            defaultValues = ["{\\rtf1\\ansi{\\fonttbl\\f0\\fswiss Helvetica;}\\f0\pardThis is some {\\b bold} text.\par}" for i in range(self.columnCount())]
            self.__entries.insert(position, defaultValues)
        self.endInsertRows()
        return True


    def insertColumns(self, position, quantity, parent = QModelIndex()):
		#inbetween these function calls because of signalling
        #print 'position %d and next %d' % (position,position+quantity)
        self.beginInsertColumns(parent, position, position + quantity-1)
        for i in range(quantity):
            print 'added column'
            self.__headers.insert(position,"default")
            #for _all_ rows update their list
            for row in range(self.rowCount()):
                self.__entries[row].insert(position, "")
        self.endInsertColumns()
        return True

    #more literally - delete a sublist
    def removeRows(self,position,quantity,parent=QModelIndex()):        
        self.beginRemoveRows(parent,position,position+quantity-1)
        for i in range(quantity):            
            del self.__entries[position]
        self.endRemoveRows()
    #more literally - delete x elements from __all__ sublists
    def removeColumns(self,position,quantity,parent=QModelIndex()):        
        self.beginRemoveColumns(parent,position,position+quantity-1)
        for row in range(self.rowCount()):
            for i in range(quantity):
                del self.__entries[row][position]
        self.endRemoveColumns()

class MyProxyModel(QSortFilterProxyModel):
    def __init__(self,main,parent=None):
        QSortFilterProxyModel.__init__(self,parent)
        self.main = main
    def lessThan(self,left,right):
        h = self.main.headers
        r = self.sourceModel().data(right)
        l = self.sourceModel().data(left)
        if left.column() == h.index("online"):
            l = self.main.servers[left.row()].di_props['online']['plainval']
            r = self.main.servers[right.row()].di_props['online']['plainval']
            if int(l) < int(r):
                return True
            else:
                return False
        if l < r:
            return True
        else:
            return False


class ROFLlabel(QLabel):
    def __init__(self,Parent=None):
        QLabel.__init__(self,Parent)
        self.__mytt = None
        
    def event(self,e):
        #he = QHelpEvent(QEvent.ToolTip,QPoint(self.pos().x(),self.pos().y()),QPoint(QCursor.pos().x(),QCursor.pos().y()))
        if e is not None:
            if e.type() == QEvent.Enter:
                print "You entered me!"
            elif e.type() == QEvent.Leave:
                print "You left me!"

            elif e.type() == QEvent.ToolTip:
                he = QHelpEvent(e)
                # print '%d' % he.globalY()
                # print 'toooooooltip'
                if self.__mytt is None :
                    x = he.globalX()+20
                    y = he.globalY()
                    self.__mytt = ROFLtooltip(x,y)
                    self.__mytt.setWindowFlags(Qt.ToolTip)                  
                    self.__mytt.resize(64,64)
                    self.__mytt.move(x,y)
                    #self.__mytt.setAttribute(Qt.WA_TranslucentBackground)                    
                    self.__mytt.show()
                else:
                    self.__mytt.show()
                e.accept()
                return True
            elif e.type() == QEvent.MouseMove:

                if self.__mytt is not None :
                    self.__mytt.hide()
                    # layout.removeWidget(self.widget_name)
                    self.__mytt.deleteLater()
                    self.__mytt = None
        return QLabel.event(self,e)                            

class ROFLtooltip(QWidget):
    def __init__(self,posx,posy,Parent=None):
        QToolTip.__init__(self,Parent)
        self.__posx = posx
        self.__posy = posy
        print 'IM ALIVE'
    def paintEvent(self,e):       
        pass
        #print 'HAHA'
        p = QPainter(self)
        p.setBrush(Qt.red)
        #print '%d %d' % (self.__posx,self.__posy)
        r = QRect(self.__posx,self.__posy,64,64)
        p.fillRect(r,QColor(255,255,255,255))
        #p.drawEllipse(r)

class RichTextDelegate(QItemDelegate):
    def __init__(self,funt,Parent=None):
        QItemDelegate.__init__(self,Parent)
        self.parent = Parent
        self.funt = funt
    def setTableView(self,view):
        self.__view = view
    def paint(self,painter,option,index):        
        #return if already has a widget set in that index
        if self.__view.indexWidget(index) is not None:
            return
        h = self.parent.headers
        if index.column() < len(h) :
            label=ROFLlabel()
            #label.setTextFormat(Qt.RichText)
            #label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            #label.setOpenExternalLinks(True)
            label.setText(index.data())
            if index.column() == h.index("map"):
                label.setAlignment(Qt.AlignLeft)
            else:
                label.setAlignment(Qt.AlignHCenter)
            label.setFont(self.funt)
            # label.setStyleSheet("color: #69a197;")

            #label.setToolTip('77.97.106.246')
            self.__view.setIndexWidget(index, label)
        """
        else:
            brown = QColor(212, 140, 95)
            button = QPushButton(QString("View"))
            pal = button.palette()
            pal.setColor(QPalette.Button,QColor(0x08,0x08,0x08))
            pal.setColor(QPalette.ButtonText,QColor(0x69,0xa1,0x97))
            button.setPalette(pal)
            button.setAutoFillBackground(True)
            self.__view.setIndexWidget(index, button)
        """
    def editorEvent(self,event,model, option, index):
        """
        if( event.type() == QEvent.MouseButtonRelease ):
            lol = sizeHintForRow(0)
            print '%d' % lol
            e = QMouseEvent(event)
            clickX = e.x();
            clickY = e.y();
            #getting the rect of the cell
            r = option.rect
            #the X coordinate
            x = r.left() + r.width() - 30
            #the Y coordinate
            y = r.top()
            #button width
            w = 30
            #button height
            h = 30

            if clickX > x and clickX < x + w :
                if clickY > y and clickY < y + h:              
                    d = QDialog()
                    d.setGeometry(0,0,100,100)
                    d.show()
                    return True
        """
        return False
"""
0.005423 0.008626 0.008858 0.010032 0.010169 0.010529 0.010695 0.010821 0.011341
upperbound = 0.012200
lowerboud =  0.007800
"""



"""
Models store data and communicate to the views that data through signals etc
"""
class SubTableModel(QAbstractTableModel):
    
	#colors is a list of lists
    def __init__(self, server,entries = [[]], headers = [],parent = None):
        QAbstractTableModel.__init__(self, parent)
        self.__entries = entries
        self.__server = server
        self.__headers = headers


    def rowCount(self, parent=None):
        if self.__entries:
            return len(self.__entries)
        return 0
    def columnCount(self, parent=None):
        if self.__entries and self.__entries[0]:
            return len(self.__entries[0])
        return 0
    def flags(self, index):
        return Qt.NoItemFlags | Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return
        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft
		#edit role is for when data is edited, return initial
        
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            return self.__entries[row][column]
        
        #when hover over elements
        if role == Qt.ToolTipRole:
            row = index.row()
            return self.__server.di_props["hostname"]['val']
        #this is for the icon next to the data
        """if role == QtCore.Qt.DecorationRole:
            row = index.row()
            column = index.column()
            value = self.__entries[row][column]
            pixmap = QtGui.QPixmap(26, 26)
            pixmap.fill(value)
            icon = QtGui.QIcon(pixmap)
            return icon"""
		#and this is the main display of data!
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.__entries[row][column]
            if column == 0 :
                return replaceColour(value)#.encode('iso-8859-1')
            return '<span style="color:#ffffff;">' + DEFAULT + value + "</span>"#.encode('iso-8859-1')
            #return QVariant(value)
            #return QString(value).toLatin1 # unicode(value,'iso-8859-1'

	#this one is for updating data via Edit usually
    def setData(self, index, value, role = Qt.EditRole):
        
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            color = QtGui.QColor(value)
      		#verification on input
            #if color.isValid():
            self.__entries[row][column] = color
            self.dataChanged.emit(index, index)
            return True
        
        return False

	#this is for the name of the columns and rows
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self.__headers):
                    return self.__headers[section]
                else:
                    return "not implemented"
			#vertical
            else:
                return QString("Server %1").arg(section+1)

    def insertRows(self, position, quantity, parent = QModelIndex()):
        position-=1
		#inbetween these function calls because of signalling
        self.beginInsertRows(parent, position, position + quantity)
        for i in range(quantity):
            #slip a new list inside the outer list at position
            defaultValues = ["{\\rtf1\\ansi{\\fonttbl\\f0\\fswiss Helvetica;}\\f0\pardThis is some {\\b bold} text.\par}" for i in range(self.columnCount())]
            self.__entries.insert(position, defaultValues)
        self.endInsertRows()
        return True


    def insertColumns(self, position, quantity, parent = QModelIndex()):
        position-=1
		#inbetween these function calls because of signalling
        self.beginInsertColumns(parent, position, position + quantity)
        for i in range(quantity):
            #for _all_ rows update their list
            for row in range(self.rowCount()):
                self.__entries[row].insert(position, "lol")
        self.endInsertColumns()
        return True

    #more literally - delete a sublist
    def removeRows(self,position,quantity,parent=QModelIndex()):
        position-=1
        self.beginRemoveRows(parent,position,position+quantity)
        for i in range(quantity):            
            del self.__entries[position]
        self.endRemoveRows()
    #more literally - delete x elements from __all__ sublists
    def removeColumns(self,position,quantity,parent=QModelIndex()):
        position-=1
        self.beginRemoveColumns(parent,position,position+quantity)
        for row in range(self.rowCount()):
            for i in range(quantity):
                del self.__entries[row][position]
        self.endRemoveColumns()

