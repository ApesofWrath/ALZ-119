# TODO: Add in more checks for rectangles
	# If only one rectangle detected, determine if leaning left or right, point from center proportional to size
	# If two but one tiny/ doesn't match the other, make sure they are similar in size
	# If only one big one, take the upper center of it

import cv2, numpy, math

class DataProcess:
	def __init__(self, cap, pipe, h_fov, f_length, sensor_width, width, height):
		self.cap = cap #cap requires compatibility with the opencv in the GRIP file
		self.pipe = pipe # the object from the grip file
		self.H_FOV = h_fov # Horizontal View of View
		self.F_LENGTH = f_length # Focal length
		self.SENSOR_WIDTH = sensor_width # Width of the sensor
		self.WIDTH = width # in pixels
		self.HEIGHT = height # in pixels

		# eyes on the prize point
		self.cx = None
		self.cy = None
		self.angle = None

		if not self.cap.isOpened():
			self.cap.open()

	# returns the linear horizontal angle from the center of the screen to x, y
	def approximateAngle(self, x, y):
		horizantal_conversion = H_FOV / WIDTH
		return (x - WIDTH / 2) * horizantal_conversion

	# returns the actual angle from the center of the screen to x, y
	def actualAngle(self, x, y):
		pixel_width_percentage = (x - self.WIDTH / 2) / (self.WIDTH / 2)
		return math.degrees(math.atan(pixel_width_percentage * self.SENSOR_WIDTH / self.F_LENGTH))

	# return the mid point of the line connecting the average of each of the top two points of rectangle
	def getReferencePoint(self, box):
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

	# @param: 2 rectangles and an image to draw the point on
	def calcAngles(self, box1 ,box2, img):
		cx1, cy1 = self.getReferencePoint(box1)
		cx2, cy2  = self.getReferencePoint(box2)
		self.cx = (cx1 + cx2) / 2
		self.cy = (cy1 + cy2) / 2

		#Draw the point on the image
		cv2.rectangle(img, (self.cx, self.cy), (self.cx + 10, self.cy + 10),  (100, 50, 50), 10)

		return self.actualAngle(self.cx, self.cy)
		# For testing
			#print ("Approx Angle: " + str(approximateAngle(cx, cy)))
			#print ("Actual Angle: " + str(actualAngle(cx, cy)))

	def update(self):
		ret, im = self.cap.read()
		self.pipe.process(im)
		img = self.pipe.cv_erode_output
		contour_data = self.pipe.find_contours_output

		# Make sure there are 2 rectangles detected
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

			self.angle = calcAngles(box1, box2, img)

		cv2.imshow("CONTOUR",  img)
