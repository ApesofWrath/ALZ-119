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
	return (x - WIDTH / 2) * horizantal_conversion

def actualAngle(x, y):
	# math.degrees(atan(o/a))
	print("X: " + str(x))
	pixel_width_percentage = (x - WIDTH / 2) / (WIDTH / 2)
	return math.degrees(math.atan(pixel_width_percentage * SENSOR_WIDTH / F_LENGTH))

def getCenters(box):
	top_right = box[0]
	top_left = box[1]
	bottom_left = box[2]
	bottom_right = box[3]
	#print ("TOP_LEFT: " + str(top_left) + "TOP RIGHT: " + str(top_right) + " BOTTOM_RIGHT: " + str(bottom_right) + " BOTTOM_LEFT: " + str(bottom_left))

	cx = (top_left[0] + top_right[0] + bottom_right[0] + bottom_left[0]) / 4
	cy = (top_left[1] + top_right[1] + bottom_right[1] + bottom_left[1]) / 4
	return cx, cy

def calcAngles(box1 ,box2):
	cx1, cy1 = getCenters(box1)
	cx2, cy2  = getCenters(box2)
	cx = (cx1 + cx2) / 2
	cy = (cy1 + cy2) / 2
	
	print ("Approx Angle: " + str(approximateAngle(cx, cy)))
	print ("Actual Angle: " + str(actualAngle(cx, cy)))

while 1:
	ret, im = cap.read()
	pipe.process(im)
	img = pipe.cv_erode_output
	contour_data = pipe.find_contours_output
	
	
	# For actual implementation, draw the rectangles with the 2 biggest areas instead of the single one
	if len(contour_data) >= 2:
		
		areas = [cv2.contourArea(c) for c in contour_data]
		max_index = numpy.argmax(areas)
		
		first_rect = contour_data[max_index]
		areas.pop(max_index)
		contour_data.pop(max_index)
		max_index = numpy.argmax(areas)
		second_rect = contour_data[max_index]
		
		rect = cv2.minAreaRect(first_rect)
		box1 = cv2.boxPoints(rect)
		box1 = numpy.int0(box1)
		cv2.drawContours(img,[box1], 0, (100, 50, 50), 10)
		
		rect = cv2.minAreaRect(second_rect)
		box2 = cv2.boxPoints(rect)
		box2 = numpy.int0(box2)
		cv2.drawContours(img,[box2], 0, (100, 50, 50), 10)
		
		calcAngles(box1, box2)

	cv2.imshow("CONTOUR",  img)
	time.sleep(1/30)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break