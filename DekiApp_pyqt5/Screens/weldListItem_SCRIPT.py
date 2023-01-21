import sys

import pandas
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import PyQt5
import db_objects
import gnrl_database_con

import resources_rc


class WeldListItem(QWidget):
    def __init__(self, weldID, parent_construction):
        super(WeldListItem, self).__init__()
        uic.loadUi(r'weldListItem.ui', self)
        self.db: gnrl_database_con.Database = parent_construction.db
        self.weldObj = db_objects.WeldObject(connected_database=self.db,
                                             table_name=f"{parent_construction.mainConstructionObject.info['tag']}_modelWelds")
        self.weldObj.fast_load_singleWeld(weldID)

        if self.weldObj.info['weld_continuity_type'] == 'normal':
            self.upperSpacing.hide()
            self.sidedSpacing.hide()
            self.staggerSignLbl.hide()
            # self.weldIntermittentSignFrame.hide()
        elif self.weldObj.info['weld_continuity_type'] == 'intermittent':
            self.staggerSignLbl.hide()
            self.upperSpacing.setText(self.weldObj.info['upper_weld_spacing'])

        # To insert a QIcon into QLabel, a Qicon has to be transformed to pixmap by .pixmap(size) method
        self.assemblyWeldLbl.setPixmap(
            QtGui.QPixmap(QtGui.QIcon(':/Icons/Icons/weldIcon_weldBanner.png').pixmap(22, 22)))
        self.assemblyWeldLbl.show() if bool(int(self.weldObj.info['field_weld'])) else self.assemblyWeldLbl.hide()
        self.allRoundWeldLbl.setPixmap(
            QtGui.QPixmap(QtGui.QIcon(':/Icons/Icons/weldIcon_weldRoundedLine.png').pixmap(22, 22)))
        self.allRoundWeldLbl.show() if bool(int(self.weldObj.info['all_around'])) else self.allRoundWeldLbl.hide()
        # ----------------------------------------------------------- upper weld info loading --------------------------
        self.upperWeldTypeLbl.setPixmap(QtGui.QPixmap(
            QtGui.QIcon(f':/Icons/Icons/weldIcon_{self.weldObj.info["upper_weld_type"]}.png').pixmap(25, 25)))
        self.upperSize.setText(f"{self.weldObj.info['upper_sizeType']}{self.weldObj.info['upper_size']}")
        self.upperLength.setText(f"{self.weldObj.info['upper_length']} mm")
        if self.weldObj.info['upper_weld_quant'] != '' and self.weldObj.info['upper_weld_quant'] is not None:
            self.upperQuantity.setText(f"{self.weldObj.info['upper_weld_quant']}x")
        else:
            self.upperQuantity.hide()
        self.weldNumberLbl.setText(f"{self.weldObj.info['weld_id_generated']}")
        for testingMethodButton in self.testingMthdsFrame.findChildren(QtWidgets.QPushButton):
            try:
                if testingMethodButton.objectName().replace('Btn', '') in self.weldObj.info['testing_methods']:
                    testingMethodButton.setChecked(True)
            except AttributeError:
                print(f'Testing methods not specified in the database.')

        self.check_sidedInfo()
        from weldPreviewDialog_SCRIPT import WeldPreviewDialog
        self.editWeldBtn.clicked.connect(lambda: self.showDialog(WeldPreviewDialog(weldObject=self.weldObj,
                                                                                   parentConstruction=parent_construction,
                                                                                   connected_database=self.db)))
        self.welds_DB_table = self.db.table_into_DF(f"{parent_construction.mainConstructionObject.info['tag']}_modelWelds")
        sameWelds_df: pandas.DataFrame = self.welds_DB_table.query(
            f"same_as_weldID == '{self.weldObj.info['weld_id_generated']}'")
        self.sameAmountLbl.setText(f"x{len(sameWelds_df) + 1}")

        self.welds_subConstructions_table = self.db.table_into_DF(f'deki_2022_SubConstructions')
        construct_name_df = self.welds_subConstructions_table.query(f"id == {self.weldObj.info['belonging_construction_ID']}")
        self.parentConstructionLbl.setText(construct_name_df['name'].to_string(index=False))

    def check_sidedInfo(self):
        if not bool(int(self.weldObj.info['double_sided'])):
            self.sidedInfoFrame.hide()
            self.resize(self.width(), self.height() - self.sidedWeldTypeLbl.height())
        else:
            self.sidedSize.setText(f"{self.weldObj.info['sided_sizeType']}{self.weldObj.info['sided_size']}")
            self.sidedLength.setText(f"{self.weldObj.info['sided_length']} mm")
            if self.weldObj.info['weld_continuity_type'] == 'intermittent' or \
                    self.weldObj.info['weld_continuity_type'] == 'staggered':
                self.sidedSpacing.setText(self.weldObj.info['sided_weld_spacing'])
                self.sidedQuantity.setText(self.weldObj.info['sided_weld_quant'])
            else:
                self.sidedSpacing.hide()
                self.sidedQuantity.hide()
            self.sidedWeldTypeLbl.setPixmap(QtGui.QPixmap(
                QtGui.QIcon(f':/Icons/Icons/weldIcon_{self.weldObj.info["sided_weld_type"]}.png').pixmap(
                    25, 25).transformed(QtGui.QTransform().scale(1, -1))))

    def removeWeld(self):  # TODO
        pass

    def showDialog(self, dialog, refreshment: bool = False):
        dialog.exec_()
        if refreshment:
            dialog.closeEvent = lambda event: (self.parent().setGraphicsEffect(QtWidgets.QGraphicsEffect()),
                                               self.refresh_subConstructionList())
        else:
            print("Closing dialog.")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    construction = db_objects.MainConstruction()
    construction.load_info(1)

    mainWindow = WeldListItem(6, construction)
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
