import olympe
import time

import os

from olympe.messages.ardrone3.Piloting import TakeOff, moveBy, Landing

from olympe.messages.ardrone3.PilotingState import FlyingStateChanged

from olympe.messages.ardrone3.Animations import Flip

import socket

#virtual machine
DRONE_IP = os.environ.get("DRONE_IP", "10.202.0.1")

#physical drone ip address
#DRONE_IP = os.environ.get("DRONE_IP", "192.168.42.1")

def getData(cs):
    cs.send("get data".encode())
    data = cs.recv(1024).decode()  # receive response
    print('Received from server: ' + data)  # show in terminal





def test_moveby2():

    drone = olympe.Drone(DRONE_IP)

    drone.connect()

    assert drone(

        TakeOff()

        >> FlyingStateChanged(state="hovering", _timeout=5)

    ).wait().success()
    time.sleep(5)
    
#drone moves 1 meters forward:
    assert drone(

    

        moveBy(1, 0, 0, 0)
        >> FlyingStateChanged(state="hovering", _timeout=5)

    ).wait().success()
    time.sleep(5)
 


#drone moves back 1 meter:
    assert drone(

    

        moveBy(-1, 0, 0, 0)
        >> FlyingStateChanged(state="hovering", _timeout=5)

    ).wait().success()
    time.sleep(5)



    assert drone(Landing()).wait().success()

    drone.disconnect()

    


if __name__ == "__main__":

    test_moveby2()