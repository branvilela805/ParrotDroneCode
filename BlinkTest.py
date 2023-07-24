import tobii_research as tr
import time
import pprint
import math
found_eyetrackers = tr.find_all_eyetrackers()

my_eyetracker = found_eyetrackers[0]

global_blink_arr = [1,1,1,1,1,1,1,1,1,1]

blinked = False

def blinkCheck():
    global global_blink_arr
    global_blink_arr = global_blink_arr[-120:]
    if all(math.isnan(element) for element in global_blink_arr):
        global_blink_arr = [1,1,1,1,1,1,1,1,1,1]
        return True
    else:
        return False

def gaze_data_callback(gaze_data):
    global blinked
    global my_eyetracker
    # print(math.isnan(gaze_data["right_gaze_point_on_display_area"][0]))
    if not blinked:
        global_blink_arr.append(gaze_data["right_gaze_point_on_display_area"][0])
        blinked = blinkCheck()
        print("Do Nothing")
    else:
        print("BLINKED")
        blinked=False
        # my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    # if gaze_data["right_gaze_point_validity"] == 0:
    #     print(type(gaze_data["right_gaze_point_on_display_area"][0]))

my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

time.sleep(20)

my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

