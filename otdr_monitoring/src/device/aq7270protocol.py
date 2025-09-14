import usb
import asyncio

#This class implements low-level routines to communicate with AQ7270
class AQ7270protocol:
    # Common commands
    cmdCls = '*CLS'  # Clears the event register and error queue.
    cmdReset = '*RST'  # Initializes the command group’s settings.
    askEventRegister = '*ESR?'  # Queries the standard event register and clears the register.
    askStatusByte = '*STB?'  # Queries the status byte register.

    # Display group
    cmdDisplayColor = ':DISPLAY:COLOR'

    # Acquire group
    cmdAcquireADSave = ':ACQuire:ADSave'  # ON | OFF
    cmdAcquireAESearch = ':ACQuire:AESearch'  # ON | OFF

    cmdAcquireAttenuation = ':ACQuire:ATTenuation'  # <NRf> | AUTO, <NRf> = 0.00 to 27.50 (steps of 2.5)
    askAcquireAttenuation = ':ACQuire:ATTenuation?'

    askAcquireAutoDrange = ':ACQuire:AUTO:DRANge?'
    askAcquireAutoPWidth = ':ACQuire:AUTO:PWIDth?'
    askAcquireAutoAttenuation = ':ACQuire:AUTO:ATTenuation?'

    askAcquireAverageCount = ':ACQuire:AVERage:COUNt?'  # Queries the current average count
    cmdAcquireAverageIndex = ':ACQuire:AVERage:INDex'  # {AUTO|E2_10|E2_11.......E2_20}
    askAcquireAverageIndex = ':ACQuire:AVERage:INDex?'
    cmdAcquireAverageMode = ':ACQuire:AVERage:MODE'  # HIREFLECTION | HISPEED
    askAcquireAverageMode = ':ACQuire:AVERage:MODE?'

    cmdAcquireSettings = ':ACQuire:SETTing' #Possible arguments: 'Simple', 'Wizard', 'Detail', 'Multi'
    askAcquireSettings = ':ACQuire:SETTing?'

    cmdAcquireAverageStart = ':ACQuire:AVERage:STARt'
    cmdAcquireAverageStop = ':ACQuire:AVERage:STOP'
    cmdAcquireAverageContinue = ':ACQuire:AVERage:CONTINUE'  # ON
    askAcquireAverageContinue = ':ACQuire:AVERage:CONTINUE?'
    cmdAcquireAverageTime = ':ACQuire:AVERage:TIME'  # <NRf> | AUTO, <NRf> = 2 to 1800 (:ACQuire:AVERage:TIME 1200, :ACQuire:AVERage:TIME AUTO)
    askAcquireAverageTime = ':ACQuire:AVERage:TIME?'
    cmdAcquireAverageType = ':ACQuire:AVERage:TYPE'  # TIMES | DURATION
    askAcquireAverageType = ':ACQuire:AVERage:TYPE?'

    cmdAcquireDrange = ':ACQuire:DRANge'  # <NRf>|AUTO, <NRf> = 500m to 512000m (0.5km to 512km) (:ACQuire:DRANge AUTO, :ACQuire:DRANge 500, :ACQuire:DRANge 500m)
    askAcquireDrange = ':ACQuire:DRANge?'
    cmdAcquireMWavelengthWavelength = ':ACQuire:MWAVelength:WAVelength<x>'  # <x> {<NRf>}, <NRf> = 850E–09 to 1650E–09, <x> = 1 to 3
    cmdAcquireOffset = ':ACQuire:OFFSet'  # NRf,  The unit is set to m. (meter)
    askAcquireOffset = ':ACQuire:OFFSet?'  # NRf,  The unit is set to m. (meter)
    cmdAcquirePlugCheck = ':ACQuire:PLUGcheck'  # ON | OFF
    cmdAcquirePWidth = ':ACQuire:PWIDth'  # <NRf>|AUTO, <NRf> = 3ns to 20us (3E-9 to 20E-6)
    askAcquirePWidth = ':ACQuire:PWIDth?'  # <NRf>|AUTO, <NRf> = 3ns to 20us (3E-9 to 20E-6)
    cmdAcquireRealtimeStart = ':ACQuire:REALtime:STARt'
    cmdAcquireRealtimeStop = ':ACQuire:REALtime:STOP'
    cmdAcquireSetting = ':ACQuire:SETTing'  # SIMPLE | DETAIL | WIZARD | MULTI
    askAcquireSetting = ':ACQuire:SETTing?'
    cmdAcquireSMPintervalData = ':ACQuire:SMPinterval:DATA'  # <NRf> | NORMAL | HI
    askAcquireSMPintervalData = ':ACQuire:SMPinterval:DATA?' #returns float or 'NORMAL' or 'HI'
    askAcquireSMPintervalValue = ':ACQuire:SMPinterval:VALue?'  # Queries the sampling interval, returns float
    cmdAcquireWavelength = ':ACQuire:WAVelength'  # <NRf>, <NRf> = 0.850um to 1.650um (850E-9 to 1650E-9)
    askAcquireWavelength = ':ACQuire:WAVelength?'
    # Wavedata group
    askWavedataLength = ':WAVedata:LENGth?'
    askWavedataASCII = ':WAVedata:SEND:ASCii?'

    # File group
    cmdFileDeleteExecute = ':FILE:DELete:EXECute'
    askFileDriveFree = ':FILE:DRIVe:FREE?'
    cmdFileDriveSet = ':FILE:DRIVe:SET'
    askFileFileGet = ':FILE:FILE:GET?'
    cmdFileFileName = ':FILE:FILE:NAME'
    askFileFileSize = ':FILE:FILE:SIZE?'
    cmdFileFolderMake = ':FILE:FOLDer:MAKE'
    cmdFileFolderPath = ':FILE:FOLDer:PATH'
    askFileFolderPath = ':FILE:FOLDer:PATH?'
    askFileFolderList = ':FILE:FOLDer:LIST?'
    askFileSubfolferList = ':FILE:SUBFolder:LIST?'
    cmdFileLoadExecute = ':FILE:LOAD:EXECute'
    cmdFileSaveComment = ':FILE:SAVE:COMMent'
    cmdFileSaveExecute = ':FILE:SAVE:EXECute'
    cmdFileSaveID = ':FILE:SAVE:ID'
    cmdFileSaveType = ':FILE:SAVE:TYPE'
    cmdFileSaveSub = ':FILE:SAVE:SUB'
    cmdFileType = ':FILE:TYPE'

    avertypes = ["TIMES", "DURATION"]
    avertypes_text = ["times", "duration"]
    avermodes = ["HIREFLECTION", "HISPEED"]
    avermodes_text = ["high reflection", "high speed"]
    wavelengths = ["1310E-09", "1550E-09"]
    wavelengths_text = ["1310 nm", "1550 nm"]
    dranges = ["AUTO", "500", "1000", "2000", "5000", "10000", "20000", "50000", "100000", "200000", "300000", "400000", "512000"]
    dranges_text = ["AUTO", "500 m", "1 km", "2 km", "5 km", "10 km", "20 km", "50 km", "100 km", "200 km", "300 km", "400 km", "512 km"]
    pwidths = ["AUTO", "3E-09", "10E-09", "20E-09", "50E-09", "100E-09", "200E-09", "500E-09", "1E-06", "2E-06", "5E-06", "10E-06", "20E-06"]
    pwidths_text = ["AUTO", "3 ns", "10 ns", "20 ns", "50 ns", "100 ns", "200 ns", "500 ns", "1 μs", "2 μs", "5 μs", "10 μs", "20 μs"]
    attenuations = ["AUTO"] + [f"{2.5 * n:.2f}" for n in range(0, 12)]
    attenuations_text = ["AUTO"] + [f"{2.5 * n:.2f}" for n in range(0, 12)]
    smpintervals = ["NORMAL", "HI", "0.05", "0.10", "0.20", "0.50", "1.00", "2.00", "4.00", "8.00", "16.00", "32.00"]
    smpintervals_text = ["NORMAL", "HI", "0.05 m", "0.1 m", "0.2 m", "0.5 m", "1 m", "2 m", "4 m", "8 m", "16 m", "32 m"]
    modes = ["HIREFLECTION", "HISPEED"]
    types = ["TIMES", "DURATION"]
    nmeasurements = ["AUTO"] + [f"E2_{n}" for n in range(10, 21)]
    nmeasurements_text = ["AUTO"] + [f"2^{n}" for n in range(10, 21)]
    avertimes = ['2', '5', '10', '20', '30', '60', '180', '300', '600', '1200', '1800']
    avertimes_text = [f"{n} sec" for n in avertimes]

    timeout = 1000

    usb_idVendor = 0xb21
    usb_idProduct = 0x29

    def __init__(self, dev = None, needReset : bool = False):
        self.outport = 0x01
        self.inport = 0x82
        self.bufsize = 64 #should be multiple of the endpoint's packet size

    def connect(self, dev = None, needReset: bool = False):
        if dev == None:
            dev = usb.core.find(idVendor=self.usb_idVendor, idProduct=self.usb_idProduct)
            if self.dev is None:
                print("Yokogawa AQ7270 not found")
            else:
                print("Found device:")
                print(self.dev)
        self.dev = dev
        if self.dev is not None:
            print("Using device:")
            print(self.dev)
            #self.cmd(":SETup:INITialize")  #Initializes all the settings to factory default.
            if needReset:
                self.printCmdResults(self.cmdReset)
            self.printCmdResults(self.cmdAcquireSettings, 'Detail')
            self.printCmdResults(self.askEventRegister)
            self.printCmdResults(self.askStatusByte)

    def send(self, text, params = None):
        if params is None:
            cmd = text
        else:
            cmd = text + ' ' + params
        cmd += chr(0x0A)
        self.dev.write(self.outport, cmd)

    def receive(self):
        res = []
        timeoutCount = 100
        while True:
            try:
                buf = self.dev.read(self.inport, self.bufsize, self.timeout)
                res.extend(buf)
                if buf[-1] == 0x0a:
                    break
            except:
                timeoutCount += 1
                if timeoutCount > 100:
                    print('Awaiting for data...')
        assert(res[-1] == 0x0a)
        res = res[:-1] #remove trailing '\n'
        return bytes(res)

    def receivefile(self):
        res = []
        buf = self.dev.read(self.inport, self.bufsize)
        assert(buf[0] == ord('#'))
        sizesize = buf[1] - ord('0')
        size = int(buf[2 : sizesize+2])
        res = buf[sizesize+2:]
        while len(res) <= size: #data should contain actual bytes from file and trailing '\n'
            buf = self.dev.read(self.inport, self.bufsize, self.timeout)
            res.extend(buf)
        assert(res[-1] == 0x0a)
        res = res[:-1] #remove trailing '\n'
        return res


    def getWaveData(self):
        text = self.cmd(self.askWavedataASCII)
        assert(text[-1] == ',')
        text = text[0:-2] #remove trailing comma
        y = text.split(',')
        return [float(yy) for yy in y]

    def cmd(self, text, params=None):
        self.send(text, params)
        if text[-1] == '?':
            buf = self.receive()
            return buf.decode("windows-1251")

