import olympe

from olympe.messages.ardrone3.Piloting import TakeOff, Landing, PCMD

from pynput.keyboard import Listener, Key

# Connect to the drone
drone = olympe.Drone("10.202.0.1")
drone.connection()

# Define keyboard control mapping
control_mapping = {
    Key.esc: Landing(),
    't': TakeOff(),
    'w': PCMD(1, 0, -50, 0, 0, 0),
    's': PCMD(1, 0, 50, 0, 0, 0),
    'a': PCMD(1, -50, 0, 0, 0, 0),
    'd': PCMD(1, 50, 0, 0, 0, 0),
}

# Keyboard control listener
def on_press(key):
    if key in control_mapping:
        drone(control_mapping[key])

def on_release(key):
    if key == Key.esc:
        drone(Landing())

# Start the keyboard control listener
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
