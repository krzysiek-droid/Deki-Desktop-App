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
from pandas import DataFrame

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
        self.openSubConstructionBtn.clicked.connect(lambda: print(f'No parentScreen detected.'))
        for widget in QApplication.topLevelWidgets():
            if widget.objectName() == 'inspectionPlannerWindow':
                self.mainWindowInstance = widget
                self.openSubConstructionBtn.clicked.connect(lambda: self.mainWindowInstance.changeScreen())
                break


class SubConstructPreviewScreen(QDialog):
    def __init__(self, parentConstruction, subConstructionID, connected_database=None):
        super(SubConstructPreviewScreen, self).__init__()
        # set loggers to print only Warnings during screen changes, w/o it prints all debug lines, which is annoying
        uic.properties.logger.setLevel(logging.WARNING)
        uic.uiparser.logger.setLevel(logging.WARNING)
        uic.loadUi(r'subconstruction_preview_UI.ui', self)
        self.setObjectName('subConstructPreviewScreen')
        self.constructNumber = subConstructionID
        self.pdfViewerWidget = None
        self.cadModelViewWidget = None
        self.parentConstructionObject = parentConstruction
        self.mainConstructionObject = parentConstruction.mainConstruction
        self.db = parentConstruction.db if parentConstruction is not None else connected_database
        self.subConstructionObject = dbo.SubConstruction(parentConstruction, connected_database=self.db)
        self.subConstructionObject.load_info(subConstructionID)
        # open database connection
        # attributes for screen (scrollArea) reloading purposes
        self.scrolledContentWidget = None
        self.scrolledContentLayout = None
        # ---------------------------------------------------------------Screen loading functions----------------------
        self.qualityMoreInfoFrame.hide()
        self.subConstructContractorFrame.hide()
        self.showParentInfoBtn.hide()
        self.hideParentInfoBtn.hide()
        self.update_parentConstructionInfo()
        self.update_subConstructionInfo()
        self.load_SubConstructionsList()
        self.load_weldList()
        # ---------------------------------------------------------------Button scripting------------------------------
        self.qualityMoreBtn.clicked.connect(
            lambda: self.qualityMoreInfoFrame.show() if not self.qualityMoreInfoFrame.isVisible() else
            self.qualityMoreInfoFrame.hide())
        self.showParentInfoBtn.clicked.connect(lambda: self.leftSidedContent.show())
        self.hideParentInfoBtn.clicked.connect(lambda: self.leftSidedContent.hide())
        from new_weld_SCRIPT import NewWeldDialog
        self.addWeldBtn.clicked.connect(
            lambda: self.showDialog(NewWeldDialog(self.subConstructionObject), self.load_weldList))
        from new_subconstruction_SCRIPT import NewSubconstructionDialog
        self.addSubConstructionBtn.clicked.connect(
            lambda: self.showDialog(NewSubconstructionDialog(self.subConstructionObject),
                                    self.load_SubConstructionsList)
        )
        self.cadDocsTab.currentChanged.connect(lambda idx: self.cadModelViewWidget.fitToParent())

        # -----------------------------------------------------------------UPDATE INFO---------------------------------

        self.cadDocsTab.setCurrentIndex(0)

    def showStepModel(self, construction):
        # Delete old widget -> for in case CAD model is changed
        for oldWidget in self.cadViewerContainer.findChildren(QWidget):
            oldWidget.deleteLater()
            oldWidget.hide()
            print(f"Step widget -- {oldWidget} -- {oldWidget.objectName()} deleted... OK")
        tmp_layout = QVBoxLayout()
        # create a widget for viewing CAD (CAD canvas widget/object)
        self.cadModelViewWidget = cadviewer.CadViewer(construction.stpModelPath)
        tmp_layout.addWidget(self.cadModelViewWidget)
        self.cadViewerContainer.setLayout(tmp_layout)
        # self.cadViewerContainer.setLayout(cadModelViewWidget) --> If cadViewer is a layout
        self.cadModelViewWidget.start_display()

    def showPdfViewer(self, construction):

        self.pdfViewerWidget = pdfviewer.pdfViewerLayout(fr'{construction.pdfDocsPath}',
                                                         parent=self.docsViewerContainer)
        self.docsViewerContainer.setLayout(self.pdfViewerWidget)

    def update_parentConstructionInfo(self):
        self.constructPicture.setPixmap(
            self.parentConstructionObject.picture.scaledToHeight(200, mode=Qt.SmoothTransformation))
        self.constructNameLbl.setText(self.parentConstructionObject.info['name'])
        self.constructTagLbl.setText(self.parentConstructionObject.info['tag'])
        self.constructLocalizationLbl.setText(self.parentConstructionObject.info['localization'])
        self.constructOwnerLbl.setText(self.parentConstructionObject.info['owner'])
        self.constructMaterialLbl.setText(self.parentConstructionObject.info['material'])
        self.constructNumberLbl.setText(self.parentConstructionObject.info['serial_number'])
        self.constructAdditionalInfoLbl.setText(self.parentConstructionObject.info['additional_info'])
        self.qualityNormLbl.setText(self.parentConstructionObject.info['quality_norm'])
        self.qualityClassLbl.setText(self.parentConstructionObject.info['quality_class'])
        self.tolerancesNormLbl.setText(self.parentConstructionObject.info['tolerances_norm'])
        self.tolerancesLevelLbl.setText(self.parentConstructionObject.info['tolerances_level'])
        if self.parentConstructionObject.info['subcontractor'] == 'N/A':
            self.mainConstrucContractorFrame.hide()
        else:
            self.mainConstructContractorNameLbl.setText(self.parentConstructionObject.info['subcontractor'])
            self.mainConstructContractorContactLbl.setText(self.parentConstructionObject.info['sub_contact'])

    def update_subConstructionInfo(self):
        self.subConstructionPictureLbl.setPixmap(
            self.subConstructionObject.picture.scaledToHeight(200, mode=Qt.SmoothTransformation))
        self.showStepModel(self.subConstructionObject)
        self.showPdfViewer(self.subConstructionObject)
        self.subConstructNameLbl.setText(self.subConstructionObject.info['name'])
        self.subConstructAdditionalInfoLbl.setText(self.subConstructionObject.info['additional_info'])
        self.subConstructSerialLbl.setText(self.subConstructionObject.info['serial_number'])
        self.subConstructOwnerLbl.setText(self.subConstructionObject.info['owner'])
        self.subConstructTypeLbl.setText(self.subConstructionObject.info['construct_type'])
        self.subConstructTagLbl.setText(self.subConstructionObject.info['tag'])
        self.subConstructTolerancesNormLbl.setText(self.subConstructionObject.info['tolerances_norm'])
        self.subConstructQualityNormLbl.setText(self.subConstructionObject.info['quality_norm'])
        self.subConstructMaterialLbl.setText(self.subConstructionObject.info['material'])
        self.subConstructTolerancesLevelLbl.setText(self.subConstructionObject.info['tolerances_level'])
        self.subConstructLocalizationLbl.setText(self.subConstructionObject.info['localization'])
        self.subConstructQualityClassLbl.setText(self.subConstructionObject.info['quality_class'])

    def load_SubConstructionsList(self):
        # Condition required for list refreshment after every call of this function
        if self.subComponentsTab.findChild(QScrollArea) is not None:
            print(f"found scrollArea at: {self.subComponentsTab.findChild(QScrollArea)} --- "
                  f"deleting {self.subComponentsTab.findChild(QScrollArea).objectName()}...")
            self.subComponentsTab.findChild(QScrollArea).deleteLater()
        tmp_scrollArea = QScrollArea()
        tmp_scrollArea.setWidgetResizable(True)
        tmp_scrollWidget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(2)
        # get dataframe with subConstructions belonging to parent mainConstructionObject, by ID
        belonging_subConstructions = \
            self.db.df_from_filteredTable('deki_2022_SubConstructions', 'parent_construction_id', self.constructNumber)
        # get list of subConstruction IDs belonging to parent mainConstructionObject
        subConstructions_IDs = belonging_subConstructions['id'].tolist()
        # iterate throughout subConstruction IDs list and create layout with listItems for obtained weld IDs
        if len(subConstructions_IDs) > 0:
            constructionObject = dbo.SubConstruction(parentConstruction=self.construction)
            for constructionID in subConstructions_IDs:
                constructionObject.load_info(int(constructionID))
                listItem = CustomListItem(int(constructionID), parentScreen=self)
                listItem.constructionTag.setText(constructionObject.info["tag"])
                listItem.constructionName.setText(constructionObject.info['name'])
                listItem.constructionPicture.setPixmap(constructionObject.picture.scaled(120, 120, 1, 1))
                listItem.seriesSize.setText(constructionObject.info['serial_number'])
                listItem.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
                layout.addWidget(listItem, alignment=Qt.AlignTop)
            layout.setAlignment(Qt.AlignTop)
        else:
            label = QLabel()
            label.setText(f'No Subconstructions found in database.')
            label.setStyleSheet('font: 12pt "Calibri";'
                                'background-color: none;')
            layout.addWidget(label, alignment=Qt.AlignCenter)
            layout.setAlignment(Qt.AlignCenter)
        # Insert prepared layout into the QWidget class and then into ScrollArea
        # QWidget class is necessary to perform DeleteLater() function that allows for list refreshment
        tmp_scrollWidget.setLayout(layout)
        tmp_scrollArea.setWidget(tmp_scrollWidget)
        self.subComponentsTabLayout.addWidget(tmp_scrollArea)
        self.tabWidget.setTabText(1, f'Subcomponents ({len(subConstructions_IDs)})')

    def load_weldList(self):
        if self.weldsTab.findChild(QScrollArea) is not None:
            print(f"found scrollArea at: {self.weldsTab.findChild(QScrollArea)} --- "
                  f"deleting {self.weldsTab.findChild(QScrollArea).objectName()}...")
            self.weldsTab.findChild(QScrollArea).deleteLater()
        tmp_scrollArea = QScrollArea()
        tmp_scrollWidget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(2)
        welds_tableName = f"{self.mainConstructionObject.info['tag']}_modelWelds"
        belonging_welds = \
            self.db.df_from_filteredTable(welds_tableName, 'belonging_construction_ID', self.constructNumber)
        if self.db.is_table(welds_tableName):
            if len(belonging_welds) > 0:
                for weldData in belonging_welds.iterrows():
                    from weldListItem_SCRIPT import WeldListItem
                    weldListItem = WeldListItem(int(weldData[1]["id"]), self.subConstructionObject)
                    layout.addWidget(weldListItem, alignment=Qt.AlignTop)
                # layout.setAlignment(Qt.AlignTop)
            else:
                label = QLabel()
                label.setText(f'No welds found in database.')
                label.setStyleSheet('font: 12pt "Calibri";'
                                    'background-color: none;')
                layout.addWidget(label, alignment=Qt.AlignCenter)
                layout.setAlignment(Qt.AlignCenter)
        tmp_scrollWidget.setLayout(layout)
        tmp_scrollArea.setWidget(tmp_scrollWidget)
        self.weldsTabLayout.addWidget(tmp_scrollArea)
        self.tabWidget.setTabText(0, f'Welds ({len(belonging_welds)})')

    def showDialog(self, dialog, closeEventFunc):
        print(f"Opening dialog {dialog}...")
        dialog.show()
        dialog.closeEvent = lambda event: closeEventFunc()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainConstruct = dbo.MainConstruction()
    mainConstruct.load_info(1)
    mainWindow = SubConstructPreviewScreen(mainConstruct, 1)
    mainWindow.showMaximized()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
