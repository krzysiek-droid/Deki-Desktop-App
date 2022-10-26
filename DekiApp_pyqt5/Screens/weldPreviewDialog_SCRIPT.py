import pathlib
import sys

from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtCore

import db_objects
import gnrl_database_con
from Screens import pdfViewWidget_SCRIPT as pdfviewer

import db_objects as dbo
import resources_rc

from weldGraphWidget_SCRIPT import WeldGraphWidget


class WeldGraphPreviewWidget(WeldGraphWidget):
    def __init__(self, weldData: dict):
        super(WeldGraphPreviewWidget, self).__init__()
        self.editGraphBtn.show()
        self.weldData = weldData
        for widget in self.mainFrame.findChildren(QWidget):
            if widget.objectName() != 'editGraphBtn':
                widget.setEnabled(False)

        self.editGraphBtn.clicked.connect(self.editGraph)
        self.load_weldGraphData()

    def editGraph(self):
        for widget in self.findChildren(QWidget):
            widget.setEnabled(True)

    def load_weldGraphData(self):
        for key in self.lineEdits.keys():
            self.lineEdits[key].setPlaceholderText(self.weldData[key])
            if self.weldData[key] is None:
                self.lineEdits[key].setPlaceholderText(' - ')
        for key in self.pushButtons.keys():
            # load weldType and weldFace (both upper and lower)
            iconPixmap = QtGui.QPixmap(QtCore.QSize(20, 20))
            if key.count('type') > 0:
                iconPath = fr":/Icons/Icons/weldIcon_{self.weldData[key]}"
                iconPixmap.load(iconPath)
                if key.count('lower') > 0:
                    iconPixmap = iconPixmap.transformed(QtGui.QTransform().scale(1, -1))
            elif key.count('face') > 0:
                iconPath = fr":/Icons/Icons/{self.weldData[key]}_weld_face"
                iconPixmap.load(iconPath)
                if key.count('lower') > 0:
                    iconPixmap = iconPixmap.transformed(QtGui.QTransform().scale(1, -1))
            elif key == 'field_weld':
                iconPath = fr':/Icons/Icons/banner_weld_face.png'
                self.pushButtons[key].setChecked(False)
                self.weldBanners[key] = False
                if int(self.weldData[key]):
                    iconPath = fr':/Icons/Icons/weldIcon_weldBanner.png'
                    self.pushButtons[key].setChecked(True)
                    self.weldBanners[key] = True
                iconPixmap.load(iconPath)
            elif key == 'all_around':
                iconPath = r':/Icons/Icons/weldIcon_weldLine.png'
                self.pushButtons[key].setChecked(False)
                self.weldBanners[key] = False
                if int(self.weldData[key]):
                    iconPath = r':/Icons/Icons/weldIcon_weldRoundedLine.png'
                    self.pushButtons[key].setChecked(True)
                    self.weldBanners[key] = True
                iconPixmap.load(iconPath)
            icon = QtGui.QIcon(iconPixmap)
            self.pushButtons[key].setIcon(icon)

        if int(self.weldData['double_sided']):
            self.addSideWeld.setChecked(True)
            self.toggleSideWeld()

        if self.weldData['tail_info'] is not None:
            self.tailMultiline.setText(self.weldData['tail_info'])
        else:
            self.tailMultiline.setPlaceholderText('n/a')
        self.upperSizeCombo.setCurrentText(f"{self.weldData['upper_sizeType']}")
        self.lowerSizeCombo.setCurrentText(f"{self.weldData['sided_sizeType']}")


class CustomLineEdit(QLineEdit):
    def __init__(self, *args):
        super(CustomLineEdit, self).__init__(*args)
        self.clearAction = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setReadOnly(True)
        self.textChanged.connect(lambda: self.customLineEdit_textChanged())
        self.customLineEdit_textChanged()
        self.setClearButtonEnabled(False)

    def customLineEdit_textChanged(self):
        if self.text() is not None and self.isReadOnly() and self.clearAction is None:
            clear_icon = QtGui.QIcon(':/Icons/Icons/edit-3.svg')
            self.clearAction = self.addAction(clear_icon, QLineEdit.ActionPosition.TrailingPosition)
            self.clearAction.triggered.connect(lambda: (self.setReadOnly(False), self.customLineEdit_textChanged()))
        else:
            self.removeAction(self.clearAction)
            self.clearAction = None
            self.setClearButtonEnabled(True)
            # TODO: add color change after text edited.


