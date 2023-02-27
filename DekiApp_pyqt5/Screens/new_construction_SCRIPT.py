import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.Qt import QTimer
from Screens import cadViewWidget_SCRIPT as cadviewer
from Screens import pdfViewWidget_SCRIPT as pdfviewer

import db_objects
import json

with open(r"D:\CondaPy - Projects\PyGUIs\DekiApp_pyqt5\app_settings.json", 'r') as s:
    file = s.read()
    quality_norms = json.loads(file)['quality_norms']
    print(quality_norms)
    tolerances_norms = json.loads(file)['tolerances_norms']
    srv_files_filepath = json.loads(file)['srv_files_filepath']

class CadViewerExtended(QWidget):
    def __init__(self, step_filepath: str):
        super().__init__()
        # set attribute that deletes the instance of this class on closeEvent
        self.setAttribute(Qt.WA_DeleteOnClose)
        loadUi(r'cadViewWidgetExtended.ui', self)
        self.filepath = step_filepath
        self.screenshot = QtGui.QPixmap()

        import cadViewWidget_SCRIPT
        self.cadViewerLayout: QLayout = cadViewWidget_SCRIPT.CadViewerLayout(self.filepath)
        self.viewerFrame.setLayout(self.cadViewerLayout)
        self.cadViewerLayout.start_display()

        self.izoViewBtn.clicked.connect(lambda: self.cadViewerLayout.display.View_Iso())
        self.snapshootBtn.clicked.connect(lambda: self.takeScreenshot())
        self.fullscreenBtn.clicked.connect(lambda: print('TODO fullscreen ?'))

    def takeScreenshot(self):
        QtCore.QTimer.singleShot(100, self.saveScreenshot)
        # self.canvas.display.ExportToImage('test.png') could do the work, but it saves image without creating a
        # class for it

    def saveScreenshot(self):
        self.screenshot = self.viewerFrame.screen().grabWindow(self.cadViewerLayout.canvas.winId())
        pic = QLabel()
        pic.setPixmap(self.screenshot.scaled(150, 100))
        self.cadModelPictureView.setText('')
        self.cadModelPictureView.setPixmap(self.screenshot.scaled(150, 100))
        # self.screenshot.save('screenshot.png', 'png')

    def screenshot_retry(self):
        pass
        # TODO: change the screenshot preview to notification dialog with approval of user in order to maintain
        # TODO: STP file open during the decision of screenshot approval

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        self.resize(300, 300)


