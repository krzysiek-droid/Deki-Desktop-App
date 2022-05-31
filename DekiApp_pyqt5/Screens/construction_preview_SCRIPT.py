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
        self.construction = dbo.Construction()
        self.construction.load_info(constructNumber)
        loadUi(r'construction_preview_UI.ui', self)

        # ---------------------------------------------------------------Screen loading functions----------------------
        self.subAssemblyListItem.hide()  # subassembly ListItem)
        self.mainConstructQualityInfoContainer.hide()
        # ---------------------------------------------------------------Button scripting------------------------------
        self.constructMoreInforBtn.clicked.connect(lambda: self.mainConstructQualityInfoContainer.hide()
                if self.mainConstructQualityInfoContainer.isVisible() else self.mainConstructQualityInfoContainer.show())

        self.addSubassemblyBtn.clicked.connect(lambda: self.add_subassembly())
        # -----------------------------------------------------------------UPDATE INFO---------------------------------
        self.constructPicture.setPixmap(self.construction.picture.scaled(200, 200, 1, 1))
        self.constructNameLabel.setText(self.construction.info['name'])
        self.constructTagLabel.setText(self.construction.info['tag'])
        self.constructNumberLabel.setText(self.construction.info['serial_number'])
        self.constructOwnerLabel.setText(self.construction.info['owner'])
        self.constructMaterialLabel.setText(self.construction.info['material'])
        self.constructLocalizationLabel.setText(self.construction.info['localization'])
        self.constructAdditionalInfoLabel.setText(self.construction.info['additional_info'])
        self.constructTypeLabel.setText(self.construction.info['construct_type'])
        self.qualityNormLabel.setText(self.construction.info['quality_norm'])
        self.qualityClassLabel.setText(self.construction.info['quality_class'])
        self.tolerancesNormLabel.setText(self.construction.info['tolerances_norm'])
        self.tolerancesLevelLabel.setText(self.construction.info['tolerances_level'])
        self.subcontractorLabel.setText(self.construction.info['subcontractor'])
        self.subcontractorContactLabel.setText(self.construction.info['sub_contact'])
        self.showStepModel()
        self.showPdfViewer()

    def showStepModel(self):
        if not self.cadModelViewWidget:
            print(self.construction.stpModelPath)
            # create a widget for viewing CAD (CAD viewer widget/object)
            self.cadModelViewWidget = cadviewer.CadViewer(self.construction.stpModelPath)
            self.cadModelViewWidget.leftMenuContainer.hide()

            # Create Layout for cadModelViewWidget
            grid = QVBoxLayout()
            grid.addWidget(self.cadModelViewWidget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)

            self.cadViewerContainer.setLayout(grid)
            self.cadModelViewWidget.fitViewer()
            self.cadModelViewWidget.start_display()
        else:
            pass

    def showPdfViewer(self):
        if not self.pdfViewerWidget:
            print(self.construction.pdfDocsPath)
            self.pdfViewerWidget = pdfviewer.pdfViewerWidget(fr'{self.construction.pdfDocsPath}')
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
