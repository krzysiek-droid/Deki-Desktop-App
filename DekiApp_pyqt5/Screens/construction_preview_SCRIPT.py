import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from Screens import cadViewWidget_SCRIPT as cadviewer
from Screens import pdfViewWidget_SCRIPT as pdfviewer
import db_objects as dbo

import resources_rc

import pathlib


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
        self.subAssemblyListItem.hide()  # subassembly ListItem
        # if self.construct.info['subcontractor'] == 'N/A':
        #     self.subcontratorFrame.hide()
        self.mainConstructQualityInfoContainer.hide()
        # self.rightSidedContent.hide()
        # ---------------------------------------------------------------Button scripting------------------------------
        self.constructMoreInforBtn.clicked.connect(lambda: self.mainConstructQualityInfoContainer.hide()
        if self.mainConstructQualityInfoContainer.isVisible() else self.mainConstructQualityInfoContainer.show())

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
        self.constructTypeLabel.setText(self.construct.info['construct_type'])
        self.qualityNormLabel.setText(self.construct.info['quality_norm'])
        self.qualityClassLabel.setText(self.construct.info['quality_class'])
        self.tolerancesNormLabel.setText(self.construct.info['tolerances_norm'])
        self.tolerancesLevelLabel.setText(self.construct.info['tolerances_level'])
        self.subcontractorLabel.setText(self.construct.info['subcontractor'])
        self.subcontractorContactLabel.setText(self.construct.info['sub_contact'])
        self.showStepModel()
        self.showPdfViewer()

    def showStepModel(self):
        if not self.cadModelViewWidget:
            print(self.construct.stpModelPath)
            self.cadModelViewWidget = cadviewer.CadViewer(self.construct.stpModelPath)
            self.cadModelViewWidget.leftMenuContainer.hide()
            self.cadModelViewWidget.setMinimumSize(650, 350)
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
            print(self.construct.pdfDocsPath)
            self.pdfViewerWidget = pdfviewer.pdfViewerWidget(fr'{self.construct.pdfDocsPath}')
            # Create layout for pdfViewerWidget
            grid = QVBoxLayout()
            grid.addWidget(self.pdfViewerWidget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            # Insert a pdfViewerWidget into docViewer Widget (widget for pdf viewing)
            # self.docsViewerContainer.removeWidget(QLabel)
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
