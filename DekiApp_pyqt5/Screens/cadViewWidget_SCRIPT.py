import logging
import sys
import resources_rc
from PyQt5.QtWidgets import *
import PyQt5
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
# Reads STEP files, checks them and translates their contents into Open CASCADE models
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.backend import load_backend, get_qt_modules
from OCC.Extend.DataExchange import read_step_file_with_names_colors
from OCC.Core.TDF import TDF_LabelSequence
from OCC.Extend.DataExchange import TopoDS_Compound
from PyQt5 import Qt

log = logging.getLogger(__name__)
used_backend = load_backend()
log.info("GUI backend set to: {0}".format(used_backend))
print("GUI backend set to: {0}".format(used_backend))


# TODO: add buttons for rotation of CAD Model etc.


class CadViewerLayout(QVBoxLayout):
    def __init__(self, step_filepath: str):
        super(CadViewerLayout, self).__init__()
        # self.setMinimumSize(viewport_width, viewport_height)
        # Class members
        self.display = None
        self.shape = None
        self.filepath = step_filepath

        # --------------------------------------------------CadViewer setup---------------------------------------------
        # Viewer init, define the widget's appearance, must be resized after definition to center itself
        # in widget container (layout)
        import OCC.Display.qtDisplay as qtDisplay
        self.canvas = qtDisplay.qtViewer3d()
        self.display = self.canvas._display
        # Nor canvas nor qtViewer3Container cannot be aligned, otherwise widget do not shows itself
        self.addWidget(self.canvas)
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
        self.canvas.InitDriver()
        from OCC.Core.Quantity import Quantity_Color as qc
        self.display.set_bg_gradient_color(qc(1, 1, 1, 0), qc(1, 1, 1, 0))
        from OCC.Core.Quantity import Quantity_Color
        self.display.DisplayColoredShape(self.shape,
                                         color=Quantity_Color(0.3, 0.3, 0.3, 0),  # fourth number means RGB
                                         update=True)
        self.display.FitAll()

    def get_assembliesList(self):
        shapes = read_step_file_with_names_colors(self.filepath)
        print(shapes)
        for key in shapes.keys():
            if type(key) is TopoDS_Compound:
                print(shapes[key])


class CadViewer(QWidget):
    def __init__(self, step_filepath: str):
        super(CadViewer, self).__init__()
        # self.setMinimumSize(viewport_width, viewport_height)
        # Class members
        self.display = None
        self.shape = None
        self.filepath = step_filepath
        self.layout = QVBoxLayout()
        # --------------------------------------------------CadViewer setup---------------------------------------------
        # Viewer init, define the widget's appearance, must be resized after definition to center itself
        # in widget container (layout)
        import OCC.Display.qtDisplay as qtDisplay
        self.canvas = qtDisplay.qtViewer3d()
        self.display = self.canvas._display
        self.canvas.resize(200, 200)
        # Nor canvas nor qtViewer3Container cannot be aligned, otherwise widget do not shows itself
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
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
        self.canvas.InitDriver()
        from OCC.Core.Quantity import Quantity_Color as qc
        self.display.set_bg_gradient_color(qc(1, 1, 1, 0), qc(1, 1, 1, 0))
        from OCC.Core.Quantity import Quantity_Color
        self.display.DisplayColoredShape(self.shape,
                                         color=Quantity_Color(0.3, 0.3, 0.3, 0),  # fourth number means RGB
                                         update=True)
        self.display.FitAll()

    def get_assembliesList(self):
        shapes = read_step_file_with_names_colors(self.filepath)
        print(shapes)
        for key in shapes.keys():
            if type(key) is TopoDS_Compound:
                print(shapes[key])

    def fitToParent(self):
        self.display.View.MustBeResized()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = QMainWindow()
    nw = CadViewer("../DekiResources/Zbiornik LNG assembly.stp")
    nw.start_display()
    mw.setCentralWidget(nw)
    mw.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
