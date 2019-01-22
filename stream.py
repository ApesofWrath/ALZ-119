import pyrealsense2 as rs
from networktables import NetworkTables
import threading
import grip
import cv2
import numpy as np
import data_process
import math
import sys

WIDTH = 1920.0
HEIGHT = 1080.0
H_FOV = 85.2
F_LENGTH = 0.00193 # in meters
SENSOR_WIDTH = 0.003549 # in meter

grip_pipe = grip.GreenProfile()

cond = threading.Condition() #global for network tables
notified = [False]

def connectionListener(connected, info):

    print(info, '; Connected=%s' % connected)
    with cond:
        notified[0] = True
        cond.notify()

def startNetworkTables():

    NetworkTables.startClientTeam(668)
    NetworkTables.initialize(server='10.6.68.2') #roborio must be on this static ip
    NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

    with cond:
        print("Waiting")
        if not notified[0]:
            cond.wait()

    print("Connected!")

try:

#    startNetworkTables()
#    table = NetworkTables.getTable('SmartDashboard')

    pipe = rs.pipeline()
    pipe.start()

    dp = data_process.DataProcess(grip_pipe, H_FOV, F_LENGTH, SENSOR_WIDTH, WIDTH, HEIGHT)

    while True:
        frames = pipe.wait_for_frames()
    #    depth = frames.get_depth_frame()
        color = frames.get_color_frame()
        if not color:
            continue
        img = np.asanyarray(color.get_data())
        grip_pipe.process(img)
        cv2.imshow("grip", grip_pipe.hsv_threshold_output)
    #    dp.update(img)
    #    print("past update")

        if cv2.waitKey(1) & 0xF == ord('q'):
            break

#        dist = depth.get_distance(640, 360)
#        print(dist)
    #    table.putNumber('depth', dist)
    exit(0)
#    # Method calls agaisnt librealsense objects may throw exceptions of type pylibrs.error
#    print("pylibrs.error was thrown when calling %s(%s):\n", % (e.get_failed_function(), e.get_failed_args()))
#    print("    %s\n", e.what())
#    exit(1)
except Exception as e:
    print(e)
    pass
