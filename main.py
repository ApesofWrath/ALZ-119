import yellowprofile, cv2, numpy, hatchdetection
import math
import sys

cap = cv2.VideoCapture(1)
# pipe = grip.GripPipeline()
pipe = yellowprofile.YellowProfile()
detection = hatchdetection.HatchDetection(pipe)

if not cap.isOpened():
    cap.open()

def main():
    while True:
        ret, im = cap.read()
        detection.update(im)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()
    sys.exit(0)
