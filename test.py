import grip, cv2, numpy, dataprocess
import math
import sys

# For the logitech web cam (https://support.logitech.com/en_us/product/hd-pro-webcam-c920/specs)
	# diagonal FOV = 78 degrees
		# Horizontal FOV 70.42 degrees
		# Vertical FOV 43.3 degrees
	# FOCAL LENGTH; 3.67mm
	# FRAME RATE: 30fps
	# DIMENSIONS: 1920x1080
	# SENSOR_WIDTH = 5.608mm (calculated with focal_length * tan(FOV/2) * 2)

cap = cv2.VideoCapture(1)

if not cap.isOpened():
	cap.open()

pipe = grip.GreenProfile()

WIDTH = 1920.0
HEIGHT = 1080.0
H_FOV = 70.42
F_LENGTH = 0.00367 # in meters
SENSOR_WIDTH = 0.005608 # in meters

dp = dataprocess.DataProcess(pipe, H_FOV, F_LENGTH, SENSOR_WIDTH, WIDTH, HEIGHT)

def main():
	while True:
		ret, im = cap.read()
		dp.update(im)
		cx = dp.cx
		cy = dp.cy
	
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

if __name__ == "__main__": 	
	main()
	sys.exit(0)