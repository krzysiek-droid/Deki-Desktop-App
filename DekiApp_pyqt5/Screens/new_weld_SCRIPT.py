import sys

from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtCore

import db_objects
from Screens import pdfViewWidget_SCRIPT as pdfviewer

import db_objects as dbo
import resources_rc


class NewWeldDialog(QDialog):
    def __init__(self, parentConstruction, connected_database=None):
        super(NewWeldDialog, self).__init__()
        loadUi(r'new_weld_UI.ui', self)
        self.selected_weldType = None
        self.selected_weldFaces = []
        self.pdfViewerWidget = None
        self.parentConstruction = parentConstruction
        self.mainConstruction = parentConstruction.mainConstruction
        self.db = self.parentConstruction.db if connected_database is None else connected_database
        self.new_weld_DbName = f'{self.mainConstruction.info["tag"]}_modelWelds'
        from db_objects import weldObject
        self.new_weldObj = weldObject(connected_database=self.db, table_name=self.new_weld_DbName)
        # ---------------------------------------------------------------Screen loading functions----------------------
        self.rightSidedContent.hide()
        self.parentConstructionLbl.setText(
            f"{self.parentConstruction.info['name']}-{self.parentConstruction.info['tag']}")
        self.mainConstructionLbl.setText(f"{self.mainConstruction.info['name']}-{self.mainConstruction.info['tag']}")
        import weldGraphWidget_SCRIPT as weldGraphWidget
        self.weldGraph = weldGraphWidget.WeldGraphWidget()
        self.weldGraphLayout.addWidget(self.weldGraph)
        self.select_jointContinuity(self.normalWeldBtn)
        self.weldGraph.transformWeldSymbolType("normal")
        # ----------------------------------------------------------------Buttons scripting----------------------------
        self.testMthdBtnLT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnLT))
        self.testMthdBtnMT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnMT))
        self.testMthdBtnPT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnPT))
        self.testMthdBtnVT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnVT))
        self.testMthdBtnRT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnRT))
        self.testMthdBtnUT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnUT))
        self.buttJointBtn.clicked.connect(lambda: self.select_jointType(self.buttJointBtn))
        self.lapJointBtn.clicked.connect(lambda: self.select_jointType(self.lapJointBtn))
        self.cornerJointBtn.clicked.connect(lambda: self.select_jointType(self.cornerJointBtn))
        self.teeJointBtn.clicked.connect(lambda: self.select_jointType(self.teeJointBtn))
        self.edgeJointBtn.clicked.connect(lambda: self.select_jointType(self.edgeJointBtn))
        self.normalWeldBtn.clicked.connect(
            lambda: (self.select_jointContinuity(self.normalWeldBtn),
                     self.weldGraph.transformWeldSymbolType("normal")))
        self.intermittentWeldBtn.clicked.connect(
            lambda: (self.select_jointContinuity(self.intermittentWeldBtn),
                     self.weldGraph.transformWeldSymbolType("intermittent")))
        self.staggeredWeldBtn.clicked.connect(
            lambda: (self.select_jointContinuity(self.staggeredWeldBtn),
                     self.weldGraph.transformWeldSymbolType("staggered")))
        self.addWeldBtn.clicked.connect(self.saveWeld)

        # -----------------------------------------------------------------UPDATE INFO---------------------------------
        self.mainConstructionLbl.setText(f"{self.parentConstruction.mainConstruction.info['name']} \n"
                                         f"{self.parentConstruction.mainConstruction.info['tag']}")
        self.parentConstructionLbl.setText(f"{self.parentConstruction.info['name']} \n"
                                           f"{self.parentConstruction.info['tag']}")

    def showPdfViewer(self):
        if not self.pdfViewerWidget:
            print(self.parentConstruction.pdfDocsPath)
            self.pdfViewerWidget = pdfviewer.pdfViewerWidget(fr'{self.parentConstruction.pdfDocsPath}')
            self.pdfViewerWidget.setMinimumSize(650, 450)
            # Create layout for pdfViewerWidget
            grid = QVBoxLayout()
            grid.addWidget(self.pdfViewerWidget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            # Insert a pdfViewerWidget into docViewer Widget (widget for pdf viewing)
            self.constructDocsViewer.setLayout(grid)
        else:
            pass

    def select_jointType(self, selected_btn: QPushButton):
        # button status changes before execution of this function!
        for JTBtn in self.jointTypesBtnsLayout.findChildren(QPushButton):
            if JTBtn is not selected_btn:
                JTBtn.setStyleSheet("border: 0px")
                JTBtn.setChecked(False)
        if not selected_btn.isChecked():
            selected_btn.setStyleSheet("border: 0px")
            self.new_weldObj.info['joint_type'] = None
            print(f"Joint type reset: {self.new_weldObj.info['joint_type']}")
        else:
            self.new_weldObj.info['joint_type'] = selected_btn.objectName().replace('JointBtn', ' joint')
            print(f"Joint type saved: {self.new_weldObj.info['joint_type']}")
            selected_btn.setStyleSheet("border: 2px solid rgb(30, 210, 80)")

    def select_testingMethod(self, selected_btn: QPushButton):
        if not selected_btn.isChecked():
            selected_btn.setStyleSheet("background-color : rgb(255, 255, 255)")
            methods_list = self.new_weldObj.info['testing_methods']
            methods_list.remove(selected_btn.text())
            methods_list.sort()
            print(f'{selected_btn.text()} removed from testing methods. New list {methods_list} saved.')
            self.new_weldObj.info['testing_methods'] = methods_list
        else:
            if self.new_weldObj.info['testing_methods'] is None:
                self.new_weldObj.info['testing_methods'] = [selected_btn.text()]
                print(f"Single testing method selected: {self.new_weldObj.info['testing_methods']} has been saved.")
                selected_btn.setStyleSheet("background-color : rgb(30, 210, 80)")
            else:
                methods_list = self.new_weldObj.info['testing_methods']
                methods_list.append(selected_btn.text())
                methods_list.sort()
                self.new_weldObj.info['testing_methods'] = methods_list
                print(f"Selected testing methods: {self.new_weldObj.info['testing_methods']} has been saved")
                selected_btn.setStyleSheet("background-color : rgb(30, 210, 80)")

    def select_jointContinuity(self, selected_btn: QPushButton):
        for btn in self.weldTypeFrame.findChildren(QPushButton):
            if btn is not selected_btn:
                btn.setStyleSheet("background-color : rgb(255, 255, 255)")
                btn.setChecked(False)
            else:
                btn.setStyleSheet("background-color : rgb(30, 210, 80)")
                btn.setChecked(True)

        self.new_weldObj.info['weld_continuity_type'] = selected_btn.text().lower()
        print(f"Joint continuity type saved: {self.new_weldObj.info['weld_continuity_type']}")

    def saveWeld(self):
        print(f'Current amount of welds in table {self.new_weld_DbName}: {self.new_weldObj.db_records}')
        if self.db.is_table(self.new_weld_DbName):
            print('Database for welds found. Adding new weld...')
            # Do not update db_records to avoid multpile inserting of same object into db
            self.new_weldObj.info['id'] = self.new_weldObj.db_records + 1
            self.db.insert(self.new_weld_DbName, list(self.new_weldObj.info.values()))
            print(f'Weld inserted with id: {self.new_weldObj.info["id"]}')
        else:
            print('Database for welds not found. Creating new table in Database...')
            self.db.create_table(self.new_weld_DbName, self.new_weldObj.info.keys())
            print(f'Table {self.new_weld_DbName} created. Adding weld...')
            self.new_weldObj.info['id'] = self.new_weldObj.db_records + 1
            self.db.insert(self.new_weld_DbName, self.new_weldObj.info.values())
            print(f'Weld inserted with id: {self.new_weldObj.info["id"]}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    subConstruction = db_objects.SubConstruction()
    subConstruction.load_info(1)
    mainWindow = NewWeldDialog(subConstruction)
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
