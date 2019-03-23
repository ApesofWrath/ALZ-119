import cv2, numpy
import math
import sys
import pyrealsense2 as rs
import time

pipeline = rs.pipeline()

#Create a config and configure the pipeline to stream
#  different resolutions of color and depth streams
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

cap = cv2.VideoCapture(2)

if not cap.isOpened():
    cap.open()

def main():
    while True:
        ret, im = cap.read()

        cv2.imshow("window", im)
        if cv2.waitKey(50) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()
    sys.exit(0)
