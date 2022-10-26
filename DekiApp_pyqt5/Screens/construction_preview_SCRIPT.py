import logging
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtGui

import db_objects
from Screens import cadViewWidget_SCRIPT as cadviewer
from Screens import pdfViewWidget_SCRIPT as pdfviewer

import db_objects as dbo
import gnrl_database_con as database

import pandas as pd
import resources_rc

import pathlib


class CustomListItem(QWidget):
    def __init__(self, subConstructionID, parentScreen):
        super(CustomListItem, self).__init__()
        uic.loadUi(r'ListItem.ui', self)
        self.subConstructionID = subConstructionID
        # Get access to QMainWindow instance for its member methods, and save its reference as a member variable
        self.mainWindowInstance = None
        self.parentScreen = parentScreen
        for widget in QApplication.topLevelWidgets():
            if widget.objectName() == 'inspectionPlannerWindow':
                self.mainWindowInstance = widget
                break

        if self.mainWindowInstance is not None:
            self.openSubConstructionBtn.clicked.connect(
                lambda: (print(f"opening subConstruction {self.subConstructionID}"),
                         self.changeToSubConstructionScreen()))

    def changeToSubConstructionScreen(self):
        from subConstruction_preview_SCRIPT import SubConstructPreviewScreen
        new_screen = SubConstructPreviewScreen(self.parentScreen.mainConstructionObject, self.subConstructionID)
        self.mainWindowInstance.stackedWidget.changeScreen(self.parentScreen, new_screen, 'Subconstruction Preview')


