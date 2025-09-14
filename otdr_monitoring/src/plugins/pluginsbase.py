import abc

class PluginBase(abc.ABC):
    """Base class for all plugins"""
    def __init__(self):
        self.canvas = None
        self.statusLabel = None
        views = self.getViews()
        if views is not None:
            self.currentView = views[0]
        else:
            self.currentView = None

    @abc.abstractmethod
    def name(self):
        """This method should be redefined in the derived class"""
        return "pluginBase"

    def clear(self):
        """This method should be redefined in the derived class"""
        pass

    @abc.abstractmethod
    def collect(self, x, y):
        """This method should be redefined in the derived class"""
        pass

    def getParameters(self):
        """This method should be redefined in the derived class"""
        return []

    def setParameters(self, parameters):
        """This method should be redefined in the derived class"""
        pass

    def getViews(self):
        """This method should be redefined in the derived class
        Example:
            return None #means than only one view is available - 1st form
            return ["Only view"] #only one view is available - 2nd form
            return ["First view", "Second view"]
        """
        return None #means than only one view is available

    @abc.abstractmethod
    def render(self):
        """This method should be redefined in the derived class"""
        pass

    def registerStatusLabel(self, statusLabel):
        self.statusLabel = statusLabel

    def activateView(self, canvas, view):
        self.canvas = canvas
        self.currentView = view
        self.render()

    def registerCanvas(self, canvas):
        self.canvas = canvas
        canvas.clear()
        self.render()

    def unregisterCanvas(self):
        self.canvas = None

    def setStatusText(self, statusText):
        if self.statusLabel is not None:
            self.statusLabel.setText(statusText)


