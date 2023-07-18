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

# found_eyetrackers = tr.find_all_eyetrackers()
# my_eyetracker = found_eyetrackers[0]

# vectorDict = {(0, 0): "Fly Up & Turn Left", (1, 0):"Fly Up & Turn Right", (0,1):"Fly Down & Turn Left", (1,1):"Fly Down & Turn Right", (0.5,0.5):"Do Nothing", (0.5,0):"Fly Up", (0.5,1):"Fly Down", (0, 0.5):"Turn Left", (1,0.5):"Turn Right"}

# def myround(x, prec=1, base=.5):
#   return round(base * round(float(x)/base),prec)



# def collectData(communicator):
#     global vectorDict
#     # while True:

#     #     xval = np.random.rand() + np.random.randint(0,1)
#     #     yval =  np.random.rand()
#     #     communicator.put([xval,yval]) # we use the Queue here to commuicate to the other process. Any process is
#     #     # allowed to put data into or extract data from. So the data collection process simply keeps putting data in.
#     #     time.sleep(0.4) # not to overload this example ;)


#     found_eyetrackers = tr.find_all_eyetrackers()
#     my_eyetracker = found_eyetrackers[0]


#     def gaze_data_callback(gaze_data):
#         x, y = gaze_data['right_gaze_point_on_display_area']
#         # print(x, y)
#         # time.sleep(1)
#         communicator.put(vectorDict[(myround(x), myround(y))])


#     my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

#     while True:
#         continue
#     # time.sleep(5)

#     # my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)


def getData(cs):
    cs.send("get data".encode())
    data = cs.recv(1024).decode()  # receive response
    print('Received from server: ' + data)  # show in terminal




class Ctrl(Enum):
    (
        QUIT,
        TAKEOFF,
        LANDING,
        MOVE_LEFT,
        MOVE_RIGHT,
        MOVE_FORWARD,
        MOVE_BACKWARD,
        MOVE_UP,
        MOVE_DOWN,
        TURN_LEFT,
        TURN_RIGHT,
    ) = range(11)


QWERTY_CTRL_KEYS = {
    Ctrl.QUIT: Key.esc,
    Ctrl.TAKEOFF: "t",
    Ctrl.LANDING: "l",
    Ctrl.MOVE_LEFT: "a",
    Ctrl.MOVE_RIGHT: "d",
    Ctrl.MOVE_FORWARD: "w",
    Ctrl.MOVE_BACKWARD: "s",
    Ctrl.MOVE_UP: Key.up,
    Ctrl.MOVE_DOWN: Key.down,
    Ctrl.TURN_LEFT: Key.left,
    Ctrl.TURN_RIGHT: Key.right,
}

AZERTY_CTRL_KEYS = QWERTY_CTRL_KEYS.copy()
AZERTY_CTRL_KEYS.update(
    {
        Ctrl.MOVE_LEFT: "q",
        Ctrl.MOVE_RIGHT: "d",
        Ctrl.MOVE_FORWARD: "z",
        Ctrl.MOVE_BACKWARD: "s",
    }
)


class KeyboardCtrl(Listener):
    def __init__(self, ctrl_keys=None):
        self._ctrl_keys = self._get_ctrl_keys(ctrl_keys)
        self._key_pressed = defaultdict(lambda: False)
        self._last_action_ts = defaultdict(lambda: 0.0)
        super().__init__(on_press=self._on_press, on_release=self._on_release)
        self.start()

    def _on_press(self, key):
        if isinstance(key, KeyCode):
            self._key_pressed[key.char] = True
        elif isinstance(key, Key):
            self._key_pressed[key] = True
        if self._key_pressed[self._ctrl_keys[Ctrl.QUIT]]:
            return False
        else:
            return True

    def _on_release(self, key):
        if isinstance(key, KeyCode):
            self._key_pressed[key.char] = False
        elif isinstance(key, Key):
            self._key_pressed[key] = False
        return True

    def quit(self):
        return not self.running or self._key_pressed[self._ctrl_keys[Ctrl.QUIT]]

    def _axis(self, left_key, right_key):
        return 100 * (
            int(self._key_pressed[right_key]) - int(self._key_pressed[left_key])
        )

    def roll(self):
        return self._axis(
            self._ctrl_keys[Ctrl.MOVE_LEFT],
            self._ctrl_keys[Ctrl.MOVE_RIGHT]
        )

    def pitch(self):
        return self._axis(
            self._ctrl_keys[Ctrl.MOVE_BACKWARD],
            self._ctrl_keys[Ctrl.MOVE_FORWARD]
        )

    def yaw(self):
        return self._axis(
            self._ctrl_keys[Ctrl.TURN_LEFT],
            self._ctrl_keys[Ctrl.TURN_RIGHT]
        )

    def throttle(self):
        return self._axis(
            self._ctrl_keys[Ctrl.MOVE_DOWN],
            self._ctrl_keys[Ctrl.MOVE_UP]
        )

    def has_piloting_cmd(self):
        return (
            bool(self.roll())
            or bool(self.pitch())
            or bool(self.yaw())
            or bool(self.throttle())
        )

    def _rate_limit_cmd(self, ctrl, delay):
        now = time.time()
        if self._last_action_ts[ctrl] > (now - delay):
            return False
        elif self._key_pressed[self._ctrl_keys[ctrl]]:
            self._last_action_ts[ctrl] = now
            return True
        else:
            return False

    def takeoff(self):
        return self._rate_limit_cmd(Ctrl.TAKEOFF, 2.0)

    def landing(self):
        return self._rate_limit_cmd(Ctrl.LANDING, 2.0)

    def _get_ctrl_keys(self, ctrl_keys):
        # Get the default ctrl keys based on the current keyboard layout:
        if ctrl_keys is None:
            ctrl_keys = QWERTY_CTRL_KEYS
            try:
                # Olympe currently only support Linux
                # and the following only works on *nix/X11...
                keyboard_variant = (
                    subprocess.check_output(
                        "setxkbmap -query | grep 'variant:'|"
                        "cut -d ':' -f2 | tr -d ' '",
                        shell=True,
                    )
                    .decode()
                    .strip()
                )
            except subprocess.CalledProcessError:
                pass
            else:
                if keyboard_variant == "azerty":
                    ctrl_keys = AZERTY_CTRL_KEYS
        return ctrl_keys


if __name__ == "__main__":
    with olympe.Drone("10.202.0.1") as drone:
        drone.connect()
        control = KeyboardCtrl()

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


        while not control.quit():
            if control.takeoff():
                drone(TakeOff())
            elif control.landing():
                drone(Landing())
            # if control.has_piloting_cmd():

            #     data = getData(client_socket)

            #     if data == "Turn Left":
            #         drone(moveBy(0,0,0,-0.261799))
            else:
                data = getData(client_socket)

                if data == "Turn Left":
                    drone(moveBy(0,0,0,-0.261799))
                # drone(PCMD(0, 0, 0, 0, 0, timestampAndSeqNum=0))
            time.sleep(0.05)
        client_socket.close()  # close the connection


