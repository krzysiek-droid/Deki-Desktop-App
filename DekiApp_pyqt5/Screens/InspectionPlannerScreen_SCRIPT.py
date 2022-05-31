import sys

from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

import db_objects as dbo
import gnrl_database_con as database

# resources_rc has to be imported here, even if it is not used directly in code, dunno why
import resources_rc

import pathlib


class CustomListItem(QWidget):
    def __init__(self, constructionID):
        super(CustomListItem, self).__init__()
        loadUi(r'ListItem.ui', self)
        self.constructionID = constructionID
        # Get access to QMainWindow instance for its member methods, and save its reference as a member variable
        self.mainWindowInstance = None
        for widget in QApplication.topLevelWidgets():
            if widget.objectName() == 'inspectionPlannerScreen':
                self.mainWindowInstance = widget

        # Trigger a method of different object, in this case the InspectionPlanningMainWindow
        # Updates the rightSidedContent of the InspectionPlanningMainWindow
        # in lambda definition an "event" has to be passed for proper functionality
        self.mouseReleaseEvent = lambda event: self.mainWindowInstance.updateRightMenu(self.constructionID)


class InspectionPlannerScreen(QWidget):
    def __init__(self):
        super().__init__()
        loadUi(r'InspectionPlannerScreen_UI.ui', self)
        # open database connection
        self.db = database.Database()
        # defining the list of constructions widget
        self.scrolledContentWidget = QWidget()
        self.scrolledContentWidget.setObjectName('scrolledContentWidget')
        self.scrolledContentLayout = QVBoxLayout()
        # Load list of constructions
        self.loadConstructionsList()
        self.scrolledContentLayout.setSpacing(1)

        # button allocations
        # change screen for 'new_construction'
        import new_construction_SCRIPT
        self.addConstructionBtn.clicked.connect(
            lambda: (self.parent().addWidget(new_construction_SCRIPT.NewConstructDialog()),
                     self.parent().setCurrentIndex(self.parent().indexOf(self) + 1),
                     self.parent().removeWidget(self)))

    def loadConstructionsList(self):
        for constructionID in range(len(self.db.table_into_DF('deki_2022_constructions'))):
            constructionObject = dbo.Construction(self.db)
            constructionObject.load_info(constructionID + 1)
            listItem = CustomListItem(constructionID + 1)
            listItem.constructionTag.setText(constructionObject.info["tag"])
            listItem.constructionName.setText(constructionObject.info['name'])
            listItem.constructionPicture.setPixmap(constructionObject.picture.scaled(120, 120, 1, 1))
            listItem.seriesSize.setText(constructionObject.info['serial_number'])
            self.scrolledContentLayout.addWidget(listItem)

        self.scrolledContentWidget.setLayout(self.scrolledContentLayout)
        self.scrollArea.setWidget(self.scrolledContentWidget)

    def updateRightMenu(self, constructionID):
        constructionObject = dbo.Construction(self.db)
        constructionObject.load_info(constructionID)
        self.constructionName.setText(constructionObject.info['name'])
        self.constructionTag.setText(constructionObject.info['tag'])
        self.constructionSerialNo.setText(constructionObject.info['id'])
        self.constructionOwner.setText(constructionObject.info['owner'])
        self.constructionType.setText(constructionObject.info['construct_type'])
        self.constructionQualityNorm.setText(constructionObject.info['quality_norm'])
        self.constructionQualityClass.setText(constructionObject.info['quality_class'])
        self.constructionTolerancesNorm.setText(constructionObject.info['tolerances_norm'])
        self.constructionTolerancesLevel.setText(constructionObject.info['tolerances_level'])
        self.constructionCoopBody.setText(constructionObject.info['subcontractor'])
        self.constructionCoopContact.setText(constructionObject.info['sub_contact'])
        self.constructionPicLarge.setPixmap(constructionObject.picture.scaled(300, 300, 1, 1))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = InspectionPlannerScreen()

    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
