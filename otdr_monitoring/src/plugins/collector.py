import numpy as np

class Collector:
    def __init__(self):
        self.averagingCount = 100
        self.npoints = None #should be None or positive integer
        self.x = None  # should be None of numpy.array of size npoints x 1
        self.yy = None # should be None of numpy.array of size npoints x k

    def clear(self):
        self.x = None
        self.yy = None
        self.npoints = None

    def getParameters(self):
        param = {"text": "aver count", "name": "avercount", "value": self.averagingCount}
        param["hint"] = "take average on n last measurements"
        return [param]

    def setParameters(self, parameters):
        for name, value in parameters.items():
            match name:
                case "avercount":
                    self.averagingCount = float(value)

    def listToArray(self, x, y):
        """Converts x and y from list to numpy array"""
        # todo: use interpolation if x was changed
        ycur = np.array(y) #create 1d array
        ycur = ycur[:, np.newaxis] #convert to column-like matrix
        xcur = np.array(x)
        return xcur, ycur

    def canAccept(self, x, y):
        assert (x.shape[0] == y.shape[0])
        if self.npoints is None:
            return True
        else:
            npoints = x.shape[0]
            return self.npoints == npoints

    def collect(self, x, y):
        assert (x.shape[0] == y.shape[0])

        npoints = x.shape[0]

        if self.npoints is not None:
            assert(self.npoints == npoints)
            #if self.npoints != npoints:
                # the number of points was changed, clear all data
                #self.yy = None
                #self.x = None
                #self.npoints = None

        if self.yy is None:
            # this is the first measurement
            self.yy = y
            self.x = x
            self.npoints = npoints
        else:
            # append this measurement to previous measurements
            assert (self.npoints == npoints)
            self.yy = np.c_[self.yy, y]
            #remove old data
            while self.yy.shape[1] > self.averagingCount:
                self.yy = self.yy[:, 1:]
