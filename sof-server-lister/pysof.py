#!/usr/bin/python
# from PyQt5.QtWidgets import QApplication,QTableView,QHeaderView
# from PyQt5.QtCore import QModelIndex,Qt,QItemSelection,QItemSelectionModel,QSortFilterProxyModel
# from PyQt5.QtGui import QFont,QPalette,QColor
import sys,os,inspect
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

# cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
# if cmd_folder not in sys.path:
#     sys.path.insert(0, cmd_folder)

# cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"subfolder")))
# if cmd_subfolder not in sys.path:
#     sys.path.insert(0, cmd_subfolder)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from code.TableModel import MyTableView,MyTableModel,MyProxyModel,RichTextDelegate
from code.SofServers import cl_server,cl_gamespy


#def keyPressEvent(event):


class Main(QMainWindow):
    def __init__(self,servers, parent=None):
        super(Main, self).__init__(parent)
        self.headers = headerData
        self.tableData = tableData
        self.servers = servers
        #Theme
        #['Windows', 'Motif', 'CDE', 'Plastique', 'GTK+', 'Cleanlooks']
        # app.setStyle(QStyleFactory.create("Fusion"))
        
        #widget // view creation - title,font,attribute(remove QThread garbage bug)
        self.tableView = MyTableView(servers,headerData,self)
        tableView = self.tableView
        tableView.setAttribute(Qt.WA_DeleteOnClose)
        tableView.setWindowTitle("Soldier of Fortune Server Listing");
        funt = QFont("comic Sans ms", 12)
        tableView.setFont(funt)

        #tweaks
        tableView.verticalHeader().setVisible(False)
        tableView.horizontalHeader().setVisible(True)
        tableView.setShowGrid(False) 
        tableView.setSortingEnabled(True)
        tableView.setStyleSheet("background-color: #000000;color: #69a197")


        #data model -> proxy model -> viewmodel        
        model = MyTableModel(gamespy.li_cl_servers,tableData, headerData)
        proxyModel=MyProxyModel(tableView)
        proxyModel.setSourceModel(model)
        tableView.setModel(proxyModel)
        viewDelegate=RichTextDelegate(funt,self)
        viewDelegate.setTableView(tableView)
        tableView.setItemDelegate(viewDelegate)

        
        
        #autosize
        horizonHead=tableView.horizontalHeader()
        horizonHead.setSectionResizeMode(QHeaderView.ResizeToContents)
        # horizonHead.setStretchLastSection(True);

        vertHead=tableView.verticalHeader()
        vertHead.setSectionResizeMode(QHeaderView.ResizeToContents)
        # vertHead.setStretchLastSection(True);

        tableView.resizeRowsToContents()
        tableView.resizeColumnsToContents()

        # self.layout().setSizeConstraint(QLayout.SetMinimumSize)
        self.setMinimumSize(
            # margins.left() + margins.right() +
            self.tableView.frameWidth() * 2 +
            vertHead.width() +
            horizonHead.length()
            # self.tableView.style().pixelMetric(QStyle.PM_ScrollBarExtent)+
            # w
            , 
            # margins.top() + margins.bottom() +
            self.tableView.frameWidth() * 2 +
            horizonHead.height() +
            vertHead.length()
            # self.tableView.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        )
        #model.insertColumns(6,1)
        #model.UpdateHeaders(6,'ENTER')


        #fetch pixel of end column to adjust window size
        #neat window size + centered horizontally
        # x = horizonHead.sectionPosition(len(headerData)-1)
        #print len(gamespy.li_cl_servers)
        # y = vertHead.sectionPosition(len(gamespy.li_cl_servers)-1)
        # tableView.resize(x+150,y+150)
        
        # w=vertHead.width()
        # for x in range(0,model.columnCount()):
        #     w+=tableView.columnWidth(x)
        self.setCentralWidget(tableView)
        margins = self.layout().contentsMargins()

        self.resize(
            # margins.left() + margins.right() +
            self.tableView.frameWidth() * 2 +
            vertHead.width() +
            horizonHead.length()
            # self.tableView.style().pixelMetric(QStyle.PM_ScrollBarExtent)+
            # w
            , 
            # margins.top() + margins.bottom() +
            self.tableView.frameWidth() * 2 +
            horizonHead.height() +
            vertHead.length()
            # self.tableView.style().pixelMetric(QStyle.PM_ScrollBarExtent)
            ) #self.height()
        self.move(app.desktop().screen().rect().center() - self.rect().center())
        
        #proxyModel.sort(0)                
        #model.insertRows(1,2)
        #model.removeColumns(1,2)
        #model.insertColumns(4,2)
        #model.removeColumns(4,2)
        """
        selectModel = tableView.selectionModel()

        topLeft = model.index(0,0,QModelIndex())
        bottomRight = model.index(len(tableData0)-1,len(tableData0[0])-1,QModelIndex())
        itemSelect = QItemSelection(topLeft,bottomRight)
        selectModel.select(itemSelect,QItemSelectionModel.Select)


        toggleSelect = QItemSelection()
        toggleSelect.select(topLeft,bottomRight)
        selectModel.select(toggleSelect,QItemSelectionModel.Toggle)

        columnSelect = QItemSelection()
        topLeft = model.index(0,1,QModelIndex())
        bottomRight = model.index(0,2,QModelIndex())
        columnSelect.select(topLeft,bottomRight)
        selectModel.select(columnSelect,QItemSelectionModel.Select | QItemSelectionModel.Columns)

        rowSelect = QItemSelection()
        rowSelect.select(topLeft,bottomRight)
        selectModel.select(rowSelect,QItemSelectionModel.Select | QItemSelectionModel.Rows)
        """

    
if __name__ == '__main__':
    
    #fetch the data    
    gamespy=cl_gamespy()
    app = None
    #If gamespy don't bug
    if gamespy.GetIpList() is None:
        #['gamemode', 'violence', 'hostname', 'numplayers', 'maxplayers', 'mapname', 'queryid', 'gametype', 'hostport', 'final']
        headerData = ["hostname","gametype","map","online"]
        # raw tableData, in Raw Value Form, Rows Columns
        tableData = [ [ server.di_props[headerData[x]]['val'] for x in range(0,len(headerData))] for server in gamespy.li_cl_servers]
        print headerData
        
        app = QApplication(sys.argv)

        main = Main(gamespy.retServers())
        main.show()
    else:
        print "Exiting... Strange Occurence"
        sys.exit()
    sys.exit(app.exec_())
