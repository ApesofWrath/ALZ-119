import pyrealsense2 as rs
import cv2
import numpy as np
import matplotlib.pyplot as plt
from networktables import NetworkTables

#NetworkTables.initialize(server='10.6.68.2')

try:
    # Create a context object. This object owns the handles to all connected realsense devices
    pipeline = rs.pipeline()
    pipeline.start()

    # This call waits until a new coherent set of frames is available on a device
    # Calls to get_frame_data(...) and get_frame_timestamp(...) on a device will return stable values until wait_for_frames(...) is called
    while True:
        frames = pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        color = frames.get_color_frame()
        pipeline.stop()
        if not depth:
            continue
        break
    dist = depth.get_distance(640, 360)
    print(dist)
    rgb = np.asanyarray(color.get_data())
    plt.rcParams["axes.grid"] = False
    plt.rcParams['figure.figsize'] = [12, 6]
    while True:
        plt.imshow(rgb)
    table = NetworkTables.getTable('SmartDashboard')
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
