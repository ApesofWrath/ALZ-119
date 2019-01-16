import pyrealsense2 as rs
from networktables import NetworkTables
import threading
import grip
import cv2
import numpy as np
import data_process as dp
import math
import sys

WIDTH = 1920.0
HEIGHT = 1080.0
H_FOV = 85.2
F_LENGTH = 0.00193 # in meters
SENSOR_WIDTH = 0.002804 # in meters #TODO: find this

grip_pipe = grip.VisionTestPipeline()

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

    startNetworkTables()
    table = NetworkTables.getTable('SmartDashboard')

    pipe = rs.pipeline()
    pipe.start()

    while True:
        frames = pipe.wait_for_frames()
        depth = frames.get_depth_frame()
        color = frames.get_color_frame()
        if not depth or not color:
            continue
        img = np.asanyarray(color.get_data())
#    dp = data_process.DataProcess(cap, pipe, H_FOV, F_LENGTH, SENSOR_WIDTH, WIDTH, HEIGHT)


    #    img = cv.CreateMat(h, w, cv.CV_32FC3)
    #   c++ original - Mat color(Size(640, 480), CV_8UC3, (void*)color_frame.get_data(), Mat::AUTO_STEP);
    #    img = np.zeros((256, 256, 1), dtype = "uint8")

         grip_pipeline.process(img)
         cv2.imshow('RealSense', img)
         cv2.waitKey(0)
        dist = depth.get_distance(640, 360)
        print(dist)
        table.putNumber('depth', dist)
    exit(0)

#except rs.error as e:
#    # Method calls agaisnt librealsense objects may throw exceptions of type pylibrs.error
#    print("pylibrs.error was thrown when calling %s(%s):\n", % (e.get_failed_function(), e.get_failed_args()))
#    print("    %s\n", e.what())
#    exit(1)
except Exception as e:
    print(e)
    pass
