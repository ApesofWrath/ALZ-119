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
	# SENSOR_WIDTH = 2.804mm (calculated with focal_length * tan(FOV/2)

cap = cv2.VideoCapture(0)
pipe = grip.GreenProfile()

WIDTH = 1920.0
HEIGHT = 1080.0
H_FOV = 70.42
F_LENGTH = 0.00367 # in meters
SENSOR_WIDTH = 0.002804 # in meters

dp = dataprocess.DataProcess(cap, pipe, H_FOV, F_LENGTH, SENSOR_WIDTH, WIDTH, HEIGHT)

def main():
	while True:
		dp.update()
		cx = dp.cx
		cy = dp.cy
	
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

if __name__ == "__main__": 	
	main()
	sys.exit(0)