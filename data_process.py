# TODO:
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
		self.ASPECT_RATIO_ERROR = 0.15 # correlates to 0.5 inches total for room (needs tuning)
		self.TAPE_ASPECT_RATIO = 0.36363 # small / big (2 inches / 5.5 inches)
		self.MAX_HEIGHT_TAPE = 200 # the highest (lowest since top of screen) that the tape can reasonably be in pixels

		# eyes on the prize point
		self.cx = 0.0
		self.cy = 0.0
		self.angle = 0.0

		# for the distance calculations in stream.py
		self.rect1 = []
		self.rect2 = []

		# For Getting the depth with missing middle
		self.x1 = 0.0
		self.y1 = 0.0
		self.x2 = 0.0
		self.y2 = 0.0

	# returns the median of the list excluding outliers
	def normalizeData(self, list):
		list.sort()
		# print(list)
		length = len(list)
		Q1 = list[int(length / 4)]
		Q3 = list[int(3 / 4 * length)]
		IQR = Q3 - Q1

		for i in range(0, length):
			if i >= len(list): # range is not continually reechecked, need to have bound check
				break
			if list[i] > 1.5 * IQR + Q3 or list[i] < Q1 - 1.5 * IQR: # remove outliers
				list.pop(i)
				i -= 1

		return numpy.median(list)

	def getCenterDistance(self, distA, ax, ay, distB, bx, by):
		A = self.actualAngle(ax, ay)
		B = self.actualAngle(bx, by)
		Bout = 90 - B
		Aout = 90 - A

		# real unit points, bx, by, etc. are pixel coordiantes
		b_x = distB * math.cos(math.radians(Bout))
		b_y = distB * math.sin(math.radians(Bout))
		a_x = distA * math.cos(math.radians(Aout))
		a_y = distA * math.sin(math.radians(Aout))

		mid_x = (b_x + a_x) / 2
		mid_y = (b_y + a_y) / 2

		return (mid_x ** 2 + mid_y ** 2) ** (0.5) # beacuse 0,0 is camera



	def drawPoint(self, x, y):
		#Draw the point on the image
		if self.img is not None:
			cv2.rectangle(self.img, (int(x), int(y)), (int(x + 10), int(y + 10)),  (100, 50, 50), 10)
		else:
			print("self.img is None")
		# cv2.imshow("CONTOUR",  self.img)
	# returns the linear horizontal angle from the center of the screen to x, y
	def approximateAngle(self, x, y):
		horizantal_conversion = self.H_FOV / self.WIDTH
		return (x - self.WIDTH / 2) * horizantal_conversion

	# returns the actual angle from the center of the screen to x, y
	def actualAngle(self, x, y):
		pixel_width_percentage = float(x - self.WIDTH / 2) / float(self.WIDTH / 2)
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

	def getMidPoint(self, box):
		totalx = 0
		totaly = 0
		for i in range(0, 4):
			totalx += int(box[i][0])
			totaly += int(box[i][1])

		return totalx / 4.0, totaly / 4.0

	def getRect1(self):
		# print(self.rect1)
		return self.rect1

	def getRect2(self):
		# print(self.rect2)
		return self.rect2


	# @param: 2 rectangles and the offset for 1 tape detected
	def calcAngles(self, box1, box2, offset_x, offset_y):
		cx1, cy1 = self.getReferencePoint(box1)
		cx2, cy2  = self.getReferencePoint(box2)
		self.cx = (cx1 + cx2) / 2 + offset_x
		self.cy = (cy1 + cy2) / 2 + offset_y

		self.drawPoint(self.cx, self.cy)


		return self.actualAngle(self.cx, self.cy)
		# For testing
			#print ("Approx Angle: " + str(approximateAngle(cx, cy)))
			#print ("Actual Angle: " + str(actualAngle(cx, cy)))

	#incorporate into getReferencePoint() return value
	def distance(self, x1, y1, x2, y2):
		return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

	# Aspect ratio is horizontal side / vertical side (should be 2 inches / 5.5 inches if perfect)
	def getAspectRatio(self, box):
		p1, p2, p3 = box[0], box[1], box[2]

		# Can do this because points are consecutive in cw or ccw order
		d1 = self.distance(p1[0], p1[1], p2[0], p2[1])
		d2 = self.distance(p2[0], p2[1], p3[0], p3[1])

		if d1 == 0:
			d1 = 0.001
		if d2 == 0:
			d2 = 0.001

		# horizontal side / vertical side
		if p1[1] - p2[1] > p2[1] - p3[1]: # if the y comp of dist1 is greater than the y comp of dist2
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

	def getSlope(self, box):
		p1, p2, p3 = box[0], box[1], box[2]
		d1 = self.distance(p1[0], p1[1], p2[0], p2[1])
		d2 = self.distance(p2[0], p2[1], p3[0], p3[1])

		# TODO: simplify to go off of negative vs. positive angles instead of slope (need to know which is above/below to get sign right?)
		slope = 0.0

		# TODO: fix the /0 check so that it works with both sets of points, not just 1 & 2
		if p2[0] == p1[0] or p3[0] == p2[0]: # fix divide by zero error
			slope = (float(p2[1]) - p1[1]) / 0.01
		elif d1 > d2:
			slope = (float(p2[1]) - p1[1]) / (float(p2[0]) - p1[0])
		else:
			slope = (float(p3[1]) - p2[1]) / (float(p3[0]) - p2[0])

		slope *= -1 # reflect across the x axis to convert to more sensical coordinate system (form upper left coordinates)

		return slope

	def oneVisionTapeDetected(self, box):
		p1, p2, p3 = box[0], box[1], box[2]
		cx, cy = self.getReferencePoint(box)

		# Can do this because points are consecutive in cw or ccw order
		d1 = self.distance(p1[0], p1[1], p2[0], p2[1])
		d2 = self.distance(p2[0], p2[1], p3[0], p3[1])

		# TODO: simplify to go off of negative vs. positive angles instead of slope (need to know which is above/below to get sign right?)
		slope = 0.0
		distance_pixels = 0.0
		angle = math.radians(14.5)
		offset_x = 0.0
		offset_y = 0.0

		distance_pixels = min(d1, d2)
		slope = self.getSlope(box)

		# TODO: fix the /0 check so that it works with both sets of points, not just 1 & 2
		if p2[0] == p1[0] or p3[0] == p2[0]: # fix divide by zero error
			angle = 0
		elif d1 > d2:
			angle = float(math.pi / 2 - math.atan(float(abs(p2[1] - p1[1])) / abs(p2[0] - p1[0])))
		else:
			angle = float(math.pi / 2 - math.atan(float(abs(p3[1] - p2[1])) / abs(p3[0] - p2[0])))

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

	# sort by biggest first, then by distance to center, always verify pairs with slopes
	def getGoalRectangles(self, contour_data):
		rects = self.convertToRects(contour_data)

		# the biggest ones
		areas = [cv2.contourArea(c) for c in contour_data]
		original_areas = areas.copy()
		manipulating_contour_data = contour_data.copy()

		index1 = numpy.argmax(areas)

		next = self.nextLargestArea(areas, manipulating_contour_data, index1)
		index2 = original_areas.index(areas[next])

		while len(areas) > 1 and len(contour_data) > 1:
			if self.getSlope(rects[index1]) * self.getSlope(rects[index2]) < 0: # if they have different signs
				contour_data = [contour_data[index1], contour_data[index2]]
				return contour_data

			next = self.nextLargestArea(areas, manipulating_contour_data, next)
			index2 = original_areas.index(areas[next])

		# the clossest to the center
		distance_to_center = []
		for rect in rects:
			x_av = 0.0
			for i in range (0, len(rect)):
				x_av += rect[i][0]
			distance_to_center.append(abs(x_av / 4 - 640 / 2))
		# print("ALL: " + str(distance_to_center))

		distance_to_center_sorted = sorted(distance_to_center)

		index1, index2 = distance_to_center.index(distance_to_center_sorted[0]), distance_to_center.index(distance_to_center_sorted[1])

		contour_data = [contour_data[index1], contour_data[index2]]

		return contour_data

	def filterContours(self, contour_data):
		rects = self.convertToRects(contour_data)
		# print("size contour_data: " + str(len(contour_data)))
		i = 0
		for j in range(0, len(rects)): # can't be j beacuse python is stupid
			if abs(self.getAspectRatio(rects[i]) - self.TAPE_ASPECT_RATIO) > self.ASPECT_RATIO_ERROR or \
			rects[i][0][1] < self.MAX_HEIGHT_TAPE: #
				contour_data.pop(i)
				rects.pop(i)
				i -= 1
			i += 1
		# print(len(contour_data))
		return contour_data

	def isTapeDetected(self):
		return len(self.pipe.find_contours_output) != -1

	def update(self, im):
		self.pipe.process(im)
		self.img = im
		contour_data = self.pipe.find_contours_output

		# future boxes for the bounded rectangles
		rect1 = None
		rect2 = None

		contour_data = self.filterContours(contour_data)

		if contour_data is not None:
			# print("about to draw rect")
			if len(contour_data) > 2:
				contour_data = self.getGoalRectangles(contour_data)

			if len(contour_data) >= 1:
				# Get the rectangle/contour with the largest area
				areas = [cv2.contourArea(c) for c in contour_data]
				max_index = numpy.argmax(areas)

				rect1 = self.generateRect(contour_data, max_index)
				self.x1, self.y1 = self.getMidPoint(rect1)
				cv2.rectangle(self.img, (int(self.x1), int(self.y1)), (int(self.x1 + 10), int(self.y1 + 10)),  (100, 50, 50), 10)


			# Make sure there are 2 rectangles detected
			if len(contour_data) == 2:
				max_index = self.nextLargestArea(areas, contour_data, max_index)
				rect2 = self.generateRect(contour_data, max_index)
				self.x2, self.y2 = self.getMidPoint(rect2)
				cv2.rectangle(self.img, (int(self.x2), int(self.y2)), (int(self.x2 + 10), int(self.y2 + 10)),  (100, 50, 50), 10)

				self.angle = self.calcAngles(rect1, rect2, 0, 0)


			elif len(contour_data) == 1:
				# TODO: check that the smaller side is the one on the top
				if abs(self.getAspectRatio(rect1) - self.TAPE_ASPECT_RATIO) < self.ASPECT_RATIO_ERROR: # +-  0.5 inches for either edge
					self.oneVisionTapeDetected(rect1)
				else: #probably won't be applicable, and might cause more hassle than good, but we can decide when testing
					# one big blob of both of the vision targets,
					# get the eyes on the prize point for it instead of centers of other things
					self.angle = self.calcAngles(rect1, rect1, 0, 0)
			# print("cx: " + str(self.cx) + " cy: " + str(self.cy) + "\n")
			# print("appx angle: " + str(self.approximateAngle(self.cx, self.cy)))
		self.rect1 = rect1
		self.rect2 = rect2
		# cv2.imshow("CONTOUR",  self.img)
