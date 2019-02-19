import cv2, numpy, math


class HatchDetection:
	def __init__(self, pipe):
		self.pipe = pipe  # the object from the grip file
		self.img = None
		self.is_hatch = False

	def generate_num_contours(self, contour_data):
		counter = 0
		for contour in contour_data:
			if cv2.contourArea(contour) < 200: # <--play with this value to change the tollerance
				counter += 1
		return counter

	def update(self, im):
		self.pipe.process(im)
		self.img = self.pipe.hsv_threshold_output

		contour_data = self.pipe.filter_contours_output

		if len(contour_data) > 0: # <--play with this value to change the tollerance
			self.is_hatch = True
		else:
			self.is_hatch = False

		print(self.is_hatch)
		cv2.imshow("CONTOUR", self.img)