class NewConstructDialog(QDialog):
    def __init__(self):
        super(NewConstructDialog, self).__init__()
        # set attribute that deletes the instance of this class on closeEvent
        self.setAttribute(Qt.WA_DeleteOnClose)
        loadUi(r'new_construction_UI.ui', self)
        print(QApplication.topLevelWidgets())

        #   ------------------------------------Class members-----------------------------------------------------------
        self.cadModelViewWidget = None  # QWidget
        self.dxfModelWidget = None  # QWidget
        self.pdfViewerWidget = None  # QWidget
        #   ------------------------------------Hidden content----------------------------------------------------------
        self.constructSubcontractorLine.hide()
        self.subContractorContact.hide()

        #   ------------------------------------Buttons scripts---------------------------------------------------------
        self.cadModelBtn_3.clicked.connect(lambda: (self.showStepModel(),
                                                    self.cadModelBtn_3.setText('Change step model')))
        self.documentationLinktbn_3.clicked.connect(lambda: self.showPdfViewer())  # Show .pdf document
        self.addConstructionBtn.clicked.connect(lambda: self.addConstruction())
        self.coopProductionBtn.toggled.connect(lambda:
                                               (self.constructSubcontractorLine.show(),
                                                self.subContractorContact.show()) if self.coopProductionBtn.isChecked() else
                                               (self.constructSubcontractorLine.hide(),
                                                self.subContractorContact.hide()))

        #   ------------------------------------ComboBoxes scripts------------------------------------------------------
        self.constructTypeCombo.addItems(quality_norms.keys())
        self.constructTypeCombo.activated.connect(
            lambda: self.quality_combos_activate(self.constructTypeCombo.currentText()))
        self.constructQualityNormCombo.addItems(norm[0] for norm in quality_norms.values())
        self.quality_combos_activate(self.constructTypeCombo.currentText())
        self.constructTolerancesNormCombo.addItems(tolerances_norms.keys())
        self.constructTolerancesNormCombo.activated.connect(lambda: self.tolerances_combos_activate(
            self.constructTolerancesNormCombo.currentText()))
        self.tolerances_combos_activate(self.constructTolerancesNormCombo.currentText())

        # ---------------------------------------Signals----------------------------------------------------------------
        # validator = QtGui.QRegExpValidator(QtCore.QRegExp(r"^[a-zA-Z0-9.,_%+- ]*"), self)
        for widget in self.findChildren(QLineEdit):
            # widget.setValidator(validator)
            widget.editingFinished.connect(lambda: self.addConstructionBtn.setEnabled(True) if self.validate_info() else
            self.addConstructionBtn.setEnabled(False))

    #   ------------------------------------Class functions-------------------------------------------------------------
    def showStepModel(self):
        # define filechooser dialog
        options = QFileDialog.Options()
        # open filechooser dialog and save selection
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "stp (*.stp);;All Files (*);;step (*.step)", options=options)
        if fileName:
            if not self.cadModelViewWidget:
                self.cadModelViewWidget = CadViewerExtended(fileName)
                # Create Layout for cadModelViewWidget
                grid = QVBoxLayout()
                grid.addWidget(self.cadModelViewWidget)
                self.cadViewerContainer.setLayout(grid)
                if self.validate_info():
                    self.addConstructionBtn.setEnabled(True)
            else:
                old_viewer = self.cadViewerContainer.findChild(CadViewerExtended)
                old_viewer.deleteLater()
                old_viewer.hide()
                # Replace old Viewer with new Viewer with new CAD model
                self.cadModelViewWidget = CadViewerExtended(fileName)
                self.cadViewerContainer.layout().addWidget(self.cadModelViewWidget)
        else:
            pass

    def showDxfViewer(self):  # unused, for legacy stuff
        options = QFileDialog.Options()

        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;dxf (*.dxf)", options=options)
        if fileName:
            print(f'Opening dxf: {fileName}')
            self.dxfModelWidget = pdfviewer.dxfViewerWidget(fileName)
            # Create Layout for cadModelViewWidget
            grid = QHBoxLayout()
            grid.addWidget(self.dxfModelWidget)
            self.dxfViewer.setLayout(grid)

    def showPdfViewer(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "pdf (*.pdf);;All Files (*)", options=options)
        if fileName:
            if not self.pdfViewerWidget:
                self.pdfViewerWidget = pdfviewer.pdfViewerWidget(fileName)
                layout = QVBoxLayout()
                layout.addWidget(self.pdfViewerWidget)
                self.docsViewerContainer.setLayout(layout)
                if self.validate_info():
                    self.addConstructionBtn.setEnabled(True)
            else:
                old_viewer = self.docsViewerContainer.findChild(pdfviewer.pdfViewerWidget)
                old_viewer.deleteLater()
                old_viewer.hide()
                # Replace old Viewer with new Viewer with new CAD model
                self.cadModelViewWidget = pdfviewer.pdfViewerWidget(fileName)
                self.docsViewerContainer.layout().addWidget(self.cadModelViewWidget)

    def addConstruction(self):
        if self.validate_info():
            print('adding to database...')
            new_construction = db_objects.MainConstruction()
            new_construction.info = {'id': f'{new_construction.update_records_amount() + 1}',
                                     'name': self.constructNameLine.text(),
                                     'tag': self.constructTagLine.text(),
                                     'serial_number': self.constructNumberLine.text(),
                                     'owner': self.constructOwnerLine.text(),
                                     'localization': self.constructLocalizationLine.text(),
                                     'material': self.constructMaterialLine.text(),
                                     'additional_info': "N/A" if len(self.additionalInfoLine.text()) == 0 else
                                     self.additionalInfoLine.text(),
                                     'subcontractor': "N/A" if len(self.constructSubcontractorLine.text()) == 0 else
                                     self.constructSubcontractorLine.text(),
                                     'sub_contact': "N/A" if len(self.subContractorContact.text()) == 0 else
                                     self.subContractorContact.text(),
                                     'construct_type': str(self.constructTypeCombo.currentText()),
                                     'quality_norm': str(self.constructQualityNormCombo.currentText()),
                                     'quality_class': str(self.constructQualityClassCombo.currentText()),
                                     'tolerances_norm': str(self.constructTolerancesNormCombo.currentText()),
                                     'tolerances_level': str(self.constructTolerancesLevelCombo.currentText())}

            new_construction.picture = self.cadModelViewWidget.screenshot
            new_construction.pdfDocsPath = self.pdfViewerWidget.filepath
            new_construction.stpModelPath = self.cadModelViewWidget.filepath
            new_construction.save_main_construction()
            print("MainConstruction added to database successfully.")

            if type(self.parent()) == QStackedWidget:
                import construction_preview_SCRIPT
                self.parent().addWidget(construction_preview_SCRIPT.MainConstructionDialog(new_construction.info['id']))
                self.parent().setCurrentIndex(self.parent().indexOf(self) + 1)
                self.parent().removeWidget(self)

    def validate_info(self):
        for lineEdit in self.findChildren(QLineEdit):
            if not lineEdit.objectName() == 'additionalInfoLine':
                if self.coopProductionBtn.isChecked():
                    print(lineEdit.text())
                    if len(lineEdit.text()) == 0:
                        print(f'Fill in the {lineEdit.objectName()}, cooperative production is checked.')
                        return False
                else:
                    if not lineEdit.objectName() == 'constructSubcontractorLine' and lineEdit.objectName() != \
                            'subContractorContact':
                        if len(lineEdit.text()) == 0:
                            print(lineEdit.text())
                            print(f'Fill in the {lineEdit.objectName()}, second condition')
                            return False
        if self.validate_members():
            print('Validation succeeded.')
            return True
        else:
            print('Validation has not succeeded. Check the CAD model and Docs paths.')
            return False

    def validate_members(self):
        if self.cadModelViewWidget is not None and self.pdfViewerWidget is not None:
            return True
        return False

    def quality_combos_activate(self, chosen):
        self.constructQualityNormCombo.setCurrentText(quality_norms[chosen][0])
        self.constructQualityClassCombo.clear()
        self.constructQualityClassCombo.setEnabled(True)
        self.constructQualityClassCombo.addItems(
            quality_norms[chosen][1]) if type(
            quality_norms[chosen][1]) == list else self.constructQualityClassCombo.addItem(quality_norms[chosen][1])

    def tolerances_combos_activate(self, chosen):
        self.constructTolerancesLevelCombo.clear()
        self.constructTolerancesLevelCombo.setEnabled(True)
        self.constructTolerancesLevelCombo.addItems(tolerances_norms[chosen])


#   ----------------------------------------Main script (for Screen testing purposes)-----------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = NewConstructDialog()
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
