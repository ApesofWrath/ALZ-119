import datetime

import grip, cv2, numpy
import time

cap = cv2.VideoCapture(0)
pipe = grip.GreenProfile()

#print(pipe.hsv_threshold_output)

if not cap.isOpened():
	cap.open()

# ret, im = cap.read()
# print(ret)
# pipe.process(im)
# img = pipe.blur_output

while 1:
	ret, im = cap.read()
	pipe.process(im)
	img = pipe.cv_erode_output
	contour_data = pipe.find_contours_output
	
# 	areas = [cv2.contourArea(c) for c in contour_data]
# 	max_index = numpy.argmax(areas)
# 	cnt = contour_data[max_index]
# 	x, y, w, h = cv2.boundingRect(cnt) 
# 	cv2.rectangle(img, (x, y), (x + w, y + h), (100, 50, 50), 2)
	
	for i in range(0, len(contour_data)):
		cv2.rectangle(img, (100, 100), (200, 200), (255, 0, 0), 2, cv2.FILLED)
		x, y, w, h = cv2.boundingRect(contour_data[i])
		cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 10)
		print("ITERATION: " + str(i))
 		print("X: " + str(x) + " Y: " + str(y) + " W: " + str(w) + " H: " + str(h))

	cv2.imshow("CONTOUR",  img)
	time.sleep(1/30)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

