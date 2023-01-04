import cv2
import socket
import pickle
import struct
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

class CamApp(App):
    def build(self):
        self.frame = Image()
        blframe = BoxLayout()
        blframe.add_widget(self.frame)
        FRAME_HOST = '127.0.0.1'
        self.frame_check(FRAME_HOST)
        Clock.schedule_interval(self.update_frame, 1.0 / 33.0)
        return blframe

    def frame_check(self, HOST):
        FRAME_HOST = HOST
        FRAME_PORT = 9090
        global frame_client
        frame_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        frame_client.connect((FRAME_HOST, FRAME_PORT))
        frame_client.send('getframe'.encode())

    def update_frame(self, dt):
        global frame_client
        payload_size = struct.calcsize(">L")
        data = b""
        while len(data) < payload_size:
            msg = frame_client.recv(100000)
            data += msg
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        frame_data = data[:msg_size]
        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        buf = cv2.flip(frame, 0).tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.frame.texture = texture


if __name__ == '__main__':
    CamApp().run()
