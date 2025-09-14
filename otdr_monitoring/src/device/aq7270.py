import asyncio
from .aq7270protocol import AQ7270protocol
from .aq7270simulator import AQ7270Simulator
import time


class AQ7270Series(AQ7270protocol,AQ7270Simulator):
	def __init__(self, dev, needReset : bool = False):
		AQ7270protocol.__init__(self, dev, needReset)
		AQ7270Simulator.__init__(self, dev)
		self.Ready = True
		self.cmdmap = {}
		self.cmdmap['wavelength'] = self.cmdAcquireWavelength
		self.cmdmap['drange'] = self.cmdAcquireDrange
		self.cmdmap['pwidth'] = self.cmdAcquirePWidth
		self.cmdmap['attenuation'] = self.cmdAcquireAttenuation
		self.cmdmap['smpinterval'] = self.cmdAcquireSMPintervalData
		self.cmdmap['nmeasurements'] = self.cmdAcquireAverageIndex
		self.cmdmap['smptime'] = self.cmdAcquireAverageTime
		self.cmdmap['avertype'] = self.cmdAcquireAverageType
		self.cmdmap['avermode'] = self.cmdAcquireAverageMode
		#self.cmdmap['offset'] = self.cmdAcquireOffset
		self.askmap = {}
		self.askmap['wavelength'] = self.askAcquireWavelength
		self.askmap['drange'] = self.askAcquireDrange
		self.askmap['pwidth'] = self.askAcquirePWidth
		self.askmap['attenuation'] = self.askAcquireAttenuation
		self.askmap['smpinterval'] = self.askAcquireSMPintervalData
		self.askmap['nmeasurements'] = self.askAcquireAverageIndex
		self.askmap['smptime'] = self.askAcquireAverageTime
		self.askmap['avertype'] = self.askAcquireAverageType
		self.askmap['avermode'] = self.askAcquireAverageMode
		#For these parameters the value can be AUTO, and the actual numeric value should be read
		#with the following commands:
		self.askautovaluesmap = {}
		self.askautovaluesmap['drange'] = self.askAcquireAutoDrange
		self.askautovaluesmap['pwidth'] = self.askAcquireAutoPWidth
		self.askautovaluesmap['attenuation'] = self.askAcquireAutoAttenuation
		self.askautovaluesmap['smpinterval'] = self.askAcquireSMPintervalValue
		self.askautovaluesmap['nmeasurements'] = self.askAcquireAverageCount
		#self.askmap['offset'] = self.askAcquireOffset
		self.connect(dev, needReset)

		self.stopped = False

	def modelName(self):
		return "Yokogawa AQ7270"

	def testParameter(self, pname, pvalue=None):
		print(f"Testing: {pname} {pvalue}")
		try:
			cmdtext = self.cmdmap[pname]
			self.cmd(cmdtext, pvalue)
			v = self.readParameter(pname)
			if v == pvalue:
				print(f"Param {pname} Ok")
				return True
			else:
				print(f"Error in param {pname}: send {pvalue}, received {v}")
				return False
		except KeyError as e:
			print("Unknown command: ", e)
		#res = self.cmd(":STATUS:ERROR?")
		#print(res)
		#res = self.cmd(":STATUS:CONDITION?")
		#print(res)
		#print()

	def readParameter(self, pname): #can return 'AUTO'
		"""This function can return AUTO for some parameters, to read
		actual value use self.readParameterActualValue"""
		cmdtext = self.askmap[pname]
		v = self.cmd(cmdtext)
		v = v.split()
		v = v[-1]
		return v

	def readParameters(self): #can return 'AUTO'
		"""This function can return AUTO for some parameters, to read
		actual value use self.readParameterActualValue"""
		res = {}
		allParams = self.getAllParameters()
		for p in allParams:
			pname = p['name']
			v = self.readParameter(pname)
			res[pname] = v
		return res

	def readParameterActualValue(self, pname):
		v = self.readParameter(pname)
		if v == 'AUTO' or v == 'HI' or v == 'NORMAL':
			#We should do this check to avoid reflectometer error
			if pname in self.askautovaluesmap.keys():
				cmdtext = self.askautovaluesmap[pname]
				v = self.cmd(cmdtext)
				v = v.split()
				v = v[-1]
			else:
				raise RuntimeError("Unexpected response from reflectometer")
		return v

	def readParametersActualValues(self):
		res = {}
		allParams = self.getAllParameters()
		for p in allParams:
			pname = p['name']
			v = self.readParameterActualValue(pname)
			res[pname] = v
		return res


	def setParameters(self, parameters : dict):
		b = True
		for key, value in parameters.items():
			b &= self.testParameter(key, value)
		return b

	def runAverage(self):
		print('\nMeasuring, please wait...')
		#if we try immediately to read condition register, it can be not updated yet.
		time.sleep(1) #wait for reflectometer to update his condition register
		self.cmd(AQ7270Series.cmdAcquireAverageStart)
		self.printCmdResults(AQ7270Series.askAcquireAverageIndex)
		conditionRegister = 2 #means 'measuring'
		averCount = 0
		self.stopped = False
		while int(conditionRegister) & 2:
			curConditionRegister = self.cmd(":STATUS:CONDITION?")
			if curConditionRegister != conditionRegister:
				conditionRegister = curConditionRegister
				print(f"Condition = {conditionRegister}")
			curAverCount = self.cmd(AQ7270Series.askAcquireAverageCount)
			if curAverCount != averCount:
				averCount = curAverCount
				print(f'Current average count: {averCount}')

			time.sleep(0.5)
			if self.stopFlag:
				print('Measuring terminated')
				self.stopFlag = False
				self.stopped = True
				break
		self.cmd(AQ7270Series.cmdAcquireAverageStop)
		if self.stopped == False:
			print('Measuring successfully finished')
		return True

	def printCmdResults(self, cmd, params = None):
		res = self.cmd(cmd, params)
		print(res)

	def printstatus(self):
		self.printCmdResults(AQ7270Series.askFileDriveFree)
		self.printCmdResults(AQ7270Series.askFileFolderPath)

		self.printCmdResults(AQ7270Series.askAcquireAttenuation)
		self.printCmdResults(AQ7270Series.askAcquireAverageMode)
		self.printCmdResults(AQ7270Series.askAcquireSetting)
		self.printCmdResults(AQ7270Series.askAcquireWavelength)
		self.printCmdResults(AQ7270Series.askAcquireDrange)
		self.printCmdResults(AQ7270Series.askAcquirePWidth)
		self.printCmdResults(AQ7270Series.askAcquireAverageContinue)
		self.printCmdResults(AQ7270Series.askAcquireAverageCount)
		self.printCmdResults(AQ7270Series.askAcquireAverageIndex)
		self.printCmdResults(AQ7270Series.askAcquireAverageTime)
		self.printCmdResults(AQ7270Series.askAcquireAverageType)
		self.printCmdResults(AQ7270Series.askAcquireSMPintervalData)
		self.printCmdResults(AQ7270Series.askAcquireSMPintervalValue)

		[subfolders, files] = self.listFiles()
		print("Files:")
		print(files)
		print("Subfolders:")
		print(subfolders)

		for f in files:
			self.downloadFile(f)

	def flushbuffer(self):
		totalLen = 0
		try:
			while(True):
				a = self.dev.read(self.inport, self.bufsize, self.timeout)
				totalLen += len(a)
				#print(a)
		except BaseException as exc:
			pass
		finally:
			print(f"Flush buffer: {totalLen} bytes read")

	def lastReflectogram(self):
		if self.stopped == False:
			y = self.getWaveData()
			#parameters = self.readParameters()
			#smpinterval = float(parameters['smpinterval'])
			smpintervalanswer = self.cmd(AQ7270protocol.askAcquireSMPintervalValue)
			smpintervalanswer = smpintervalanswer.split()
			smpinterval = float(smpintervalanswer[-1])
			x = [smpinterval*i for i in range(0, len(y))]
			return x, y
		else:
			# The reflectogram is not valid when measurements were stopped. Return None, None
			return None, None


