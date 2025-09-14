import numpy as np

from plugins.collector import Collector
from .pluginsbase import PluginBase


class StatAlarm:
    def __init__(self):
        super().__init__()
        self.xmin = None
        self.xmax = None
        self.nsigma = 3  # parameter
        self.vthreshold = 0.5
        self.zmean = None
        self.zsigma = None
        self.zup = None
        self.zbottom = None

    def clear(self):
        self.xmin = None
        self.xmax = None
        #self.nsigma = 3  # do not change this parameter during clear
        #self.vthreshold = 0.5 # do not change this parameter during clear
        self.zmean = None
        self.zsigma = None
        self.zup = None
        self.zbottom = None

    def getParameters(self):
        param1 = {"text": "xmin, m", "name": "xmin", "value": self.xmin}
        param2 = {"text": "xmax, m", "name": "xmax", "value": self.xmax}
        param3 = {"text": "nsigma", "name": "nsigma", "value": self.nsigma}
        param3["hint"] = "alert, when the deviation is greater than n*sigma"
        param4 = {"text": "violation threshold", "name": "vthreshold", "value": self.vthreshold}
        param4["hint"] = "if violation is greater than this threshold, the alarm signal is emited"
        return [param1, param2, param3, param4]

    def setParameters(self, parameters):
        Collector.setParameters(self, parameters)
        for name, value in parameters.items():
            match name:
                case "xmin":
                    self.xmin = float(value)
                case "xmax":
                    self.xmax = float(value)
                case "nsigma":
                    self.nsigma = float(value)
                case "vthreshold":
                    self.vthreshold = float(value)
        self.update()

    def available(self):
        return self.zmean is not None and self.zup is not None and self.zbottom is not None

    def update(self, zz):
        #self.updateZ()
        self.zmean = None
        self.zsigma = None
        self.zup = None
        self.zbottom = None
        self.zz = zz
        if zz is not None and zz.shape[1] >= 2:
            self.zmean = np.mean(zz, 1)
            if zz.shape[1] >= 5:
                self.zsigma = np.std(zz, 1, ddof=1) #square root of the average of the squared deviations from the mean
                self.zup = self.zmean + self.nsigma * self.zsigma
                self.zbottom = self.zmean - self.nsigma * self.zsigma

    def checkViolations(self, x, z):
        violations = None
        if not self.available():
            print("Alarm not initialized")
            print(f"Number of measurements: {self.zz.shape[1]}")
        else:
            idx = self.xToIndex([self.xmin, self.xmax], x)
            if self.xmin is None:
                idx[0] = 0
            if self.xmax is None:
                idx[1] = z.shape[0]
            count = 0
            for n in range(idx[0], idx[-1]):
                if z[n] < self.zbottom[n] or z[n] > self.zup[n]:
                    count += 1
            violations = count / (idx[1] - idx[0] + 1)
        return violations

    def xToIndex(self, xcur, xlist):
        res = xcur
        xleft = xlist[0]
        xright = xlist[-1]
        npoints = len(xlist)
        for n in range(len(xcur)):
            if xcur[n] is None:
                continue
            res[n] = int(npoints * (xcur[n] - xleft) / (xright - xleft))
            if res[n] > self.npoints:
                res[n] = self.npoints
        return res


class DiffAverager:
    def __init__(self):
        super().__init__()
        self.collector = Collector()
        self.statAlarm = StatAlarm()
        self.x = None
        self.z = None
        self.zup = None
        self.zbottom = None
        self.zmean = None

    def clear(self):
        self.collector.clear()
        self.statAlarm.clear()
        self.x = None
        self.z = None
        self.zup = None
        self.zbottom = None
        self.zmean = None

    def name(self):
        return "averager"

    def getParameters(self):
        return self.collector.getParameters() + self.statAlarm.getParameters()

    def collect(self, x, y):
        #Convert to numpy arrays
        x, y = self.collector.listToArray(x, y)
        if self.collector.canAccept(x, y) is False:
            self.clear()
        self.y = y #save current value of y


        #Transform data
        z = y
        zz = self.collector.yy

        #Update alarms
        self.statAlarm.update(zz)

        if self.statAlarm.available():
            #if statistics is available, calculate violations
            violations = self.statAlarm.checkViolations(x, z)
            if violations < self.statAlarm.vthreshold:
                #collect
                self.collector.collect(x, y)
        else:
            #statistics is not available yet, collect data
            self.collector.collect(x, y)
            zz = self.collector.yy
            self.statAlarm.update(zz)

        self.x = x
        self.z = z
        self.zup = self.statAlarm.zup
        self.zbottom = self.statAlarm.zbottom
        self.zmean = self.statAlarm.zmean


class StatisticsPlotter(PluginBase):
    def __init__(self, mathbackend):
        super().__init__()
        self.alarmLevel = None
        self.statusLabel = None
        self.mathbackend = mathbackend

    def clear(self):
        self.mathbackend.clear()
        self.alarmLevel = None
        self.statusLabel = None
        self.render()

    def getParameters(self):
        return self.mathbackend.getParameters()

    def setParameters(self, parameters):
        self.mathbackend.setParameters(parameters)

    def collect(self, x, y):
        self.mathbackend.collect(x, y)

    def name(self):
        return self.mathbackend.name()

    def registerStatusLabel(self, statusLabel):
        self.statusLabel = statusLabel

    def setXLimits(self, xmin, xmax):
        self.xmin = xmin
        self.xmax = xmax

    def status(self):
        nmeasurements = self.mathbackend.yy.shape[1]
        print(f'nmeasurements = {nmeasurements}')

    def getViews(self):
        minus = bytes([0xE2, 0x88, 0x92])
        return ['Signal', 'Signal '+minus.decode('utf-8')+' mean'] #Qt uses utf-8 encoding

    def render(self):
        if self.canvas is None:
            return
        x = None
        z = None
        zup = None
        zmean = None
        zbottom = None
        self.setStatusText("No data")
        if self.mathbackend.x is not None:
            x = self.mathbackend.x.copy()
            z = self.mathbackend.z.copy()
            self.setStatusText("Not enough data ")
        if self.mathbackend.zup is not None:
            zup = self.mathbackend.zup.copy()
            zmean = self.mathbackend.zmean.copy()
            zbottom = self.mathbackend.zbottom.copy()
            self.setStatusText("Ok")

        views = self.getViews()
        if self.currentView == views[1]:
            if zmean is not None:
                z -= zmean[:, np.newaxis]
                if zup is not None:
                    zup -= zmean
                if zbottom is not None:
                    zbottom -= zmean
                zmean -= zmean
            else:
                zup, zmean = None, None
                self.setStatusText("Not enough data to plot average values")
        self.canvas.namedLine('cur', x, z, color='blue', linewidth=1)
        self.canvas.namedLine('mean', x, zmean, color='green', linewidth=1)
        self.canvas.namedLine('up', x, zup, color='red', linewidth=1)
        self.canvas.namedLine('bottom', x, zbottom, color='red', linewidth=1)
        self.canvas.axes.relim()
        self.canvas.axes.autoscale_view()
        self.canvas.axes.set_xlabel('range, m')
        self.canvas.axes.set_ylabel('dB')
        self.canvas.axes.grid(True)
        self.canvas.draw()

class Averager(StatisticsPlotter):
    def __init__(self):
        StatisticsPlotter.__init__(self, DiffAverager())



