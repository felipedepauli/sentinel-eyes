#!/usr/bin/env python

# Import the MultiWii module from the msp package
from msp import MultiWii

# Print a message indicating the start of the drone test
print("Testing the drone")

try:
    # Attempt to establish a connection with the drone's board
    # The board is connected via the serial port "/dev/ttyACM0" on Raspberry
    board = MultiWii("/dev/ttyACM0")
    
    # If the connection is successful, print a message indicating readiness to receive telemetry
    print("Board ready to get telemetry.")
    
    # Enter an infinite loop to continuously receive and print telemetry data
    while True:
        # Get the drone's attitude data and print it
        board.getData(MultiWii.ATTITUDE)
        print(board.attitude)
        
        # Get the drone's RC channel data and print it
        board.getData(MultiWii.RC)
        print(board.rcChannels)
        
except Exception as e:
    # If an error occurs while trying to establish the connection, print an error message and the exception
    print("Erro ao tentar se conectar à porta serial:")
    print(e)
