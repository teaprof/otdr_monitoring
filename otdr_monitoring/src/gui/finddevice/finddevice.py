#import PySide6
from PySide6.QtWidgets import QDialog, QPushButton, QComboBox, QVBoxLayout, QDialogButtonBox, QCheckBox
from device.usbhelper import findAllDevices
from device.aq7270 import AQ7270Series

class FindDeviceWnd(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.cmbBox = QComboBox()
        self.btnBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.resetCheckBox = QCheckBox("Reset device to default settings")
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.cmbBox)
        self.layout.addWidget(self.resetCheckBox)
        self.layout.addWidget(self.btnBox)
        self.setWindowTitle("Select device")
        self.findAllDevices()

        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

    def findAllDevices(self):
        devices = findAllDevices(idVendor = None)
        curidx = 0
        matchidx = None
        for devdescr in devices:
            text = str(devdescr['text'])
            text += ' idVendor: ' + hex(devdescr['dev'].idVendor)
            text += ' idProduct' + hex(devdescr['dev'].idProduct)
            self.cmbBox.addItem(text, devdescr['dev'])
            if(devdescr['dev'].idVendor == AQ7270Series.usb_idVendor):
                matchidx = curidx
            curidx += 1
        self.cmbBox.addItem('AQ7270 Simulator', None)
        if matchidx is not None:
            self.cmbBox.setCurrentIndex(matchidx)
        else:
            print('Yokogawa devices are not found')

    def accept(self):
        idx = self.cmbBox.currentIndex()
        self.dev = self.cmbBox.itemData(idx)
        self.needReset = self.resetCheckBox.isChecked()
        super().accept()

