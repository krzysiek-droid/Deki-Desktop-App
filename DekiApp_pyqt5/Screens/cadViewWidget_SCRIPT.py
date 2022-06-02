import logging
import sys

import resources_rc

import PyQt5.QtCore
from PyQt5.QtWidgets import *

from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from PyQt5 import QtGui

from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
# Reads STEP files, checks them and translates their contents into Open CASCADE models
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.backend import load_backend, get_qt_modules

log = logging.getLogger(__name__)
used_backend = load_backend()
log.info("GUI backend set to: {0}".format(used_backend))
print("GUI backend set to: {0}".format(used_backend))


# TODO: add buttons for rotation of CAD Model etc.


class CadViewer(QWidget):
    def __init__(self, step_filepath: str, viewport_width=300, viewport_height=300):
        super(CadViewer, self).__init__()
        self.setMinimumSize(viewport_width, viewport_height)
        # Class members
        self.display = None
        self.shape = None
        self.filepath = step_filepath

        # --------------------------------------------------CadViewer setup---------------------------------------------
        # Create layout for 3D canvas
        self.qtViewer3DContainer = QVBoxLayout(self)

        # Viewer init, define the widget's appearance, must be resized after definition to center itself
        # in widget container (layout)
        import OCC.Display.qtDisplay as qtDisplay
        self.canvas = qtDisplay.qtViewer3d()
        self.canvas.resize(viewport_width - 10, viewport_height - 10)

        # Nor canvas nor qtViewer3Container cannot be aligned, otherwise widget do not shows itself
        self.qtViewer3DContainer.addWidget(self.canvas)
        self.setLayout(self.qtViewer3DContainer)
        # ---------------------------------------------------Buttons----------------------------------------------------

        # ------------------------------------------------Call class functions------------------------------------------
        self.read_stepFile(self.filepath)

    # ----------------------------------------------Class Functions---------------------------------------------------
    def read_stepFile(self, step_filepath):
        step_reader = STEPControl_Reader()
        status = step_reader.ReadFile(step_filepath)
        if status == IFSelect_RetDone:  # RetDone : normal execution with a result
            # to print stepByStep rendering:
            # step_reader.PrintCheckLoad(True, IFSelect_ItemsByEntity)
            step_reader.TransferRoot()
            self.shape = step_reader.Shape()
        else:
            print("Error: can't read file.")
            sys.exit(0)

    def start_display(self):
        self.canvas.resize(300, 300)
        self.canvas.InitDriver()
        self.display = self.canvas._display

        from OCC.Core.Quantity import Quantity_Color as qc
        self.display.set_bg_gradient_color(qc(1, 1, 1, 0), qc(1, 1, 1, 0))

        from OCC.Core.Quantity import Quantity_Color
        self.display.DisplayColoredShape(self.shape,
                                         color=Quantity_Color(0.3, 0.3, 0.3, 0),  # fourth number means RGB
                                         update=True)
        self.display.FitAll()

    def clearLayout(self, layout):
        print("-- -- input layout: " + str(layout))
        for i in reversed(range(layout.count())):
            layoutItem = layout.itemAt(i)
            if layoutItem.widget() is not None:
                widgetToRemove = layoutItem.widget()
                print("found widget: " + str(widgetToRemove))
                widgetToRemove.setParent(None)
                layout.removeWidget(widgetToRemove)
            elif layoutItem.spacerItem() is not None:
                print("found spacer: " + str(layoutItem.spacerItem()))
            else:
                layoutToRemove = layout.itemAt(i)
                print("-- found Layout: " + str(layoutToRemove))
                self.clearLayout(layoutToRemove)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = QMainWindow()
    nw = CadViewer("../DekiResources/Zbiornik LNG assembly.stp")
    mw.setCentralWidget(nw)
    nw.start_display()
    mw.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
