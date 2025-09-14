import numpy

from gui.loaduiwidget import loadUiWidget

from device.reflectometerIOThread import ReflectometerIOThread

from gui.finddevice.finddevice import FindDeviceWnd
from gui.chooseparameters.chooseparameterswnd import ChooseParametersWnd
from gui.pluginparameters.plugingparameterswnd import PluginParametersWnd
from device.aq7270 import AQ7270Series
from device.aq7270simulator import AQ7270Simulator
from plugins.averager import Averager
from plugins.partsum import PartSum
from plugins.lastreflectogram import LastReflectogram
from gui.plotter.plotterwidget import PlotterWidget

from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer, QMimeDatabase
from PySide6.QtWidgets import QMessageBox, QToolButton, QMenu, QRadioButton, QGridLayout, QDialogButtonBox, QDialog, QLabel, QSpinBox, QDateTimeEdit, QTimeEdit, QFileDialog
from PySide6.QtWidgets import QApplication
from gui.settings.settingswindow import SettingsWindow
import PySide6.QtCore #for ToolButtonStyle
from .controlfsm import MeasurementsControl
from datetime import datetime, timedelta
import time, json, os, csv

class MainWindow:
    def __init__(self):
        self.ui = loadUiWidget("gui/mainwindow/mainwnd.ui", None)
        self.ui.show()

        #Create programmatically UI elements that could not be added in Qt Designer
        #Create Monitoring toolbtn on the toolbar with menu
        monitoringBtn = QToolButton(self.ui)
        monitoringBtn.setText("Monitoring")
        monitoringBtn.setToolButtonStyle(PySide6.QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        monitoringBtn.setIcon(QIcon.fromTheme("go-next-skip"))
        monitoringMenu = QMenu(self.ui)
        monitoringMenu.setToolTipsVisible(True)
        actionRunTimes = monitoringMenu.addAction(QIcon.fromTheme("go-last"), "Times")
        actionRunTimes.setToolTip("Run measurements a specified number of times")
        actionRunDuration = monitoringMenu.addAction(QIcon.fromTheme("clock"), "Duration")
        actionRunDuration.setToolTip("Run measurements for a specified duration")
        actionRunContinuos = monitoringMenu.addAction(QIcon.fromTheme("media-playlist-repeat"), "Continuous")
        actionRunContinuos.setToolTip("Run measurements until stopped by user")
        monitoringBtn.setMenu(monitoringMenu)
        monitoringBtn.setPopupMode(QToolButton.InstantPopup)
        self.monitoringBtn = monitoringBtn

        actionRunTimes.triggered.connect(self.actionRunTimesTriggered)
        actionRunDuration.triggered.connect(self.actionRunDurationTriggered)
        actionRunContinuos.triggered.connect(self.actionRunContinuousTriggered)


        self.ui.toolBar.insertWidget(self.ui.actionStop, monitoringBtn)

        self.statusLabel = QLabel("Idle")
        self.ui.statusBar().insertWidget(0, self.statusLabel)
        self.stopConditionsLabel = QLabel("")
        self.ui.statusBar().insertWidget(1, self.stopConditionsLabel)


        self.ui.actionFindDevice.triggered.connect(self.actionFindDeviceTriggered)
        self.ui.actionSelectParameters.triggered.connect(self.actionReflectometerParametersTriggered)
        self.ui.actionSingleMeasurement.triggered.connect(self.actionSingleMeasurementTriggered)
        self.ui.actionStop.triggered.connect(self.actionStopTriggered)
        self.ui.actionCreateDataPlotter.triggered.connect(self.actionCreateDataPlotterTriggered)
        self.ui.actionCreateAveragerPlotter.triggered.connect(self.actionCreateAveragerPlotterTriggered)
        self.ui.actionPlugins.triggered.connect(self.actionPluginsParametersTriggered)
        self.ui.actionSettings.triggered.connect(self.onSettings)
        self.ui.actionClear.triggered.connect(self.actionClearTriggered)
        self.ui.actionSaveFigureAs.triggered.connect(self.saveFigureAsTriggered)
        self.ui.actionExportReflectogram.triggered.connect(self.exportReflectogramTriggered)
        self.ui.tabWidget.tabCloseRequested.connect(self.onTabCloseRequested)

        self.ui.actionExit.triggered.connect(self.ui.close)


        #self.reflectometer = None
        self.reflectometer = AQ7270Simulator()
        self.reflectometerIO = ReflectometerIOThread(self.reflectometer)
        self.AQ7270parameters = {}

        self.actionCreateDataPlotterTriggered()
        self.actionCreateAveragerPlotterTriggered()
        #self.actionCreatePartialSumPlotterTriggered()
        self.timer = QTimer(self.ui)

        self.pollTimer = QTimer(self.ui)
        self.pollTimer.singleShot(100, self.onTimer)

        self.currentReflectogram = None
        self.measurementControl = MeasurementsControl()
        self.stoppingConditions = {"timesLeft": None, "stopTime": None} #continuos monitoring
        self.measurementInterval = 5 #seconds

        QApplication.instance().aboutToQuit.connect(self.onQuit)

        self.settings = {}
        self.loadSettings()

        #icon = QIcon.fromTheme("messagebox-question-icon")
        #style = QApplication.style()
        #icon = style.standardIcon(QStyle.SP_MessageBoxQuestion)
        #self.ui.actionClear.setIcon(icon)
#        views = self.averager.getViews()
#        self.averager.setAxes('2D', self.static_axes)

        self.ui.actionCreatePartialSumPlotter.setVisible(False)

    def onSettings(self):
        setwnd = SettingsWindow(self.settings)
        if setwnd.exec():
            self.settings = setwnd.readSettings()

    def loadSettings(self):
        self.settings = {}
        self.settings['autosavepath'] = '../data'
        self.settings['autosaveAsJSON'] = True
        self.settings['autosaveAsCSV'] = True
        try:
            loadsettings = None
            with open("settings.json", "r") as f:
                loadsettings = json.load(f)
            if loadsettings is not None:
                self.settings |= loadsettings
        except:
            pass

    def saveSettings(self):
        js = json.dumps(self.settings, indent=2)
        with open("settings.json", "w") as f:
            f.write(js)

    def onQuit(self):
        if self.reflectometerIO:
            self.reflectometerIO.close()
        self.saveSettings()

    def actionCreateDataPlotterTriggered(self):
        plugin = LastReflectogram()
        plotter = PlotterWidget(None, [plugin])
        title = self.getUniqNameWithPrefix("Current data")
        icon = self.ui.actionCreateDataPlotter.icon()
        self.ui.tabWidget.addTab(plotter, icon, title)


    def actionCreateAveragerPlotterTriggered(self):
        plugin = Averager()
        plotter = PlotterWidget(None, [plugin])
        title = self.getUniqNameWithPrefix("Average")
        icon = self.ui.actionCreateAveragerPlotter.icon()
        self.ui.tabWidget.addTab(plotter, icon, title)

    def actionCreatePartialSumPlotterTriggered(self):
        plugin = PartSum()
        plotter = PlotterWidget(None, [plugin])
        title = self.getUniqNameWithPrefix("Partial sum")
        icon = self.ui.actionCreateAveragerPlotter.icon()
        self.ui.tabWidget.addTab(plotter, icon, title)


    def actionPluginsParametersTriggered(self):
        wnd = PluginParametersWnd(self.ui)
        for p in self.getPlugins():
            if isinstance(p, Averager):
                wnd.registerPlugin(p)
        #wnd.registerPlugin(self.averager)
        wnd.exec()

    def actionFindDeviceTriggered(self):
        wnd = FindDeviceWnd(self.ui)
        if wnd.exec() == FindDeviceWnd.Accepted:
            self.dev = wnd.dev
            if self.dev is not None:
                try:
                    self.reflectometer = AQ7270Series(self.dev, wnd.needReset)
                except Exception as err:
                    text = "Can''t connect to device.\n"
                    text += "Err: "+str(err) + "\n"
                    text += 'Fallback to simulator'
                    print(text)
                    msg = QMessageBox(self.ui)
                    msg.critical(self.ui, "Connection error", text)
                    self.reflectometer = AQ7270Simulator()
            else:
                self.reflectometer = AQ7270Simulator()
        self.reflectometerIO = ReflectometerIOThread(self.reflectometer)



    def actionReflectometerParametersTriggered(self):
        if self.reflectometerIO is not None:
            wnd = ChooseParametersWnd(self.ui, self.reflectometerIO)
            wnd.selectParameters(self.AQ7270parameters)
            if wnd.exec() == ChooseParametersWnd.Accepted:
                self.AQ7270parameters = wnd.parameters
                self.setParameters()
        else:
            print("Error: chooseParameters: No connection with reflectometer")

    def setParameters(self):
        if self.reflectometerIO is not None:
            self.reflectometerIO.setParameters(self.AQ7270parameters)
            if isinstance(self.reflectometer, AQ7270Series):
                self.settings['AQ7270Series'] = self.AQ7270parameters
            if isinstance(self.reflectometer, AQ7270Simulator):
                self.settings['AQ7270Simulator'] = self.AQ7270parameters

        else:
            print("Error: setParameters: No connection with reflectometer")

    def actionSingleMeasurementTriggered(self):
        #self.singleMeasurementStart()
        self.stoppingConditions["timesLeft"] = 1
        self.stoppingConditions["stopTime"] = None
        self.measurementControl.run()

        #self.measurementControl.runOnce()

    def actionRunTimesTriggered(self):
        dlg = QDialog(self.ui)
        dlg.setWindowTitle("Run measurements")
        layout = QGridLayout(dlg)

        nTimesSpinBox = QSpinBox()
        layout.addWidget(QLabel("Number of times"), 0, 0)
        layout.addWidget(nTimesSpinBox, 0, 1)
        nTimesSpinBox.setRange(1, 10000)
        nTimesSpinBox.setValue(10)

        layout.addWidget(QLabel("Interval (hh:mm:ss)"), 1, 0)
        intervalTimeEdit = QTimeEdit()
        intervalTimeEdit.setDisplayFormat("hh:mm:ss")
        intervalTimeEdit.setTime(PySide6.QtCore.QTime(0, 0, 30))
        layout.addWidget(intervalTimeEdit, 1, 1)

        btnbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btnbox.button(QDialogButtonBox.Ok).setText("Run")
        layout.addWidget(btnbox, 2, 0, 1, 2)

        btnbox.accepted.connect(dlg.accept)
        btnbox.rejected.connect(dlg.reject)


        if dlg.exec() == QDialog.Accepted:
            self.stoppingConditions["timesLeft"] = nTimesSpinBox.value()
            self.stoppingConditions["stopTime"] = None
            interval = intervalTimeEdit.time()
            self.measurementInterval = interval.hour()*3600 + interval.minute()*60 + interval.second()
            self.measurementControl.run()

    def actionRunDurationTriggered(self):
        dlg = QDialog(self.ui)
        dlg.setWindowTitle("Run measurements")
        layout = QGridLayout(dlg)

        #Create ui elements to specify the duration of measurements
        panel = PySide6.QtWidgets.QGroupBox()
        panel.setTitle("Measurements duration")
        layout2 = QGridLayout(panel)
        btnStopAtTime = QRadioButton("Run measurements until (dd.MM.yyyy hh:mm:ss)")
        layout2.addWidget(btnStopAtTime, 0, 0, 1, 2)
        dateTimeEdit = QDateTimeEdit()
        dateTimeEdit.setDisplayFormat("dd.MM.yyyy hh:mm:ss")
        layout2.addWidget(dateTimeEdit, 1, 0, 1, 2)
        dateTimeEdit.setMinimumDateTime(PySide6.QtCore.QDateTime.currentDateTime())

        layout2.addWidget(QRadioButton("Specify the duration of measurements"), 2, 0, 1, 2)
        hoursSpinBox = QSpinBox()
        minutesSpinBox = QSpinBox()
        secondsSpinBox = QSpinBox()
        hoursSpinBox.setRange(0, 1000)
        minutesSpinBox.setRange(0, 59)
        secondsSpinBox.setRange(0, 59)
        layout2.addWidget(QLabel("hours:"), 3, 0)
        layout2.addWidget(QLabel("minutes:"), 4, 0)
        layout2.addWidget(QLabel("seconds:"), 5, 0)
        layout2.addWidget(hoursSpinBox, 3, 1)
        layout2.addWidget(minutesSpinBox, 4, 1)
        layout2.addWidget(secondsSpinBox, 5, 1)
        layout.addWidget(panel, 0, 0, 1, 2)

        #create ui elements to specify interval between measurements
        layout.addWidget(QLabel("Interval (hh:mm:ss)"), 1, 0)
        intervalTimeEdit = QTimeEdit()
        intervalTimeEdit.setDisplayFormat("hh:mm:ss")
        intervalTimeEdit.setTime(PySide6.QtCore.QTime(0, 0, 30))
        layout.addWidget(intervalTimeEdit, 1, 1)

        #create dialog buttons
        btnbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btnbox.button(QDialogButtonBox.Ok).setText("Run")
        layout.addWidget(btnbox, 2, 0, 1, 2)

        btnbox.accepted.connect(dlg.accept)
        btnbox.rejected.connect(dlg.reject)

        def radioButtonSwitched(checked):
            hoursSpinBox.setEnabled(not checked)
            minutesSpinBox.setEnabled(not checked)
            secondsSpinBox.setEnabled(not checked)
            dateTimeEdit.setEnabled(checked)

        btnStopAtTime.toggled.connect(radioButtonSwitched)
        btnStopAtTime.setChecked(True)

        if dlg.exec() == QDialog.Accepted:
            if btnStopAtTime.isChecked() is True:
                stopTime = dateTimeEdit.dateTime()
                stopTime = stopTime.toPython()
            else:
                h = hoursSpinBox.value()
                m = minutesSpinBox.value()
                s = secondsSpinBox.value()
                stopTime = datetime.now()
                stopTime = stopTime + timedelta(0, h*3600 + m*60 + s)
            self.stoppingConditions["timesLeft"] = None
            self.stoppingConditions["stopTime"] = stopTime
            interval = intervalTimeEdit.time()
            self.measurementInterval = interval.hour()*3600 + interval.minute()*60 + interval.second()
            self.measurementControl.run()

    def actionRunContinuousTriggered(self):
        dlg = QDialog(self.ui)
        dlg.setWindowTitle("Run measurements")
        layout = QGridLayout(dlg)

        layout.addWidget(QLabel("Interval (hh:mm:ss)"), 0, 0)
        intervalTimeEdit = QTimeEdit()
        intervalTimeEdit.setDisplayFormat("hh:mm:ss")
        intervalTimeEdit.setTime(PySide6.QtCore.QTime(0, 0, 2))
        layout.addWidget(intervalTimeEdit, 0, 1)

        btnbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btnbox.button(QDialogButtonBox.Ok).setText("Run")
        layout.addWidget(btnbox, 1, 0, 1, 2)

        btnbox.accepted.connect(dlg.accept)
        btnbox.rejected.connect(dlg.reject)


        if dlg.exec() == QDialog.Accepted:
            self.stoppingConditions["timesLeft"] = None
            self.stoppingConditions["stopTime"] = None
            interval = intervalTimeEdit.time()
            self.measurementInterval = interval.hour()*3600 + interval.minute()*60 + interval.second()
            self.measurementControl.run()

    def actionStopTriggered(self):
        if self.reflectometer is not None:
            self.reflectometer.stopFlag = True
        self.measurementControl.manualStop()
        self.updateActions()

    def updateActions(self):
        isRunning = False
        isSingleRun = False
        match self.measurementControl.state:
            case "idle":
                isRunning = False
            case "measuring":
                isRunning = True
            case "measuringOnce":
                isRunning = True
                isSingleRun = True
            case "waiting":
                isRunning = True
        self.ui.actionStop.setEnabled(isRunning)
        self.ui.actionSingleMeasurement.setEnabled(not isRunning)
        self.monitoringBtn.setEnabled(not isRunning)
        if isRunning:
            self.monitoringBtn.setChecked(not isSingleRun)

    def onTimer(self):
        #1. Call triggers
        # calls measurementControl.dataAcquired, if neccessary
        self.pollMeasurementResults()
        #calls measurementControl.stop if neccessary
        self.measurementControl.checkStopConditions(self.stoppingConditions)
        # check sleepTimeElapsed if neccessary
        self.measurementControl.checkSleepTimeElapsed(self.measurementInterval)

        #2. Call event handlers
        if self.measurementControl.needToStartMeasuring():
            self.singleMeasurementStart()

        #3. Update status bar
        self.statusLabel.setText(self.measurementControl.statusText())
        self.stopConditionsLabel.setText(self.measurementControl.stopConditionsText())


        self.updateActions()

        self.pollTimer.singleShot(100, self.onTimer)

    def singleMeasurementStart(self): #replace by "run nTimes, nTimes = 1"
        if self.reflectometer is not None:
            self.reflectometerIO.runAverageAsync()
            if self.stoppingConditions["timesLeft"] is not None:
                self.stoppingConditions["timesLeft"] -= 1

    def pollMeasurementResults(self):
        if self.reflectometerIO is not None:
            r = self.reflectometerIO.lastReflectogram()
            if r is not None:
                for p in self.getPlugins():
                    p.collect(r["X"], r["Y"])
                    p.render()
                params = self.reflectometerIO.readParametersActualValues()
                params["model"] = self.reflectometer.modelName()
                self.currentReflectogram = r
                self.currentReflectogram["params"] = params
                if self.ui.actionAutosave.isChecked():
                    self.autosaveCurrentReflectogram()
                if self.measurementControl.is_measuring():
                    self.measurementControl.dataAcquired()
        else:
            print("Error: singleMeasurement: No connection with reflectometer")


    def getUniqNameWithPrefix(self, prefix):
        n = 1
        #generate uniq label
        labels = [self.ui.tabWidget.tabText(idx) for idx in range(self.ui.tabWidget.count())]
        while True:
            str = f'{prefix} {n}'
            if str not in labels:
                break
            else:
                n += 1
        return str


    def onTabCloseRequested(self, tabidex):
        self.ui.tabWidget.removeTab(tabidex)

    def saveFigureAsTriggered(self):
        plotter = self.ui.tabWidget.currentWidget()
        if plotter is None:
            msgbox =QMessageBox(QMessageBox.Warning, "Warning", "No figure to save", parent=self)
            msgbox.setIconPixmap(QIcon.fromTheme("error").pixmap(32, 32))
            msgbox.exec()
            return
        plotter.navigationBar.save_figure()

    def exportReflectogramTriggered(self):
        if self.currentReflectogram is None:
            msgbox = QMessageBox(QMessageBox.Warning, "Warning", "No data to save", parent=self.ui)
            msgbox.setIconPixmap(QIcon.fromTheme("error").pixmap(32, 32))
            msgbox.exec()
            return
        dlg = QFileDialog(self.ui, "Export reflectogram as...")
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setMimeTypeFilters(["application/json", "text/csv"])
        if dlg.exec() == QDialog.Accepted:
            filenames = dlg.selectedFiles()
            if len(filenames) > 0:
                filename = filenames[0]
                self.exportReflectogram(self.currentReflectogram, filename)

    def exportReflectogram(self, reflectogram, filename, t):
        mdb = QMimeDatabase()
        match mdb.mimeTypeForFile(filename, QMimeDatabase.MatchExtension).name():
            case 'application/json':
                self.exportReflectogramAsJSON(reflectogram, filename, t)
            case 'text/csv':
                self.exportReflectogramAsCSV(reflectogram, filename)
            case _:
                box = QMessageBox(self.ui)
                box.setIcon(QMessageBox.Warning)
                box.setWindowTitle("Can't save")
                box.setText(f"Can not decide which format to use. Please, select a correct file type (filename = \"{filename}\").")
                box.setIconPixmap(QIcon.fromTheme("error").pixmap(32, 32))
                box.exec()

    def exportReflectogramAsCSV(self, reflectogram, filename):
        X = reflectogram["X"]
        Y = reflectogram["Y"]
        with open(filename, "w+", newline='') as csvfile:
            writer = csv.writer(csvfile, dialect='excel')
            for row in zip(X, Y):
                writer.writerow(row)

    def exportReflectogramAsJSON(self, reflectogram, filepath, time=datetime.now()):
        params = reflectogram["params"]
        X = reflectogram["X"]
        Y = reflectogram["Y"]

        XY = [xy for xy in zip(X, Y)]
        js = json.dumps({'params': params, 'filesavetime': time, 'XY': XY}, indent = 2)

        with open(filepath, "w+") as f:
            f.write(js)

    def generateFileName(self, extensions):
        path = self.settings['autosavepath']
        path = os.path.abspath(path)
        if not os.path.exists(path):
            print(f'The specified path {path} doesn''t exists. Saving to the current directory')
            path = '.'
        t =  time.localtime()
        filepathes = []
        for ext in extensions:
            filename = f'otdr_{t.tm_year:4}_{t.tm_mon:02}_{t.tm_mday:02}_{t.tm_hour:02}_{t.tm_min:02}_{t.tm_sec:02}.{ext}'
            filepathes.append(os.path.join(path, filename))
        return filepathes, t

    def autosaveCurrentReflectogram(self):
        extensions = []
        if self.settings['autosaveAsJSON']:
            extensions.append('json')
        if self.settings['autosaveAsCSV']:
            extensions.append('csv')
        filepathes, t = self.generateFileName(extensions)
        for p in filepathes:
            self.exportReflectogram(self.currentReflectogram, p, t)

    def actionClearTriggered(self):
        for idx in range(self.ui.tabWidget.count()):
            self.ui.tabWidget.widget(idx).clear()

    def getPlugins(self):
        plugins = []
        for idx in range(self.ui.tabWidget.count()):
            plugins.extend(self.ui.tabWidget.widget(idx).plugins)
        return plugins



