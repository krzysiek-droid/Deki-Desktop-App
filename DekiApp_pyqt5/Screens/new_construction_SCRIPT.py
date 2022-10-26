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

quality_norms = {'pressure equipment': ['PED_97_23_WE', 'N/A'], 'pipelines': ['EN 13480', 'N/A'], 'railways':
    ['EN 15085', 'N/A'], 'welded structures': ['EN 1090', ['EXC1', 'EXC2', 'EXC3', 'EXC4']]}

tolerances_norms = {'ISO 13920': ['1', '2', '3'], 'ISO 2768': ['s', 'm', 'l']}
srv_files_filepath = r'D:\dekiApp\Deki_ServerFiles'


class CadViewerExtended(QWidget):
    def __init__(self, step_filepath: str):
        super().__init__()
        # set attribute that deletes the instance of this class on closeEvent
        self.setAttribute(Qt.WA_DeleteOnClose)
        loadUi(r'cadViewWidgetExtended.ui', self)
        self.filepath = step_filepath
        self.screenshot = QtGui.QPixmap()

        import cadViewWidget_SCRIPT
        self.cadViewerWidget = cadViewWidget_SCRIPT.CadViewer(self.filepath,
                                                              viewport_width=self.viewerFrame.baseSize().width(),
                                                              viewport_height=self.viewerFrame.baseSize().height())
        self.viewerFrameLayout.addWidget(self.cadViewerWidget)
        self.cadViewerWidget.start_display()

        self.izoViewBtn.clicked.connect(lambda: self.cadViewerWidget.display.View_Iso())
        self.snapshootBtn.clicked.connect(lambda: self.takeScreenshot())
        self.fullscreenBtn.clicked.connect(lambda: print('TODO fullscreen ?'))

    def takeScreenshot(self):
        QtCore.QTimer.singleShot(100, self.saveScreenshot)
        # self.canvas.display.ExportToImage('test.png') could do the work, but it saves image without creating a
        # class for it

    def saveScreenshot(self):
        self.screenshot = self.cadViewerWidget.screen().grabWindow(self.cadViewerWidget.canvas.winId())
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
        self.cadModelBtn_3.clicked.connect(lambda: self.showStepModel())  # Show CAD step model
        self.documentationLinktbn_3.clicked.connect(lambda: self.showPdfViewer())  # Show .pdf document
        self.addConstructionBtn.clicked.connect(lambda: self.addConstruction())
        self.coopProductionBtn.toggled.connect(lambda:
                                               (self.constructSubcontractorLine.show(),
                                                self.subContractorContact.show()) if self.coopProductionBtn.isChecked() else
                                               (self.constructSubcontractorLine.hide(),
                                                self.subContractorContact.hide()))

        # import InspectionPlannerScreen_SCRIPT
        # self.goBackBtn.clicked.connect(lambda:
        #     self.parent().changeScreen(self, InspectionPlannerScreen_SCRIPT.InspectionPlannerScreen()) if self.parent() is not None
        #     else print('no parent'))

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
                pass
            # TODO: add the script for STEP preview model change

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
            print(f'Opening pdf: {fileName}')
            self.pdfViewerWidget = pdfviewer.pdfViewerLayout(fileName, parent=self.docsViewerContainer)
            # Insert a pdfViewerLayout into docViewer Widget (widget for pdf viewing)
            self.docsViewerContainer.setLayout(self.pdfViewerWidget.main_layout)
            if self.validate_info():
                self.addConstructionBtn.setEnabled(True)

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
                self.parent().addWidget(construction_preview_SCRIPT.ConstructPreviewDialog(new_construction.info['id']))
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

    # mainWindow = CadViewerExtended("../DekiResources/Zbiornik LNG assembly.stp")
    mainWindow = NewConstructDialog()
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
