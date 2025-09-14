import usb
from PySide6.QtWidgets import QMessageBox


def findAllDevices(idVendor):
    devices = []
    try:
        if idVendor is not None:
            devices = usb.core.find(find_all=True, idVendor = idVendor)
        else:
            devices = usb.core.find(find_all=True)
    except usb.core.NoBackendError:
        msgBox = QMessageBox(None)
        msgBox.setWindowTitle("Error")
        msgBox.setText("No valid backend found. Please, check that libusb is installed in the correct dir")
        msgBox.addButton(QMessageBox.Ok)
        msgBox.exec()
    
    res = []
    for dev in devices:
        try:
            manufacturer = dev.manufacturer
        except:
            manufacturer = 'Unknown manufacturer'
        try:
            product = dev.product
        except:
            product = 'Unknown product'
        try:
            serialNumber = dev.serial_number
        except:
            serialNumber = 'Unknown'
        str = f'{manufacturer}:{product}, SN: {serialNumber}'
        dev_descriptor = {'text': str, 'dev': dev}
        res.append(dev_descriptor)
    return res

