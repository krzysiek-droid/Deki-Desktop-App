from kivy.uix.screenmanager import Screen
from plyer import filechooser


# first screen, popping up when app initialized
class Welcome_screen(Screen):
    def open_filechooser(self):
        # initialized filechooser of Windows type (thanks to plyer lib.)
        path = filechooser.open_file(title="Pick a .csv file",
                                     filters=[("Comma-separated values", "*.csv")])

        return path
