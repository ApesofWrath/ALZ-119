import datetime

import grip, cv2, numpy
import time
import math

cap = cv2.VideoCapture(1)
pipe = grip.GreenProfile()

WIDTH = 1920.0
HEIGHT = 1080.0
H_FOV = 70.42
F_LENGTH = 0.00367 # in meters
SENSOR_WIDTH = 0.002804

#print(pipe.hsv_threshold_output)

if not cap.isOpened():
	cap.open()

# For the logitech web cam (https://support.logitech.com/en_us/product/hd-pro-webcam-c920/specs)
	# diagonal FOV = 78 degrees
		# Horizontal FOV 70.42 degrees
		# Vertical FOV 43.3 degrees
	# FOCAL LENGTH; 3.67mm
	# FRAME RATE: 30fps
	# DIMENSIONS: 1920x1080

def approximateAngle(x, y):
	horizantal_conversion = H_FOV / WIDTH
	return (cx - WIDTH / 2) * horizantal_conversion

def actualAngle(x, y):
	# math.degrees(atan(o/a))
	print("X: " + str(x))
	pixel_width_percentage = (x - WIDTH / 2) / (WIDTH / 2)
	return math.degrees(math.atan(pixel_width_percentage * SENSOR_WIDTH / F_LENGTH))

while 1:
	ret, im = cap.read()
	pipe.process(im)
	img = pipe.cv_erode_output
	contour_data = pipe.find_contours_output
	
	# For actual implementation, draw the rectangles with the 2 biggest areas instead of the single one
	if len(contour_data) > 0:
		areas = [cv2.contourArea(c) for c in contour_data]
		max_index = numpy.argmax(areas)
		cnt = contour_data[max_index]
		x, y, w, h = cv2.boundingRect(cnt) 
		cv2.rectangle(img, (x, y), (x + w, y + h), (100, 50, 50), 5)
		
		cx = (2 * x + w) / 2
		cy = (2 * y + h) / 2
		print ("Approx Angle: " + str(approximateAngle(cx, cy)))
		print ("Actual Angle: " + str(actualAngle(cx, cy)))
		

	cv2.imshow("CONTOUR",  img)
	time.sleep(1/30)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
