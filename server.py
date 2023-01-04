import sys
import cv2
import socket
import struct
import pickle
import threading

HOST = '0.0.0.0'
PORT = 9090
print(socket.gethostbyname_ex(socket.gethostname()))

def send_frame(server, addr):
  connection = server.makefile('wb')
  cap = cv2.VideoCapture(0)
  img_counter = 0
  encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
  while True:
    ret, frame = cap.read()
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    data = pickle.dumps(frame, 0)
    size = len(data)
    print(sys.getsizeof(struct.pack(">L", size) + data))
    if sys.getsizeof(struct.pack(">L", size) + data) < 65535:
      server.sendto(struct.pack(">L", size) + data, addr)
    img_counter += 1

def listen(HOST, PORT):
  server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  server.bind((HOST, PORT))
  members = []
  while True:
    try:
      msg, addr = server.recvfrom(1024)
    except:
      continue
    if addr not in members:
      members.append(addr)
    if not msg:
      continue
    client_id = addr[1]
    if msg.decode() == 'join':
      print(f'Client {client_id} joined chat')
      continue
    print(f'Client {client_id}: {msg.decode()}')
    if msg.decode() == 'getframe':
      threading.Thread(target=send_frame, args=(server, addr), daemon=True).start()

if __name__ == '__main__':
  listen(HOST, PORT)