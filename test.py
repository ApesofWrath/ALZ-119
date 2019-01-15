import datetime

import grip, cv2, numpy
import time
import math

# For the logitech web cam (https://support.logitech.com/en_us/product/hd-pro-webcam-c920/specs)
	# diagonal FOV = 78 degrees
		# Horizontal FOV 70.42 degrees
		# Vertical FOV 43.3 degrees
	# FOCAL LENGTH; 3.67mm
	# FRAME RATE: 30fps
	# DIMENSIONS: 1920x1080
	# SENSOR_WIDTH = 2.804mm (calculated with focal_length * tan(FOV/2)

cap = cv2.VideoCapture(1)
pipe = grip.GreenProfile()

WIDTH = 1920.0
HEIGHT = 1080.0
H_FOV = 70.42
F_LENGTH = 0.00367 # in meters
SENSOR_WIDTH = 0.002804 # in meters


if not cap.isOpened():
	cap.open()

def approximateAngle(x, y):
	horizantal_conversion = H_FOV / WIDTH
	return (x - WIDTH / 2) * horizantal_conversion

def actualAngle(x, y):
	pixel_width_percentage = (x - WIDTH / 2) / (WIDTH / 2)
	return math.degrees(math.atan(pixel_width_percentage * SENSOR_WIDTH / F_LENGTH))

def getReferencePoint(box):
	# Find the two greatest lowest, from top left >:( y values and take the average
	# this is the center highest reliable point to use for output
	greatest_y = [box[0], box[1]]
	for i in range(2, 4):
		if box[i][1] < greatest_y[0][1]:
			greatest_y[0] = box[i]
		elif box[i][1] < greatest_y[1][1]:
			greatest_y[1] = box[i];
 
 	cx = (greatest_y[0][0] + greatest_y[1][0]) / 2
 	cy = (greatest_y[0][1] + greatest_y[1][1]) / 2

	return cx, cy

# Rewrite function for non-testing purposes
def calcAngles(box1 ,box2, img):
	cx1, cy1 = getReferencePoint(box1)
	cx2, cy2  = getReferencePoint(box2)
	cx = (cx1 + cx2) / 2
	cy = (cy1 + cy2) / 2
	
	#display the point
	cv2.rectangle(img, (cx, cy), (cx + 10, cy + 10),  (100, 50, 50), 10)
	
	#print the angles)
	print ("Approx Angle: " + str(approximateAngle(cx, cy)))
	print ("Actual Angle: " + str(actualAngle(cx, cy)))

while 1:
	ret, im = cap.read()
	pipe.process(im)
	img = pipe.cv_erode_output
	contour_data = pipe.find_contours_output
	
	#M Make sure we see 
	if len(contour_data) >= 2:
		# Get the rectangle/contour with the largest area
		areas = [cv2.contourArea(c) for c in contour_data]
		max_index = numpy.argmax(areas)
		first_rect = contour_data[max_index]
		
		# remove the first greatest area and find the second
		areas.pop(max_index)
		contour_data.pop(max_index)
		max_index = numpy.argmax(areas)
		second_rect = contour_data[max_index]
		
		# Draw the first rectangle
		rect = cv2.minAreaRect(first_rect)
		box1 = cv2.boxPoints(rect)
		box1 = numpy.int0(box1)
		cv2.drawContours(img,[box1], 0, (100, 50, 50), 10)
		
		# Draw the second rectangle
		rect = cv2.minAreaRect(second_rect)
		box2 = cv2.boxPoints(rect)
		box2 = numpy.int0(box2)
		cv2.drawContours(img,[box2], 0, (100, 50, 50), 10)
		
		calcAngles(box1, box2, img)

	cv2.imshow("CONTOUR",  img)
	time.sleep(1/30)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break