import tobii_research as tr
import time

from pprint import pprint

found_eyetrackers = tr.find_all_eyetrackers()

my_eyetracker = found_eyetrackers[0]

def gaze_data_callback(gaze_data):
    data = gaze_data['left_gaze_origin_in_trackbox_coordinate_system']
    # pprint(gaze_data["left_gaze_origin_validity"])
    
    if gaze_data["left_gaze_origin_validity"] == 1:

        # x = data[0]

        # # print(x)

        # if x >= .66:
        #     print("Move Left")

        # elif x <= .33:
        #     print("Move Right")
        
        # else:
        #     print("Nothing")

        z = data[2]

        if z > 0.5:
            print("backwards")
        elif z < 0.4:
            print("Forwards")
        else:
            print("do nothing")



my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

time.sleep(1000)

my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
