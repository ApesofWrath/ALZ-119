import cv2, numpy, math


class HatchDetection:
	def __init__(self, pipe, width, height):
		self.pipe = pipe  # the object from the grip file
		self.img = None
		self.is_hatch = False

	def update(self, im):
		self.pipe.process(im)
		self.img = im
		contour_data = self.pipe.find_contours_output

		if len(contour_data) >= 1:
			self.is_hatch = True

		cv2.imshow("CONTOUR", self.img)



