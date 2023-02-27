from PyQt5 import Qt
from PyQt5.QtCore import QPropertyAnimation, QRect
from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QScrollArea, QApplication
from PyQt5.uic import loadUi

import db_objects as dbo

import resources_rc


class InspectionPlannerPage(QDialog):
    def __init__(self):
        super(InspectionPlannerPage, self).__init__()
        loadUi(r'inspectionPlannerPage_UI.ui', self)
        self.setObjectName('InspectionPlannerPage')
        self.db = QApplication.instance().database
        self.scrollAreaContent: QWidget
        self.scrollLayout = QVBoxLayout()
        self.scrollArea: QScrollArea
        self.scrollArea.setLayout(self.scrollLayout)
        self.loadConstructionList()

    def loadConstructionList(self):
        construction = dbo.MainConstruction()
        construction.load_info(1)
        testItem = ConstructionListItemPageVersion(self, construction)
        self.scrollLayout.addWidget(testItem, alignment=Qt.Qt.AlignTop)


class ConstructionListItemPageVersion(QWidget):
    def __init__(self, parentScreenObj: InspectionPlannerPage, loadedConstructionObject: dbo.MainConstruction):
        super(ConstructionListItemPageVersion, self).__init__()
        # set attribute that deletes the instance of this class on closeEvent
        loadUi(r'MainConstructionListItem_UI.ui', self)
        self.constructionID = loadedConstructionObject.info['id']
        self.parentScreen = parentScreenObj
        self.constructionObj = loadedConstructionObject
        self.db = QApplication.instance().database

        self.assignInfoToWidgets()

    def assignInfoToWidgets(self):
        self.constructionTag.setText(self.constructionObj.info["tag"])
        self.constructionName.setText(self.constructionObj.info['name'])
        self.constructionPicture.setPixmap(
            self.constructionObj.picture.scaledToHeight(120, mode=Qt.Qt.SmoothTransformation))
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


if __name__ == "__main__":
    print('mainWidnow_Pages script')
