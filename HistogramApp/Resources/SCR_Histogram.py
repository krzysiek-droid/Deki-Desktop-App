import matplotlib.pyplot as plt
import pandas as pd
import os

from kivy.uix.screenmanager import Screen
from kivy.config import value


def load_values_from_csv(filepath, column_index: int, separator):

    file_opened = pd.read_csv(filepath[0], sep=separator)  # check if file is seperated by ";"
    column_name = file_opened.columns[column_index]

    values = file_opened.get(column_name)

    print(values)
    values = list(values)
    return column_name, values


class Histogram_screen(Screen):
    def __init__(self):
        super().__init__()
        self.sorting_time = value
        self.sorted = value
        self.filepath = value
        self.records_q = value
        self.sep = ''



    def draw_hist(self, filepath, column_idx):
        # Data acquisition
        data = list(load_values_from_csv(filepath, column_idx, self.sep))

        # Creating histogram
        fig, ax = plt.subplots(1, 1)
        ax.hist(x=data[1], bins=10, alpha=0.5)
        ax.set_title(f"{os.path.basename(filepath[0])}\nHistogram for {data[0]}")
        ax.set_ylabel("Counts")
        ax.set_xlabel(f"{data[0]}")

        #labeling bars
        rects = ax.patches
        #labels = ["label%d" % i for i in range(len(rects))]

        values_summary = 0
        bar_heights = []
        x_axis_length = 0


        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height + 0.01, height,
                    ha='center', va='bottom')
            if rect.get_x() <= 0.3:
                values_summary += height
            bar_heights.append(height)
            x_axis_length = rect.get_x()
        print(bar_heights, x_axis_length)
        ax.text(x_axis_length*0.7, max(bar_heights)*0.95, f"Sum of counts <= 0.3: {round(int(values_summary),0)}",
                ha='left', va='center')
        plt.show()
