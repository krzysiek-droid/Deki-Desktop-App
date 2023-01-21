import sys

from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QRunnable
from PyQt5 import sip
import db_objects as dbo
import gnrl_database_con as database

# resources_rc has to be imported here, even if it is not used directly in code, dunno why
import resources_rc

import pathlib


class CustomListItem(QWidget):
    def __init__(self, constructionID):
        super(CustomListItem, self).__init__()
        # set attribute that deletes the instance of this class on closeEvent
        self.setAttribute(Qt.WA_DeleteOnClose)
        loadUi(r'MainConstructionListItem_UI.ui', self)
        self.constructionID = constructionID
        # Get access to QMainWindow instance for its member methods, and save its reference as a member variable
        self.mainWindowInstance = None
        # Trigger a method of different new_screen_ref, in this case the InspectionPlanningMainWindow
        # Updates the rightSidedContent of the InspectionPlanningMainWindow
        # in lambda definition an "event" has to be passed for proper functionality
        self.mouseReleaseEvent = lambda event: self.update_selfInfo()

    def update_selfInfo(self):
        for widget in QApplication.topLevelWidgets():
            searched_child = widget.findChild(QWidget, name='inspectionPlannerScreen')
            if searched_child is not None:
                self.mainWindowInstance = searched_child
                self.mainWindowInstance.updateRightMenu(self.constructionID)
                break
            elif widget.objectName() == 'inspectionPlannerScreen':
                self.mainWindowInstance = widget
                self.mainWindowInstance.updateRightMenu(self.constructionID)
                break


class InspectionPlannerScreen(QWidget):
    def __init__(self, connected_database=None):
        super().__init__()
        loadUi(r'InspectionPlannerScreen_UI.ui', self)
        self.currentListItemID = None
        self.mainWindowObject = None
        for widget in QApplication.topLevelWidgets():
            if widget.objectName() == 'inspectionPlannerWindow':
                from inspectionPlannerWindow_SCRIPT import InspectionPlannerWindow
                self.mainWindowObject: InspectionPlannerWindow = widget
                print(f"found {self.mainWindowObject}")
        # Screen loading scripts
        self.goToConstructionBtn.setEnabled(False)
        # open database connection
        self.db = database.Database() if connected_database is None else connected_database
        # defining the list of constructions widget
        self.scrolledContentWidget = None
        # Load list of constructions
        self.loadConstructionsList()
        # --------------------------------------------------------------------------button allocations
        # show dialog 'new_construction'
        import new_construction_SCRIPT
        self.addConstructionBtn.clicked.connect(
            lambda: (self.showDialog(new_construction_SCRIPT.NewConstructDialog())))

        # change screen for 'construction_preview'
        # from construction_preview_SCRIPT import ConstructPreviewDialog
        # self.goToConstructionBtn.clicked.connect(
        #     lambda: (print(f"Loading mainConstructionObject Preview Screen for mainConstructionObject ID {self.currentListItemID}"),
        #              self.mainWindowObject.stackedWidget.changeScreen(self, ConstructPreviewDialog(
        #                  self.currentListItemID, connected_database=self.db), 'Main Construction Preview') \
        #                  if self.parent() is not None else print('no parent')))

        from construction_preview_SCRIPT import ConstructPreviewDialog
        self.goToConstructionBtn.clicked.connect(
            lambda: self.mainWindowObject.stackedWidget.changeScreen_withSplash(ConstructPreviewDialog,
                    [self.currentListItemID, self.db])
        )

    def loadConstructionsList(self):
        self.scrolledContentWidget = QWidget()
        self.scrolledContentWidget.setObjectName('scrolledContentWidget')
        scrolledContentLayout = QVBoxLayout()
        scrolledContentLayout.setSpacing(1)
        scrolledContentLayout.setAlignment(Qt.AlignTop)
        constructionObject = dbo.MainConstruction(connected_database=self.db)
        db_tableLength = len(self.db.table_into_DF('deki_2022_mainConstructions'))
        for constructionID in range(db_tableLength):
            constructionObject.load_info(constructionID + 1)
            listItem = CustomListItem(constructionID + 1)
            listItem.constructionTag.setText(constructionObject.info["tag"])
            listItem.constructionName.setText(constructionObject.info['name'])
            listItem.constructionPicture.setPixmap(constructionObject.picture.scaledToHeight(120, mode=Qt.SmoothTransformation))
            listItem.seriesSize.setText(constructionObject.info['serial_number'])
            listItem.clientLbl.setText(constructionObject.info['owner'])
            in_preparation_style = 'color: rgb(250,150,0);' \
                                   'font: 75 bold 9pt "Arial";'
            released_style = 'color: rgb(30, 210, 80);' \
                             'font: 75 bold 9pt "Arial";' \
                             'text-decoration: underline;'
            (listItem.stateLbl.setText('In preparation'), listItem.stateLbl.setStyleSheet(in_preparation_style)) if not \
                self.db.is_table(f'{constructionObject.info["tag"]}_allWelds') else \
                (listItem.stateLbl.setText('Released at: 17 Dec 22'), listItem.stateLbl.setStyleSheet(released_style))
            counter = len(self.db.df_from_filteredTable('deki_2022_SubConstructions', 'main_construction_id',
                                                        constructionObject.info['id']))
            listItem.subsAmountLbl.setText(str(counter))
            counter = len(self.db.table_into_DF(f"{constructionObject.info['tag']}_modelWelds"))
            listItem.weldsAmountLbl.setText(str(counter))
            scrolledContentLayout.addWidget(listItem, alignment=Qt.AlignTop)
        self.scrolledContentWidget.setLayout(scrolledContentLayout)
        self.scrollArea.setWidget(self.scrolledContentWidget)

    def refresh_scrollArea(self):
        self.scrolledContentWidget.deleteLater()
        self.loadConstructionsList()

    def updateRightMenu(self, constructionID):
        constructionObject = dbo.MainConstruction(connected_database=self.db)
        constructionObject.load_info(constructionID)
        self.currentListItemID = constructionID
        self.constructionName.setText(constructionObject.info['name'])
        self.constructionTag.setText(constructionObject.info['tag'])
        self.constructionSerialNo.setText(str(constructionObject.info['id']))  # TODO: change 'id' for 'serialNo'
        self.constructionOwner.setText(constructionObject.info['owner'])
        self.constructionType.setText(constructionObject.info['construct_type'])
        self.constructionQualityNorm.setText(constructionObject.info['quality_norm'])
        self.constructionQualityClass.setText(constructionObject.info['quality_class'])
        self.constructionTolerancesNorm.setText(constructionObject.info['tolerances_norm'])
        self.constructionTolerancesLevel.setText(constructionObject.info['tolerances_level'])
        self.constructionCoopBody.setText(constructionObject.info['subcontractor'])
        self.constructionCoopContact.setText(constructionObject.info['sub_contact'])
        self.constructionPicLarge.setPixmap(constructionObject.picture.scaledToHeight(250, mode=Qt.SmoothTransformation))
        print(self.constructionPicLarge.size())
        self.goToConstructionBtn.setEnabled(True)

    def showDialog(self, dialog):
        dialog.show()
        dialog.closeEvent = lambda event: (
            self.refresh_scrollArea())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = InspectionPlannerScreen()

    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