class WeldPreviewDialog(QDialog):
    def __init__(self, parentConstruction, weldID, connected_database=None):
        super(WeldPreviewDialog, self).__init__()
        self.wps_filepath = None
        loadUi('weld_preview_UI.ui', self)
        self.lineEdits = {
            'wps_number': self.wpsNumberLine,
            'weld_id_prefix': self.weldIDprefixLine,
            'weld_id_suffix': self.weldIDsuffixLine,
            'first_material': self.firstMaterialLine,
            'second_material': self.secondMaterialLine,
            'first_welded_part': self.firstJointPartLine,
            'second_welded_part': self.secondJointPartLine
        }
        self.db = gnrl_database_con.Database() if connected_database is None else connected_database
        self.weldObj = dbo.WeldObject(mainConstructionTag=parentConstruction.mainConstruction.info['tag'],
                                      connected_database=self.db)
        self.weldObj.load_info(weldID)

        self.weldGraph = WeldGraphPreviewWidget(self.weldObj.info)
        self.weldGraphLayout.addWidget(self.weldGraph)
        self.parentConstructionLbl.setText(parentConstruction.info['tag'])
        self.mainConstructionLbl.setText(parentConstruction.mainConstruction.info['tag'])
        #   ------------------------------ Scripts to be performed Before loading the info from db
        self.highlight_jointType()
        self.highlight_jointContinuity()
        self.jointTypeEditBtn.clicked.connect(self.edit_jointType)
        self.editJointContinuity.clicked.connect(self.edit_jointContinuity)
        self.editTestingMethodsBtn.clicked.connect(self.edit_testingMethods)
        self.saveChangesBtn.clicked.connect(lambda: self.replaceWeld())

        self.load_lineInfo()
        self.load_testingMethods()
        self.showPdfViewer(self.drawingDocsViewer, filepath=parentConstruction.pdfDocsPath)
        #   ---------------------------------------------- Post info load scripts
        self.firstMaterialLine.textChanged.connect(
            lambda: self.weldObj.info.update({'first_material': self.firstMaterialLine.text()}))
        self.firstMaterialLine.textChanged.connect(lambda x: self.secondMaterialLine.setText(x))
        self.firstJointPartLine.textChanged.connect(
            lambda: self.weldObj.info.update({'first_welded_part': self.firstJointPartLine.text()}))
        self.secondMaterialLine.textChanged.connect(
            lambda: self.weldObj.info.update({'second_material': self.secondMaterialLine.text()}))
        self.secondJointPartLine.textChanged.connect(
            lambda: self.weldObj.info.update({'second_welded_part': self.secondJointPartLine.text()}))
        self.wpsNumberLine.textChanged.connect(
            lambda: self.weldObj.info.update({'wps_number': self.wpsNumberLine.text()}))
        self.weldIDprefixLine.textChanged.connect(
            lambda: self.weldObj.info.update({'weld_id_prefix': self.weldIDprefixLine.text()}))
        self.weldIDsuffixLine.textChanged.connect(
            lambda: self.weldObj.info.update({'weld_id_suffix': self.weldIDsuffixLine.text()}))
        self.addWPSBtn.clicked.connect(lambda: self.showPdfViewer(self.wpsDocsViewer))
        #   ------------ has to be placed after wpsNumberLine.editingFinished signal
        self.wpsMissingCBox.stateChanged.connect(
            lambda x: ((self.wpsNumberLine.clear(), self.wpsNumberLine.setEnabled(False)) if x != 0 else
                       (self.wpsNumberLine.setEnabled(True), self.wpsNumberLine.clear())))

    def highlight_jointType(self):
        # button status changes before execution of this function!
        jointType_btnName = self.weldObj.info['joint_type'].replace(' ', '').replace('joint', 'Joint') + 'Btn'
        for JTBtn in self.jointTypesBtnsLayout.findChildren(QPushButton):
            if JTBtn.objectName() == jointType_btnName:
                JTBtn.setStyleSheet("border: 2px solid rgb(30, 210, 80)")
                JTBtn.setChecked(True)
            else:
                JTBtn.setChecked(False)
                JTBtn.setEnabled(False)

    def select_jointType(self, selected_btn: QPushButton):
        # button status changes before execution of this function!
        # uncheck not selected buttons
        for JTBtn in self.jointTypesBtnsLayout.findChildren(QPushButton):
            if JTBtn is not selected_btn:
                JTBtn.setStyleSheet("border: 0px")
                JTBtn.setChecked(False)
        # highlight and save the selected button
        if not selected_btn.isChecked():
            selected_btn.setStyleSheet("border: 0px")
            self.weldObj.info['joint_type'] = None
            print(f"Joint type reset: {self.weldObj.info['joint_type']}")
        else:
            self.weldObj.info['joint_type'] = selected_btn.objectName().replace('JointBtn', ' joint')
            print(f"Joint type saved: {self.weldObj.info['joint_type']}")
            selected_btn.setStyleSheet("border: 2px solid rgb(30, 210, 80)")

    def edit_jointType(self):
        for JTBtn in self.jointTypesBtnsLayout.findChildren(QPushButton):
            if not JTBtn.isEnabled():
                JTBtn.setChecked(False)
                JTBtn.setEnabled(True)
        self.buttJointBtn.clicked.connect(lambda: self.select_jointType(self.buttJointBtn))
        self.lapJointBtn.clicked.connect(lambda: self.select_jointType(self.lapJointBtn))
        self.cornerJointBtn.clicked.connect(lambda: self.select_jointType(self.cornerJointBtn))
        self.teeJointBtn.clicked.connect(lambda: self.select_jointType(self.teeJointBtn))
        self.edgeJointBtn.clicked.connect(lambda: self.select_jointType(self.edgeJointBtn))

    def highlight_jointContinuity(self):
        # button status changes before execution of this function!
        jointContinuity_btnName = self.weldObj.info['weld_continuity_type'] + 'WeldBtn'
        for btn in self.weldTypeFrame.findChildren(QPushButton):
            if btn.objectName() != jointContinuity_btnName and btn.objectName() != 'editJointContinuity':
                btn.setChecked(False)
                btn.setEnabled(False)
            else:
                if btn.objectName() != 'editJointContinuity':
                    btn.setChecked(True)
                    btn.setEnabled(True)
        self.weldGraph.transformWeldSymbolType(self.weldObj.info['weld_continuity_type'])

    def select_jointContinuity(self, selected_btn: QPushButton):
        for btn in self.weldTypeFrame.findChildren(QPushButton):
            if btn is not selected_btn:
                btn.setChecked(False)
            else:
                btn.setChecked(True)
        self.weldObj.info['weld_continuity_type'] = selected_btn.text().lower()
        print(f"Joint continuity type saved: {self.weldObj.info['weld_continuity_type']}")

    def edit_jointContinuity(self):
        for btn in self.weldTypeFrame.findChildren(QPushButton):
            if not btn.isEnabled():
                btn.setChecked(False)
                btn.setEnabled(True)

        self.normalWeldBtn.clicked.connect(
            lambda: (self.select_jointContinuity(self.normalWeldBtn),
                     self.weldGraph.transformWeldSymbolType("normal")))
        self.intermittentWeldBtn.clicked.connect(
            lambda: (self.select_jointContinuity(self.intermittentWeldBtn),
                     self.weldGraph.transformWeldSymbolType("intermittent")))
        self.staggeredWeldBtn.clicked.connect(
            lambda: (self.select_jointContinuity(self.staggeredWeldBtn),
                     self.weldGraph.transformWeldSymbolType("staggered")))

    def load_lineInfo(self):
        for key in self.lineEdits.keys():
            self.lineEdits[key].setText(self.weldObj.info[key])
            if self.weldObj.info[key] is None:
                self.lineEdits[key].setPlaceholderText('not specified')
                if key == 'wps_number':
                    self.wpsMissingCBox.setChecked(True)
            else:
                if key == 'wps_number':
                    self.showPdfViewer(self.wpsDocsViewer, self.weldObj.wps_filepath)
                    self.tabWidget.setCurrentIndex(1)

    def showPdfViewer(self, container: QWidget, filepath=None):
        if filepath is None:
            options = QFileDialog.Options()
            filepath, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                      "pdf (*.pdf);;All Files (*)", options=options)
            self.wps_filepath = filepath
        if len(container.findChildren(QLayout)) == 0:
            pdfViewerWidget = pdfviewer.pdfViewerWidget(fr'{filepath}')
            print(f"Creating layout for pdfViewerWidget...")
            layout = QVBoxLayout()
            layout.setObjectName(f'wpsDocsViewerLayout')
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(pdfViewerWidget)
            container.setLayout(layout)
        else:
            old_pdf = container.findChild(pdfviewer.pdfViewerWidget)
            old_pdf.deleteLater()
            old_pdf.hide()
            newPdfViewer = pdfviewer.pdfViewerWidget(fr'{filepath}')
            container.layout().addWidget(newPdfViewer)
            self.wps_filepath = filepath
            self.wpsNumberLine.setText(pathlib.Path(filepath).stem)
            #   TODO: reprogram the pdfViewer to be QWidget so it could be easily replaced.

    def load_testingMethods(self):
        methods_selected = self.weldObj.info['testing_methods']
        for btn in self.weldTestingBtns.findChildren(QPushButton):
            if methods_selected.count(btn.objectName().replace('testMthdBtn', '')) > 0:
                btn.setChecked(True)
            else:
                btn.setEnabled(False)

    def edit_testingMethods(self):
        for btn in self.weldTestingBtns.findChildren(QPushButton):
            if not btn.isEnabled():
                btn.setEnabled(True)
        self.testMthdBtnLT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnLT))
        self.testMthdBtnMT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnMT))
        self.testMthdBtnPT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnPT))
        self.testMthdBtnVT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnVT))
        self.testMthdBtnRT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnRT))
        self.testMthdBtnUT.clicked.connect(lambda: self.select_testingMethod(self.testMthdBtnUT))

    def select_testingMethod(self, selected_btn: QPushButton):
        if type(self.weldObj.info['testing_methods']) is str:
            self.weldObj.info['testing_methods'] = self.weldObj.info['testing_methods'].split(';')
        if not selected_btn.isChecked():
            self.weldObj.info['testing_methods'].remove(selected_btn.text())
            self.weldObj.info['testing_methods'].sort()
            print(
                f"{selected_btn.text()} removed from testing methods. New list {self.weldObj.info['testing_methods']} saved.")
        else:
            if self.weldObj.info['testing_methods'] is None:
                self.weldObj.info['testing_methods'] = [selected_btn.text()]
                print(f"Single testing method selected: {self.weldObj.info['testing_methods']} has been saved.")
            else:
                self.weldObj.info['testing_methods'].append(selected_btn.text())
                self.weldObj.info['testing_methods'].sort()
                print(f"Selected testing methods: {self.weldObj.info['testing_methods']} has been saved")

    def replaceWeld(self):  # TODO
        print(self.weldObj.info)
        for key in self.weldGraph.upperWeldData.keys():
            self.weldObj.info[key] = self.weldGraph.upperWeldData[key]
        if self.weldGraph.lowerWeldInfo.isVisible():
            for key in self.weldGraph.lowerWeldData.keys():
                self.weldObj.info[key] = self.weldGraph.lowerWeldData[key]
        for key in self.weldGraph.weldBanners.keys():
            self.weldObj.info[key] = self.weldGraph.weldBanners[key]
        if self.weldObj.info['testing_methods'] is not None:
            if type(self.weldObj.info['testing_methods']) is str:
                self.weldObj.info['testing_methods'] = self.weldObj.info['testing_methods'].split(';')
            self.weldObj.info['testing_methods'] = ';'.join((self.weldObj.info['testing_methods']))
        else:
            self.weldObj.info['testing_methods'] = None
        self.weldObj.replace_weld(self.wps_filepath)
        self.close()


if __name__ == '__main__':
    db = gnrl_database_con.Database()
    app = QApplication(sys.argv)
    mainConstruction = db_objects.MainConstruction(connected_database=db)
    mainConstruction.load_info(1)
    subConstruction = db_objects.SubConstruction(parentConstruction=mainConstruction, connected_database=db)
    subConstruction.load_info(1)
    # mainWindow = NewWeldDialog(parentConstruction=subConstruction)
    mainWindow = WeldPreviewDialog(subConstruction, 5)
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
