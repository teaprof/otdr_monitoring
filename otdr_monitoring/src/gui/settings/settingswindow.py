from gui.loaduiwidget import loadUiWidget
from PySide6.QtWidgets import QFileDialog, QCompleter, QFileSystemModel
import os

class SettingsWindow:
    def __init__(self, params):
        self.ui = loadUiWidget("gui/settings/settingswnd.ui", None)
        self.ui.selectAutosavePathBtn.clicked.connect(self.onSelectAutosavePathBtn)

        completer = QCompleter(self.ui)
        model = QFileSystemModel(completer)
        model.setRootPath('.') #works on Win and Linux
        completer.setModel(model)
        self.ui.autosavePathEdit.setCompleter(completer)
        self.ui.autosavePathEdit.textChanged.connect(self.onAutosavePathEditTextChanged)

        self.parseSettings(params)
        self.ui.saveAsJSONcheckBox.toggled.connect(self.autosaveAsJSONtoggled)
        self.ui.saveAsCSVcheckBox.toggled.connect(self.autosaveAsCSVtoggled)

    def autosaveAsJSONtoggled(self, checked):
        if checked is False:
            self.ui.saveAsCSVcheckBox.setChecked(True)

    def autosaveAsCSVtoggled(self, checked):
        if checked is False:
            self.ui.saveAsJSONcheckBox.setChecked(True)

    def exec(self):
        return self.ui.exec()

    def onSelectAutosavePathBtn(self):
        url = QFileDialog.getExistingDirectory(self.ui, "Select directory")
        if url:
            self.ui.autosavePathEdit.setText(url)

    def onAutosavePathEditTextChanged(self, text):
        if os.path.exists(text):
            self.ui.autosavePathEdit.setStyleSheet("")
        else:
            self.ui.autosavePathEdit.setStyleSheet("color: red;")

    def parseSettings(self, settings):
        if 'autosavepath' in settings:
            autosavepath = settings['autosavepath']
        else:
            autosavepath = '.'
        self.ui.autosavePathEdit.setText(autosavepath)
        if 'autosaveAsJSON' in settings:
            saveAsJSON = settings['autosaveAsJSON']
        else:
            saveAsJSON = True
        self.ui.saveAsJSONcheckBox.setChecked(saveAsJSON)
        if 'autosaveAsCSV' in settings:
            saveAsCSV = settings['autosaveAsCSV']
        else:
            saveAsCSV = True
        self.ui.saveAsCSVcheckBox.setChecked(saveAsCSV)

    def readSettings(self):
        settings = {}
        settings['autosavepath'] = self.ui.autosavePathEdit.text()
        settings['autosaveAsJSON'] = self.ui.saveAsJSONcheckBox.isChecked()
        settings['autosaveAsCSV'] = self.ui.saveAsCSVcheckBox.isChecked()
        return settings

