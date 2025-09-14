from .aq7270protocol import AQ7270protocol
from numpy import random
from .abstractreflectometer import AbstractReflectometer

class AQ7270Simulator(AbstractReflectometer):
	def __init__(self, dev = None):
		self.params = None
		self.initParameters()
		super().__init__()

	def getAllParameters(self): #overrides AbstractReflectometer.getAllParameters
		p0 = {'name': 'wavelength', 'text': 'wave length', 'values': AQ7270protocol.wavelengths, 'values_text': AQ7270protocol.wavelengths_text}
		p1 = {'name': 'drange',  'text': 'distance range', 'values': AQ7270protocol.dranges, 'values_text': AQ7270protocol.dranges_text}
		p2 = {'name': 'pwidth',  'text': 'pulse width', 'values': AQ7270protocol.pwidths, 'values_text': AQ7270protocol.pwidths_text}
		p3 = {'name': 'attenuation', 'text': 'attenuation', 'values': AQ7270protocol.attenuations, 'values_text': AQ7270protocol.attenuations_text}
		p4 = {'name': 'smpinterval', 'text': 'sampling interval', 'values': AQ7270protocol.smpintervals, 'values_text': AQ7270protocol.smpintervals_text}
		p5 = {'name': 'avermode', 'text': 'averaging mode', 'values': AQ7270protocol.avermodes, 'values_text': AQ7270protocol.avermodes_text}
		p6 = {'name': 'avertype', 'text': 'averaging type', 'values': AQ7270protocol.avertypes, 'values_text': AQ7270protocol.avertypes_text}
		p7 = {'name': 'nmeasurements', 'text': 'Number of measurements', 'values': AQ7270protocol.nmeasurements, 'values_text': AQ7270protocol.nmeasurements_text}
		p8 = {'name': 'smptime', 'text': 'averaging time', 'values': AQ7270protocol.avertimes, 'values_text': AQ7270protocol.avertimes_text}
		#p9 = {'name': 'offset', 'text': 'offset, m', 'values': 'positive'}
		allParameters = [p0, p1, p2, p3, p4, p5, p6, p7, p8]
		for p in allParameters:
			p['enabled'] = True
		return allParameters

	def modelName(self):
		return "Yokogawa AQ7270 simulator"

	def updateVisibility(self, allParameters, values): #overrides AbstractReflectometer.updateVisibility
		assert allParameters[6]['name'] == 'avertype'
		assert allParameters[7]['name'] == 'nmeasurements'
		assert allParameters[8]['name'] == 'smptime'
		if values['avertype'] == 'TIMES':
			allParameters[7]['enabled'] = True
			allParameters[8]['enabled'] = False
		else:
			allParameters[7]['enabled'] = False
			allParameters[8]['enabled'] = True

		if values['avermode'] == 'HIREFLECTION':
			allParameters[3]['enabled'] = False
		else:
			allParameters[3]['enabled'] = True

	def testParameter(self, pname, pvalue):
		print(f"Simulator: testing: {pname} {pvalue}")
		self.params[pname] = pvalue
		return True

	def setParameters(self, parameters : dict): #overrides AbstractReflectometer.setParameters
		b = True
		for key, value in parameters.items():
			b &= self.testParameter(key, value)
			if not b:
				return False
		return True

	def initParameters(self): #overrides AbstractReflectometer.readParameters
		allParams = self.getAllParameters()
		self.params = {}
		for p in allParams:
			self.params[p['name']] = p['values'][0]
			match p['name']:
				case 'drange':
					self.params[p['name']] = p['values'][10]
		return self.params

	def readParameters(self): #overrides AbstractReflectometer.readParameters
		return self.params

	def readParametersActualValues(self): #overrides AbstractReflectometer.readParameters
		return self.readParameters()

	def runAverage(self): #overrides AbstractReflectometer.runAverage
		y0 = 0
		yend = -25 # dB
		if self.params['drange'] == 'AUTO':
			xrange = 100e+3 #m
		else:
			xrange = float(self.params['drange'])
		smpiterval = 2 #todo: read this values from self.params
		Npoints = int(xrange/smpiterval)+1
		sigma = 0.1
		self.y = [0]*Npoints
		self.x = [0]*Npoints
		for n in range(Npoints):
			self.x[n] = xrange*n/Npoints
			self.y[n] = y0 + (yend-y0)*n/Npoints + random.normal(0, sigma)
		self.stopFlag = False #return stopFlag to False
		return True

	def getWaveData(self):
		if self.y is not None:
			y = self.y
			self.y = None
			return y

	def	lastReflectogram(self): #overrides AbstractReflectometer.lastReflectogram
		return self.x, self.y


