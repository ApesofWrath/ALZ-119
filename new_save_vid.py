import numpy as np
import cv2
import grip
import pyrealsense2 as rs

grip_pipeline = grip.HatchPipeline()
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

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
    out.write(depth_colormap)
#out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

    cv2.imshow('frame',depth_colormap)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    else:
        break

# Release everything if job is finished
pipeline.stop()
out.release()
cv2.destroyAllWindows()
