#!/usr/bin/env python

"""multiwii.py: Handles Multiwii Serial Protocol."""

__author__ = "Aldo Vargas"
__copyright__ = "Copyright 2017 Altax.net"

__license__ = "GPL"
__version__ = "1.6"
__maintainer__ = "Aldo Vargas"
__email__ = "alduxvm@gmail.com"
__status__ = "Development"


import serial
import time
import struct
import util


class MultiWii:

    """Multiwii Serial Protocol message ID"""
    """ notice: just attitude, rc channels and raw imu, set raw rc are implemented at the moment """
    REBOOT = 68
    VTX_CONFIG = 88
    VTX_SET_CONFIG = 89
    ARMING_DISABLE = 99
    IDENT = 100
    STATUS = 101
    RAW_IMU = 102
    SERVO = 103
    MOTOR = 104
    RC = 105
    RAW_GPS = 106
    COMP_GPS = 107
    ATTITUDE = 108
    ALTITUDE = 109
    ANALOG = 110
    RC_TUNING = 111
    PID = 112
    BOX = 113
    MISC = 114
    MOTOR_PINS = 115
    BOXNAMES = 116
    PIDNAMES = 117
    WP = 118
    BOXIDS = 119
    RC_RAW_IMU = 121
    SET_RAW_RC = 200
    SET_RAW_GPS = 201
    SET_PID = 202
    SET_BOX = 203
    SET_RC_TUNING = 204
    ACC_CALIBRATION = 205
    MAG_CALIBRATION = 206
    SET_MISC = 207
    RESET_CONF = 208
    SET_WP = 209
    SWITCH_RC_SERIAL = 210
    IS_SERIAL = 211
    SET_MOTOR = 214
    EEPROM_WRITE = 250
    DEBUG = 254

    """Class initialization"""

    def __init__(self, serPort):
        """Global variables of data"""
        self.PIDcoef = {'rp': 0, 'ri': 0, 'rd': 0, 'pp': 0,
                        'pi': 0, 'pd': 0, 'yp': 0, 'yi': 0, 'yd': 0}
        self.rcChannels = {'roll': 0, 'pitch': 0, 'yaw': 0,
                           'throttle': 0, 'elapsed': 0, 'timestamp': 0}
        self.rawIMU = {'ax': 0, 'ay': 0, 'az': 0, 'gx': 0, 'gy': 0,
                       'gz': 0, 'mx': 0, 'my': 0, 'mz': 0, 'elapsed': 0, 'timestamp': 0}
        self.motor = {'m1': 0, 'm2': 0, 'm3': 0,
                      'm4': 0, 'elapsed': 0, 'timestamp': 0}
        self.attitude = {'angx': 0, 'angy': 0,
                         'heading': 0, 'elapsed': 0, 'timestamp': 0}
        self.altitude = {'estalt': 0, 'vario': 0, 'elapsed': 0, 'timestamp': 0}
        self.message = {'angx': 0, 'angy': 0, 'heading': 0, 'roll': 0,
                        'pitch': 0, 'yaw': 0, 'throttle': 0, 'elapsed': 0, 'timestamp': 0}
        self.vtxConfig = {'device': 0, 'band': 0,
                          'channel': 0, 'power': 0, 'pit': 0, 'unknown': 0}
        self.temp = ()
        self.temp2 = ()
        self.elapsed = 0
        self.PRINT = 1

        self.ser = serial.Serial()
        self.ser.port = serPort
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 0
        self.ser.xonxoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.writeTimeout = 2
        """Time to wait until the board becomes operational"""

        while True:
            try:
                self.ser.open()
                time.sleep(1)
                break
            except Exception as error:
                time.sleep(0.1)

    """Function for sending a command to the board"""

    def sendCMD(self, code, data):
        data_length = len(data)
        data_format = str(data_length) + 'B' if data else ''
        checksum = 0
        total_data = ['$'.encode('utf-8'), 'M'.encode('utf-8'),
                      '<'.encode('utf-8'), data_length, code] + data
        for i in struct.pack('<2B' + data_format, *total_data[3:len(total_data)]):
            checksum = checksum ^ i
        total_data.append(checksum)
        try:
            b = None
            b = self.ser.write(struct.pack(
                '<3c2B' + data_format + 'B', *total_data))
        except Exception as error:
            print("\n\nError in sendCMD.")
            print("("+str(error)+")\n\n")
            pass

    """Function for sending a command to the board and receive attitude"""
    """
    Modification required on Multiwii firmware to Protocol.cpp in evaluateCommand:

    case MSP_SET_RAW_RC:
      s_struct_w((uint8_t*)&rcSerial,16);
      rcSerialCount = 50; // 1s transition
      s_struct((uint8_t*)&att,6);
      break;

    """

    def sendCMDreceiveATT(self, data_length, code, data):
        checksum = 0
        total_data = ['$'.encode('utf-8'), 'M'.encode('utf-8'),
                      '<'.encode('utf-8'), data_length, code] + data
        for i in struct.pack('<2B%dH' % len(data), *total_data[3:len(total_data)]):
            checksum = checksum ^ i
        total_data.append(checksum)
        try:
            start = time.time()
            b = None
            b = self.ser.write(struct.pack('<3c2B%dHB' %
                                           len(data), *total_data))

            while True:
                header = self.ser.read().decode('utf-8')
                if header == '$':
                    header = header+self.ser.read(2).decode('utf-8')
                    break
            datalength = struct.unpack('<b', self.ser.read())[0]
            code = struct.unpack('<b', self.ser.read())
            data = self.ser.read(datalength)
            temp = struct.unpack('<'+'h'*int(datalength/2), data)
            self.ser.flushInput()
            self.ser.flushOutput()
            elapsed = time.time() - start
            self.attitude['angx'] = float(temp[0]/10.0)
            self.attitude['angy'] = float(temp[1]/10.0)
            self.attitude['heading'] = float(temp[2])
            self.attitude['elapsed'] = round(elapsed, 3)
            self.attitude['timestamp'] = "%0.2f" % (time.time(),)
            return self.attitude
        except Exception as error:
            print("\n\nError in sendCMDreceiveATT.")
            print("("+str(error)+")\n\n")
            pass

    """Function to arm / disarm """

    def enable_arm(self):
        print('Enabling arming...')
        buf = []
        util.push8(buf, 0)
        util.push8(buf, 1)
        self.sendCMD(MultiWii.ARMING_DISABLE, buf)
        time.sleep(5.5)
        print('Arm protection off; arming is allowed')

    def arm(self):
        print('Arming...')
        # keep disarmed for 1s
        for _ in range(20):
            buf = []
            util.push16(buf, 1500)
            util.push16(buf, 1500)
            util.push16(buf, 1000)
            util.push16(buf, 1500)
            util.push16(buf, 1000)  # aux1 disarm position
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            self.sendCMD(MultiWii.SET_RAW_RC, buf)
            time.sleep(0.05)

        # continuous arm signal for 1s
        for _ in range(100):
            buf = []
            util.push16(buf, 1500)
            util.push16(buf, 1500)
            util.push16(buf, 1010)
            util.push16(buf, 1500)
            util.push16(buf, 1500)  # aux1 arm position
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            self.sendCMD(MultiWii.SET_RAW_RC, buf)
            time.sleep(0.05)
        print('ARMED')

    def disarm(self):
        print('Disarming')
        # keep armed for 1s
        for _ in range(20):
            buf = []
            util.push16(buf, 1500)
            util.push16(buf, 1500)
            util.push16(buf, 1010)
            util.push16(buf, 1500)
            util.push16(buf, 1500)  # aux1 arm position
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            self.sendCMD(MultiWii.SET_RAW_RC, buf)
            time.sleep(0.05)

        # continuous disarm signal for 1s
        for _ in range(20):
            buf = []
            util.push16(buf, 1500)
            util.push16(buf, 1500)
            util.push16(buf, 1000)
            util.push16(buf, 1500)
            util.push16(buf, 1000)  # aux1 disarm position
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            self.sendCMD(MultiWii.SET_RAW_RC, buf)
            time.sleep(0.05)
        print('DISARMED')

    def disable_arm(self):
        print('Enabling arm protection...')
        buf = []
        util.push8(buf, 1)
        util.push8(buf, 0)
        self.sendCMD(MultiWii.ARMING_DISABLE, buf)
        time.sleep(0.05)
        print('Arm protection on; arming is disallowed...')

    # def setPID(self, pd):
    #     nd = []
    #     for i in np.arange(1, len(pd), 2):
    #         nd.append(pd[i]+pd[i+1]*256)
    #     data = pd
    #     print("PID sending:", data)
    #     self.sendCMD(MultiWii.SET_PID, data)
    #     self.sendCMD(MultiWii.EEPROM_WRITE, [])

    # def setVTX(self, band, channel, power):
    #     band_channel = ((band-1) << 3) | (channel-1)
    #     t = None
    #     while t == None:
    #         t = self.getData(MultiWii.VTX_CONFIG)
    #     different = (self.vtxConfig['band'] != band) | (
    #         self.vtxConfig['channel'] != channel) | (self.vtxConfig['power'] != power)
    #     data = [band_channel, power, self.vtxConfig['pit']]
    #     while different:
    #         self.sendCMD(MultiWii.VTX_SET_CONFIG, data)
    #         time.sleep(1)
    #         self.sendCMD(MultiWii.EEPROM_WRITE, [])
    #         self.ser.close()
    #         time.sleep(3)
    #         self.ser.open()
    #         time.sleep(3)
    #         t = None
    #         while t == None:
    #             t = self.getData(MultiWii.VTX_CONFIG)
    #         print(t)
    #         different = (self.vtxConfig['band'] != band) | (
    #             self.vtxConfig['channel'] != channel) | (self.vtxConfig['power'] != power)

    """Function to receive a data packet from the board"""

    def getData(self, cmd):
        try:
            start = time.time()
            self.sendCMD(cmd, [])
            while True:
                header = self.ser.read().decode('utf-8')
                if header == '$':
                    header = header+self.ser.read(2).decode('utf-8')
                    break
            datalength = struct.unpack('<b', self.ser.read())[0]
            code = struct.unpack('<b', self.ser.read())
            data = self.ser.read(datalength)

            self.ser.flushInput()
            self.ser.flushOutput()
            elapsed = time.time() - start
            if cmd == MultiWii.ATTITUDE:
                temp = struct.unpack('<'+'h'*int(datalength/2), data)
                self.attitude['angx'] = float(temp[0]/10.0)
                self.attitude['angy'] = float(temp[1]/10.0)
                self.attitude['heading'] = float(temp[2])
                self.attitude['elapsed'] = round(elapsed, 3)
                self.attitude['timestamp'] = "%0.2f" % (time.time(),)
                return self.attitude
            elif cmd == MultiWii.ALTITUDE:
                temp = struct.unpack('<'+'h'*int(datalength/2), data)
                self.altitude['estalt'] = float(temp[0])
                self.altitude['vario'] = float(temp[1])
                self.altitude['elapsed'] = round(elapsed, 3)
                self.altitude['timestamp'] = "%0.2f" % (time.time(),)
                return self.altitude
            elif cmd == MultiWii.RC:
                print('Getting RC data')
                temp = struct.unpack('<'+'h'*int(datalength/2), data)
                print(temp)
                print('Received RC data')
                self.rcChannels['roll'] = temp[0]
                self.rcChannels['pitch'] = temp[1]
                self.rcChannels['yaw'] = temp[2]
                self.rcChannels['throttle'] = temp[3]
                self.rcChannels['elapsed'] = round(elapsed, 3)
                self.rcChannels['timestamp'] = "%0.2f" % (time.time(),)
                return self.rcChannels
            elif cmd == MultiWii.RAW_IMU:
                temp = struct.unpack('<'+'h'*int(datalength/2), data)
                self.rawIMU['ax'] = float(temp[0])
                self.rawIMU['ay'] = float(temp[1])
                self.rawIMU['az'] = float(temp[2])
                self.rawIMU['gx'] = float(temp[3])
                self.rawIMU['gy'] = float(temp[4])
                self.rawIMU['gz'] = float(temp[5])
                self.rawIMU['mx'] = float(temp[6])
                self.rawIMU['my'] = float(temp[7])
                self.rawIMU['mz'] = float(temp[8])
                self.rawIMU['elapsed'] = round(elapsed, 3)
                self.rawIMU['timestamp'] = "%0.2f" % (time.time(),)
                return self.rawIMU
            elif cmd == MultiWii.MOTOR:
                temp = struct.unpack('<'+'h'*int(datalength/2), data)
                self.motor['m1'] = float(temp[0])
                self.motor['m2'] = float(temp[1])
                self.motor['m3'] = float(temp[2])
                self.motor['m4'] = float(temp[3])
                self.motor['elapsed'] = "%0.3f" % (elapsed,)
                self.motor['timestamp'] = "%0.2f" % (time.time(),)
                return self.motor
            elif cmd == MultiWii.PID:
                temp = struct.unpack('<'+'h'*int(datalength/2), data)
                dataPID = []
                if len(temp) > 1:
                    d = 0
                    for t in temp:
                        dataPID.append(t % 256)
                        dataPID.append(t/256)
                    for p in [0, 3, 6, 9]:
                        dataPID[p] = dataPID[p]/10.0
                        dataPID[p+1] = dataPID[p+1]/1000.0
                    self.PIDcoef['rp'] = dataPID = [0]
                    self.PIDcoef['ri'] = dataPID = [1]
                    self.PIDcoef['rd'] = dataPID = [2]
                    self.PIDcoef['pp'] = dataPID = [3]
                    self.PIDcoef['pi'] = dataPID = [4]
                    self.PIDcoef['pd'] = dataPID = [5]
                    self.PIDcoef['yp'] = dataPID = [6]
                    self.PIDcoef['yi'] = dataPID = [7]
                    self.PIDcoef['yd'] = dataPID = [8]
                return self.PIDcoef
            elif cmd == MultiWii.VTX_CONFIG:
                if datalength > 1:
                    temp = struct.unpack('<bbbbb', data)
                    self.vtxConfig['device'] = temp[0]
                    self.vtxConfig['band'] = temp[1]
                    self.vtxConfig['channel'] = temp[2]
                    self.vtxConfig['power'] = temp[3]
                    self.vtxConfig['pit'] = temp[4]
                    self.vtxConfig['unknown'] = 0
                    return self.vtxConfig
                else:
                    temp = struct.unpack('<b', data)
                    self.vtxConfig['unknown'] = temp[0]
                    return self.vtxConfig
            else:
                return "No return error!"
        except Exception as error:
            print("Error in getData")
            print(error)
            pass

    """Function to receive a data packet from the board. Note: easier to use on threads"""

    def getDataInf(self, cmd):
        while True:
            try:
                start = time.clock()
                self.sendCMD(cmd, [])
                while True:
                    header = self.ser.read().decode('utf-8')
                    if header == '$':
                        header = header+self.ser.read(2).decode('utf-8')
                        break
                datalength = struct.unpack('<b', self.ser.read())[0]
                code = struct.unpack('<b', self.ser.read())
                data = self.ser.read(datalength)
                temp = struct.unpack('<'+'h'*int(datalength/2), data)
                elapsed = time.clock() - start
                self.ser.flushInput()
                self.ser.flushOutput()
                if cmd == MultiWii.ATTITUDE:
                    self.attitude['angx'] = float(temp[0]/10.0)
                    self.attitude['angy'] = float(temp[1]/10.0)
                    self.attitude['heading'] = float(temp[2])
                    self.attitude['elapsed'] = "%0.3f" % (elapsed,)
                    self.attitude['timestamp'] = "%0.2f" % (time.time(),)
                elif cmd == MultiWii.RC:
                    self.rcChannels['roll'] = temp[0]
                    self.rcChannels['pitch'] = temp[1]
                    self.rcChannels['yaw'] = temp[2]
                    self.rcChannels['throttle'] = temp[3]
                    self.rcChannels['elapsed'] = "%0.3f" % (elapsed,)
                    self.rcChannels['timestamp'] = "%0.2f" % (time.time(),)
                elif cmd == MultiWii.RAW_IMU:
                    self.rawIMU['ax'] = float(temp[0])
                    self.rawIMU['ay'] = float(temp[1])
                    self.rawIMU['az'] = float(temp[2])
                    self.rawIMU['gx'] = float(temp[3])
                    self.rawIMU['gy'] = float(temp[4])
                    self.rawIMU['gz'] = float(temp[5])
                    self.rawIMU['elapsed'] = "%0.3f" % (elapsed,)
                    self.rawIMU['timestamp'] = "%0.2f" % (time.time(),)
                elif cmd == MultiWii.MOTOR:
                    self.motor['m1'] = float(temp[0])
                    self.motor['m2'] = float(temp[1])
                    self.motor['m3'] = float(temp[2])
                    self.motor['m4'] = float(temp[3])
                    self.motor['elapsed'] = "%0.3f" % (elapsed,)
                    self.motor['timestamp'] = "%0.2f" % (time.time(),)
            except Exception as error:
                print("Error in getDataInf")
                print(error)
                pass

    """Function to ask for 2 fixed cmds, attitude and rc channels, and receive them. Note: is a bit slower than others"""

    def getData2cmd(self, cmd):
        try:
            start = time.time()
            self.sendCMD(self.ATTITUDE, [])
            while True:
                header = self.ser.read().decode('utf-8')
                if header == '$':
                    header = header+self.ser.read(2).decode('utf-8')
                    break
            datalength = struct.unpack('<b', self.ser.read())[0]
            code = struct.unpack('<b', self.ser.read())
            data = self.ser.read(datalength)
            temp = struct.unpack('<'+'h'*int(datalength/2), data)
            self.ser.flushInput()
            self.ser.flushOutput()

            self.sendCMD(self.RC, [])
            while True:
                header = self.ser.read().decode('utf-8')
                if header == '$':
                    header = header+self.ser.read(2).decode('utf-8')
                    break
            datalength = struct.unpack('<b', self.ser.read())[0]
            code = struct.unpack('<b', self.ser.read())
            data = self.ser.read(datalength)
            temp2 = struct.unpack('<'+'h'*int(datalength/2), data)
            elapsed = time.time() - start
            self.ser.flushInput()
            self.ser.flushOutput()

            if cmd == MultiWii.ATTITUDE:
                self.message['angx'] = float(temp[0]/10.0)
                self.message['angy'] = float(temp[1]/10.0)
                self.message['heading'] = float(temp[2])
                self.message['roll'] = temp2[0]
                self.message['pitch'] = temp2[1]
                self.message['yaw'] = temp2[2]
                self.message['throttle'] = temp2[3]
                self.message['elapsed'] = round(elapsed, 3)
                self.message['timestamp'] = "%0.2f" % (time.time(),)
                return self.message
            else:
                return "No return error!"
        except Exception as error:
            print("Error in getData2cmd")
            print(error)
            
    def init(self):
        self.enable_arm()
        self.arm()
    
    def close(self):
        self.disarm()
        self.disable_arm()
        
    def move(self, Aileron=1500, Elevator=1500, Throttle=1020, Rudder=1500):
        # for _ in range(20):
        #     buf = []
        #     util.push16(buf, Aileron)
        #     util.push16(buf, Elevator)
        #     util.push16(buf, Throttle)
        #     util.push16(buf, Rudder)
        #     util.push16(buf, 1500)  # aux1 arm position
        #     util.push16(buf, 1000)
        #     util.push16(buf, 1000)
        #     util.push16(buf, 1000)
        #     self.sendCMD(MultiWii.SET_RAW_RC, buf)
        #     time.sleep(0.05)
        # continuous arm signal for 1s
        for _ in range(100):
            buf = []
            util.push16(buf, Aileron)
            util.push16(buf, Elevator)
            util.push16(buf, Throttle)
            util.push16(buf, Rudder)
            util.push16(buf, 1500)  # aux1 arm position
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            self.sendCMD(MultiWii.SET_RAW_RC, buf)
            time.sleep(0.05)
