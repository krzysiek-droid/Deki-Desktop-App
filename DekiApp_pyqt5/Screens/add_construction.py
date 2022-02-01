import sys
import win32gui
from PyQt5 import QtGui
from PyQt5 import QtOpenGL
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from Screens import resources_rc

import cadview_script


class addConsPos(QDialog):
    def __init__(self):
        super(addConsPos, self).__init__()
        loadUi(r'add_construction.ui', self)

        self.cadModelViewWidget = cadview_script.CadViewer(
            step_filepath="../DekiResources/Zbiornik LNG assembly.stp")

        # Create Layout for cadModelViewWidget
        grid = QHBoxLayout()

        grid.addWidget(self.cadModelViewWidget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        self.cadViewerContainer.setLayout(grid)

        # To start vieweing the cadModel it is needed to call the _display member of viewer, and call the method for
        # render and display such as DisplayShape() etc.;   Test() to display sample model
        self.cadModelViewWidget.start_display()





def main():
    app = QApplication(sys.argv)

    mainWindow = addConsPos()
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")


if __name__ == '__main__':
    main()
