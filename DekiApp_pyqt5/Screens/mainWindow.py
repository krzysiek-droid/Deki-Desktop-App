from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from Screens import resources_rc
from PyQt5.QtCore import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Load Ui from .ui file
        loadUi(r'Screens/mainWindow.ui', self)
        
        # Hide notification widget
        self.popupNotificationContainer.deleteLater()

        # Buttons scripts allocation
        # Show/Hide extension of left Menu with width of 300 pxls
        self.MenuBtn.clicked.connect(lambda: self.showMenu(self.CenterMenuContainer, 300))

        # Show/Hide extension of right Menu with width of 250 pxls
        self.moreMenuBtn.clicked.connect(lambda: self.showMenu(self.RightMenuContainer, 250))

        # Left Menu buttons
        self.HomeBtn.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.HomePage))
        self.wpsCreatorBtn.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.wpsCreatorPage))
        self.InspectionPlanBtn.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.InsPlanPage))
        self.ReportsBtn.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.ReportsPage))

    # MainWindow button scripts
    def showMenu(self, menu_widget, opened_width):
        width = menu_widget.width()
        if width == 0:
            newWidth = opened_width
        else:
            newWidth = 0
        self.animation = QPropertyAnimation(menu_widget, b"maximumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
