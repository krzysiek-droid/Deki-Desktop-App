from PyQt5.QtCore import pyqtSignal, QPropertyAnimation, QRect
from PyQt5.QtWidgets import QLineEdit, QSizePolicy, QToolButton
from PyQt5.uic.properties import QtGui


class CustomLineEdit(QLineEdit):
    def __init__(self, *args):
        super(CustomLineEdit, self).__init__(*args)
        self.clearAction = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.textChanged.connect(lambda: self.customLineEdit_textChanged())
        self.customLineEdit_textChanged()
        self.setClearButtonEnabled(False)

    def customLineEdit_textChanged(self):
        if self.isReadOnly() and self.clearAction is None:
            clear_icon = QtGui.QIcon(':/Icons/Icons/edit-3.svg')
            self.clearAction = self.addAction(clear_icon, QLineEdit.ActionPosition.TrailingPosition)
            self.clearAction.triggered.connect(lambda: (self.setReadOnly(False), self.customLineEdit_textChanged()))
            self.setClearButtonEnabled(False)
            self.setReadOnly(True)
        else:
            self.removeAction(self.clearAction)
            self.clearAction = None
            self.setClearButtonEnabled(True)


class MouseClearableLineEdit(QLineEdit):
    clicked = pyqtSignal()
    confirmed = pyqtSignal(bool)
    isConfirmed = False
    hasValue = False

    def mousePressEvent(self, event):
        super(MouseClearableLineEdit, self).mousePressEvent(event)
        if not self.isReadOnly():
            self.clicked.emit()

    def setValue(self, a0: str):
        if float(a0) > 0:
            self.hasValue = True
        else:
            self.hasValue = False

    def setNeutral(self):
        style = "border-bottom: 2px solid rgb(125, 125, 125);"
        self.setStyleSheet(style)
        self.hasValue = False

    def setConfirmed(self, boolean: bool):
        self.confirmed.emit(boolean)
        if boolean:
            style = "border-bottom: 2px solid rgb(30, 210, 80);"
            self.setStyleSheet(style)
            self.setReadOnly(True)
            self.isConfirmed = True
            return self.isConfirmed
        elif not boolean:
            style = "border-bottom: 2px solid rgb(255, 150, 0);"
            self.setStyleSheet(style)
            self.setReadOnly(False)
            self.isConfirmed = False
            return self.isConfirmed


class CustomToolCircleButton(QToolButton):
    def __init__(self, *arg, **kwargs):
        super(CustomToolCircleButton, self).__init__(*arg, **kwargs)

        self.clicked.connect(lambda x:print(x))

    def focusInEvent(self, event):
        super(CustomToolCircleButton, self).focusInEvent(event)
        print('Mouse moved')
        # animation = QPropertyAnimation(self, "size")
        # animation.setDuration(250)
        # animation.setStartValue(QRect(60, 60, self.width(), self.height()))
        # animation.setEndValue(QRect(80, 80, self.width(), self.height()))
        # animation.start()

    def focusOutEvent(self, e: QtGui.QFocusEvent) -> None:
        super(CustomToolCircleButton, self).focusOutEvent(e)
        print('focused out')