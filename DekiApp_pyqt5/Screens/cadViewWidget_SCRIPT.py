import logging
import sys

import resources_rc

import PyQt5.QtCore
from PyQt5.QtWidgets import *
from PyQt5.Qt import QTimer
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

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
    def __init__(self, step_filepath: str):
        super(CadViewer, self).__init__()
        loadUi(r'D:\CondaPy - Projects\PyGUIs\DekiApp_pyqt5\Screens\cadViewWidget.ui', self)
        # Class parameters
        self.filepath = step_filepath
        self.shape = None
        self.screenshot = PyQt5.Qt.QPixmap()
        # --------------------------------------------------CadViewer setup---------------------------------------------
        # Create layout for 3D viewer
        self.qtViewer3DContainer = QVBoxLayout(self)
        # Viewer init, define the widget's appearance
        import OCC.Display.qtDisplay as qtDisplay
        self.viewer = qtDisplay.qtViewer3d()
        self.containerBaseSize = {'width': self.viewerWidget.size().width(),
                                  'height': self.viewerWidget.size().height()}
        print(f'Cad model container type: {type(self.viewerWidget)} with size of {self.containerBaseSize["width"]}x'
              f'{self.containerBaseSize["height"]}')
        self.viewer.setMinimumSize(self.containerBaseSize['width'], self.containerBaseSize['height'])
        self.qtViewer3DContainer.addWidget(self.viewer, alignment=Qt.AlignHCenter)
        self.viewerWidget.setLayout(self.qtViewer3DContainer)
        from OCC.Core.Quantity import Quantity_Color as qc
        self.viewer.display.set_bg_gradient_color(qc(1, 1, 1, 0), qc(1, 1, 1, 0))

        # ---------------------------------------------------Buttons----------------------------------------------------
        self.izoViewBtn.clicked.connect(lambda: self.viewer.display.View_Iso())
        self.snapshootBtn.clicked.connect(lambda: self.takeScreenshot())
        self.fullscreenBtn.clicked.connect(lambda: print('TODO fullscreen ?'))

        # ------------------------------------------------Call class functions------------------------------------------
        self.read_stepFile(self.filepath)

    # ----------------------------------------------Class Functions---------------------------------------------------
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
        self.viewer.InitDriver()
        self.viewer.createCursors()
        from OCC.Core.Quantity import Quantity_Color as qc
        self.viewer.display.set_bg_gradient_color(qc(1, 1, 1, 0), qc(1, 1, 1, 0))
        from OCC.Core.Quantity import Quantity_Color
        self.viewer.display.EnableAntiAliasing()
        self.viewer.display.DisplayColoredShape(self.shape,
                                                color=Quantity_Color(0.3, 0.3, 0.3, 0),  # fourth number means RGB
                                                update=True)

    def takeScreenshot(self):
        QTimer.singleShot(100, self.saveScreenshot)
        # self.viewer.display.ExportToImage('test.png') could do the work, but it saves image without creating a
        # class for it

    def saveScreenshot(self):
        self.screenshot = self.viewer.screen().grabWindow(self.viewer.winId())
        pic = QLabel()
        pic.setPixmap(self.screenshot.scaled(150, 100))
        self.cadModelPictureView.setText('')
        self.cadModelPictureView.setPixmap(self.screenshot.scaled(150, 100))
        # self.screenshot.save('screenshot.png', 'png')
    def screenshot_retry(self):
        pass
        # TODO: change the screenshot preview to notification dialog with approval of user in order to maintain
        #                                               STP file open during the decision of screenshot approval

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
    #nw.start_display()
    mw.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
