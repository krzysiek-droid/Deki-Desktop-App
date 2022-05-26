import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from Screens import cadViewWidget_SCRIPT as cadviewer
from Screens import pdfViewWidget_SCRIPT as pdfviewer
import db_objects as dbo

import resources_rc

import pathlib


class CustomListItem(QWidget):
    def __init__(self):
        super(CustomListItem, self).__init__()
        loadUi(r'ListItem.ui', self)
        print(f'Custom list item added to {self.parent()}')


class InspectionPlanningMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(r'Inspection_Planning_MW.ui', self)

        listItems = [CustomListItem() for x in range(10)]

        wid = QWidget()
        scrollLayoutWidget = QVBoxLayout()
        for listItem in listItems:
            scrollLayoutWidget.addWidget(listItem)
        self.scrollAreaWidgetContents.setLayout(scrollLayoutWidget)
        wid.setLayout(scrollLayoutWidget)
        self.scrollArea.setWidget(wid)



if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = InspectionPlanningMainWindow()
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
