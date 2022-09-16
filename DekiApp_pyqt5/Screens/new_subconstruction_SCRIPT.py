import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
import db_objects
import new_construction_SCRIPT as newConstructionScreen


class NewSubconstructionDialog(QDialog):
    # db_ParentConstruction has to be a database object class -> db_object.MainConstruction
    def __init__(self, db_ParentConstruction=None):
        super(NewSubconstructionDialog, self).__init__()
        self.pdfViewerWidget = None
        self.cadModelViewWidget = None
        self.parentConstruction = db_ParentConstruction
        loadUi(r'new_subconstruction_UI.ui', self)
        if not db_ParentConstruction:
            print(f'Subconstruction screen loaded without parent construction')
        else:
            print(f'Parent construction loaded: {self.parentConstruction.info}')

        #   ------------------------------------Hidden content----------------------------------------------------------
        self.newSubconstructionSubcontractor.hide()
        self.newSubconstructionSubcontractorContact.hide()

        # ----------------------------------------Screen boarding
        # scripts-----------------------------------------------------
        self.parentConstructionPicture.setPixmap(self.parentConstruction.picture.scaled(250, 250, 1, 1))
        self.parentConstructNameLabel.setText(self.parentConstruction.info['name'])
        self.parentConstructTagLabel.setText(self.parentConstruction.info['tag'])
        self.parentConstructNumberLabel.setText(self.parentConstruction.info['serial_number'])
        self.parentConstructOwnerLabel.setText(self.parentConstruction.info['owner'])
        self.parentConstructMaterialLabel.setText(self.parentConstruction.info['material'])
        self.parentConstructLocalizationLabel.setText(self.parentConstruction.info['localization'])
        self.parentConstructAdditionalInfoLabel.setText(self.parentConstruction.info['additional_info'])
        self.parentConstructTypeLabel.setText(self.parentConstruction.info['construct_type'])
        self.parentConstructQualityNormLabel.setText(self.parentConstruction.info['quality_norm'])
        self.parentConstructQualityClassLabel.setText(self.parentConstruction.info['quality_class'])
        self.parentConstructTolerancesNormLabel.setText(self.parentConstruction.info['tolerances_norm'])
        self.parentConstructTolerancesLevelLabel.setText(self.parentConstruction.info['tolerances_level'])
        self.parentConstructSubcontractorLabel.setText(self.parentConstruction.info['subcontractor'])
        self.parentConstructSubcontractorContactLabel.setText(self.parentConstruction.info['sub_contact'])
        # ----------------------------------------Button
        # scripts--------------------------------------------------------------
        self.showParentConstructionCadModel.clicked.connect(lambda: print(f'show parent CAD'))
        self.goToParentConstructionPreview.clicked.connect(lambda: print(f'going back to parent construction'))
        self.showParentConstructionDocs.clicked.connect(lambda: print(f'showing parent construction 2D documentary'))
        self.newSubconstructionAddCadBtn.clicked.connect(lambda: self.showStepModel())
        self.newSubconstructionAddDocsBtn.clicked.connect(lambda: self.showPdfViewer())

        self.newSubconstructionAddSubcontractorBtn.toggled.connect(lambda: (self.newSubconstructionSubcontractor.show(),
                                                                            self.newSubconstructionSubcontractorContact.show()) if self.newSubconstructionAddSubcontractorBtn.isChecked()
        else (self.newSubconstructionSubcontractor.hide(), self.newSubconstructionSubcontractorContact.hide()))

        self.newSubconstructionAddSubconstruction.clicked.connect(lambda: self.addSubConstruction())
        #   -----------------------------------------Signals------------------------------------------------------------

        #   ------------------------------------ComboBoxes scripts------------------------------------------------------
        self.newSubconstructionTypeCombo.addItems(newConstructionScreen.quality_norms.keys())
        self.newSubconstructionTypeCombo.activated.connect(
            lambda: self.quality_combos_activate(self.newSubconstructionTypeCombo.currentText()))
        self.newSubconstructionQualityNormCombo.addItems(
            norm[0] for norm in newConstructionScreen.quality_norms.values())
        self.quality_combos_activate(self.newSubconstructionTypeCombo.currentText())
        self.newSubconstructionTolerancesNormCombo.addItems(newConstructionScreen.tolerances_norms.keys())
        self.newSubconstructionTolerancesNormCombo.activated.connect(lambda: self.tolerances_combos_activate(
            self.newSubconstructionTolerancesNormCombo.currentText()))
        self.tolerances_combos_activate(self.newSubconstructionTolerancesNormCombo.currentText())

    def showStepModel(self):
        # define filechooser dialog
        options = QFileDialog.Options()
        # open filechooser dialog and save selection
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "stp (*.stp);;All Files (*);;step (*.step)", options=options)
        if fileName:
            if not self.cadModelViewWidget:
                self.cadModelViewWidget = newConstructionScreen.CadViewerExtended(fileName)
                # Create Layout for cadModelViewWidget
                grid = QVBoxLayout()
                grid.addWidget(self.cadModelViewWidget)
                self.cadViewerContainer.setLayout(grid)
            else:
                pass

    def showPdfViewer(self):
        from Screens import pdfViewWidget_SCRIPT as pdfviewer
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "pdf (*.pdf);;All Files (*)", options=options)
        if fileName:
            print(f'Opening pdf: {fileName}')
            self.pdfViewerWidget = pdfviewer.pdfViewerWidget(fileName, parent=self.docsViewerContainer)
            # Create layout for pdfViewerWidget
            grid = QHBoxLayout()
            grid.addWidget(self.pdfViewerWidget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            # Insert a pdfViewerWidget into docViewer Widget (widget for pdf viewing)
            self.docsViewerContainer.setLayout(grid)

    def addSubConstruction(self):
        print('adding to database...')
        new_subConstruction = db_objects.SubConstruction(parentConstruction=self.parentConstruction)
        print(self.parentConstruction.info)
        new_subConstruction.info = {'id': new_subConstruction.update_records_amount() + 1,
                                    'parent_construction_id': self.parentConstruction.info['id'],
                                    'main_construction_id': self.parentConstruction.main_constructionID,
                                    'name': self.newSubconstructionName.text(),
                                    'tag': self.newSubconstructionTag.text(),
                                    'serial_number': self.newSubconstructionSerialNo.text(),
                                    'owner': self.newSubconstructionOwner.text(),
                                    'localization': self.newSubconstructionLocalization.text(),
                                    'material': self.newSubconstructionMainMaterial.text(),
                                    'additional_info': "N/A" if len(self.newSubconstructionAdditionalInfoLine.text()) == 0 else
                                    self.newSubconstructionAdditionalInfoLine.text(),
                                    'subcontractor': "N/A" if len(self.newSubconstructionSubcontractor.text()) == 0 else
                                    self.newSubconstructionSubcontractor.text(),
                                    'sub_contact': "N/A" if len(self.newSubconstructionSubcontractorContact.text()) == 0 else
                                    self.newSubconstructionSubcontractorContact.text(),
                                    'construct_type': str(self.newSubconstructionTypeCombo.currentText()),
                                    'quality_norm': str(self.newSubconstructionQualityNormCombo.currentText()),
                                    'quality_class': str(self.newSubconstructionQualityClassCombo.currentText()),
                                    'tolerances_norm': str(self.newSubconstructionTolerancesNormCombo.currentText()),
                                    'tolerances_level': str(self.newSubconstructionTolerancesLevelCombo.currentText())}
        new_subConstruction.picture = self.cadModelViewWidget.screenshot
        new_subConstruction.pdfDocsPath = self.pdfViewerWidget.filepath
        new_subConstruction.stpModelPath = self.cadModelViewWidget.filepath
        print('subconstruct created.')
        new_subConstruction.save_subConstruction()
        print("MainConstruction added to database successfully.")
        if type(self.parent()) == QStackedWidget:
            import construction_preview_SCRIPT
            self.parent().addWidget(
                construction_preview_SCRIPT.ConstructPreviewDialog(new_subConstruction.info['id']))
            self.parent().setCurrentIndex(self.parent().indexOf(self) + 1)
            self.parent().removeWidget(self)

    def quality_combos_activate(self, chosen):
        self.newSubconstructionQualityNormCombo.setCurrentText(newConstructionScreen.quality_norms[chosen][0])
        self.newSubconstructionQualityClassCombo.clear()
        self.newSubconstructionQualityClassCombo.setEnabled(True)
        self.newSubconstructionQualityClassCombo.addItems(
            newConstructionScreen.quality_norms[chosen][1]) if type(
            newConstructionScreen.quality_norms[chosen][
                1]) == list else self.newSubconstructionQualityClassCombo.addItem(
            newConstructionScreen.quality_norms[chosen][1])

    def tolerances_combos_activate(self, chosen):
        self.newSubconstructionTolerancesLevelCombo.clear()
        self.newSubconstructionTolerancesLevelCombo.setEnabled(True)
        self.newSubconstructionTolerancesLevelCombo.addItems(newConstructionScreen.tolerances_norms[chosen])


#   ----------------------------------------Main script (for Screen testing purposes)-----------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # mainWindow = CadViewerExtended("../DekiResources/Zbiornik LNG assembly.stp")
    dummy_constructionObject = db_objects.MainConstruction()
    dummy_constructionObject.load_info(1)
    mainWindow = NewSubconstructionDialog(db_ParentConstruction=dummy_constructionObject)
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
