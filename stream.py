import pyrealsense2 as rs
from networktables import NetworkTables
import hatchdetection as hd
import threading
import grip

cond = threading.Condition()
notified = [False]

# grip_pipe = grip.GripPipeline()
# detection = hatchdetection.HatchDetection(grip_pipe)

DS5_product_ids = ["0AD1", "0AD2", "0AD3", "0AD4", "0AD5", "0AF6", "0AFE", "0AFF", "0B00", "0B01", "0B03", "0B07"]

def find_device_that_supports_advanced_mode():
    ctx = rs.context()
    ds5_dev = rs.device()
    devices = ctx.query_devices();
    for dev in devices:
        if dev.supports(rs.camera_info.product_id) and str(dev.get_info(rs.camera_info.product_id)) in DS5_product_ids:
            if dev.supports(rs.camera_info.name):
                print("Found device that supports advanced mode:", dev.get_info(rs.camera_info.name))
            return dev
    raise Exception("No device that supports advanced mode was found")

try:
    dev = find_device_that_supports_advanced_mode()
    advnc_mode = rs.rs400_advanced_mode(dev)
    print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")

     # Loop until we successfully enable advanced mode
    while not advnc_mode.is_enabled():
        print("Trying to enable advanced mode...")
        advnc_mode.toggle_advanced_mode(True)
        # At this point the device will disconnect and re-connect.
        print("Sleeping for 5 seconds...")
        time.sleep(5)
        # The 'dev' object will become invalid and we need to initialize it again
        dev = find_device_that_supports_advanced_mode()
        advnc_mode = rs.rs400_advanced_mode(dev)
        print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")

    print("Auto Exposure Control: \n", advnc_mode.get_ae_control())

    # Create a context object. This object owns the handles to all connected realsense devices
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, int(640), int(480), rs.format.bgr8, 60)
    pipeline.start(config)

    # This call waits until a new coherent set of frames is available on a device
    # Calls to get_frame_data(...) and get_frame_timestamp(...) on a device will return stable values until wait_for_frames(...) is called
    while True:
        frames = pipeline.wait_for_frames()
        color = frames.get_color_frames()
        if not color:
            continue

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("leave")
            break


    pipe.stop()
    cv2.destroyAllWindows()
    exit(0)

except Exception as e:
    print(e)
    exit(1)
