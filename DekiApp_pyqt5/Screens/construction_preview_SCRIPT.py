import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5 import QtGui
from Screens import resources_rc
import db_objects as dbo

import cadview_script
import pdfView_script


class ConstructPreviewDialog(QDialog):
    def __init__(self, constructNumber):
        super(ConstructPreviewDialog, self).__init__()
        self.pdfViewerWidget = None
        self.cadModelViewWidget = None
        self.constructNumber = constructNumber
        self.construct = dbo.Construction()
        self.construct.load_info(constructNumber)
        loadUi(r'construction_preview_UI.ui', self)

        # ---------------------------------------------------------------Screen loading functions----------------------
        self.constructMoreBtns.hide()
        self.subAssemblyListItem.hide()  # subassembly ListItem
        # self.rightSidedContent.hide()
        # ---------------------------------------------------------------Button scripting------------------------------
        self.constructMoreInforBtn.clicked.connect(lambda:
                                                   self.constructMoreBtns.hide() if self.constructMoreBtns.isVisible()
                                                   else self.constructMoreBtns.show())
        self.addSubassemblyBtn.clicked.connect(lambda: self.add_subassembly())
        # -----------------------------------------------------------------UPDATE INFO---------------------------------
        self.constructPicture.setPixmap(self.construct.picture.scaled(200, 200, 1, 1))
        self.constructNameLabel.setText(self.construct.info['name'])
        self.constructTagLabel.setText(self.construct.info['tag'])
        self.constructNumberLabel.setText(self.construct.info['serial_number'])
        self.constructOwnerLabel.setText(self.construct.info['owner'])
        self.constructMaterialLabel.setText(self.construct.info['material'])
        self.constructLocalizationLabel.setText(self.construct.info['localization'])
        self.constructAdditionalInfoLabel.setText(self.construct.info['additional_info'])

        self.showStepModel()
        self.showPdfViewer()

    def showStepModel(self):
        if not self.cadModelViewWidget:
            self.cadModelViewWidget = cadview_script.CadViewer(self.construct.stpModelPath)
            # Create Layout for cadModelViewWidget
            grid = QVBoxLayout()
            grid.addWidget(self.cadModelViewWidget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            self.cadViewerContainer.setLayout(grid)
            # To start viewing the cadModel it is needed to call the _display member of viewer, and call the
            # method for render and display such as DisplayShape() etc.;   Test() to display sample model
            self.cadModelViewWidget.start_display()
            # if self.validate_info():
            #     self.addConstructionBtn.setEnabled(True)
        else:
            pass
        # TODO: add the script for STEP preview model change

    def showPdfViewer(self):
        if not self.pdfViewerWidget:
            self.pdfViewerWidget = pdfView_script.pdfViewerWidget(self.construct.pdfDocsPath)
            print(type(self.construct.pdfDocsPath))
            # Create layout for pdfViewerWidget
            grid = QVBoxLayout()
            grid.addWidget(self.pdfViewerWidget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            # Insert a pdfViewerWidget into docViewer Widget (widget for pdf viewing)
            self.docsViewerContainer.setLayout(grid)
            # if self.validate_info():
            #     self.addConstructionBtn.setEnabled(True)
        else:
            pass

    def add_subassembly(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = ConstructPreviewDialog(1)
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
