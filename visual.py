# visual.py
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class MiniPlot(FigureCanvas):
    def __init__(self, width=4, height=2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        self.ax = fig.add_subplot(111)
        self.x = []
        self.y = []
        self.line, = self.ax.plot([], [])
        self.ax.set_ylim(0, 10)

    def refresh_plot(self, x, y):
        """Update the live graph without conflicting with Qt's update()"""
        self.x = x
        self.y = y
        self.ax.clear()
        self.ax.plot(self.x, self.y)
        self.ax.relim()
        self.ax.autoscale_view()
        self.draw()
