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

class WeldGraphWidget(QWidget):
    def __init__(self):
        super(WeldGraphWidget, self).__init__()
        loadUi(r"weldGraphWidget.ui", self)

        self.lowerWeldInfo.hide()
        self.lowerWeldInfo.setEnabled(False)
        self.addSideWeld.clicked.connect(lambda: self.toggleSideWeld())
        # ---------------------------------------------------------------Button scripting------------------------------
        self.upperWeldTypeIcon.clicked.connect(
            lambda: self.openWeldTypeDialog(self.upperWeldTypeIcon, 'weldType', False))
        self.upperWeldFaceIcon.clicked.connect(
            lambda: self.openWeldTypeDialog(self.upperWeldFaceIcon, 'weldFace', False))

        self.lowerWeldTypeIcon.clicked.connect(
            lambda: self.openWeldTypeDialog(self.lowerWeldTypeIcon, 'weldType', True))
        self.lowerWeldFaceIcon.clicked.connect(
            lambda: self.openWeldTypeDialog(self.lowerWeldFaceIcon, 'weldFace', True))

        self.weldAsemblyIcon.clicked.connect(lambda: self.weldAsemblyIcon.setIcon(QtGui.QIcon(QtGui.QPixmap(
            r':/Icons/Icons/weldIcon_weldBanner.png'))) if self.weldAsemblyIcon.isChecked() else
        self.weldAsemblyIcon.setIcon(QtGui.QIcon(QtGui.QPixmap(r':/Icons/Icons/banner_weld_face.png'))))
        self.weldRoundedIcon.clicked.connect(lambda: self.weldRoundedIcon.setIcon(QtGui.QIcon(QtGui.QPixmap(
            r':/Icons/Icons/weldIcon_weldRoundedLine.png'))) if self.weldRoundedIcon.isChecked() else
        self.weldRoundedIcon.setIcon(QtGui.QIcon(QtGui.QPixmap(r':/Icons/Icons/weldIcon_weldLine.png'))))

    def toggleSideWeld(self):
        if self.addSideWeld.isChecked():
            self.lowerWeldInfo.show()
            self.addSideWeld.setStyleSheet("color: rgb(0, 0, 0);"
                                           "background-color : rgb(30, 210, 80)")
            self.lowerWeldInfo.setEnabled(True)
        else:
            self.lowerWeldInfo.hide()
            self.lowerWeldInfo.setEnabled(False)
            self.addSideWeld.setStyleSheet("color: rgb(150, 150, 150);"
                                           "background-color : rgb(255, 255, 255)")

    def openWeldTypeDialog(self, triggering_btn, dialogType: str, rotated: bool):
        # TODO: Make the dialog pop inside the weldGraphWidget not in the QApp center
        weld_dialog = weldTypeDialog(dialogType)
        weld_dialog.setWindowFlags(Qt.FramelessWindowHint)
        weld_dialog.exec_()  # exec_() opens the Dialog and waits for user input
        # weld_dialog.show() just opens the Dialog and do not wait for user input
        print(f'Chosen btn: {weld_dialog.selected_btn}')
        px = weld_dialog.selected_btn_icon.pixmap(QtCore.QSize(20, 20))
        if rotated:
            px = px.transformed(QtGui.QTransform().scale(1, -1))
        px = QtGui.QIcon(px)
        triggering_btn.setIcon(px)

    def transformWeldSymbolType(self, new_type):
        if new_type == "normal":
            self.staggeredGraph.hide()
            self.upperWeldAmountLabel.hide()
            self.upperWeldLengthLine.hide()
            self.upperWeldSpacingFrame.hide()
            self.lowerWeldLengthLine.hide()
            self.lowerWeldAmountLabel.hide()
            self.lowerWeldSpacingFrame.hide()
        elif new_type == 'staggered':
            self.staggeredGraph.hide()
            self.upperStaggerSpacer.hide()
            self.lowerStaggerSpacer.hide()
            self.upperWeldAmountLabel.show()
            self.upperWeldLengthLine.show()
            self.upperWeldSpacingFrame.show()
            self.lowerWeldAmountLabel.show()
            self.lowerWeldLengthLine.show()
            self.lowerWeldSpacingFrame.show()
        else:
            self.staggeredGraph.show()
            self.upperStaggerSpacer.show()
            self.lowerStaggerSpacer.show()
            self.upperWeldAmountLabel.show()
            self.upperWeldLengthLine.show()
            self.upperWeldSpacingFrame.show()
            self.lowerWeldAmountLabel.show()
            self.lowerWeldLengthLine.show()
            self.lowerWeldSpacingFrame.show()


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
            self.weldFace_convex.clicked.connect(
                lambda: self.select_button(self.weldFaceBtns, self.weldFace_convex))
            self.weldFace_rect.clicked.connect(lambda: self.select_button(self.weldFaceBtns, self.weldFace_rect))
            self.weldFace_flat.clicked.connect(lambda: self.select_button(self.weldFaceBtns, self.weldFace_flat))
            self.weldFace_concave.clicked.connect(
                lambda: self.select_button(self.weldFaceBtns, self.weldFace_concave))
            self.weldFace_anchor.clicked.connect(
                lambda: self.select_button(self.weldFaceBtns, self.weldFace_anchor))
            self.weldFace_chord.clicked.connect(lambda: self.select_button(self.weldFaceBtns, self.weldFace_chord))
            self.weldFace_banner.clicked.connect(
                lambda: self.select_button(self.weldFaceBtns, self.weldFace_banner))
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
    dialog = WeldGraphWidget()
    dialog.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
