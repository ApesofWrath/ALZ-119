# import datetime
#
# import grip, cv2, numpy
# import time
#
# cap = cv2.VideoCapture(0)
# pipe = grip.GreenProfile()
#
# # print(pipe.hsl_threshold_output)
#
# if not cap.isOpened():
#     cap.open()
#
# ret, im = cap.read()
# print(ret)
# pipe.process(im)
# img = pipe.blur_output
# contour_data = pipe.find_contours_output
#
# areas = [cv2.contourArea(c) for c in contour_data]
# print(areas)
# # max_index = numpy.argmax(areas)
# # cnt = contour_data[max_index]
# # print(cv2.boundingRect(cnt))
#
# slpt = 1/30
# x = 1
# c = 1
# while 1:
#     ret, im = cap.read()
#     pipe.process(im)
#     img = pipe.cv_erode_output
#     if pipe.find_contours_output != []:
#         contour_data = pipe.find_contours_output
#
#         print(contour_data)
#
#     # areas = [cv2.contourArea(c) for c in contour_data]
#     # max_index = numpy.argmax(areas)
#     # cnt = contour_data[max_index]
#         cnt = contour_data[0]
#         x, y, w, h = cv2.boundingRect(cnt)
#         img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#
#     img = cv2.rectangle(img, (100, 100), (200, 200), (0, 255, 0), 2, cv2.FILLED)
#     cv2.imshow("CONTOUR",  img)
#     time.sleep(slpt)
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
#
import numpy as np
import cv2, datetime

c, x = 1, 10

cap = cv2.VideoCapture(0)
st = datetime.datetime.now()
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.flip(frame,c)

    # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if datetime.datetime.now().second - st.second < 10:
        c = 1

    x -= 1

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()