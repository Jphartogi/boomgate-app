from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5 import QtCore, QtGui, QtWidgets
from threading import Thread
from collections import deque
import cv2
import time
import imutils

class CameraStream(QWidget):
    def __init__(self, video_frame, width, height, stream_link=0, aspect_ratio=False, parent=None, deque_size=1):
        super().__init__(parent)
        
        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle("Information")
        self.msg.setIcon(QMessageBox.Warning)

        self.verify_network_handler = self.VerifyNetworkHandler()
        self.verify_network_handler.verify_status.connect(self.on_status_verify)

        # Initialize deque used to store frames read from the stream
        self.deque = deque(maxlen=deque_size)

        # Slight offset is needed since PyQt layouts have a built in padding
        # So add offset to counter the padding
        self.offset = 16
        self.screen_width = width - self.offset
        self.screen_height = height - self.offset
        self.maintain_aspect_ratio = aspect_ratio

        self.camera_stream_link = stream_link

        # Flag to check if camera is valid/working
        self.online = False
        self.capture = None

        self.video_frame = video_frame
        
        print('Connceting to the camera: {}'.format(self.camera_stream_link))

        self.load_network_stream()

        # Periodically set video frame to display
        self.timer = QtCore.QTimer()
        self.timer.setInterval(int(1000/30))
        self.timer.timeout.connect(self.set_frame)
        self.timer.start()
        
    def load_network_stream(self):
        """Verifies stream link and open new stream if valid"""

        def load_network_stream_thread():
            if self.verify_network_stream(self.camera_stream_link):
                # Start background frame grabbing
                self.get_frame_thread = Thread(target=self.get_frame, args=())
                self.get_frame_thread.daemon = True
                self.get_frame_thread.start()

                self.capture = cv2.VideoCapture(self.camera_stream_link)
                self.online = True


        self.load_stream_thread = Thread(
            target=load_network_stream_thread, args=())
        self.load_stream_thread.daemon = True
        self.load_stream_thread.start()

    def verify_network_stream(self, link):
        """Attempts to receive a frame from given link"""
        try:
            cap = cv2.VideoCapture(link)                
            if not cap.isOpened():
                raise NameError("Can't connect to the Camera")
                return False
        except Exception as e:
            self.msg.setText(QtWidgets.QApplication.translate("MainWindow", "Can't connect to the Camera"))
            self.verify_network_handler.verify_status.emit(False)
            print("Exception:", e)
        else:
            print('Started camera: {}'.format(self.camera_stream_link))
            cap.release()
            self.verify_network_handler.verify_status.emit(True)
            return True

    def get_frame(self):
        """Reads frame, resizes, and converts image to pixmap"""

        while True:
            try:
                if self.capture.isOpened() and self.online:
                    # Read next frame from stream and insert into deque
                    status, frame = self.capture.read()
                    if status:
                        self.deque.append(frame)
                    else:
                        self.capture.release()
                        self.online = False
                else:
                    # Attempt to reconnect
                    print('attempting to reconnect', self.camera_stream_link)
                    self.load_network_stream()
                    self.spin(2)
                self.spin(.001)
            except AttributeError:
                pass

    def spin(self, seconds):
        """Pause for set amount of seconds, replaces time.sleep so program doesnt stall"""

        time_end = time.time() + seconds
        while time.time() < time_end:
            QApplication.processEvents()

    def set_frame(self):
        """Sets pixmap image to video frame"""

        if not self.online:
            self.spin(1)
            return

        if self.deque and self.online:
            # Grab latest frame
            frame = self.deque[-1]

            # Keep frame aspect ratio
            if self.maintain_aspect_ratio:
                self.frame = imutils.resize(frame, width=self.screen_width)
            # Force resize
            else:
                self.frame = cv2.resize(
                    frame, (self.screen_width, self.screen_height))

            # Convert to pixmap and set to video frame
            self.img = QtGui.QImage(
                self.frame, self.frame.shape[1], self.frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            self.pix = QPixmap.fromImage(self.img)
            self.pix = self.pix.scaledToHeight(self.video_frame.height())
            self.video_frame.setPixmap(self.pix)

    def get_video_frame(self):
        return self.video_frame

    class VerifyNetworkHandler(QObject):
        verify_status = pyqtSignal(bool)
    
    @pyqtSlot(bool)
    def on_status_verify(self, verify):
        if verify == False:
            self.msg.show()
        else:
            self.msg.hide()
