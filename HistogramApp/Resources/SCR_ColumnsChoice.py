from kivy.uix.screenmanager import Screen

import Resources.DLG_columnChoice as DLG_col

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem

import pandas as pd


class ItemConfirm(OneLineAvatarIconListItem):
    divider = None

    def set_icon(self, instance_check):
        print(instance_check)
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False


class Columns_choice(Screen):
    def __init__(self):
        super(Columns_choice, self).__init__()
        self.dialog = None

    def display_columns(self, filepath, separator):  # Displays .csv file columns names
        data = pd.read_csv(filepath[0], sep=separator, engine='python')
        self.manager.cols_headers = list(data.columns)  # Send cols headers to global variable in ScreenManager
        self.show_Cols_dialog()

    def show_Cols_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                auto_dismiss=False,
                title="Select column name:",
                type="custom",
                content_cls=DLG_col.dialogContent(self.manager.cols_headers),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", on_release=self.closeDialog
                    ),
                    MDFlatButton(
                        text="OK", on_release=self.grabText
                    ),
                ],
            )

        self.dialog.open()

    def show_Separator_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                auto_dismiss=False,
                title="Select separator for .csv:",
                type="confirmation",
                items=[
                    ItemConfirm(text=";"),
                    ItemConfirm(text=","),
                    ItemConfirm(text="."),
                    ItemConfirm(text=":"),
                    ItemConfirm(text="\t"),
                    ItemConfirm(text="Custom"),
                ],
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        on_release=self.closeDialog
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        on_release=self.grabSeparator
                    ),
                ],
            )
        self.dialog.open()

    def grabText(self, inst):
        self.manager.usrColumn = self.dialog.content_cls.ids.scrolledDialog.text
        self.ids.chosen_column.text = f'Chosen column:      {self.manager.usrColumn}'
        self.dialog.dismiss()
        self.dialog = None
        self.ids.proceed_button.visible = True

    def closeDialog(self, inst):
        self.dialog.dismiss()
        self.dialog = None
        print("dialog closed")

    def grabSeparator(self, inst):
        for item in self.dialog.items:
            if item.ids.check.active:
                self.manager.separator = item.text
                self.ids.custom_separator_field.visible = False
                if self.manager.separator == "Custom":
                    self.ids.separator_display.text = ''
                    self.ids.custom_separator_field.visible = True
                    self.ids.column_selection.visible = False
                else:
                    self.ids.column_selection.visible = True
                    self.ids.separator_display.text = f'Chosen separator:           {self.manager.separator}'
        self.dialog.dismiss()
        self.dialog = None
        print("separator grabbed")

    def error_handler(self, separator):
        separator = str(separator)
        if len(separator) == 1 and not separator.isalnum():
            self.ids.error_display.text = f"Wybrany separator to: {separator}"
            return False
        else:
            self.ids.error_display.text = "Separator musi być pojedyńczym znakiem, oraz nie może być literą ani cyfrą."
            return True

    def acquire_columnData(self, headers: list, column_name: str):
        idx = 0
        for header in headers:
            header = str(header).lower()
            if header == column_name.lower():
                self.manager.current = "histogram_screen"
                return idx  # index of header on headers list
            idx += 1

        self.ids.header_error.text = "Nie ma takiej kolumny w wybranym pliku"


if __name__ == "__main__":
    pass
