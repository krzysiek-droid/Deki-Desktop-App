import logging
import sys

from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import *
from PyQt5 import uic

import db_objects
from Screens import cadViewWidget_SCRIPT as cadviewer
from Screens import pdfViewWidget_SCRIPT as pdfviewer
import db_objects as dbo
import gnrl_database_con as database

import pandas as pd
import resources_rc

import pathlib


class CustomListItem(QWidget):
    def __init__(self, subConstructionID):
        super(CustomListItem, self).__init__()
        uic.loadUi(r'ListItem.ui', self)
        self.subConstructionID = subConstructionID
        # Get access to QMainWindow instance for its member methods, and save its reference as a member variable
        self.mainWindowInstance = None
        for widget in QApplication.topLevelWidgets():
            if widget.objectName() == 'inspectionPlannerScreen':
                self.mainWindowInstance = widget


class ConstructPreviewDialog(QDialog):
    def __init__(self, constructNumber, connected_database=None):
        super(ConstructPreviewDialog, self).__init__()
        # set loggers to print only Warnings during screen changes, w/o it prints all debug lines, which is annoying
        uic.properties.logger.setLevel(logging.WARNING)
        uic.uiparser.logger.setLevel(logging.WARNING)
        uic.loadUi(r'construction_preview_UI.ui', self)
        self.pdfViewerWidget = None
        self.cadModelViewWidget = None
        self.constructNumber = constructNumber
        self.construction = dbo.MainConstruction()
        self.construction.load_info(constructNumber)
        # open database connection
        self.db = database.Database() if connected_database is None else connected_database
        # attributes for screen (scrollArea) reloading purposes
        self.scrolledContentWidget = None
        self.scrolledContentLayout = None
        # ---------------------------------------------------------------Screen loading functions----------------------
        self.mainConstructQualityInfoContainer.hide()
        self.load_weldList()
        self.load_SubConstructionsList()
        # ---------------------------------------------------------------Button scripting------------------------------
        self.constructMoreInforBtn.clicked.connect(lambda: self.mainConstructQualityInfoContainer.hide()
        if self.mainConstructQualityInfoContainer.isVisible() else self.mainConstructQualityInfoContainer.show())
        self.addSubassemblyBtn.clicked.connect(lambda: self.add_subassembly())
        import InspectionPlannerScreen_SCRIPT
        self.goBackBtn.clicked.connect(lambda: self.parent().changeScreen(self,
                                                                          InspectionPlannerScreen_SCRIPT.InspectionPlannerScreen()) if self.parent() is not None else print(
            'no parent'))
        import new_subconstruction_SCRIPT
        self.addSubassemblyBtn.clicked.connect(
            lambda: (self.showDialog(new_subconstruction_SCRIPT.NewSubconstructionDialog(self.construction))))

        self.editConstructBtn.clicked.connect(lambda: self.refresh_subConstructionList())
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
            # create a widget for viewing CAD (CAD canvas widget/object)
            self.cadModelViewWidget = cadviewer.CadViewer(self.construction.stpModelPath,
                                                          viewport_width=self.cadViewerContainer.size().width(),
                                                          viewport_height=self.cadViewerContainer.size().height())
            # Create Layout for cadModelViewWidget
            grid = QVBoxLayout()
            grid.addWidget(self.cadModelViewWidget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            self.cadViewerContainer.setLayout(grid)
            self.cadModelViewWidget.start_display()
        else:
            pass

    def showPdfViewer(self):
        if not self.pdfViewerWidget:
            self.pdfViewerWidget = pdfviewer.pdfViewerWidget(fr'{self.construction.pdfDocsPath}',
                                                             parent=self.docsViewerContainer)
            # Create layout for pdfViewerWidget
            grid = QVBoxLayout()
            grid.addWidget(self.pdfViewerWidget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            # Insert a pdfViewerWidget into docViewer Widget (widget for pdf viewing)
            # self.docsViewerContainer.removeWidget(QLabel)
            self.docsViewerContainer.setLayout(grid)
        else:
            pass

    def add_subassembly(self):
        pass

    def load_SubConstructionsList(self):
        # Check if scrollArea needs to be refreshed, if its empty load all subs
        # get dataframe with subConstructions belonging to parent construction, by ID
        belonging_subConstructions = pd.merge(self.db.df_from_filteredTable('deki_2022_SubConstructions',
                                               'main_construction_id', self.constructNumber),
                                              self.db.df_from_filteredTable('deki_2022_SubConstructions',
                                               'parent_construction_id', self.constructNumber), how='outer')
        # get list of subConstruction IDs belonging to parent construction
        subConstructions_IDs = belonging_subConstructions['id']
        # iterate throughout subConstruction IDs list and load those subConstructions into the screen
        self.scrolledContentWidget = QWidget()
        self.scrolledContentWidget.setObjectName('scrolledContentWidget')
        self.scrolledContentLayout = QVBoxLayout()
        self.scrolledContentLayout.setSpacing(1)
        if len(subConstructions_IDs) != 0:
            constructionObject = dbo.SubConstruction(parentConstruction=self.construction)
            for constructionID in subConstructions_IDs:
                constructionObject.load_info(int(constructionID))
                listItem = CustomListItem(int(constructionID))
                listItem.constructionTag.setText(constructionObject.info["tag"])
                listItem.constructionName.setText(constructionObject.info['name'])
                listItem.constructionPicture.setPixmap(constructionObject.picture.scaled(120, 120, 1, 1))
                listItem.seriesSize.setText(constructionObject.info['serial_number'])
                self.scrolledContentLayout.addWidget(listItem, alignment=Qt.AlignTop)
            self.scrolledContentWidget.setLayout(self.scrolledContentLayout)
            self.scrolledContentLayout.setAlignment(Qt.AlignTop)
            self.scrollArea.setWidget(self.scrolledContentWidget)
        else:
            print(f"No subConstructions to be loaded. ---- subConstructions Ids: {subConstructions_IDs}")

    def load_weldList(self):
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignTop)
        welds_tableName = f"{self.construction.info['tag']}_modelWelds"
        if self.db.is_table(welds_tableName):
            for weld in range(self.db.check_records_number(welds_tableName)):
                print(f'Loading weld id {weld} into {self.weldListWidgetContent.objectName()}')
                from weldListItem_SCRIPT import WeldListItem
                layout.addWidget(WeldListItem(weld + 1, self.construction), alignment=Qt.AlignTop)
        layout.setAlignment(Qt.AlignTop)
        self.weldListWidgetContent.setLayout(layout)

    def refresh_subConstructionList(self):
        self.scrolledContentWidget.deleteLater()
        self.load_SubConstructionsList()

    def showDialog(self, dialog):
        dialog.show()
        dialog.closeEvent = lambda event: (
            self.refresh_subConstructionList())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = ConstructPreviewDialog(1)
    mainWindow.showMaximized()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
