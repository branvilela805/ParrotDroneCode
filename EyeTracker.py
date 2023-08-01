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



def getData(cs):
    cs.send("get data".encode())
    data = cs.recv(1024).decode()  # receive response
    print('Received from server: ' + data)  # show in terminal
    return str(data)



if __name__ == "__main__":
    with olympe.Drone("10.202.0.1") as drone:
        drone.connect()

        # communicator = Queue()
        # print('Start process...')
        # eyeTrackerData = Process(target=collectData, args=(communicator,))
        # eyeTrackerData.start()
        # drone(TakeOff())

        host = "10.247.5.44"
        port = 9123  # socket server port number

        client_socket = socket.socket()  # instantiate
        client_socket.connect((host, port))  # connect to the server

        # message = input(" -> ")  # take input

        tookoff = False
        alreadyBlinked = False
        f = False
        while True:

            # if not f:
            #     f = True
            #     drone(TakeOff() >> FlyingStateChanged(state="hovering", _timeout=.6)).wait().success()



            data = getData(client_socket)
            if "Blinked" in data and not tookoff:
                tookoff = True
                alreadyBlinked = True
                drone(TakeOff() >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            if "Land" in data and tookoff:
                tookoff = False
                alreadyBlinked = True
                drone(Landing()).wait().success()
            # elif data == "Blinked" and tookoff:
            #     drone(Landing() >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()


            x = 0
            y = 0
            z = 0
            r = 0

            movementConst = 0.25
            turningConst = 0.261799

            if "Turn Left" in data:
                r = -turningConst
            elif "Turn Right" in data:
                r = turningConst
            
            if "Fly Up" in data:
                z = -movementConst
            elif "Fly Down" in data:
                z = movementConst
            
            if "Move Left" in data:
                y = -movementConst
            elif "Move Right" in data:
                y = movementConst
            
            if "Move Forward" in data:
                x = movementConst
            elif "Move Backward" in data:
                x = -movementConst

            drone(moveBy(x,y,z,r) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()

            # match data:
            #     case "Turn Left":
            #         drone(moveBy(0,0,0,-0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            #     case "Turn Right":
            #         drone(moveBy(0,0,0,0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            #     case "Fly Up":
            #         drone(moveBy(0,0,-.25,0) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            #     case "Fly Down":
            #         drone(moveBy(0,0,.25,0) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            #     case "Fly Up & Turn Left":
            #         drone(moveBy(0,0,-.25,-0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            #     case "Fly Up & Turn Right":
            #         drone(moveBy(0,0,-.25,0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()  
            #     case "Fly Down & Turn Left":
            #         drone(moveBy(0,0,.25,-0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            #     case "Fly Down & Turn Right":
            #         drone(moveBy(0,0,.25,0.261799) >> FlyingStateChanged(state="hovering", _timeout=.1)).wait().success()
            #     case _:
            #         drone(moveBy(0,0,0,0))                                                        
            # if data == "Turn Left":
            #     drone(moveBy(0,0,0,-0.261799) >> FlyingStateChanged(state="hovering", _timeout=5)).wait().success()
            # if data == "Turn Right":
            #     drone(moveBy(0,0,0,0.261799))
            # drone(PCMD(0, 0, 0, 0, 0, timestampAndSeqNum=0))
            time.sleep(0.05)
        client_socket.close()  # close the connection