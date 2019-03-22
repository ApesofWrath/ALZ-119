import numpy as np
import cv2

vid = cv2.VideoCapture("output.avi")
d = 0
ret, frame = vid.read()

while ret:
    ret, frame = vid.read()
    filename = "images/file_%d.jpg"%d
    cv2.imwrite(filename, frame)
    d+=1
