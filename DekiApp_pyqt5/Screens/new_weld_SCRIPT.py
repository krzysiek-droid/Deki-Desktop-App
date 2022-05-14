import sys

from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtCore

from Screens import pdfViewWidget_SCRIPT as pdfviewer

import db_objects as dbo
import resources_rc


class NewWeldDialog(QDialog):
    def __init__(self, parent_constructionId):
        super(NewWeldDialog, self).__init__()
        loadUi(r'new_weld_UI.ui', self)
        self.selected_weldType = None
        self.selected_weldFaces = []
        self.pdfViewerWidget = None
        self.parentConstruction = dbo.Construction()
        self.parentConstruction.load_info(parent_constructionId)
        # ---------------------------------------------------------------Screen loading functions----------------------
        for line in self.lowerWeldFrame.children():
            if not line.objectName() == 'gridLayout_7' and not line.objectName() == 'lowerWeldTypeIcon':
                line.hide()
        self.showPdfViewer()

        # ---------------------------------------------------------------Button scripting------------------------------
        self.upperWeldTypeIcon.clicked.connect(lambda: self.openUpperWeldTypeDialog(self.upperWeldTypeIcon, 'weldType'))
        self.upperWeldFaceIcon.clicked.connect(lambda: self.openUpperWeldTypeDialog(self.upperWeldFaceIcon, 'weldFace'))

        self.lowerWeldTypeIcon.clicked.connect(lambda: self.openLowerWeldTypeDialog(self.lowerWeldTypeIcon, 'weldType'))
        self.lowerWeldFaceIcon.clicked.connect(lambda: self.openLowerWeldTypeDialog(self.lowerWeldFaceIcon, 'weldFace'))

        self.weldAsemblyIcon.clicked.connect(lambda: self.weldAsemblyIcon.setIcon(QtGui.QIcon(QtGui.QPixmap(
            r':/Icons/Icons/weldIcon_weldBanner.png'))) if self.weldAsemblyIcon.isChecked() else
        self.weldAsemblyIcon.setIcon(QtGui.QIcon(QtGui.QPixmap(r':/Icons/Icons/banner_weld_face.png'))))
        self.weldRoundedIcon.clicked.connect(lambda: self.weldRoundedIcon.setIcon(QtGui.QIcon(QtGui.QPixmap(
            r':/Icons/Icons/weldIcon_weldRoundedLine.png'))) if self.weldRoundedIcon.isChecked() else
        self.weldRoundedIcon.setIcon(QtGui.QIcon(QtGui.QPixmap(r':/Icons/Icons/weldIcon_weldLine.png'))))

        self.testMthdBtnLT.clicked.connect(lambda: self.select_buttons(self.weldTestingBtns, self.testMthdBtnLT))
        self.testMthdBtnMT.clicked.connect(lambda: self.select_buttons(self.weldTestingBtns, self.testMthdBtnMT))
        self.testMthdBtnPT.clicked.connect(lambda: self.select_buttons(self.weldTestingBtns, self.testMthdBtnPT))
        self.testMthdBtnVT.clicked.connect(lambda: self.select_buttons(self.weldTestingBtns, self.testMthdBtnVT))
        self.testMthdBtnRT.clicked.connect(lambda: self.select_buttons(self.weldTestingBtns, self.testMthdBtnRT))
        self.testMthdBtnUT.clicked.connect(lambda: self.select_buttons(self.weldTestingBtns, self.testMthdBtnUT))
        # -----------------------------------------------------------------UPDATE INFO---------------------------------

    def openUpperWeldTypeDialog(self, triggering_btn, dialogType: str):
        weld_dialog = weldTypeDialog(dialogType)
        weld_dialog.setWindowFlags(Qt.FramelessWindowHint)
        weld_dialog.exec_()  # exec_() opens the Dialog and waits for user input
        # weld_dialog.show() just opens the Dialog and do not wait for user input
        print(f'Chosen btn: {weld_dialog.selected_btn}')
        triggering_btn.setIcon(weld_dialog.selected_btn_icon)

    def openLowerWeldTypeDialog(self, triggering_btn, dialogType: str):
        weld_dialog = weldTypeDialog(dialogType)
        weld_dialog.setWindowFlags(Qt.FramelessWindowHint)
        weld_dialog.exec_()  # exec_() opens the Dialog and waits for user input
        # weld_dialog.show() just opens the Dialog and do not wait for user input
        print(f'Chosen btn: {weld_dialog.selected_btn}')
        px = weld_dialog.selected_btn_icon.pixmap(QtCore.QSize(20, 20))
        px = px.transformed(QtGui.QTransform().scale(1, -1))
        px = QtGui.QIcon(px)
        triggering_btn.setIcon(px)
        for line in self.lowerWeldFrame.children():
            if not line.objectName() == 'gridLayout_7' and not line.objectName() == 'lowerWeldTypeIcon':
                line.show()

    def select_buttons(self, btns_container: QFrame, selected_btn: QPushButton):
        if not selected_btn.isChecked():
            selected_btn.setStyleSheet("background-color : rgb(255, 255, 255)")
        else:
            selected_btn.setStyleSheet("background-color : rgb(30, 210, 80)")

    def showPdfViewer(self):
        if not self.pdfViewerWidget:
            print(self.parentConstruction.pdfDocsPath)
            self.pdfViewerWidget = pdfviewer.pdfViewerWidget(fr'{self.parentConstruction.pdfDocsPath}')
            # Create layout for pdfViewerWidget
            grid = QVBoxLayout()
            grid.addWidget(self.pdfViewerWidget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
            # Insert a pdfViewerWidget into docViewer Widget (widget for pdf viewing)
            # self.docsViewerContainer.removeWidget(QLabel)
            self.constructDocsViewer.setLayout(grid)
            # if self.validate_info():
            #     self.addConstructionBtn.setEnabled(True)
        else:
            pass

class weldTypeDialog(QDialog):
    def __init__(self, dialogType):
        super(weldTypeDialog, self).__init__()
        if dialogType == "weldType":
            loadUi(r"weldTypeDialog.ui", self)
            self.selected_btn = None
            self.selected_btn_icon = None

            self.weldType_184.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_184))
            self.weldType_114.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_114))
            self.weldType_064.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_064))
            self.weldType_134.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_134))
            self.weldType_164.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_164))
            self.weldType_174.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_174))
            self.weldType_014.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_014))
            self.weldType_104.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_104))
            self.weldType_074.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_074))
            self.weldType_124.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_124))
            self.weldType_204.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_204))
            self.weldType_194.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_194))
            self.weldType_024.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_024))
            self.weldType_094.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_094))
            self.weldType_144.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_144))
            self.weldType_054.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_054))
            self.weldType_044.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_044))
            self.weldType_084.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_084))
            self.weldType_214.clicked.connect(lambda: self.select_button(self.weldTypesBtns, self.weldType_214))
        else:
            loadUi(r"weldFaceDialog.ui", self)
            self.selected_btn = None
            self.selected_btn_icon = None
            self.weldFace_circline.clicked.connect(
                lambda: self.select_button(self.weldFaceBtns, self.weldFace_circline))
            self.weldFace_convex.clicked.connect(lambda: self.select_button(self.weldFaceBtns, self.weldFace_convex))
            self.weldFace_rect.clicked.connect(lambda: self.select_button(self.weldFaceBtns, self.weldFace_rect))
            self.weldFace_flat.clicked.connect(lambda: self.select_button(self.weldFaceBtns, self.weldFace_flat))
            self.weldFace_concave.clicked.connect(lambda: self.select_button(self.weldFaceBtns, self.weldFace_concave))
            self.weldFace_anchor.clicked.connect(lambda: self.select_button(self.weldFaceBtns, self.weldFace_anchor))
            self.weldFace_chord.clicked.connect(lambda: self.select_button(self.weldFaceBtns, self.weldFace_chord))
            self.weldFace_banner.clicked.connect(lambda: self.select_button(self.weldFaceBtns, self.weldFace_banner))
            self.weldFace_circ.clicked.connect(lambda: self.select_button(self.weldFaceBtns, self.weldFace_circ))

    def select_button(self, btns_container: QFrame, selected_btn: QPushButton):
        if not selected_btn.isChecked():
            selected_btn.setStyleSheet("background-color : rgb(255, 255, 255)")
        else:
            for btn in btns_container.findChildren(QPushButton):
                if not btn == selected_btn:
                    btn.setStyleSheet("background-color : rgb(255, 255, 255)")
            selected_btn.setStyleSheet("background-color : rgb(30, 210, 80)")
            self.selected_btn = selected_btn.objectName()
            self.selected_btn_icon = selected_btn.icon()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = NewWeldDialog(1)
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")