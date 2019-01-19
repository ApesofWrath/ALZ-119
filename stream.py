import pyrealsense2 as rs
from networktables import NetworkTables
import threading
import numpy as np
import cv2

#will not need to pass anything but a bool to network Tables

neural network
no COLOr vision
vision with depth stream
height of cam must be very specific
lighting change
disco ball error
grip process the depth stream color



cond = threading.Condition()
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
    # Create a context object. This object owns the handles to all connected realsense devices
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    pipeline.start(config)

    # This call waits until a new coherent set of frames is available on a device
    # Calls to get_frame_data(...) and get_frame_timestamp(...) on a device will return stable values until wait_for_frames(...) is called
    while True:
        frames = pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        if not depth:
            continue
        depth_image = np.asanyarray(depth.get_data())
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', depth_colormap)
        cv2.waitKey(1)

finally:
#13.5
#17
#19
    pipeline.stop()
