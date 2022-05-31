import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi



# resources_rc has to be imported here, even if it is not used directly in code, dunno why
import Screens.InspectionPlannerScreen_SCRIPT
import resources_rc

import pathlib


class InspectionPlannerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(r'InspectionPlannerWindow_UI.ui', self)
        # define QStackedWidget for screen changing purposes
        self.stackedWidget = QStackedWidget()
        # QStackedWidget contains QStackedLayout, which is important in case of children and parent finding
        self.stackedWidget.findChild(QStackedLayout).setObjectName('screenManager')
        self.stackedWidgetContainer.addWidget(self.stackedWidget)

        # add the first screen (QWidget) to screenManager (stackedWidget)
        import InspectionPlannerScreen_SCRIPT
        self.stackedWidget.addWidget(InspectionPlannerScreen_SCRIPT.InspectionPlannerScreen())


        # show all pages allocated in QStackedWidget
        print(*[(stackedPage, stackedPage.objectName()) for stackedPage in self.stackedWidget.children()])

        # button allocations
        self.closeBtn.clicked.connect(lambda: self.close())

        # define screens


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = InspectionPlannerWindow()

    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
