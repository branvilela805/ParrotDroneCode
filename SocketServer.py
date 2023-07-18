import socket
import time
from multiprocessing import Process, Queue
import tobii_research as tr




# found_eyetrackers = tr.find_all_eyetrackers()
# my_eyetracker = found_eyetrackers[0]

# vectorDict = {(0, 0): "Fly Up & Turn Left", (1, 0):"Fly Up & Turn Right", (0,1):"Fly Down & Turn Left", (1,1):"Fly Down & Turn Right", (0.5,0.5):"Do Nothing", (0.5,0):"Fly Up", (0.5,1):"Fly Down", (0, 0.5):"Turn Left", (1,0.5):"Turn Right"}

def myround(x, prec=1, base=.5):
  return round(base * round(float(x)/base),prec)



def collectData(communicator):
    global vectorDict
    # while True:

    #     xval = np.random.rand() + np.random.randint(0,1)
    #     yval =  np.random.rand()
    #     communicator.put([xval,yval]) # we use the Queue here to commuicate to the other process. Any process is
    #     # allowed to put data into or extract data from. So the data collection process simply keeps putting data in.
    #     time.sleep(0.4) # not to overload this example ;)


    found_eyetrackers = tr.find_all_eyetrackers()
    my_eyetracker = found_eyetrackers[0]


    def gaze_data_callback(gaze_data):
        x, y = gaze_data['right_gaze_point_on_display_area']
        # print(x, y)
        # time.sleep(1)
        communicator.put(vectorDict[(myround(x), myround(y))])


    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

    while True:
        continue
    # time.sleep(5)

    # my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)



# def server_program():
if __name__ == '__main__':

    found_eyetrackers = tr.find_all_eyetrackers()
    my_eyetracker = found_eyetrackers[0]

    vectorDict = {(0, 0): "Fly Up & Turn Left", (1, 0):"Fly Up & Turn Right", (0,1):"Fly Down & Turn Left", (1,1):"Fly Down & Turn Right", (0.5,0.5):"Do Nothing", (0.5,0):"Fly Up", (0.5,1):"Fly Down", (0, 0.5):"Turn Left", (1,0.5):"Turn Right"}
    currvalue = ""
    def gaze_data_callback(gaze_data):
        global currvalue
        x, y = gaze_data['right_gaze_point_on_display_area']
        # print(x, y)
        # time.sleep(1)
        currvalue=vectorDict[(myround(x), myround(y))]
    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    # get the hostname
    host = socket.gethostname()
    port = 9123  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind(("", port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))

    # communicator = Queue()
    # print('Start process...')
    # eyeTrackerData = Process(target=collectData, args=(communicator,))
    # eyeTrackerData.start()

    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()
        if not data:
            # if data is not received break
            break
        # print("from connected user: " + str(data))
        if str(data) == "get data":
            data = time.strftime("%H:%M:%S")
            data = currvalue
            conn.send(data.encode())
        time.sleep(2)  # send data to the client

    conn.close()  # close the connection


# if __name__ == '__main__':
#     server_program()