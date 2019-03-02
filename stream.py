import pyrealsense2 as rs
from networktables import NetworkTables
import threading
import grip
import cv2
import numpy as np
import data_process
import math
import sys
# import cscore as cs UNCOMMENT


cos = 0
zero_error = 0

WIDTH = 640
HEIGHT = 480
H_FOV = 45.6 # 53.13 empirically # need to recalculate if change WIDTH dimension  (line up meter stick and get distance then atan)
F_LENGTH = 0.00193 # in meters
SENSOR_WIDTH = 0.003896 # in meter

grip_pipe = grip.GreenProfile()

cond = threading.Condition() #global for network tables
notified = [False]

dp = data_process.DataProcess(grip_pipe, H_FOV, F_LENGTH, SENSOR_WIDTH, WIDTH, HEIGHT)

def connectionListener(connected, info):

    print(info, '; Connected=%s' % connected)
    with cond:
        notified[0] = True
        cond.notify()

def startNetworkTables():

    NetworkTables.startClientTeam(668)
    NetworkTables.initialize(server='10.6.68.2') #roborio must be on this static ip
    NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

    with cond:
        print("Waiting")
        if not notified[0]:
            cond.wait()

    print("Connected!")

def getValidDepthToPoint(x, y):
    max_distance = 1.5
    dist_center = depth.get_distance(int(x), int(y))

    if dist_center != 0.0 and dist_center <= max_distance:
        return dist_center

    counter = 0
    x_left = x - 5
    x_right = x + 5
    while counter <= 5: # 25 pixel leeway in either direction
        dp.drawPoint(int(x_left), int(y))
        dp.drawPoint(int(x_right), int(y))

        dist_left = depth.get_distance(int(x_left), int(y))
        dist_right = depth.get_distance(int(x_right), int(y))
        # print("d left: " + str(dist_left))
        # print("d right: " + str(dist_right))
        if dist_left < max_distance and dist_left != 0.0:
            print("\n")
            return dist_left
        if dist_right < max_distance and dist_right != 0.0:
            # print("\n")
            return dist_right
        x_right += 5
        x_left -= 5
        counter += 1

    return 0.0

# distance sensor breaks with retreoref tape because of how the distance is calculated (intersection from equation of lines from dual cameras to points in dot map, limited to resolution of dot map)
# @return: the direction that it shifted
def getDistance(x, y, isLeft):
    global dp
    shift = 0.07 # tape length / 2 in meters(2.75 inches)

    if dp.rect1 is None or dp.rect2 is None:
        return 0.0, -1

    if isLeft:
        rx, ry = dp.getReferencePoint(dp.rect1)
    else:
        rx, ry = dp.getReferencePoint(dp.rect2)

    pixel_offset = dp.distance(rx, ry, x, y) # the pixel distane between the 2 reference point and the center of the tape / 2 (see data_process.py for what ref point is)

    # distances to left and right offset to a single tape
    left_dist = getValidDepthToPoint(int(x - pixel_offset), int(y))
    right_dist = getValidDepthToPoint(int(x + pixel_offset), int(y))

    side = "error"

    if right_dist == 0.0 and left_dist == 0.0:
        side = "error"
    elif right_dist == 0.0 or left_dist < right_dist:
        side = "left"
    elif left_dist == 0.0 or right_dist < left_dist:
        side = "right"

    if side == "right":
        if isLeft:
            return right_dist, shift * -1
        return right_dist, shift
    elif side == "left":
        if not isLeft:
            return left_dist, shift * -1
        return left_dist, shift
    elif side == "error":
        return 0.0, -1


