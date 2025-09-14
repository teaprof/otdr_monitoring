from PySide6 import QtUiTools
from PySide6.QtCore import QFile

def loadUiWidget(uifilename, parent=None):
    uiFile = QFile(uifilename)
    uiFile.open(QFile.ReadOnly)
    loader = QtUiTools.QUiLoader()
    ui = loader.load(uiFile, parent)
    return ui
