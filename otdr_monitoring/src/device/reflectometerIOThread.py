import threading, queue
import enum
import time
from .abstractreflectometer import AbstractReflectometer

class ReflectometerIOThread:
    commands = enum.IntEnum('commands', 'readParams readParamsActualValues setParams runAverage stop')

    def __init__(self, reflectometer: AbstractReflectometer):
        self.reflectometer = reflectometer
        self.stop = False
        self.cmdQueue = queue.Queue()
        self.resultsQueue = queue.Queue()
        self.reflectogram = None
        self.parameters = None
        self.thread = threading.Thread(target = thread, args = (self.cmdQueue, self.resultsQueue, self.reflectometer))
        self.thread.start()

    def __del__(self):
        print('ReflectometerIOThread::__del__')
        self.close()

    def close(self):
        print('ReflectometerIOThread::close')
        self.cmdQueue.put(ReflectometerIOThread.commands.stop)
        print('joining IOthread')
        self.thread.join()
        #self.cmdQueue.join()
        print('joining Ok')

    def stop(self):
        self.reflectometer.stopFlag = True

    def readParametersAsync(self):
        self.cmdQueue.put(self.commands.readParams)

    def readParametersActualValuesAsync(self):
        self.cmdQueue.put(self.commands.readParamsActualValues)

    def readParameters(self):
        self.cmdQueue.join()
        self.readParametersAsync()
        res = None
        while res is None:
            res = self.lastParameters()
        return res

    def readParametersActualValues(self):
        self.cmdQueue.join()
        self.readParametersActualValuesAsync()
        res = None
        while res is None:
            res = self.lastParameters()
        return res

    def setParametersAsync(self, parameters : dict):
        self.cmdQueue.put(self.commands.setParams)
        self.cmdQueue.put(parameters)

    def setParameters(self, parameters):
        self.cmdQueue.join()
        self.setParametersAsync(parameters)
        res = None
        while(self.resultsQueue.empty()):
            pass
        cmd = self.resultsQueue.get()
        while(self.resultsQueue.empty()):
            pass
        res = self.resultsQueue.get()
        return res

    def runAverageAsync(self):
        self.cmdQueue.put(self.commands.runAverage)

    def parseResults(self):
        while not self.resultsQueue.empty():
            cmd = self.resultsQueue.get()
            match cmd:
                case self.commands.readParams:
                    self.parameters = self.resultsQueue.get()
                case self.commands.readParamsActualValues:
                    self.parameters = self.resultsQueue.get()
                case self.commands.runAverage:
                    self.reflectogram = self.resultsQueue.get()
                case _:
                    raise NotImplementedError

    def lastReflectogram(self):
        self.parseResults()
        if self.reflectogram is not None:
            res = self.reflectogram
            self.reflectogram = None
            return res
        else:
            return None

    def lastParameters(self):
        self.parseResults()
        if self.parameters is not None:
            res = self.parameters
            self.parameters = None
            return res
        else:
            return None

    def getAllParameters(self):
        return self.reflectometer.getAllParameters()

    def updateVisibility(self, parameters, values):
        """Updates the visibility of parameters"""
        return self.reflectometer.updateVisibility(parameters, values)


def thread(cmdQueue, resultsQueue, reflectometer):
    """
    This function is a separate thread to work with the reflectometer object.
    :param cmdQueue: the queue object to send commands from the main thread to this function
    :param resultsQueue: the queue object to pass results from this function to the main thread
    :param reflectometer: the reflectometer object, see aq7270protocol
    :return: None

    Design: If this function would be the member function of the ReflectometerIOThread, the program will sometimes hang
    on exit. I don't know the exact reason of this. So, this function is placed out of the ReflectometerIOThread class.
    """
    stop = False
    while not stop:
        cmd = cmdQueue.get()
        match cmd:
            case ReflectometerIOThread.commands.readParams:
                print('readParams')
                params = reflectometer.readParameters()
                resultsQueue.put(ReflectometerIOThread.commands.readParams)
                resultsQueue.put(params)
            case ReflectometerIOThread.commands.readParamsActualValues:
                print('readParams: actual values')
                params = reflectometer.readParametersActualValues()
                resultsQueue.put(ReflectometerIOThread.commands.readParamsActualValues)
                resultsQueue.put(params)
            case ReflectometerIOThread.commands.setParams:
                params = cmdQueue.get()
                print('setParams', params)
                res = reflectometer.setParameters(params)
                resultsQueue.put(ReflectometerIOThread.commands.setParams)
                resultsQueue.put(res)
                cmdQueue.task_done()
            case ReflectometerIOThread.commands.runAverage:
                print('runAverage')
                reflectometer.runAverage()
                X, Y = reflectometer.lastReflectogram()
                if X is not None and Y is not None:
                    res = {'X': X, 'Y': Y}
                    resultsQueue.put(ReflectometerIOThread.commands.runAverage)
                    resultsQueue.put(res)
            case ReflectometerIOThread.commands.stop:
                print('stop')
                stop = True
        cmdQueue.task_done()
    print('IOThread exits')