# dist1 will always be the leftmost point and dist2 will always be the rightmost
# TODO: does it make sense to return -1 if missed point, or the last valid point
def getOrientationAngle(dist1, dist2, offset_left, offset_right, dist_center, yaw): # has to be here because need depths
    global cos, zero_error
    tape_dist = 0.2985 + offset_left + offset_right # in meters to match other units, 11.75 inches
    # tape_dist /= 2.0

    print("dist2: " + str(dist2))
    print("dist1: " + str(dist1))
    # print("offset left: " + str(offset_left))
    # print("offset right: " + str(offset_right))
    # print("dist_center: " + str(dist_center))
    # print("tape_dist: " + str(tape_dist))
    # print("yaw: " + str(yaw) + "\n")
    # print("zero distance error: "+ str(zero_error))
    # print("cosine error: " + str(cos))

    # Right = +theta
    # Left = -theta
    if dist2 == 0 or dist1 == 0:
        zero_error += 1
        print("DIST 0 ERROR")
        return -1

    angleA = 0.0
    cos_expression = 0.0
    sign = 0.0

    if dist1 > dist2:
        cos_expression = (dist2 * dist2 - tape_dist * tape_dist - dist1 * dist1) / (-2.0 * tape_dist * dist1)
        sign = 1.0
        dp.actualAngle(dp.x1, dp.y1)
    else:
        cos_expression = (dist1 * dist1 - tape_dist * tape_dist - dist2 * dist2) / (-2.0 * tape_dist * dist2)
        sign = -1.0
        dp.actualAngle(dp.x2, dp.y2)

    # check cos domain
    if cos_expression > 1 or cos_expression < -1:
        print("COS DOMAIN ERROR: " + str(cos_expression))
        return -1

    return sign * (180.0 - (90 + abs(angleA)) - math.degrees(math.acos(cos_expression)))


try:
    # startNetworkTables()
    # table = NetworkTables.getTable('SmartDashboard')

    counter = 0 # used to take intervals of exit angle data
    exit_angles = []

    pipe = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, int(WIDTH), int(HEIGHT), rs.format.bgr8, 60) #numbers that work: 6, 15
    config.enable_stream(rs.stream.depth, int(WIDTH), int(HEIGHT), rs.format.z16, 60)
    pipe.start(config)

#    cam = cs.UsbCamera("webcam", 0)
    # cserver = cs.CameraServer() UNCOMMENT

    # src = cs.CvSource("server", cs.VideoMode.PixelFormat.kMJPEG, WIDTH, HEIGHT, 70) UNCOMMENT
    # cserver.startAutomaticCapture(camera=src)UNCOMMENT
    while True:
        frames = pipe.wait_for_frames()
        depth = frames.get_depth_frame()
        color = frames.get_color_frame()
        if not (color and depth):
            continue

        img = np.asarray(color.get_data())
        grip_pipe.process(img)

        dp.update(img)
        left = int(dp.cx)
        down = int(dp.cy)

        # dist = depth.get_distance(int(WIDTH / 2), int(HEIGHT / 2))
        dist1 = 0.0
        dist2 = 0.0
        offset_left = 0.0
        offst_right = 0.0

        # Make sure that dist1 is on the left and dist2 is on the right
        if dp.x1 < dp.x2:
            dist1, offset_left = getDistance(dp.x1, dp.y1, True)
            dist2, offset_right = getDistance(dp.x2, dp.y2, False)
        else:
            dist2, offset_left = getDistance(dp.x1, dp.y1, True)
            dist1, offset_right = getDistance(dp.x2, dp.y2, False)

        print("dist1: "  + str(dist1) + " off left: " + str(offset_left))
        print("dist2: " + str(dist2) + " off right: " + str(offset_right))

        dist = (dist1 + dist2) / 2

        exit_angles.append(getOrientationAngle(dist1, dist2, offset_left, offset_right, dist, dp.angle))
        counter += 1

        # print(getOrientationAngle(dist1, dist2, offset_left, offset_right, dist, dp.angle))

        # print("dist: " + str(dist))
        # print("yaw ang: " + str(dp.angle))
        # print("exit ang: " + str(exit_angles[len(exit_angles) - 1]) + "\n")

        if not dp.isTapeDetected:
            dist = -1
            dp.angle = -1


        # table.putNumber('depth', dist) UNCOMMENT
        # table.putNumber('yaw', dp.angle) UNCOMMENT

        # TODO account for -1 issue (repeating, corrupting data)
        if counter >= 10: # analyze exit angle data in groups of x, should only take a little longer than x milliseconds (waitKey(milliseconds) + procesing time)
            final_exit_angle = dp.normalizeData(exit_angles)
            # print(final_exit_angle)
            # table.putNumber('exit_angle', final_exit_angle) UNCOMMENT
            counter = 0
            exit_angles = []

        # src.putFrame(img) UNCOMMENT


        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("leave")
            break

except Exception as e:
    print(e)
finally:
    pipe.stop()
    cv2.destroyAllWindows()
    # Method calls agaisnt librealsense objects may throw exceptions of type pylibrs.error
    # print("pylibrs.error was thrown when calling %s(%s):\n" % (e.get_failed_function(), e.get_failed_args()))
    # print("    %s\n", e.what())
    exit(1)
