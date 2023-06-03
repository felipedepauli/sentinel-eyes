#!/usr/bin/env python
import time
import threading
import numpy as np
from msp import MultiWii

# This class is responsible for connecting to the drone board and sending it commands
class Wings:
    # It initializes the drone connecting to the flight controller
    def __init__(self):
        print("[Sentinel] Connecting to board...")
        self.board = MultiWii("/dev/ttyACM0")  # Connect to the board
        print("[Sentinel] Connected to board.")
        self.buffer = []  # Initialize the command buffer

    # Enable the arm (get it prepared for the first time)
    def starting(self):
        self.board.enable_arm() # enable the drone
        self.board.arm()        # test the drone

    # Disable the arm (avoid commands)
    def shutting_down(self):
        self.board.disarm()     # test the stopping of the drone
        self.board.disable_arm()# disble the drone

    # Add to buffer (command sent to drone) a value of 8 bits
    def push8(self, val):
        self.buffer.append(0xFF & val)

    def push16(self, val):
        # Add to buffer (command sent to drone) a value of 16 bits
        self.push8(val)         # Push a byte
        self.push8(val >> 8)    # Push the byte's higher 8 bits

    # This method sends the RC command to the drone
    def aetr1234(self, A, E, T, R, AUX1=1500, AUX2=1000, AUX3=1000, AUX4=1000):
        print(f"[Sentinel] Sending  AETR command: A={A}, E={E}, T={T}, R={R}, AUX1={AUX1}")
        buffer = []  # Clean the buffer
        self.push8(0xAA)  # Start byte

        # Push channels
        self.push8(A)       # Aileron                       [1000 to 2000]
        self.push8(E)       # Elevator                      [1000 to 2000]
        self.push8(T)       # Throttle                      [1000 to 2000]
        self.push8(R)       # Rudder                        [1000 to 2000]
        self.push8(AUX1)    # Auxiliar 1 - Arm the drone    [1400 to 1600 armed]
        self.push8(AUX2)    # No configuration 
        self.push8(AUX3)    # No configuration
        self.push8(AUX4)    # No configuration
        
        # Verify if the program lost control of Throttle (motor's speed of spin)
        if (T > 1050):
            print("Error! Throttle is too high!", T)
            self.shutting_down()
            while True:
                pass
            
        # Send the command to the drone
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
    IDLE                = 0 # Drone is disarmd
    READY               = 1 # Drone is ready to fly
    KEEPING             = 2 # Keep the current movement
    RISING              = 3 # Drone is rising
    FALLING             = 4 # Drone is falling
    MOVING_RIGHT        = 5 # Drone is spinnig to right direction
    MOVING_LEFT         = 6 # Drone is falling to left direction
    SHUTTING_DOWN       = 7 # Drone will be shut down (disarmed)
    
    # Target values
    THROTTLE_IDLE       = 1000
    THROTTLE_READY      = 1010
    THROTTLE_RISING     = 1030
    THROTTLE_FLOATING   = 1020
    THROTTLE_FALLING    = 1010
    
    states = ["IDLE", "READY", "KEEPING", "RISING", "FALLING", "MOVING_RIGHT", "MOVING_LEFT", "SHUTTING_DOWN"]

    def __init__(self):
        self.commands = DroneCommands()     # The Drone Controller
        self.arm = 1000 # Initial value of arm (disarmed)
        self.A   = 1500 # Centralized value - neutral
        self.E   = 1500 # Centralized value - neutral
        self.T   = 1010 # No flighting, but propellers are spinning
        self.R   = 1500 # Centralized value - neutral
        self.state = self.IDLE
        self.keep_alive_running = False
        self.keep_alive_thread  = None
        self.update_step        = 1  # Value change per update
        self.steps              = 5  # Value change per button press
        self.update_in_progress = False

    # This methos is used by the API do set the states.
    # When a state is set, a procedure of changing values of drone will be executed
    def set_state(self, state):
        # When system is not started, nothing happens
        print(state)
        if (self.state == self.IDLE) and not (state == self.READY):
            print("[Sentinel] Drone is IDLE.")
            return
        else:
            # Else set the state to the received state
            self.state = state
        
        # When the command is to arm the drone, it will
        if self.state == self.READY:
            print("[Sentinel] Starting the drone...")
            self.commands.starting()
            self.arm = 1500
            self.keep_alive_running = True  # Allow the keep-alive thread to run again
            self.keep_alive_thread = threading.Thread(target=self.keep_alive, daemon=True)
            self.keep_alive_thread.start()  # Start the keep-alive thread
            print("[Sentinel] Drone is READY...")
            
        # When the command is to disarm the drone, it will
        elif self.state == self.SHUTTING_DOWN:
            print("[Sentinel] Shutting down the drone...")
            self.arm = 1000
            self.keep_alive_running = False  # Tell the keep-alive thread to stop
            self.keep_alive_thread.join()  # Wait for the current keep-alive command to finish
            self.keep_alive_thread = None  # Reset the keep_alive_thread

        # Whatever other state, it will use the self.update method
        else:
            print(f"[Sentinel] Changing state to: {Drone.states[state]}")
            self.update()
    
    # States control
    def update(self):
        # All states will turn the drone neutral and then bring it to the correct target      
        if self.state == self.KEEPING:
            print("[Sentinel] Drone is keeping position.")
            self.gradual_update("T", Drone.THROTTLE_FLOATING) # to neutral
            self.gradual_update("R", 1500)                    # to target
            
        elif self.state == self.RISING:
            print("[Sentinel] Drone is rising...")
            self.gradual_update("R", 1500)                    # to neutral
            self.gradual_update("T", Drone.THROTTLE_RISING)   # to target
            
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

    # Keep alive is a way to avoid the Drone's motors to stop
    def keep_alive(self):
        while self.keep_alive_running:          # Only run the loop while keep_alive_running is True
            if not self.update_in_progress:     # Only send command if not updating
                # Send the command to the drone
                self.commands.aetr1234(self.A, self.E, self.T, self.R, self.arm, 1500, 1500, 1500)

    # It's an extension of keep alive, but to turn the transitions smooth
    def gradual_update(self, param, target):
            self.update_in_progress = True  # Indicate that an update is in progress
            current_value = getattr(self, param)
            direction = np.sign(target - current_value)  # +1 if we need to increase the value, -1 if we need to decrease
            while current_value != target:
                current_value += direction * self.update_step
                setattr(self, param, current_value)
                self.commands.aetr1234(self.A, self.E, self.T, self.R, self.arm, 1500, 1500, 1500)
            self.update_in_progress = False  # Indicate that the update is finished