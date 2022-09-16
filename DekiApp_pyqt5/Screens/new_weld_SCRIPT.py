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


def toggleBtn(selected_btn: QPushButton):
    # TODO get selected btns to list of selected test methods for added weld
    if not selected_btn.isChecked():
        selected_btn.setStyleSheet("background-color : rgb(255, 255, 255)")
    else:
        selected_btn.setStyleSheet("background-color : rgb(30, 210, 80)")


def toggleOnlyOneBtn(selected_btn: QPushButton, container):
    print(container.findChildren(QPushButton))
    for btn in container.findChildren(QPushButton):
        if btn is not selected_btn:
            btn.setStyleSheet("background-color : rgb(255, 255, 255)")
            btn.setChecked(False)
        else:
            btn.setStyleSheet("background-color : rgb(30, 210, 80)")
            btn.setChecked(True)


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
        toggleOnlyOneBtn(self.normalWeldBtn, self.normalWeldBtn.parent())
        self.weldGraph.transformWeldSymbolType("normal")
        # ----------------------------------------------------------------Buttons scripting----------------------------
        self.testMthdBtnLT.clicked.connect(lambda: toggleBtn(self.testMthdBtnLT))
        self.testMthdBtnMT.clicked.connect(lambda: toggleBtn(self.testMthdBtnMT))
        self.testMthdBtnPT.clicked.connect(lambda: toggleBtn(self.testMthdBtnPT))
        self.testMthdBtnVT.clicked.connect(lambda: toggleBtn(self.testMthdBtnVT))
        self.testMthdBtnRT.clicked.connect(lambda: toggleBtn(self.testMthdBtnRT))
        self.testMthdBtnUT.clicked.connect(lambda: toggleBtn(self.testMthdBtnUT))
        self.buttJointBtn.toggled.connect(lambda: self.select_jointType(self.buttJointBtn))
        self.lapJointBtn.toggled.connect(lambda: self.select_jointType(self.lapJointBtn))
        self.cornerJointBtn.clicked.connect(lambda: self.select_jointType(self.cornerJointBtn))
        self.teeJointBtn.clicked.connect(lambda: self.select_jointType(self.teeJointBtn))
        self.edgeJointBtn.clicked.connect(lambda: self.select_jointType(self.edgeJointBtn))
        self.normalWeldBtn.clicked.connect(
            lambda: (toggleOnlyOneBtn(self.normalWeldBtn, self.normalWeldBtn.parent()),
                     self.weldGraph.transformWeldSymbolType("normal")))
        self.intermittentWeldBtn.clicked.connect(
            lambda: (toggleOnlyOneBtn(self.intermittentWeldBtn, self.intermittentWeldBtn.parent()),
                     self.weldGraph.transformWeldSymbolType("intermittent")))
        self.staggeredWeldBtn.clicked.connect(
            lambda: (toggleOnlyOneBtn(self.staggeredWeldBtn, self.staggeredWeldBtn.parent()),
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
        selected_btn.setStyleSheet(
            "border: 2px solid rgb(30, 210, 80)") if selected_btn.isChecked() else selected_btn.setStyleSheet(
            'border: 0px')
        for JTBtn in self.jointTypesBtnsLayout.findChildren(QPushButton):
            if not JTBtn == selected_btn:
                JTBtn.setStyleSheet("border: 0px")
                JTBtn.setChecked(False)

    def saveWeld(self):
        # TODO: all
        print(f'Current amount of welds in table {new_weld_DbName}: {self.new_weldObj.db_records}')
        self.new_weldObj.info = {'id': self.new_weldObj.db_records + 1,
                            'belonging_construction_tag': 1,
                            'belonging_construction_ID': 1,
                            'wps_number': 1,
                            'weld_id_prefix': 1,
                            'weld_id_generated': 1,
                            'weld_id_suffix': 1,
                            'joint_type': 1,
                            'weld_continuity_type': 1,
                            'all_around': 1,
                            'field_weld': 1,
                            'upper_sizeType': 1,
                            'upper_size': 1,
                            'upper_weld_type': 1,
                            'upper_weld_face': 1,
                            'upper_weld_quant': 1,
                            'upper_length': 1,
                            'upper_weld_spacing': 1,
                            'double_sided': 1,
                            'sided_sizeType': 1,
                            'sided_size': 1,
                            'sided_weld_type': 1,
                            'sided_weld_face': 1,
                            'sided_weld_quant': 1,
                            'sided_length': 1,
                            'sided_weld_spacing': 1,
                            'tail_info': 1,
                            'first_material': 1,
                            'second_material': 1,
                            'first_welded_part': 1,
                            'second_welded_part': 1,
                            'testing_methods': 1,
                            }

        if self.db.is_table(new_weld_DbName):
            print('Database for welds found. Adding new weld...')
            self.db.insert(new_weld_DbName, list(self.new_weldObj.info.values()))
            print(f'Weld inserted with id: {self.new_weldObj.info["id"]}')
        else:
            print('Database for welds not found. Creating new table in Database...')
            self.db.create_table(new_weld_DbName, self.new_weldObj.info.keys())
            print(f'Table {new_weld_DbName} created. Adding weld...')

            self.db.insert(new_weld_DbName, self.new_weldObj.info.values())
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
