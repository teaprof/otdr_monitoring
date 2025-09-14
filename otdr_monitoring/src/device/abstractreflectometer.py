from abc import ABCMeta
class AbstractReflectometer:
    def __init__(self):
        self.stopFlag = False #When set to True, the current measuring operation will be stop and flag will be returned to False

    def getAllParameters(self):
        """
        :return:
            list of parameters, each parameter is a dictionary with following keys:
                'name' : some string value that is unique and can be used as key value in dictionaries
                'text' : text representation of this parameter
                'values' : list of possible values
                'values_text' : text representation of the possible values
                'enabled': true of false, see updateVisibility
        """
        raise NotImplementedError

    def modelName(self):
        raise NotImplementedError

    def updateVisibility(self, parameters, values):
        raise NotImplementedError

    def setParameters(self, parameters: dict):
        raise NotImplementedError

    def readParameters(self):
        raise NotImplementedError

    def runAverage(self):
        raise NotImplementedError

    def lastReflectogram(self):
        """
        X, Y = lastReflectogram(self):
        :return:
            X, Y: x (km) and y (dB) values
        """
        raise NotImplementedError
