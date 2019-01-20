import pyrealsense2 as rs
from networktables import NetworkTables
import threading
import numpy as np
import cv2
import grip

grip_pipeline = grip.HatchPipeline()

#will not need to pass anything but a bool to network Tables

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

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    pipeline.start(config)

    while True:
        frames = pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        if not depth:
            continue
        depth_image = np.asanyarray(depth.get_data())
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        grip_pipeline.process(depth_colormap)
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        #show_img = np.asanyarray(grip_pipeline.find_blobs_output)
        cv2.imshow('RealSense', grip_pipeline.hsl_threshold_output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:

    pipeline.stop()
