from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.list import MDList
from kivymd.uix.list import OneLineListItem

import kivy.utils as utils


class dialListItem(OneLineListItem):
    def highlight_choice(self):
        self.bg_color = utils.get_color_from_hex("8ce089")


class colsList(MDList):
    def refresh_list(self):
        items = self.children
        for listItem in items:
            listItem.bg_color = self.parent.background_color


class dialogContent(BoxLayout):
    def __init__(self, array):
        super(dialogContent, self).__init__()
        self.scrolledList = colsList()
        for column in array:
            self.scrolledList.add_widget(dialListItem(text=f"{column}"))

        self.ids.scrolledDialog.add_widget(self.scrolledList)