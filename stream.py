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
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipe.start(config)

    for x in range(5):
        pipe.wait_for_frames()

    #dp = data_process.DataProcess(grip_pipe, H_FOV, F_LENGTH, SENSOR_WIDTH, WIDTH, HEIGHT)

    while True:
        frames = pipe.wait_for_frames()
    #    depth = frames.get_depth_frame()
        color = frames.get_color_frame()
        if not color:
            continue
        img = np.asarray(color.get_data()) #for ndarray?
#       depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        grip_pipe.process(img)
        #out.write(grip_pipeline.hsl_threshold_output)
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', grip_pipe.hsv_threshold_output)
    #    dp.update(img)
    #    print("past update")

        if cv2.waitKey(1) & 0xF == ord('q'):
            print("leave")
            break

#        dist = depth.get_distance(640, 360)
#        print(dist)
    #    table.putNumber('depth', dist)
finally:
    pipe.stop()
    cv2.destroyAllWindows()
#    # Method calls agaisnt librealsense objects may throw exceptions of type pylibrs.error
#    print("pylibrs.error was thrown when calling %s(%s):\n", % (e.get_failed_function(), e.get_failed_args()))
#    print("    %s\n", e.what())
#    exit(1)
