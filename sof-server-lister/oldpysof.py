#!/usr/bin/python
from PyQt4.QtGui import QApplication,QTableView,QItemSelection,QItemSelectionModel,QHeaderView,QSortFilterProxyModel,QFont
from PyQt4.QtCore import QModelIndex,Qt
import sys
from code.TableModel import MyTableModel,MyProxyModel,RichTextDelegate
from code.SofServers import cl_server,cl_gamespy

def sizeHint(data):
    return 8
#def keyPressEvent(event):
    
if __name__ == '__main__':

    #fetch the data    
    gamespy=cl_gamespy()
    app = None
    #If gamespy don't bug
    if gamespy.GetIpList() is None:
        #create the table data
        tableData = [ [ value for key,value in server.di_props.iteritems()] for server in gamespy.li_cl_servers]
        headerData = [key for key in gamespy.li_cl_servers[0].di_props]
        app = QApplication(sys.argv)
        #Theme
        #['Windows', 'Motif', 'CDE', 'Plastique', 'GTK+', 'Cleanlooks']
        style = app.setStyle("GTK+")
        app.setPalette(style.standardPalette())
        
        #widget // view creation - title,font,attribute(remove QThread garbage bug)
        tableView = QTableView()
        tableView.setAttribute(Qt.WA_DeleteOnClose)
        tableView.setWindowTitle("Soldier of Fortune Server Listing");
        tableView.setFont(QFont("Courier New", 8))

        #tweaks
        tableView.verticalHeader().setVisible(False)
        tableView.setShowGrid(False) 
        tableView.setSortingEnabled(True)

        #virtual function detour - force row height
        tableView.sizeHintForRow = sizeHint

        #data model -> proxy model -> viewmodel        
        model = MyTableModel(gamespy.li_cl_servers,tableData, headerData)
        proxyModel=MyProxyModel()
        proxyModel.setSourceModel(model)
        tableView.setModel(proxyModel)
        viewDelegate=RichTextDelegate()
        viewDelegate.setTableView(tableView)
        tableView.setItemDelegate(viewDelegate)

        #tableView.resizeRowsToContents()
        #tableView.resizeColumnsToContents()
        
        #autosize
        horizonHead=tableView.horizontalHeader()
        horizonHead.setResizeMode(QHeaderView.ResizeToContents)
        horizonHead.setStretchLastSection(True);

        #fetch pixel of end column to adjust window size

        #neat window size + centered horizontally
        x = horizonHead.sectionPosition(5)
        tableView.resize(x+80,tableView.maximumHeight())
        tableView.move(app.desktop().screen().rect().center() - tableView.rect().center())
        tableView.show()
        
        proxyModel.sort(0)                
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
    else:
        print "Exiting... Strange Occurence"
        sys.exit()
    sys.exit(app.exec_())
