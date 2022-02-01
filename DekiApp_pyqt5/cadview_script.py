'''
You can translate a STEP file into an OCCT shape in the following steps:
 1.load the file,
 2.check file consistency,
 3.set the translation parameters,
 4.perform the translation,
 5.fetch the results.
'''
import logging
import sys
import os
from OCC.Display.SimpleGui import init_display
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
# Reads STEP files, checks them and translates their contents into Open CASCADE models
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QWindow


from OCC.Display.backend import load_backend, get_qt_modules

log = logging.getLogger(__name__)
used_backend = load_backend()
log.info("GUI backend set to: {0}".format(used_backend))
print("GUI backend set to: {0}".format(used_backend))
from OCC.Display.qtDisplay import qtViewer3d

QtCore, QtGui, QtWidgets, QtOpenGl = get_qt_modules()


class CadViewer(QWidget):
    def __init__(self, step_filepath: str):
        super(CadViewer, self).__init__()

        # Class parameters
        self.step_filepath = step_filepath
        self.shape = None

        # Why this 2 lines instead of 1 ?
        # Layout init for 3D viewer
        grid = QGridLayout(self)

        # Viewer init
        import OCC.Display.qtDisplay as qtDisplay
        self.viewer = qtDisplay.qtViewer3d()
        self.viewer.setMinimumSize(400, 400)
        grid.addWidget(self.viewer)
        self.viewer.display.FitAll()
        self.setLayout(grid)

        self.read_stepFile(self.step_filepath)

# -------------------------------------------------------------------------------------------------------Class Functions
    def read_stepFile(self, step_filepath):
        step_reader = STEPControl_Reader()
        status = step_reader.ReadFile(step_filepath)
        if status == IFSelect_RetDone:  # RetDone : normal execution with a result
            step_reader.PrintCheckLoad(True, IFSelect_ItemsByEntity)
            step_reader.TransferRoot()
            self.shape = step_reader.Shape()
        else:
            print("Error: can't read file.")
            sys.exit(0)

    def start_display(self):
        from OCC.Core.Quantity import Quantity_Color
        self.viewer.display.View_Iso()
        self.viewer.display.EnableAntiAliasing()
        self.viewer.display.DisplayColoredShape(self.shape,
                                                color=Quantity_Color(0.3, 0.3, 0.3, 0),     # fourth number means RGB
                                                update=True)
        


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mw = QMainWindow()
    nw = CadViewer("DekiResources/Zbiornik LNG assembly.stp")
    mw.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
