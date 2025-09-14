from .pluginsbase import PluginBase

class LastReflectogram(PluginBase):
    def __init__(self):
        super().__init__()
        self.x = None
        self.y = None

    def name(self):
        return "Current data"

    def clear(self):
        self.x = None
        self.y = None
        self.render()

    def collect(self, x, y):
        self.x = x
        self.y = y

    def render(self):
        self.canvas.namedLine("curreflectogram", self.x, self.y)
        if self.y is None:
            self.setStatusText("No data")
        else:
            self.setStatusText("Ok")
        self.canvas.axes.relim()
        self.canvas.axes.autoscale_view()
        self.canvas.axes.set_xlabel('range, m')
        self.canvas.axes.set_ylabel('dB')
        self.canvas.axes.grid(True)
        self.canvas.draw()
