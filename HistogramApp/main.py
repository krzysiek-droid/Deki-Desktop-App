import kivy
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

#   Imports related to App's different screens
import Resources.SCR_Welcome as WelcomeSCR
import Resources.SCR_ColumnsChoice as ColumnsChoiceSCR
import Resources.SCR_Histogram as HistSCR

from kivymd.app import MDApp
from kivy.app import Builder

# requirement for kivy version
kivy.require("2.0.0")

# import front-ends for screens
Builder.load_file(f"Resources/App_frontend.kv")
Builder.load_file(f"Resources/SCR_ColumnsChoice.kv")
Builder.load_file(f"Resources/SCR_Histogram.kv")

# Prime window size etc.
Window.size = (750, 500)


# Class object definition required for screens handling and data exchange
class WindowManager(ScreenManager):
    filepath = ''  # handler for chosen filepath
    data = None  # handler of data taken from chosen column
    separator = ''  # separator of .csv file chosen by the user
    cols_headers = ''  # handler for headers in chosen .csv file
    usrColumn_idx = 0  # index of column chosen by user
    colsList_widget = None  # MDlist for columns headers
    usrColumn = None  # User column choice, updated in MDDialog-Columns_Choice

    hist_opt = []

# Main App definition
class PorosityApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Green"

        screen_manager = WindowManager()

        screen_manager.add_widget(screen=WelcomeSCR.Welcome_screen(name='welcome_screen'))

        cols_screen = ColumnsChoiceSCR.Columns_choice()
        screen_manager.add_widget(screen=cols_screen)

        histogram = HistSCR.Histogram_screen()
        screen_manager.add_widget(screen=histogram)

        return screen_manager


# main
if __name__ == '__main__':
    PorosityApp().run()
