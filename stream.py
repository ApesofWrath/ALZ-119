import pyrealsense2 as rs
from networktables import NetworkTables
import threading
import grip
import cv2
import numpy as np
import data_process
import math
import sys
import cscore as cs
import os

file = open("log.txt", 'w') # Remove after testing

WIDTH = 640
HEIGHT = 480
H_FOV = 45.6 # 53.13 empirically # need to recalculate if change WIDTH dimension  (line up meter stick and get distance then atan)
F_LENGTH = 0.00193 # in meters
SENSOR_WIDTH = 0.003896 # in meter

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


def reboot(e):
    file.write()
    os.system("reboot")



try:
    startNetworkTables()
    table = NetworkTables.getTable('SmartDashboard')
    counter = 0 # used to take intervals of exit angle data
    exit_angles = []

    pipe = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, int(WIDTH), int(HEIGHT), rs.format.bgr8, 60) #numbers that work: 6, 15
    config.enable_stream(rs.stream.depth, int(WIDTH), int(HEIGHT), rs.format.z16, 60)
    pipe.start(config)

#    cam = cs.UsbCamera("webcam", 0)
    cserver = cs.CameraServer()

    src = cs.CvSource("server", cs.VideoMode.PixelFormat.kMJPEG, WIDTH, HEIGHT, 70)
    cserver.startAutomaticCapture(camera=src)
    while True:
        frames = pipe.wait_for_frames()
        depth = frames.get_depth_frame()
        color = frames.get_color_frame()
        if not (color and depth):
            continue

        img = np.asarray(color.get_data())
        grip_pipe.process(img)

        table.putNumber('depth', dist)
        src.putFrame(img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("leave")
            break

except Exception as e:
    reboot(e)
finally:
    pipe.stop()
    cv2.destroyAllWindows()
    file.close()
    # Method calls agaisnt librealsense objects may throw exceptions of type pylibrs.error
    # print("pylibrs.error was thrown when calling %s(%s):\n" % (e.get_failed_function(), e.get_failed_args()))
    # print("    %s\n", e.what())
    exit(1)
