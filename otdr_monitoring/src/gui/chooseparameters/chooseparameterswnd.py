from PySide6.QtWidgets import (QDialog, QLabel, QFormLayout, QComboBox,
                               QDialogButtonBox, QPushButton, QLineEdit, QMessageBox)
from PySide6.QtCore import QTimer

class ChooseParametersWnd(QDialog):
    """Creates and runs window for selecting of reflectometer parameters"""
    def __init__(self, parent, reflectometerIO):
        super().__init__(parent)
        self.setWindowTitle("Reflectometer parameters")
        self.layout = QFormLayout(self)
        self.btnBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.cmbBoxes = []
        self.reflectometerIO = reflectometerIO
        self.allParams = reflectometerIO.getAllParameters()
        for p in self.allParams:
            label = QLabel(p['text'] + ':')
            if p['values'] == 'positive':
                #create QLineEdit
                lineEdit = QLineEdit()
                self.cmbBoxes.append(lineEdit)
                self.layout.addRow(label, lineEdit)
            else:
                #create QComboBox
                variantsComboBox = QComboBox()
                for text, value in zip(p['values_text'], p['values']):
                    variantsComboBox.addItem(text, value)
                variantsComboBox.currentIndexChanged.connect(self.updateVisibility)
                self.cmbBoxes.append(variantsComboBox)
                self.layout.addRow(label, variantsComboBox)
        self.acquireParamsBtn = QPushButton('read current settings')
        self.setValuesBtn = QPushButton('set these values')
        self.layout.addRow(self.acquireParamsBtn)
        self.layout.addRow(self.setValuesBtn)
        self.layout.addRow(self.btnBox)

        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)
        self.acquireParamsBtn.clicked.connect(self.acquireParams)
        self.setValuesBtn.clicked.connect(self.setValues)
        self.updateVisibility(None)

        self.timer = QTimer(self)
        self.timer.singleShot(100, self.update) #why update is on timer?

    def update(self):
        params = self.reflectometerIO.lastParameters()
        if params is not None:
            print(params)
            self.selectParameters(params)

    def selectParameters(self, parameters):
        names = [p['name'] for p in self.allParams]
        for key, value in parameters.items():
            try:
                keyidx = names.index(key)
                valueidx = self.allParams[keyidx]['values'].index(value)
                self.cmbBoxes[keyidx].setCurrentIndex(valueidx)
            except ValueError:
                print(f'Error while initializing {key}={value}, ignoring this pair')

    def getValues(self):
        parameters = {}
        for p, editItem in zip(self.allParams, self.cmbBoxes):
            if isinstance(editItem, QComboBox):
                parameters[p['name']] = editItem.currentData()
            elif isinstance(editItem, QLineEdit):
                parameters[p['name']] = editItem.text()
        return parameters

    def updateVisibility(self, index):
        v = self.getValues()
        self.reflectometerIO.updateVisibility(self.allParams, v)
        for p, cmbBox in zip(self.allParams, self.cmbBoxes):
            cmbBox.setEnabled(p['enabled'])

    def accept(self):
        self.parameters = self.getValues()
        super().accept()

    def acquireParams(self):
        params = self.reflectometerIO.readParameters()
        self.selectParameters(params)

    def setValues(self):
        values = self.getValues()
        if self.reflectometerIO.setParameters(values):
            print("Ok")
        else:
            print("These values are incompatible")
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle("Monitoring")
            msgBox.setText("These values are incompatible. Do you want to read correct actual values?")
            msgBox.addButton(QMessageBox.Ok)
            msgBox.addButton(QMessageBox.Cancel)
            msgBox.setIcon(QMessageBox.Question)
            if msgBox.exec() == QMessageBox.Ok:
                self.acquireParams()


