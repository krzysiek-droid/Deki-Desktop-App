import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import PyQt5
import db_objects

import resources_rc


class WeldListItem(QWidget):
    def __init__(self, weldID, parent_construction):
        super(WeldListItem, self).__init__()
        uic.loadUi(r'weldListItem.ui', self)
        self.weldObj = db_objects.weldObject(connected_database=parent_construction.db,
                                             parentConstructName=parent_construction.info['tag'])
        self.weldObj.load_info(weldID)
        print(self.weldObj.info['weld_continuity_type'])
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
        #self.staggerSignLbl.setPixmap(QtGui.QPixmap(QtGui.QIcon(':/Pictures/Pictures/stagger_thick.svg').pixmap(25, 25)))

        # ----------------------------------------------------------- upper weld info loading --------------------------
        self.upperWeldTypeLbl.setPixmap(QtGui.QPixmap(
            QtGui.QIcon(f':/Icons/Icons/weldIcon_{self.weldObj.info["upper_weld_type"]}.png').pixmap(20, 20)))
        self.upperSize.setText(f"{self.weldObj.info['upper_sizeType']}{self.weldObj.info['upper_size']}")
        self.upperLength.setText(f"Length: {self.weldObj.info['upper_length']} mm")
        self.weldNumberLbl.setText(f"{self.weldObj.info['weld_id_prefix']}")

        for testingMethodButton in self.testingMthdsFrame.findChildren(QtWidgets.QPushButton):
            try:
                if testingMethodButton.objectName().replace('Btn', '') in self.weldObj.info['testing_methods'].split(';'):
                    testingMethodButton.setChecked(True)
            except AttributeError:
                print(f'Testing methods not specified in the database.')

        self.check_sidedInfo()

    def check_sidedInfo(self):
        if not bool(int(self.weldObj.info['double_sided'])):
            print(f'double sided weld not specified.')
            self.sidedInfoFrame.hide()
            self.resize(self.width(), self.height() - self.sidedWeldTypeLbl.height())
        else:
            self.sidedSize.setText(f"{self.weldObj.info['sided_sizeType']}{self.weldObj.info['sided_size']}")
            self.sidedLength.setText(f"Length: {self.weldObj.info['sided_length']} mm")
            if self.weldObj.info['weld_continuity_type'] == 'intermittent':
                self.sidedSpacing.setText(self.weldObj.info['sided_weld_spacing'])
            self.sidedWeldTypeLbl.setPixmap(QtGui.QPixmap(
                QtGui.QIcon(f':/Icons/Icons/weldIcon_{self.weldObj.info["sided_weld_type"]}.png').pixmap(
                    20, 20).transformed(QtGui.QTransform().scale(1, -1))))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    construction = db_objects.MainConstruction()
    construction.load_info(1)

    mainWindow = WeldListItem(5, construction)
    print(mainWindow.weldObj.info.keys())
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
