from kivy.uix.screenmanager import Screen


# Sorting algorithm choice screen
class sorting_algorithms(Screen):
    def __init__(self, ):
        super().__init__()
        self.filepath = ' initialized path '

    def set_filepath(self, value):
        self.filepath = value
        self.ids.filepath.text = value

    def show_path(self):
        self.ids.filepath.text = "sorting_algorithm"