class ConstructPreviewDialog(QDialog):
    def __init__(self, constructNumber, connected_database=None):
        super(ConstructPreviewDialog, self).__init__()
        # set loggers to print only Warnings during screen changes, w/o it console prints all debug lines,
        # which is annoying
        self.cadModelViewWidget = None
        uic.properties.logger.setLevel(logging.WARNING)
        uic.uiparser.logger.setLevel(logging.WARNING)
        uic.loadUi(r'construction_preview_UI.ui', self)
        self.setObjectName('mainConstructionPreviewScreen')
        self.mainConstructionIdNum = constructNumber
        self.mainConstructionObject = dbo.MainConstruction()
        self.mainConstructionObject.load_info(self.mainConstructionIdNum)
        # open database connection
        self.db = database.Database() if connected_database is None else connected_database
        # ---------------------------------------------------------------Screen loading functions----------------------
        # self.mainConstructQualityInfoContainer.hide()
        self.load_weldList()
        self.load_SubConstructionsList()
        self.showStepModel()
        self.showPdfViewer()
        # ---------------------------------------------------------------Button scripting------------------------------
        # self.constructMoreInforBtn.clicked.connect(lambda: self.mainConstructQualityInfoContainer.hide()
        # if self.mainConstructQualityInfoContainer.isVisible() else self.mainConstructQualityInfoContainer.show()) -> legacy
        from InspectionPlannerScreen_SCRIPT import InspectionPlannerScreen
        self.goBackBtn.clicked.connect(
            lambda: self.parent().changeScreen(self, InspectionPlannerScreen()) if self.parent() is not None else \
                print('no parent'))
        from new_subconstruction_SCRIPT import NewSubconstructionDialog
        self.addSubassemblyBtn.clicked.connect(
            lambda: (self.showDialog(NewSubconstructionDialog(self.mainConstructionObject))))
        self.addWeldBtn.clicked.connect(lambda: self.add_weld())
        # -----------------------------------------------------------------UPDATE INFO---------------------------------
        self.constructPicture.setPixmap(self.mainConstructionObject.picture.scaled(200, 200, 1, 1))
        self.constructNameLabel.setText(self.mainConstructionObject.info['name'])
        self.constructTagLabel.setText(self.mainConstructionObject.info['tag'])
        self.constructNumberLabel.setText(self.mainConstructionObject.info['serial_number'])
        self.constructOwnerLabel.setText(self.mainConstructionObject.info['owner'])
        self.constructMaterialLabel.setText(self.mainConstructionObject.info['material'])
        self.constructLocalizationLabel.setText(self.mainConstructionObject.info['localization'])
        self.constructAdditionalInfoLabel.setText(self.mainConstructionObject.info['additional_info'])
        self.constructTypeLabel.setText(self.mainConstructionObject.info['construct_type'])
        self.qualityNormLabel.setText(self.mainConstructionObject.info['quality_norm'])
        self.qualityClassLabel.setText(self.mainConstructionObject.info['quality_class'])
        self.tolerancesNormLabel.setText(self.mainConstructionObject.info['tolerances_norm'])
        self.tolerancesLevelLabel.setText(self.mainConstructionObject.info['tolerances_level'])
        self.subcontractorLabel.setText(self.mainConstructionObject.info['subcontractor'])
        self.subcontractorContactLabel.setText(self.mainConstructionObject.info['sub_contact'])

        self.cadDocsTab.currentChanged.connect(lambda idx: self.cadModelViewWidget.fitToParent())

    def showStepModel(self):
        # Delete old widget -> for in case CAD model is changed
        for oldWidget in self.cadViewerContainer.findChildren(QWidget):
            oldWidget.deleteLater()
            oldWidget.hide()
            print(f"Step widget -- {oldWidget} -- {oldWidget.objectName()} deleted... OK")
        tmp_layout = QVBoxLayout()
        # create a widget for viewing CAD (CAD canvas widget/object)
        self.cadModelViewWidget = cadviewer.CadViewer(self.mainConstructionObject.stpModelPath)
        tmp_layout.addWidget(self.cadModelViewWidget)
        self.cadViewerContainer.setLayout(tmp_layout)
        # self.cadViewerContainer.setLayout(cadModelViewWidget) --> If cadViewer is a layout
        self.cadModelViewWidget.start_display()

    def showPdfViewer(self):
        pdfViewerWidget = pdfviewer.pdfViewerLayout(fr'{self.mainConstructionObject.pdfDocsPath}',
                                                    parent=self.docsViewerContainer)
        self.docsViewerContainer.setLayout(pdfViewerWidget)

    def add_weld(self):
        pass

    def load_SubConstructionsList(self):
        # Condition required for list refreshment after every call of this function
        if self.subAssembliesListWidget.findChild(QScrollArea) is not None:
            print(f"found scrollArea at: {self.subAssembliesListWidget.findChild(QScrollArea)} --- "
                  f"deleting {self.subAssembliesListWidget.findChild(QScrollArea).objectName()}...")
            self.subAssembliesListWidget.findChild(QScrollArea).deleteLater()
        # Check if scrollArea needs to be refreshed, if its empty load all subs
        # get dataframe with subConstructions belonging to parent mainConstructionObject, by ID
        belonging_subConstructions = self.db.df_from_filteredTable('deki_2022_SubConstructions',
                                                                   'main_construction_id', self.mainConstructionIdNum)
        # get list of subConstruction IDs belonging to parent mainConstructionObject
        subConstructions_IDs = belonging_subConstructions['id'].tolist()
        # iterate throughout subConstruction IDs list and load those subConstructions into the screen
        tmp_scrollArea = QScrollArea()
        tmp_scrollArea.setWidgetResizable(True)
        tmp_scrollWidget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(2)
        if len(subConstructions_IDs) != 0:
            constructionObject = dbo.SubConstruction(parentConstruction=self.mainConstructionObject,
                                                     connected_database=self.mainConstructionObject.db)
            for constructionID in subConstructions_IDs:
                constructionObject.load_info(int(constructionID))
                listItem = CustomListItem(int(constructionID), parentScreen=self)
                listItem.constructionTag.setText(constructionObject.info["tag"])
                listItem.constructionName.setText(constructionObject.info['name'])
                listItem.constructionPicture.setPixmap(constructionObject.picture.scaled(120, 120, 1, 1))
                listItem.seriesSize.setText(constructionObject.info['serial_number'])

                layout.addWidget(listItem, alignment=Qt.AlignTop)
            layout.setAlignment(Qt.AlignTop)
        else:
            label = QLabel()
            label.setText(f'No Subconstructions found in database.')
            label.setStyleSheet('font: 12pt "Calibri";'
                                'background-color: none;')
            layout.addWidget(label, alignment=Qt.AlignCenter)
            layout.setAlignment(Qt.AlignCenter)

        tmp_scrollWidget.setLayout(layout)
        tmp_scrollArea.setWidget(tmp_scrollWidget)
        self.subAssembliesListLayout.addWidget(tmp_scrollArea)

    def load_weldList(self):
        if self.middleContentFrame.findChild(QScrollArea) is not None:
            print(f"found scrollArea at: {self.middleContentFrame.findChild(QScrollArea)} --- Deleting...", end='')
            self.middleContentFrame.findChild(QScrollArea).deleteLater()
            print(f'OK')
        tmp_scrollArea = QScrollArea()
        # Make widgets that goes into ScrollArea to resize to ScrollArea width
        tmp_scrollArea.setWidgetResizable(True)
        tmp_scrollWidget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(2)
        welds_tableName = f"{self.mainConstructionObject.info['tag']}_modelWelds"
        belonging_welds = self.db.table_into_DF(welds_tableName)
        if self.db.is_table(welds_tableName):
            if len(belonging_welds) > 0:
                for weldData in belonging_welds.iterrows():
                    from weldListItem_SCRIPT import WeldListItem
                    weldListItem = WeldListItem(int(weldData[1]["id"]), self.mainConstructionObject)
                    layout.addWidget(weldListItem, alignment=Qt.AlignTop)
                layout.setAlignment(Qt.AlignTop)
            else:
                label = QLabel()
                label.setText(f'No welds found in database.')
                label.setStyleSheet('font: 12pt "Calibri";'
                                    'background-color: none;')
                layout.addWidget(label, alignment=Qt.AlignCenter)
                layout.setAlignment(Qt.AlignCenter)

        tmp_scrollWidget.setLayout(layout)
        tmp_scrollArea.setWidget(tmp_scrollWidget)
        self.middleContentLayout.addWidget(tmp_scrollArea)

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