#NOT USED:
	def Average(self, wavelength, drange, pwidth, attenuation, smpinterval, nmeasurements):
		'''Set the specified parameters and run averaging measurements.'''
		'''See also: setParameters, runAverage'''
		print("Running averaging measurements:")
		print(f"\twavelength = {wavelength}")
		print(f"\tdrange = {drange}")
		print(f"\tpwidth = {pwidth}")
		print(f"\tattenuation = {attenuation}")
		print(f"\tsmpinterval = {smpinterval}")
		print(f"\tnmeasurements = {nmeasurements}")
		self.cmd(AQ7270Series.cmdAcquireSetting, "DETAIL")
		self.cmd(AQ7270Series.cmdAcquireAverageMode, "HISPEED") #modes = ["HIREFLECTION", "HISPEED"]
		b = True
		b &= self.testParameter(AQ7270Series.cmdAcquireWavelength, wavelength)
		b &= self.testParameter(AQ7270Series.cmdAcquireDrange, drange)
		b &= self.testParameter(AQ7270Series.cmdAcquirePWidth, pwidth)
		b &= self.testParameter(AQ7270Series.cmdAcquireAttenuation, attenuation)
		b &= self.testParameter(AQ7270Series.cmdAcquireSMPintervalData, smpinterval)
		b &= self.testParameter(AQ7270Series.cmdAcquireAverageType, "TIMES") #types = ["TIMES", "DURATION"]
		b &= self.testParameter(AQ7270Series.cmdAcquireAverageIndex, str(nmeasurements))
		if b == False:
			return False
		self.runAverage()
