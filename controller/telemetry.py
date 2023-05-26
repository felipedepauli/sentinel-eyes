#!/usr/bin/env python

from msp import MultiWii

print("oi")

try:
    board = MultiWii("/dev/ttyACM0")
    print("vamo")
    
    

    while True:
        board.getData(MultiWii.ATTITUDE)
        print(board.attitude)
        board.getData(MultiWii.RC)
        print(board.rcChannels)
        # print(f'[Sentinel] Received AETR command: A={board.rcChannels["roll"]}, E={board.rcChannels["pitch"]}, T={board.rcChannels["throttle"]}, R={board.rcChannels["yaw"]}')
        
except Exception as e:
    print("Erro ao tentar se conectar à porta serial:")
    print(e)