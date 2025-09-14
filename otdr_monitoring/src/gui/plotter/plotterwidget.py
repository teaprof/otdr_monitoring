from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget, QFrame, QPushButton, QToolBar, QToolButton, QComboBox, QLabel, QSpacerItem, QSizePolicy

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        #self.axes = fig.add_subplot(111)
        self.axes = fig.subplots()
        super(MplCanvas, self).__init__(fig)
        self.objects = {} #associative map of existing objects

    def namedLine(self, name, x, y, **kwargs):
        if x is None or y is None:
            xx, yy = [], []
        else:
            xx, yy = x, y
        if name not in self.objects.keys():
            #create a new line object
            lines = self.axes.plot(xx, yy, **kwargs)
            self.objects[name] = lines[0]
        else:
            #update existing line object
            self.objects[name].set_ydata(yy)
            self.objects[name].set_xdata(xx)

    def clear(self):
        self.objects = {}
        self.axes.clear()


class PlotterWidget(QFrame):
    def __init__(self, parent, plugins):
        super().__init__(parent)
        self.plugins = plugins

        #Create matplotlib objects: self.canvas, self.navigationBar, self.axes
        f = Figure(figsize=(5, 3))
        f.set_tight_layout(True)
        self.fig = f
        self.canvas = MplCanvas(f)
        self.canvas.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.navigationBar = NavigationToolbar(self.canvas, self)
        self.axes = self.canvas.axes

        #Create toolbar with combobox to select view, and statusLabel
        self.viewComboBox = QComboBox()

        for plugin in plugins:
            views = plugin.getViews()
            if views is not None:
                for view in views:
                    self.viewComboBox.addItem(view, (plugin, view))
            else:
                self.viewComboBox.addItem(plugin.name(), (plugin, None))
        self.viewComboBox.currentIndexChanged.connect(self.currentViewIndexChanged)
        self.toolbar = QToolBar()
        self.toolbar.addWidget(self.viewComboBox)
        self.statusLabel = QLabel("Status:")

        #Create layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.navigationBar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.statusLabel)

        self.curplugin = None
        self.curview = None
        self.currentViewIndexChanged(self.viewComboBox.currentIndex())

    def currentViewIndexChanged(self, index):
        if self.curplugin is not None:
            self.curplugin.unregisterCanvas()
        cmbBoxUserData = self.viewComboBox.currentData()
        self.curplugin = cmbBoxUserData[0]
        self.curview = cmbBoxUserData[1]
        self.curplugin.activateView(self.canvas, self.curview)
        self.curplugin.registerStatusLabel(self.statusLabel)

    def render(self):
        self.curplugin.render()

    def clear(self):
        for plugin in self.plugins:
            plugin.clear()

