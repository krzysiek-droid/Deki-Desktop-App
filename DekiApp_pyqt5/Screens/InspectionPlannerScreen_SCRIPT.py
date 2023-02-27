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


class InspectionPlannerScreen(QWidget):
    def __init__(self, mainWindowObj: QMainWindow, connected_database=None):
        super().__init__()
        self.mainConstructionObject = None
        loadUi(r'InspectionPlannerScreen_UI.ui', self)
        self.currentListItemID = None
        self.mainWindowObject = mainWindowObj
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


        self.mainWindowObject.centerWindow(self)

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
            listItem = CustomListItem(self, constructionObject)
            scrolledContentLayout.addWidget(listItem, alignment=Qt.AlignTop)
        self.scrolledContentWidget.setLayout(scrolledContentLayout)
        self.scrollArea.setWidget(self.scrolledContentWidget)

    def refresh_scrollArea(self):
        self.scrolledContentWidget.deleteLater()
        self.loadConstructionsList()

    def updateRightMenu(self, mainConstructionObj):
        self.mainConstructionObject = mainConstructionObj

        from construction_preview_SCRIPT import MainConstructionDialog
        self.goToConstructionBtn.clicked.connect(
            lambda: self.mainWindowObject.stackedWidget.changeScreen_withSplash(MainConstructionDialog,
                                                                                [self.mainConstructionObject]))

        self.currentListItemID = mainConstructionObj.info['id']
        self.constructionName.setText(mainConstructionObj.info['name'])
        self.constructionTag.setText(mainConstructionObj.info['tag'])
        self.constructionSerialNo.setText(str(mainConstructionObj.info['serial_number']))
        self.constructionOwner.setText(mainConstructionObj.info['owner'])
        self.constructionType.setText(mainConstructionObj.info['construct_type'])
        self.constructionQualityNorm.setText(mainConstructionObj.info['quality_norm'])
        self.constructionQualityClass.setText(mainConstructionObj.info['quality_class'])
        self.constructionTolerancesNorm.setText(mainConstructionObj.info['tolerances_norm'])
        self.constructionTolerancesLevel.setText(mainConstructionObj.info['tolerances_level'])
        self.constructionCoopBody.setText(mainConstructionObj.info['subcontractor'])
        self.constructionCoopContact.setText(mainConstructionObj.info['sub_contact'])
        self.constructionPicLarge.setPixmap(
            mainConstructionObj.picture.scaledToHeight(250, mode=Qt.SmoothTransformation))
        self.goToConstructionBtn.setEnabled(True)

    def showDialog(self, dialog):
        dialog.show()
        dialog.closeEvent = lambda event: (
            self.refresh_scrollArea())


class CustomListItem(QWidget):
    def __init__(self, parentScreenObj: InspectionPlannerScreen, loadedConstructionObject: dbo.MainConstruction):
        super(CustomListItem, self).__init__()
        # set attribute that deletes the instance of this class on closeEvent
        self.setAttribute(Qt.WA_DeleteOnClose)
        loadUi(r'MainConstructionListItem_UI.ui', self)
        self.constructionID = loadedConstructionObject.info['id']
        self.parentScreen = parentScreenObj
        self.constructionObj = loadedConstructionObject
        self.db = loadedConstructionObject.db

        self.mouseReleaseEvent = lambda event: self.parentScreen.updateRightMenu(self.constructionObj)

        self.releaseConstructionBtn.clicked.connect(self.releaseConstruction)

        self.assignInfoToWidgets()

    def releaseConstruction(self):
        from constructionReleaseScreen_SCRIPT import ConstructionReleaseWindow
        dialog = ConstructionReleaseWindow(self.constructionObj)
        self.parentScreen.mainWindowObject.close()
        dialog.show()

    def assignInfoToWidgets(self):
        self.constructionTag.setText(self.constructionObj.info["tag"])
        self.constructionName.setText(self.constructionObj.info['name'])
        self.constructionPicture.setPixmap(
            self.constructionObj.picture.scaledToHeight(120, mode=Qt.SmoothTransformation))
        self.seriesSize.setText(self.constructionObj.info['serial_number'])
        self.clientLbl.setText(self.constructionObj.info['owner'])
        in_preparation_style = 'color: rgb(250,150,0);' \
                               'font: 75 bold 9pt "Arial";'
        released_style = 'color: rgb(30, 210, 80);' \
                         'font: 75 bold 9pt "Arial";' \
                         'text-decoration: underline;'
        (self.stateLbl.setText('In preparation'), self.stateLbl.setStyleSheet(in_preparation_style)) if not \
            self.db.is_table(f'{self.constructionObj.info["tag"]}_allWelds') else \
            (self.stateLbl.setText('Released at: 17 Dec 22'), self.stateLbl.setStyleSheet(released_style))
        counter = len(self.db.df_from_filteredTable('deki_2022_SubConstructions', 'main_construction_id',
                                                    self.constructionObj.info['id']))
        self.subsAmountLbl.setText(str(counter))
        counter = len(self.db.table_into_DF(f"{self.constructionObj.info['tag']}_modelWelds"))
        self.weldsAmountLbl.setText(str(counter))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = InspectionPlannerScreen()

    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
