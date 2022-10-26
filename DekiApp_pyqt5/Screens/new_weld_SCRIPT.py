import pathlib
import sys

from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5 import QtGui

import db_objects
import gnrl_database_con
from Screens import pdfViewWidget_SCRIPT as pdfviewer

import db_objects as dbo
import resources_rc


class NewWeldDialog(QDialog):
    def __init__(self, parentConstruction, connected_database=None):
        super(NewWeldDialog, self).__init__()
        loadUi(r'new_weld_UI.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.parentConstruction = parentConstruction if parentConstruction is not None else None
        self.mainConstruction = parentConstruction.mainConstruction if parentConstruction is not None else None
        self.db = self.parentConstruction.db if connected_database is None else connected_database
        self.new_weld_DbName = f'{self.mainConstruction.info["tag"]}_modelWelds'
        self.wps_filepath = None
        from db_objects import WeldObject
        self.new_weldObj = WeldObject(self.mainConstruction.info['tag'], self.db,
                                      table_name=self.new_weld_DbName)
        # ---------------------------------------------------------------Screen loading functions----------------------

        self.parentConstructionLbl.setText(
            f"{self.parentConstruction.info['name']}-{self.parentConstruction.info['tag']}")
        self.mainConstructionLbl.setText(f"{self.mainConstruction.info['name']}-{self.mainConstruction.info['tag']}")
        self.new_weldObj.info.update({'belonging_construction_tag': self.parentConstruction.info['tag'],
                                      'belonging_construction_ID': self.parentConstruction.info['id']})
        import weldGraphWidget_SCRIPT as weldGraphWidget
        self.weldGraph = weldGraphWidget.WeldGraphWidget()
        self.weldGraphLayout.addWidget(self.weldGraph)
        self.select_jointContinuity(self.normalWeldBtn)
        self.weldGraph.transformWeldSymbolType("normal")

        # ----------------------------------------------------------------Buttons scripting----------------------------
        self.closeBtn.clicked.connect(lambda: self.close())
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
        self.addWPSBtn.clicked.connect(lambda: self.showPdfViewer(self.wpsDocsViewer))
        # -----------------------------------------------------------------LineEdits scripts---------------------------
        self.firstMaterialLine.editingFinished.connect(
            lambda: self.new_weldObj.info.update({'first_material': self.firstMaterialLine.text()}))
        self.firstMaterialLine.textChanged.connect(lambda x: self.secondMaterialLine.setText(x))
        self.firstJointPartLine.editingFinished.connect(
            lambda: self.new_weldObj.info.update({'first_welded_part': self.firstJointPartLine.text()}))
        self.secondMaterialLine.editingFinished.connect(
            lambda: self.new_weldObj.info.update({'second_material': self.secondMaterialLine.text()}))
        self.secondJointPartLine.editingFinished.connect(
            lambda: self.new_weldObj.info.update({'second_welded_part': self.secondJointPartLine.text()}))
        self.wpsNumberLine.editingFinished.connect(
            lambda: self.new_weldObj.info.update({'wps_number': self.wpsNumberLine.text()}))
        self.weldIDprefixLine.editingFinished.connect(
            lambda: self.new_weldObj.info.update({'weld_id_prefix': self.weldIDprefixLine.text()}))
        self.weldIDsuffixLine.editingFinished.connect(
            lambda: self.new_weldObj.info.update({'weld_id_suffix': self.weldIDsuffixLine.text()}))
        self.wpsMissingCBox.toggled.connect(
            lambda status: (self.wpsNumberLine.setEnabled(False), self.wpsNumberLine.setText("WPS missing checked"),
                            self.new_weldObj.info.update({'wps_number': 'missing'}))
            if status is True else
            self.wpsNumberLine.setEnabled(True))
        self.TMnotSpecifiedRadioBtn.toggled.connect(
            lambda status: (self.new_weldObj.info.update({'testing_methods': []}),
                            [(btn.setEnabled(False), btn.setChecked(False)) for btn in
                             self.weldTestingBtns.findChildren(QPushButton)])
            if status is True else [btn.setEnabled(True) for btn in self.weldTestingBtns.findChildren(QPushButton)])

        # -----------------------------------------------------------------UPDATE INFO---------------------------------
        self.mainConstructionLbl.setText(f"{self.parentConstruction.mainConstruction.info['name']} \n"
                                         f"{self.parentConstruction.mainConstruction.info['tag']}")
        self.parentConstructionLbl.setText(f"{self.parentConstruction.info['name']} \n"
                                           f"{self.parentConstruction.info['tag']}")
        self.showPdfViewer(self.drawingDocsViewer, filepath=self.parentConstruction.pdfDocsPath)

    def showPdfViewer(self, container: QWidget, filepath=None):
        if filepath is None:
            options = QFileDialog.Options()
            filepath, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                      "pdf (*.pdf);;All Files (*)", options=options)
            self.wpsNumberLine.setText(pathlib.Path(filepath).stem)
            self.wps_filepath = filepath
        if len(container.findChildren(QLayout)) < 1:
            pdfViewerWidget = pdfviewer.pdfViewerLayout(fr'{filepath}')
            container.setLayout(pdfViewerWidget)
        else:
            print(f'Layout {container.objectName()} already exist.')

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
            methods_list = self.new_weldObj.info['testing_methods']
            methods_list.remove(selected_btn.text())
            methods_list.sort()
            print(f'{selected_btn.text()} removed from testing methods. New list {methods_list} saved.')
            self.new_weldObj.info['testing_methods'] = methods_list
        else:
            if self.new_weldObj.info['testing_methods'] is None:
                self.new_weldObj.info['testing_methods'] = [selected_btn.text()]
                print(f"Single testing method selected: {self.new_weldObj.info['testing_methods']} has been saved.")
            else:
                methods_list = self.new_weldObj.info['testing_methods']
                methods_list.append(selected_btn.text())
                methods_list.sort()
                self.new_weldObj.info['testing_methods'] = methods_list
                print(f"Selected testing methods: {self.new_weldObj.info['testing_methods']} has been saved")

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
        for key in self.weldGraph.upperWeldData.keys():
            self.new_weldObj.info[key] = self.weldGraph.upperWeldData[key]
        if self.weldGraph.lowerWeldInfo.isVisible():
            for key in self.weldGraph.lowerWeldData.keys():
                self.new_weldObj.info[key] = self.weldGraph.lowerWeldData[key]
        for key in self.weldGraph.weldBanners.keys():
            self.new_weldObj.info[key] = self.weldGraph.weldBanners[key]
        if self.new_weldObj.info['testing_methods'] is not None:
            print(f'Changing list of testing methods into a string.')
            self.new_weldObj.info['testing_methods'] = ';'.join((self.new_weldObj.info['testing_methods']))
        else:
            self.new_weldObj.info['testing_methods'] = None
        if self.db.is_table(self.new_weld_DbName):
            self.new_weldObj.save_weld(self.new_weld_DbName, self.wps_filepath)
        else:
            self.db.create_table(self.new_weld_DbName, self.new_weldObj.info.keys())
        self.close()


if __name__ == '__main__':
    db = gnrl_database_con.Database()
    app = QApplication(sys.argv)
    mainConstruction = db_objects.MainConstruction(connected_database=db)
    mainConstruction.load_info(1)
    subConstruction = db_objects.SubConstruction(parentConstruction=mainConstruction, connected_database=db)
    subConstruction.load_info(1)
    # mainWindow = NewWeldDialog(parentConstruction=subConstruction)
    mainWindow = NewWeldDialog(subConstruction)
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