#     def keepFloating(self, Throttle=1010):
#         self.move(Throttle)  # assumindo que 1500 é a velocidade necessária para manter a flutuação
#         print(">> Keep Floating")

    def goUp(self, Throttle=1025):
        self.move(Throttle)  # assumindo que 2000 aumenta a altitude
        print(">> Going up")

    def goDown(self, Throttle=1010):
        self.move(Throttle)  # assumindo que 1000 reduz a altitude
        print(">> Going down")
        
        
    def change(self):
        print('Arming...')
        # keep disarmed for 1s
        for _ in range(100):
            print(f"{1010+_*2}, ")

            buf = []
            util.push16(buf, 1500)
            util.push16(buf, 1500)
            util.push16(buf, 1010+_*2)
            util.push16(buf, 1500)
            util.push16(buf, 1000)  # aux1 disarm position
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            self.sendCMD(MultiWii.SET_RAW_RC, buf)
            time.sleep(0.05)
        print("\n")
        # continuous arm signal for 1s
        for _ in range(100):
            print(f"{1050-_*2}, ")
            buf = []
            util.push16(buf, 1500)
            util.push16(buf, 1500)
            util.push16(buf, 1050-_*2)
            util.push16(buf, 1500)
            util.push16(buf, 1500)  # aux1 arm position
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            util.push16(buf, 1000)
            self.sendCMD(MultiWii.SET_RAW_RC, buf)
            time.sleep(0.05)
        print("\n")
        


#     def goForward(self):
#         self.move(Elevator=1500)  # assumindo que 2000 faz o drone ir para frente
#         print(">> Go foward")

#     def goBackward(self):
#         self.move(Elevator=1000)  # assumindo que 1000 faz o drone ir para trás
#         print(">> Go backward")

#     def backToDock(self):
#         # Aqui, você precisará implementar lógica para retornar ao ponto de partida, que está além do escopo desta demonstração
#         pass

#     def spinToLeft(self):cd
#         self.move(Rudder=1400)  # assumindo que 1000 faz o drone girar para a esquerda
#         print(">> Spin to Left")

#     def spinToRight(self):
#         self.move(Rudder=1600)  # assumindo que 2000 faz o drone girar para a direita
#         print(">> Sping to Right")


# board = MultiWii("/dev/ttyACM0")
# board.init()

# # # board.goUp()
# # # board.goDown()
# # # # # # board.goUp()
# # # # # # board.keepFloating()
# # # # # # board.goDown()

# board.close()


