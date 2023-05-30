#!/usr/bin/env python
import time
import threading
import numpy as np
from msp import MultiWii

# This class is responsible for connecting to the drone board and sending it commands
class DroneCommands:
    def __init__(self):
        print("[Sentinel] Connecting to board...")
        self.board = MultiWii("/dev/ttyACM0")  # Connect to the board
        print("[Sentinel] Connected to board.")
        self.buffer = []  # Initialize the command buffer

    def starting(self):
        # print("[Sentinel] READY the drone...")
        self.board.enable_arm()
        self.board.arm()  # Send the arm command

    def shutting_down(self):
        # print("[Sentinel] Shutting down the drone...")
        self.board.disarm()  # Send the disarm command
        self.board.disable_arm()

    def push8(self, val):
        self.buffer.append(0xFF & val)  # Push a byte into the buffer

    def push16(self, val):
        self.push8(val)  # Push a byte
        self.push8(val >> 8)  # Push the byte's higher 8 bits

    # This method sends a RC command to the drone
    def aetr1234(self, A, E, T, R, AUX1=1500, AUX2=1000, AUX3=1000, AUX4=1000):
        print(f"[Sentinel] Sending  AETR command: A={A}, E={E}, T={T}, R={R}, AUX1={AUX1}")
        buffer = []  # Clean the buffer
        self.push8(0xAA)  # Start byte

        # Push channels
        self.push8(A)
        self.push8(E)
        self.push8(T)
        self.push8(R)
        self.push8(AUX1)
        self.push8(AUX2)
        self.push8(AUX3)
        self.push8(AUX4)
        
        # Send the command to the drone
        if (T > 1050):
            print("Error! Throttle is too high!", T)
            self.shutting_down()
            while True:
                pass
        for _ in range(5):
            # print(f"[Sentinel] {'.'*_}")
            time.sleep(0.05)
            self.board.sendCMD(MultiWii.SET_RAW_RC, buffer)
        # self.board.getData(MultiWii.ATTITUDE)
        # print(self.board.attitude)
        # self.board.getData(MultiWii.RC)
        # print(self.board.rcChannels)
        # print(f'[Sentinel] Received AETR command: A={self.board.rcChannels["roll"]}, E={self.board.rcChannels["pitch"]}, T={self.board.rcChannels["throttle"]}, R={self.board.rcChannels["yaw"]}, AUX1={AUX1}')
        
    


# This class represents the drone itself and handles the state transitions
class Drone:
    # Define possible states
    IDLE = 0
    READY = 1
    KEEPING = 2
    RISING = 3
    FALLING = 4
    MOVING_RIGHT = 5
    MOVING_LEFT = 6
    SHUTTING_DOWN = 7
    
    THROTTLE_IDLE = 1000
    THROTTLE_READY = 1010
    THROTTLE_RISING = 1030
    THROTTLE_FLOATING = 1020
    THROTTLE_FALLING = 1010

    
    states = ["IDLE", "READY", "KEEPING", "RISING", "FALLING", "MOVING_RIGHT", "MOVING_LEFT", "SHUTTING_DOWN"]

    def __init__(self):
        # Initialize drone control variables
        self.arm = 1000
        self.A = 1500
        self.E = 1500
        self.T = 1010
        self.R = 1500
        self.state = self.IDLE
        self.commands = DroneCommands()
        self.keep_alive_running = False
        self.keep_alive_thread = None
        self.update_step = 1  # Value change per update
        self.steps = 5  # Value change per button press
        self.update_in_progress = False


    def set_state(self, state):
        print(state)
        if (self.state == self.IDLE) and not (state == self.READY):
            print("[Sentinel] Drone is IDLE.")
            return
        else:
            self.state = state
        
        if self.state == self.READY:
            print("[Sentinel] Starting the drone...")
            self.commands.starting()
            self.arm = 1500
            self.keep_alive_running = True  # Allow the keep-alive thread to run again
            self.keep_alive_thread = threading.Thread(target=self.keep_alive, daemon=True)
            self.keep_alive_thread.start()  # Start the keep-alive thread
            print("[Sentinel] Drone is READY...")
        elif self.state == self.SHUTTING_DOWN:
            print("[Sentinel] Shutting down the drone...")
            self.arm = 1000
            self.keep_alive_running = False  # Tell the keep-alive thread to stop
            self.keep_alive_thread.join()  # Wait for the current keep-alive command to finish
            self.keep_alive_thread = None  # Reset the keep_alive_thread
        else:
            print(f"[Sentinel] Changing state to: {Drone.states[state]}")
            self.update()
        
    def update(self):            
        if self.state == self.KEEPING:
            print("[Sentinel] Drone is keeping position.")
            self.gradual_update("T", Drone.THROTTLE_FLOATING)
            self.gradual_update("R", 1500)
            
        elif self.state == self.RISING:
            print("[Sentinel] Drone is rising...")
            self.gradual_update("R", 1500)
            self.gradual_update("T", Drone.THROTTLE_RISING)
            
        elif self.state == self.FALLING:
            print("[Sentinel] Drone is falling...")
            self.gradual_update("R", 1500)
            self.gradual_update("T", Drone.THROTTLE_FALLING)
            
        elif self.state == self.MOVING_RIGHT:
            print("[Sentinel] Drone is moving to the right...")
            self.gradual_update("T", Drone.THROTTLE_FLOATING)
            self.gradual_update("R", 1510)
            
        elif self.state == self.MOVING_LEFT:
            print("[Sentinel] Drone is moving to the left...")
            self.gradual_update("T", Drone.THROTTLE_FLOATING)
            self.gradual_update("R", 1490)
            
        elif self.state == self.SHUTTING_DOWN:
            print("[Sentinel] Drone is shutting down...")
            self.gradual_update("T", Drone.THROTTLE_READY)
            self.gradual_update("T", Drone.THROTTLE_IDLE)
            self.gradual_update("R", 1500)
            self.arm = 1000
            self.commands.shutting_down()

    def keep_alive(self):
        while self.keep_alive_running:  # Only run the loop while keep_alive_running is True
            if not self.update_in_progress:  # Only send command if not updating
                # Send the command to the drone
                self.commands.aetr1234(self.A, self.E, self.T, self.R, self.arm, 1500, 1500, 1500)

    def gradual_update(self, param, target):
            self.update_in_progress = True  # Indicate that an update is in progress
            current_value = getattr(self, param)
            direction = np.sign(target - current_value)  # +1 if we need to increase the value, -1 if we need to decrease
            while current_value != target:
                current_value += direction * self.update_step
                setattr(self, param, current_value)
                self.commands.aetr1234(self.A, self.E, self.T, self.R, self.arm, 1500, 1500, 1500)
            self.update_in_progress = False  # Indicate that the update is finished