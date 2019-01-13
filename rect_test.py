import numpy as np
import cv2
img = cv2.imread('picture.png', cv2.IMREAD_COLOR)
cv2.rectangle(img,(15,25),(200,150),(0,0,255),2)
cv2.imshow('test', img)
cv2.waitKey(0)
cv2.destroyAllWindows()