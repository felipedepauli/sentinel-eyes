import cv2
import socket
import struct
import pickle

cap = cv2.VideoCapture(0)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8488))
server_socket.listen(10)

while True:
    client_socket, address = server_socket.accept()
    print(f"Connection from: {address}")

    while True:
        ret, frame = cap.read()
        data = pickle.dumps(frame)
        message_size = struct.pack("L", len(data))

        client_socket.sendall(message_size + data)
