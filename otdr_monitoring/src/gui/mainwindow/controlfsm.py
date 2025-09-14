#ControlFSM - control finite state machine
import transitions, datetime

class MeasurementsControl:
    def __init__(self):
        mystates = ['idle', 'measuring', 'waiting']
        mytransitions = [
            #Small submachine for single measurements: idle -> measuringOnce -> idle
            #{'trigger': 'runOnce', 'source': 'idle', 'dest': 'measuringOnce'},
            #{'trigger': 'dataAcquired', 'source': 'measuringOnce', 'dest': 'idle', 'after': 'dataAcquiredAfter'},

            # Submachine for monitoring mode: idle -> measuringOnce -> waiting -> measuringOnce -> waiting -> ... -> finished
            {'trigger': 'run', 'source': 'idle', 'dest': 'measuring'},
            {'trigger': 'dataAcquired', 'source': 'measuring', 'dest': 'waiting'},
            {'trigger': 'sleepTimeElapsed', 'source': 'waiting', 'dest': 'measuring'},
            {'trigger': 'stop', 'source': 'waiting', 'dest': 'idle', 'after': 'stopAfter'},
            {'trigger': 'manualStop', 'source': '*', 'dest': 'idle', 'after': 'manualStopAfter'}
        ]
        self.machine = transitions.Machine(self, states=mystates, transitions=mytransitions, initial='idle')
        self._startMeasure = False
        self.lastMeasurementFinishedTime = None
        self._waitElapsedText = None
        self._stopConditionsText = None
        self._reason = None

    def statusText(self):
        str = self.state
        if self._waitElapsedText is not None:
            str += self._waitElapsedText
        if self._reason is not None:
            str += "(" + self._reason + ")"
        return str

    def stopConditionsText(self):
        return self._stopConditionsText

    def checkStopConditions(self, stoppingConditions):
        if self.is_waiting():
            nTimesIsOver = False
            self._stopConditionsText = ""
            if stoppingConditions["timesLeft"] is not None:
                nTimesIsOver = stoppingConditions["timesLeft"] == 0
                self._stopConditionsText += f"{stoppingConditions['timesLeft']} measurements left"
            timeElapsed = False
            if stoppingConditions["stopTime"] is not None:
                timeElapsed = datetime.datetime.now() > stoppingConditions["stopTime"]
                self._stopConditionsText += f" run until {stoppingConditions['stopTime']: %d %b, %Y, %H:%M:%S}"
            if nTimesIsOver or timeElapsed:
                #self._reason = "successfully finished"
                self.stop()
        else:
            self._stopConditionsText = None

    def checkSleepTimeElapsed(self, measurementInterval):
        if self.is_waiting():
            curtime = datetime.datetime.now()
            elapsed = measurementInterval - (curtime - self.lastMeasurementFinishedTime).total_seconds()
            if self.lastMeasurementFinishedTime is None or elapsed <= 0:
                lastMeasurementFinishedTime = curtime
                self.sleepTimeElapsed()
            self._waitElapsedText = f" {int(elapsed):3} s"
        else:
            self._waitElapsedText = None


    def on_enter_measuring(self):
        self._startMeasure = True
        self._reason = None

    def on_enter_measuringOnce(self):
        self._startMeasure = True

    def on_exit_measuring(self):
        self.lastMeasurementFinishedTime = datetime.datetime.now()

    def needToStartMeasuring(self):
        res = self._startMeasure
        self._startMeasure = False
        return res

    def stopAfter(self):
        self._reason = "success"

    def manualStopAfter(self):
        self._reason = "terminated by user"






