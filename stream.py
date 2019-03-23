import pyrealsense2 as rs
from networktables import NetworkTables
import threading
import grip
import cv2
import numpy as np
import data_process
import math
import sys
import cscore as cs

file = open("graphing_data.txt", 'w') # Remove after testing

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

# returns depth, x, y
def getValidDepthToPoint(x, y):
    max_distance = 2.0 #m
    dist_center = depth.get_distance(int(x), int(y))

    if dist_center != 0.0 and dist_center <= max_distance:
        return dist_center, x

    counter = 0
    x_left = x - 5
    x_right = x + 5
    while counter <= 15: # 45 pixel leeway in either direction
        dist_left = depth.get_distance(int(x_left), int(y))
        dist_right = depth.get_distance(int(x_right), int(y))
        # print("d left: " + str(dist_left))
        # print("d right: " + str(dist_right))
        if dist_left < max_distance and dist_left != 0.0:
            # print("\n")
            return dist_left, x_left
        if dist_right < max_distance and dist_right != 0.0:
            # print("\n")
            return dist_right, x_right
        x_right += 5
        x_left -= 5
        counter += 1

    return 0.0, x

# distance sensor breaks with retreoref tape because of how the distance is calculated (intersection from equation of lines from dual cameras to points in dot map, limited to resolution of dot map)
# @return: the direction that it shifted
def getDistance(x, y, isLeft):
    global dp

    if dp.rect1 is None or dp.rect2 is None:
        return 0.0, -1

    dist_tape_pixels = dp.distance(dp.x1, dp.y1, dp.x2, dp.y2)
    dist_tape_meters = 0.2985 # distance between the mid points of the pieces of tape
    approx_conversion = dist_tape_meters / dist_tape_pixels # meters /pixel

    # distances to left and right offset to a single tape
    depth, x_point = getValidDepthToPoint(int(x), int(y))
    dp.drawPoint(x_point, y)

    change_x = x_point - x
    offset = change_x * approx_conversion

    # right directions are fine, right moves away, left moves closer
    if isLeft: # if the left tape, left moves away, right moves closer
        offset *= -1.0

    return depth, offset


# dist1 will always be the leftmost point and dist2 will always be the rightmost
# TODO: does it make sense to return -1 if missed point, or the last valid point
def getOrientationAngle(left_dist, right_dist, offset_left, offset_right, dist_center, yaw): # has to be here because need depths
    global cos, zero_error
    tape_dist = 0.2985 + offset_left + offset_right # in meters to match other units, 11.75 inches
    # tape_dist /= 2.0

    print("dist2: " + str(right_dist))
    print("dist1: " + str(left_dist))

    # left_dist = 1.0
    # right_dist = 1.2

    # print("offset left: " + str(offset_left))
    # print("offset right: " + str(offset_right))
    # print("dist_center: " + str(dist_center))
    # print("tape_dist: " + str(tape_dist))
    # print("yaw: " + str(yaw) + "\n")
    # print("zero distance error: "+ str(zero_error))
    # print("cosine error: " + str(cos))

    # Right = +theta
    # Left = -theta
    if float(right_dist) == 0.0 or float(left_dist) == 0.0:
        zero_error += 1
        print("DIST ERROR")
        print(float(left_dist) == 0.0)
        print(right_dist == 0)
        return -1

    angleA = 0.0
    cos_expression = 0.0
    sign = 0.0

    if left_dist > right_dist:
        cos_expression = (right_dist * right_dist - tape_dist * tape_dist - left_dist * left_dist) / (-2.0 * tape_dist * left_dist)
        sign = 1.0
        dp.actualAngle(dp.x1, dp.y1)
    else:
        cos_expression = (left_dist * left_dist - tape_dist * tape_dist - right_dist * right_dist) / (-2.0 * tape_dist * right_dist)
        sign = -1.0
        dp.actualAngle(dp.x2, dp.y2)

    # check cos domain
    if cos_expression > 1 or cos_expression < -1:
        print("COS DOMAIN ERROR: " + str(cos_expression))
        return -1

    return sign * (180.0 - (90 + abs(angleA)) - math.degrees(math.acos(cos_expression)))


try:
    startNetworkTables()
    table = NetworkTables.getTable('SmartDashboard')

    counter = 0 # used to take intervals of exit angle data
    exit_angles = []


    pipe = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, int(WIDTH), int(HEIGHT), rs.format.bgr8, 60) #numbers that work: 6, 15
    config.enable_stream(rs.stream.depth, int(WIDTH), int(HEIGHT), rs.format.z16, 60)
    prof = pipe.start(config)
    s = prof.get_device().query_sensors()[1]
    s.set_option(rs.option.exposure, 225)

#    cam = cs.UsbCamera("webcam", 0)
    cserver = cs.CameraServer()

    src = cs.CvSource("server", cs.VideoMode.PixelFormat.kMJPEG, WIDTH, HEIGHT, 70)
    cserver.startAutomaticCapture(camera=src)
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
        dist = 0.0

        if dp.x1 < dp.x2:
            dist1, offset_left = getDistance(dp.x1, dp.y1, True)
            dist2, offset_right = getDistance(dp.x2, dp.y2, False)
            dist = dp.getCenterDistance(dist1, dp.x1, dp.y1, dist2, dp.x2, dp.y2)
        else:
            dist1, offset_left = getDistance(dp.x1, dp.y1, False)
            dist2, offset_right = getDistance(dp.x2, dp.y2, True)
            dist = dp.getCenterDistance(dist2, dp.x2, dp.y2, dist1, dp.x1, dp.y1)

        print("DIST: " + str(dist))
        # if dist != 0 and dist1 != 0 and dist2 != 0:
        #     file.write(str(dp.cx) + " ")
        #     file.write(str(dp.angle) + "\n")

        # uncomment if using below
                # exit_angles.append(getOrientationAngle(dist1, dist2, offset_left, offset_right, dist, dp.angle))
                # counter += 1

        exit_angle = getOrientationAngle(float(dist1), float(dist2), offset_left, offset_right, dist, dp.angle)
        print("exit angle before: " + str(exit_angle))
        if abs(exit_angle) < 10.0:
            exit_angle = 0
        print("exit angle after: " + str(exit_angle))

        if not dp.isTapeDetected:
            dist = -1
            dp.angle = -1

        table.putNumber('depth', dist)
        table.putNumber('yaw', dp.angle)
        table.putNumber('exit_angle', exit_angle)

        # Uncomment if consistency of angles is an issue
                # TODO account for -1 issue (repeating, corrupting data)
                # if counter >= 10: # analyze exit angle data in groups of x, should only take a little longer than x milliseconds (waitKey(milliseconds) + procesing time)
                #     final_exit_angle = dp.normalizeData(exit_angles)
                #     # print(final_exit_angle)
                #     # table.putNumber('exit_angle', final_exit_angle) UNCOMMENT
                #     counter = 0
                #     exit_angles = []

        src.putFrame(img)

        print("\n")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("leave")
            break

except Exception as e:
    print(e)
finally:
    file.close()
    pipe.stop()
    cv2.destroyAllWindows()
    # Method calls agaisnt librealsense objects may throw exceptions of type pylibrs.error
    # print("pylibrs.error was thrown when calling %s(%s):\n" % (e.get_failed_function(), e.get_failed_args()))
    # print("    %s\n", e.what())
    exit(1)
