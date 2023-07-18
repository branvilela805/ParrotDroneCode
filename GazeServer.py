from multiprocessing import Process, Queue
import time
import socket

def collectdata(communicator):
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    communicator.put(current_time)
