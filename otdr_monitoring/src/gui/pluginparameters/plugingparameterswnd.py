from PySide6.QtWidgets import QDialog, QLabel, QFormLayout, QComboBox, QDialogButtonBox, QPushButton, QTabWidget, QWidget, QLineEdit

class PluginParametersWnd(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Plugin parameters")
        self.layout = QFormLayout(self)
        self.tabWidget = QTabWidget()
        self.btnBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout.addRow(self.tabWidget)
        self.layout.addRow(self.btnBox)
        self.plugins = {}
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)


    def registerPlugin(self, plugin):
        self.plugins[plugin] = {"edits": [], "names": []}
        widget = QWidget()
        widget.layout = QFormLayout(widget)
        allparams = plugin.getParameters()
        for p in allparams:
            label = QLabel(p["text"])
            if "hint" in p.keys():
                label.setToolTip(p["hint"])
            edit = QLineEdit(str(p["value"]))
            self.plugins[plugin]["edits"].append(edit)
            self.plugins[plugin]["names"].append(p["name"])
            widget.layout.addRow(label, edit)

        self.tabWidget.addTab(widget, plugin.name())

    def accept(self):
        for plugin, data in self.plugins.items():
            params = {}
            for edit, name in zip(data["edits"], data["names"]):
                params[name] = edit.text()
            plugin.setParameters(params)
        super().accept()


