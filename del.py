import socket
import time
from multiprocessing import Process, Queue
import tobii_research as tr
import math



# found_eyetrackers = tr.find_all_eyetrackers()
# my_eyetracker = found_eyetrackers[0]

# vectorDict = {(0, 0): "Fly Up & Turn Left", (1, 0):"Fly Up & Turn Right", (0,1):"Fly Down & Turn Left", (1,1):"Fly Down & Turn Right", (0.5,0.5):"Do Nothing", (0.5,0):"Fly Up", (0.5,1):"Fly Down", (0, 0.5):"Turn Left", (1,0.5):"Turn Right"}

def myround(x, prec=1, base=.5):
  return round(base * round(float(x)/base),prec)

global_blink_arr = [1,1,1,1,1,1,1,1,1,1]
global_land_arr = [1,1,1,1,1,1,1,1,1,1]

blinked = False
landing = False

s = ""

def landCheck():
    global global_land_arr
    global_land_arr = global_land_arr[-10:]
    if all(math.isnan(element) for element in global_land_arr):
        global_land_arr = [1,1,1,1,1,1,1,1,1,1]
        return "Land"
    else:
        return ""

def blinkCheck():
    global global_blink_arr
    global_blink_arr = global_blink_arr[-10:]
    if all(math.isnan(element) for element in global_blink_arr):
        global_blink_arr = [1,1,1,1,1,1,1,1,1,1]
        return "Blinked"
    else:
        return ""



# def server_program():
if __name__ == '__main__':

    found_eyetrackers = tr.find_all_eyetrackers()
    my_eyetracker = found_eyetrackers[0]

    vectorDict = {(0, 0): "Fly Up & Turn Left", (1, 0):"Fly Up & Turn Right", (0,1):"Fly Down & Turn Left", (1,1):"Fly Down & Turn Right", (0.5,0.5):"Do Nothing", (0.5,0):"Fly Up", (0.5,1):"Fly Down", (0, 0.5):"Turn Left", (1,0.5):"Turn Right"}
    currvalue = ""
    gesture = ""
    def gaze_data_callback(gaze_data):
        global blinked
        global landing
        global gesture
        global currvalue
        global s
        # if not blinked:
        currvalue = ""
        global_blink_arr.append(gaze_data["right_gaze_point_on_display_area"][0])
        global_land_arr.append(gaze_data["left_gaze_point_on_display_area"][0])
        gesture = ""
        blinked = blinkCheck()
        if blinked == "Blinked":
            landing = landCheck()
            if landing != "":
                gesture = landing
            else:
                gesture = blinked

        x, y = gaze_data['right_gaze_point_on_display_area']
        currvalue=vectorDict[(myround(x), myround(y))]

        data = gaze_data['left_gaze_origin_in_trackbox_coordinate_system']
        # pprint(gaze_data["left_gaze_origin_validity"])
        
        s = ""

        x = data[0]

        # print(x)

        if x >= .66:
            s += " Move Left "

        elif x <= .56:
            s += " Move Right "
        
        else:
            pass
            # print("Nothing")

        z = data[2]

        if z > 0.5:
            s += " Move Backward "
        elif z < 0.4:
            s+=" Move Forward "
        else:
            pass
            # s+= " do nothing"

        # else:
            # landing = landCheck()
            # if landing != "":
            #     currvalue = landing
            # else:
            #     currvalue="Blinked"



    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    # get the hostname


    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = currvalue + s
        if gesture != "":
            data = gesture
        print(data)
        time.sleep(.01)
        # time.sleep(2)  # send data to the client



# if __name__ == '__main__':
#     server_program()