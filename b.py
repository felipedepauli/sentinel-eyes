import cv2
import socket
import struct
import os
import base64
import pickle

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8488))

unix_socket_path = "/tmp/synapse.sock"
if os.path.exists(unix_socket_path):
    os.remove(unix_socket_path)

unix_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
unix_socket.connect(unix_socket_path)

data = b""
payload_size = struct.calcsize("L")

while True:
    while len(data) < payload_size:
        data += client_socket.recv(4096)

    packed_message_size = data[:payload_size]
    data = data[payload_size:]
    message_size = struct.unpack("L", packed_message_size)[0]

    while len(data) < message_size:
        data += client_socket.recv(4096)

    frame_data = data[:message_size]
    data = data[message_size:]

    frame = pickle.loads(frame_data)
    frame_base64 = base64.b64encode(frame_data)

    unix_socket.sendall(frame_base64)

unix_socket.close()
client_socket.close()
