import numpy as np

from plugins.collector import Collector
from .pluginsbase import PluginBase


class CumSumAlarm:
    def __init__(self):
        super().__init__()
        self.xmin = None
        self.xmax = None
        self.nsigma = 3  # parameter
        self.vthreshold = 0.5
        self.zmean = None
        self.zsigma = None
        self.cumsum = None
        self.zup1 = None
        self.zup2 = None
        self.zup3 = None
        self.zbottom1 = None
        self.zbottom2 = None
        self.zbottom3 = None

    def clear(self):
        self.xmin = None
        self.xmax = None
        #self.nsigma = 3  # do not change this parameter during clear
        #self.vthreshold = 0.5 # do not change this parameter during clear
        self.zmean = None
        self.zsigma = None
        self.cumsum = None
        self.zup1 = None
        self.zup2 = None
        self.zup3 = None
        self.zbottom1 = None
        self.zbottom2 = None
        self.zbottom3 = None

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

    def update(self, yy, y):
        if yy is None:
            return
        nPoints = yy.shape[0]
        nMeasurements = yy.shape[1]
        if nPoints == 0 or nMeasurements == 0:
            return

        #yy -= np.mean(yy[0:100, :])
        #y -= np.mean(y[0:100])

        self.ymean = None
        self.yy = yy
        if yy is not None and nMeasurements >= 5:
            self.ymean = np.mean(yy, 1)
            self.zsigma = np.std(yy - self.ymean[:, np.newaxis], 1, ddof=1)  # sqrt of the average of the squared deviations
            zeroflags = self.zsigma == 0
            self.zsigma[zeroflags] = 1
            z = y - self.ymean[:, np.newaxis]
            z = z[:, 0]
            z /= self.zsigma
            z[zeroflags] = 0
            self.cumsum = np.cumsum(z)
            nn = np.arange(0, nPoints) + 1
            self.zup1 = np.sqrt(nn)
            self.zup2 = 5*np.sqrt(nn)
            self.zup3 = 10*np.sqrt(nn)
            self.zbottom1 = -np.sqrt(nn)
            self.zbottom2 = -5*np.sqrt(nn)
            self.zbottom3 = -10*np.sqrt(nn)
            pass

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


class DiffAverager2:
    def __init__(self):
        super().__init__()
        self.collector = Collector()
        self.statAlarm = CumSumAlarm()
        self.x = None
        self.z = None
        self.zup1 = None
        self.zup2 = None
        self.zup3 = None
        self.zbottom1 = None
        self.zbottom2 = None
        self.zbottom3 = None
        self.zmean = None
        self.cumsum = None

    def clear(self):
        self.collector.clear()
        self.statAlarm.clear()
        self.x = None
        self.z = None
        self.zup1 = None
        self.zup2 = None
        self.zup3 = None
        self.zbottom1 = None
        self.zbottom2 = None
        self.zbottom3 = None
        self.zmean = None
        self.cumsum = None

    def name(self):
        return "partsum"

    def getParameters(self):
        return self.collector.getParameters() + self.statAlarm.getParameters()

    def collect(self, x, y):
        #Convert to numpy arrays
        x, y = self.collector.listToArray(x, y)
        if self.collector.canAccept(x, y) is False:
            self.clear()

        y -= np.mean(y[100:1000])
        self.y = y #save current value of y

        #Update alarms
        self.statAlarm.update(self.collector.yy, y)
        self.collector.collect(x, y)
        self.x = self.collector.x
        self.cumsum = self.statAlarm.cumsum
        self.zup1 = self.statAlarm.zup1
        self.zup2 = self.statAlarm.zup2
        self.zup3 = self.statAlarm.zup3
        self.zbottom1 = self.statAlarm.zbottom1
        self.zbottom2 = self.statAlarm.zbottom2
        self.zbottom3 = self.statAlarm.zbottom3


class PartSumPlotter(PluginBase):
    def __init__(self, mathbackend):
        super().__init__()
        self.mathbackend = mathbackend

    def clear(self):
        self.mathbackend.clear()
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
        return ['Signal']

    def render(self):
        if self.canvas is None:
            return
        x = None
        cumsum = None
        zup1 = None
        zup2 = None
        zup3 = None
        zbottom1 = None
        zbottom2 = None
        zbottom3 = None
        self.setStatusText("No data")
        if self.mathbackend.cumsum is not None:
            x = self.mathbackend.x
            cumsum = self.mathbackend.cumsum
            zup1 = self.mathbackend.zup1
            zup2 = self.mathbackend.zup2
            zup3 = self.mathbackend.zup3
            zbottom1 = self.mathbackend.zbottom1
            zbottom2 = self.mathbackend.zbottom2
            zbottom3 = self.mathbackend.zbottom3
            self.setStatusText("Ok")

        self.canvas.namedLine('cumsum', x, cumsum, color='blue', linewidth=1)
        self.canvas.namedLine('up1sigma', x, zup1, color='red', linewidth=1)
        self.canvas.namedLine('up2sigma', x, zup2, color='red', linewidth=1)
        self.canvas.namedLine('up3sigma', x, zup3, color='red', linewidth=1)
        self.canvas.namedLine('bottom1sigma', x, zbottom1, color='red', linewidth=1)
        self.canvas.namedLine('bottom2sigma', x, zbottom2, color='red', linewidth=1)
        self.canvas.namedLine('bottom3sigma', x, zbottom3, color='red', linewidth=1)
        self.canvas.axes.relim()
        self.canvas.axes.autoscale_view()
        self.canvas.axes.set_xlabel('range, m')
        self.canvas.axes.set_ylabel('dB')
        self.canvas.axes.grid(True)
        self.canvas.draw()

class PartSum(PartSumPlotter):
    def __init__(self):
        PartSumPlotter.__init__(self, DiffAverager2())



