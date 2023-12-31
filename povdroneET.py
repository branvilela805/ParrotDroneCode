import olympe
from olympe.messages.ardrone3.Piloting import TakeOff, moveBy, Landing, moveTo, NavigateHome
import threading
import time
import queue
import cv2
import logging

import tobii_research as tr
import time
import pprint
from multiprocessing import Process, Queue
import olympe
import subprocess
import time
from olympe.messages.ardrone3.Piloting import TakeOff, Landing, PCMD
from pynput.keyboard import Listener, Key, KeyCode
from collections import defaultdict
from enum import Enum
import socket
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged

from olympe.messages.ardrone3.Piloting import TakeOff, moveBy, Landing

class OlympeStreaming(threading.Thread):
    def __init__(self, drone):
        self.drone = drone
        self.frame_queue = queue.Queue()
        self.flush_queue_lock = threading.Lock()
        self.frame_num = 0
        self.renderer = None
        super().__init__()
        super().start()


    def start(self):
        # Setup your callback functions to do some live video processing
        self.drone.streaming.set_callbacks(
            raw_cb=self.yuv_frame_cb,
            h264_cb=self.h264_frame_cb,
            start_cb=self.start_cb,
            end_cb=self.end_cb,
            flush_raw_cb=self.flush_cb,
        )
        # Start video streaming
        self.drone.streaming.start()
        #self.renderer = PdrawRenderer(pdraw=self.drone.streaming)

    def stop(self):
        if self.renderer is not None:
            self.renderer.stop()
        # Properly stop the video stream and disconnect
        self.drone.streaming.stop()

    def yuv_frame_cb(self, yuv_frame):
        """
        This function will be called by Olympe for each decoded YUV frame.
            :type yuv_frame: olympe.VideoFrame
        """
        yuv_frame.ref()
        self.frame_queue.put_nowait(yuv_frame)

    def flush_cb(self, stream):
        if stream["vdef_format"] != olympe.VDEF_I420:
            return True
        with self.flush_queue_lock:
            while not self.frame_queue.empty():
                self.frame_queue.get_nowait().unref()
        return True

    def start_cb(self):
        pass

    def end_cb(self):
        pass

    def h264_frame_cb(self, h264_frame):
        pass

    def display_frame(self, yuv_frame):
        # the VideoFrame.info() dictionary contains some useful information
        # such as the video resolution
        info = yuv_frame.info()

        height, width = (  # noqa
            info["raw"]["frame"]["info"]["height"],
            info["raw"]["frame"]["info"]["width"],
        )

        # yuv_frame.vmeta() returns a dictionary that contains additional
        # metadata from the drone (GPS coordinates, battery percentage, ...)
        # convert pdraw YUV flag to OpenCV YUV flag
        cv2_cvt_color_flag = {
            olympe.VDEF_I420: cv2.COLOR_YUV2BGR_I420,
            olympe.VDEF_NV12: cv2.COLOR_YUV2BGR_NV12,
        }[yuv_frame.format()]

        # yuv_frame.as_ndarray() is a 2D numpy array with the proper "shape"
        # i.e (3 * height / 2, width) because it's a YUV I420 or NV12 frame

        # Use OpenCV to convert the yuv frame to RGB
        cv2frame = cv2.cvtColor(yuv_frame.as_ndarray(), cv2_cvt_color_flag)
        cv2.imshow("Frames via Olympe", cv2frame)
        cv2.waitKey(1)

    def run(self):
        main_thread = next(
            filter(lambda t: t.name == "MainThread", threading.enumerate())
        )
        while main_thread.is_alive():
            with self.flush_queue_lock:
                try:
                    yuv_frame = self.frame_queue.get(timeout=0.01)
                except queue.Empty:
                    continue
                try:
                    self.display_frame(yuv_frame)
                except Exception as e:
                    print(e)
                finally:
                    # Don't forget to unref the yuv frame. We don't want to
                    # starve the video buffer pool
                    yuv_frame.unref()


logger = logging.getLogger(__name__)

def getData(cs):
    cs.send("get data".encode())
    data = cs.recv(1024).decode()  # receive response
    print('Received from server: ' + data)  # show in terminal
    return str(data)


if __name__ == "__main__":
       
    #eventually IP will be specified depending on what drone is chosen
    IP = "10.202.0.1"
    drone = olympe.Drone(IP)
    drone.connect()
   


    ### Flight commands here ###

    host = "10.247.5.44"
    port = 9123  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    # message = input(" -> ")  # take input

    f = False
    while True:
        streamer = OlympeStreaming(drone)
        streamer.start()   
        if not f:
            f = True
            drone(TakeOff() >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()

        data = getData(client_socket)
        match data:
            case "Turn Left":
                drone(moveBy(0,0,0,-0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            case "Turn Right":
                drone(moveBy(0,0,0,0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            case "Fly Up":
                drone(moveBy(0,0,.25,0) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            case "Fly Down":
                drone(moveBy(0,0,-.25,0) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            case "Fly Up & Turn Left":
                drone(moveBy(0,0,.25,-0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            case "Fly Up & Turn Right":
                drone(moveBy(0,0,.25,0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()  
            case "Fly Down & Turn Left":
                drone(moveBy(0,0,-.25,-0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success() 
            case "Fly Down & Turn Right":
                drone(moveBy(0,0,-.25,0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            case _:
                drone(moveBy(0,0,0,0))                                                         

        time.sleep(0.05)
    streamer.stop()
    client_socket.close()
    drone(Landing()).wait().success()
    drone.disconnect()
