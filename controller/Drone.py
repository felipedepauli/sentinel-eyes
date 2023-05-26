#!/usr/bin/env python
from msp import MultiWii
import time

class DroneCommands:
    def __init__(self):
        print("Connecting to board")
        self.board = MultiWii("/dev/ttyACM0")
        print("Connected to board")
        self.buffer = []
        
    def starting(self):
        self.arm = 1500
        # self.board.enable_arm()
        self.board.arm()
        
    def shutting_down(self):
        self.arm = 1000
        self.board.disarm()
        # self.board.disable_arm()

    def push8(self, val):
        self.buffer.append(0xFF & val)

    def push16(self, val):
        self.push8(val)
        self.push8(val >> 8)

    def aetr1234(self, A, E, T, R, AUX1=1500, AUX2=1000, AUX3=1000, AUX4=1000):
        # clean buffer
        self.buffer = []

        # start byte
        self.push8(0xAA)

        # push channels
        self.push8(A)
        self.push8(E)
        self.push8(T)
        self.push8(R)
        self.push8(AUX1)
        self.push8(AUX2)
        self.push8(AUX3)
        self.push8(AUX4)
        for _ in range(20):
            self.board.sendCMD(16, MultiWii.SET_RAW_RC, self.buffer)
            time.sleep(0.05)
class Drone:
    IDLE            = 0
    STARTING        = 1
    RISING          = 2
    FALLING         = 3
    KEEPING         = 4
    MOVING_RIGHT    = 5
    MOVING_LEFT     = 6
    SHUTTING_DOWN   = 7

    def __init__(self):
        self.A = 1500
        self.E = 1500
        self.T = 1010
        self.R = 1500
        self.commands = DroneCommands()
        
        
        self.set_state(self.STARTING)
        self.set_state(self.KEEPING)
        self.set_state(self.RISING)
        self.set_state(self.KEEPING)
        self.set_state(self.FALLING)
        self.set_state(self.SHUTTING_DOWN)

    def set_state(self, state):
        self.state = state
        self.update()

    def update(self):
        if self.state == self.IDLE:
            pass

        elif self.state == self.STARTING:
            print("Drone initialized")
            self.A = 1500
            self.E = 1500
            self.T = 1010
            self.R = 1500
            self.commands.starting()
            
        elif self.state == self.KEEPING:
            print("Keeping with A: {}, E: {}, T: {}, R: {}".format(self.A, self.E, self.T, self.R))
            self.commands.aetr1234(self.A, self.E, self.T, self.R)
                
        elif self.state == self.RISING:
            print("Rising")
            i = 0
            for _ in range(20):  # Gradually increase throttle
                if i % 2 == 0:
                    self.commands.aetr1234(1500, 1500, self.T + i, 1500)
                    time.sleep(0.05)
                    i += 1

        elif self.state == self.FALLING:
            for _ in range(10):  # Gradually decrease throttle
                self.commands.aetr1234(1500, 1500, 1020 - _, 1500)

        elif self.state == self.MOVING_RIGHT:
            for _ in range(100):  # Gradually increase rightward movement
                self.commands.aetr1234(1500 + _, 1500, 1500, 1500)

        elif self.state == self.MOVING_LEFT:
            for _ in range(100):  # Gradually increase leftward movement
                self.commands.aetr1234(1500 - _, 1500, 1500, 1500)

        elif self.state == self.SHUTTING_DOWN:
            self.commands.shutting_down()
            print("Drone shut down")