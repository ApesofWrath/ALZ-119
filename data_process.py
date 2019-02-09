# TODO: Add in more checks for rectangles
	# tune tape_aspect_ratio error to be more robust (probably needs to be increased)
	# Add functionality to sort vision targets on Cargo bay (most centered, other attributes to pick the right 2)
		# Check to make sure that they're both facing inwards
		# take the targets that are closest to the middle
	# Make self.img global (too many functions need it)

import cv2, numpy, math

class DataProcess:
	def __init__(self, pipe, h_fov, f_length, sensor_width, width, height):
		self.pipe = pipe # the object from the grip file
		self.H_FOV = h_fov # Horizontal View of View
		self.F_LENGTH = f_length # Focal length
		self.SENSOR_WIDTH = sensor_width # Width of the sensor
		self.WIDTH = width # in pixels
		self.HEIGHT = height # in pixels
		self.img = None

		# constants that depend on the specs of the vision tape
		self.ASPECT_RATIO_ERROR = 0.25 # correlates to 0.5 inches total for room (needs tuning)
		self.TAPE_ASPECT_RATIO = 0.36363 # small / big (2 inches / 5.5 inches)

		# eyes on the prize point
		self.cx = 0.0
		self.cy = 0.0
		self.angle = 0.0

	# returns the linear horizontal angle from the center of the screen to x, y
	def approximateAngle(self, x, y):
		horizantal_conversion = H_FOV / WIDTH
		return (x - WIDTH / 2) * horizantal_conversion

	# returns the actual angle from the center of the screen to x, y
	def actualAngle(self, x, y):
		pixel_width_percentage = (x - self.WIDTH / 2) / (self.WIDTH / 2)
		return math.degrees(math.atan(pixel_width_percentage * self.SENSOR_WIDTH * 0.5 / self.F_LENGTH))

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
	def calcAngles(self, box1, box2, offset_x, offset_y):
		cx1, cy1 = self.getReferencePoint(box1)
		cx2, cy2  = self.getReferencePoint(box2)
		self.cx = (cx1 + cx2) / 2 + offset_x
		self.cy = (cy1 + cy2) / 2 + offset_y

		#Draw the point on the image
		cv2.rectangle(self.img, (int(self.cx), int(self.cy)), (int(self.cx + 10), int(self.cy + 10)),  (100, 50, 50), 10)

		return self.actualAngle(self.cx, self.cy)
		# For testing
			#print ("Approx Angle: " + str(approximateAngle(cx, cy)))
			#print ("Actual Angle: " + str(actualAngle(cx, cy)))

	#incorporate into getRefPoint() return value
	def __distance__(self, x1, y1, x2, y2):
		return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

	# Aspect ratio is small/big (should be 2 inches / 5.5 inches if perfect)
	def getAspectRatio(self, box):
		p1, p2, p3 = box[0], box[1], box[2]

		# Can do this because points are consecutive in cw or ccw order
		d1 = self.__distance__(p1[0], p1[1], p2[0], p2[1])
		d2 = self.__distance__(p2[0], p2[1], p3[0], p3[1])

		# figure out which side is the smaller side and
		if d1 > d2:
			return d2 / d1

		return d1 / d2

	# returns a bounded rectangle from contour_data[max_index] and draws it to @param: self.img
	def generateRect(self, contour_data, max_index):
		rect = cv2.minAreaRect(contour_data[max_index])
		box = cv2.boxPoints(rect)
		box = numpy.int0(box)
		cv2.drawContours(self.img,[box], 0, (100, 50, 50), 10)

		return box

	# remove the current largest area from the array and return the next largest area
	def nextLargestArea(self, areas, contour_data, current_max):
			# remove the first greatest area and find the second
			areas.pop(current_max)
			contour_data.pop(current_max)
			max_index = numpy.argmax(areas)

			return max_index

	def oneVisionTapeDetected(self, box):
		p1, p2, p3 = box[0], box[1], box[2]
		cx, cy = self.getReferencePoint(box)

		# Can do this because points are consecutive in cw or ccw order
		d1 = self.__distance__(p1[0], p1[1], p2[0], p2[1])
		d2 = self.__distance__(p2[0], p2[1], p3[0], p3[1])
		#print("d1: " + str(d1) + " d2: " + str(d2))

		# TODO: simplify to go off of negative vs. positive angles instead of slope (need to know which is above/below to get sign right?)
		slope = 0.0
		distance_pixels = 0.0
		angle = math.radians(14.5)
		offset_x = 0.0
		offset_y = 0.0

		distance_pixels = min(d1, d2)

		if p2[0] == p1[0] or p3[0] == p2[0]: # fix divide by zero error
			slope = (float(p2[1]) - p1[1]) / 0.01
			angle = 0
		elif d1 > d2:
			slope = (float(p2[1]) - p1[1]) / (float(p2[0]) - p1[0])
			angle = float(math.pi / 2 - math.atan(float(abs(p2[1] - p1[1])) / abs(p2[0] - p1[0])))
		else:
			slope = (float(p3[1]) - p2[1]) / (float(p3[0]) - p2[0])
			angle = float(math.pi / 2 - math.atan(float(abs(p3[1] - p2[1])) / abs(p3[0] - p2[0])))


		slope *= -1 # reflect about the x axis to convert to more sensical coordinate system (form upper left coordinates)

		EOP_default = (4 + math.cos(14.5)) * distance_pixels / 2


		offset_x = EOP_default * math.cos(angle - math.radians(14.5))
		offset_y = EOP_default * math.sin(angle - math.radians(14.5))

		if slope < 0: # left leaning (right vision target)
			offset_x *= -1

		#print("p1: " + str(p1) + " p2: " + str(p2) + " p3: " + str(p3) + " slope: " + str(slope) )

		self.angle = self.calcAngles(box, box, offset_x, offset_y)

	def convertToRects(self, contour_data):
		rects = []
		for i in range(0, len(contour_data)):
			rects.append(self.generateRect(contour_data, i))
		return rects

	def getGoalRectangles(self, contour_data):
		# index1, index2 = len(contour_data) / 2, len(contour_data) / 2 + 1
		# contour_data = [contour_data[index1], contour_data[index2]]
		# get the centers of the contours
		rects = self.convertToRects(contour_data)
		# print(contour_data)
		distance_to_center = []
		for rect in rects:
			x_av = 0.0
			for i in range (0, len(rect)):
				x_av += rect[i][0]
			distance_to_center.append(abs(x_av / 4 - 640 / 2))
		# print("ALL: " + str(distance_to_center))

		distance_to_center_sorted = sorted(distance_to_center)
		# print("SORTED: " + str(centers_sorted))
		index1, index2 = distance_to_center.index(distance_to_center_sorted[0]), distance_to_center.index(distance_to_center_sorted[1])
		# print("PICKED: " + str(index1) + ", " + str(index2))
		contour_data = [contour_data[index1], contour_data[index2]]

		return contour_data

	def update(self, im):
		self.pipe.process(im)
		self.img = im
		contour_data = self.pipe.find_contours_output
		# print(contour_data)
		# future boxes for the bounded rectangles
		rect1 = None
		rect2 = None
		# print("about to draw rect")
		if len(contour_data) > 2:
			contour_data = self.getGoalRectangles(contour_data)
		if len(contour_data) >= 1:
			# Get the rectangle/contour with the largest area
			areas = [cv2.contourArea(c) for c in contour_data]
			max_index = numpy.argmax(areas)

			rect1 = self.generateRect(contour_data, max_index)

		# Make sure there are 2 rectangles detected
		if len(contour_data) == 2:
			max_index = self.nextLargestArea(areas, contour_data, max_index)
			rect2 = self.generateRect(contour_data, max_index)
			self.angle = self.calcAngles(rect1, rect2, 0, 0)

		elif len(contour_data) == 1:
			# TODO: check that the smaller side is the one on the top
			if abs(self.getAspectRatio(rect1) - self.TAPE_ASPECT_RATIO) < self.ASPECT_RATIO_ERROR: # +-  0.5 inches for either edge
				self.oneVisionTapeDetected(rect1)
			else: #probably won't be applicable, and might cause more hassle than good, but we can deside when testing
				# one big blob of both of the vision targets,
				# get the eyes on the prize point for it instead of centers of other things
				self.angle = self.calcAngles(rect1, rect1, 0, 0)

		cv2.imshow("CONTOUR",  self.img)