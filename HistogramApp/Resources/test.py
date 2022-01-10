from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivy.uix.button import Button


class Content(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.kpads = self.ids.kpads
        for i in range(1, 13):
            btn = Button(text=str(i))
            self.kpads.add_widget(btn)


class MainApp(MDApp):
    dialog = None


    def show_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                type="custom",
                size_hint=(.7, .6),
                content_cls=Content())

        self.dialog.open()


MainApp().run()