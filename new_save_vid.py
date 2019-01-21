import numpy as np
import cv2
import grip
import pyrealsense2 as rs

grip_pipeline = grip.HatchPipeline()

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
pipeline.start(config)

d = 0

while True:
    frames = pipeline.wait_for_frames()
    depth = frames.get_depth_frame()
    if not depth:
        continue

    depth_image = np.asanyarray(depth.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    grip_pipeline.process(depth_colormap)

    filename = "images/file_%d.jpg"%d
    cv2.imwrite(filename, grip_pipeline.hsl_threshold_output)
    d+=1

    cv2.imshow('frame',  grip_pipeline.hsl_threshold_output) #
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release everything if job is finished
pipeline.stop()
cv2.destroyAllWindows()
