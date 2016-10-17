from __future__ import print_function
from cv_bridge import CvBridge, CvBridgeError
from collections import defaultdict
import os
import sys
import glob
import cv2
import rosbag
import argparse
import pandas as pd
from sensor_msgs.msg import CompressedImage
import numpy as np

LEFT_CAMERA_TOPIC = "/left_camera/image_color"
LEFT_CAMERA_TOPIC_COMPRESSED = "/left_camera/image_color/compressed"
CENTER_CAMERA_TOPIC = "/center_camera/image_color"
CENTER_CAMERA_TOPIC_COMPRESSED = "/center_camera/image_color/compressed"
RIGHT_CAMERA_TOPIC = "/right_camera/image_color"
RIGHT_CAMERA_TOPIC_COMPRESSED = "/right_camera/image_color/compressed"
CAMERA_TOPICS = [LEFT_CAMERA_TOPIC, CENTER_CAMERA_TOPIC, RIGHT_CAMERA_TOPIC, LEFT_CAMERA_TOPIC_COMPRESSED, CENTER_CAMERA_TOPIC_COMPRESSED, RIGHT_CAMERA_TOPIC_COMPRESSED]
STEERING_TOPIC = "/vehicle/steering_report"
GPS_FIX_TOPIC = "/vehicle/gps/fix"
GPS_TIME_TOPIC = "/vehicle/gps/time"
GPS_VEL_TOPIC = "/vehicle/gps/vel"
GPS_TOPICS = [GPS_FIX_TOPIC, GPS_TIME_TOPIC, GPS_VEL_TOPIC]


def get_outdir(base_dir, name):
    outdir = os.path.join(base_dir, name)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    return outdir
def write_image(bridge, topic, outdir, msg, fmt='png'):
    image_filename = os.path.join(outdir, str(msg.header.stamp.to_nsec()) + '.' + fmt)
    try:
        if '/compressed' in topic:
            nparr = np.fromstring(msg.data, np.uint8)
            cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
        cv2.imwrite(image_filename, cv_image)
    except CvBridgeError as e:
        print(e)
    return image_filename

img_format = "png"
base_outdir = "./output"
rosbag_pattern = "./*.bag"
debug_print = False
bagfiles = glob.glob(rosbag_pattern)

bridge = CvBridge()
filter_topics = [CENTER_CAMERA_TOPIC, STEERING_TOPIC, GPS_FIX_TOPIC, CENTER_CAMERA_TOPIC_COMPRESSED]
for bagfile in bagfiles:
    print(bagfile)
    dataset_name = os.path.splitext(os.path.basename(bagfile))[0]
    dataset_dir = get_outdir(base_outdir, dataset_name)
    left_outdir = get_outdir(dataset_dir, "left")
    center_outdir = get_outdir(dataset_dir, "center")
    right_outdir = get_outdir(dataset_dir, "right")
    camera_cols = ["seq", "timestamp", "width", "height", "frame_id", "filename"]
    camera_dict = defaultdict(list)
    steering_cols = ["seq", "timestamp", "angle", "torque", "speed"]
    steering_dict = defaultdict(list)
    gps_cols = ["seq", "timestamp", "latitude", "longitude"]
    gps_dict = defaultdict(list)

    with rosbag.Bag(bagfile, "r") as bag:
        for topic, msg, t in bag.read_messages(topics=filter_topics):
            if topic in CAMERA_TOPICS:
                if topic[1] == 'l':
                    outdir = left_outdir
                elif topic[1] == 'c':
                    outdir = center_outdir
                elif topic[1]  == 'r':
                    outdir = right_outdir
                if debug_print:
                    print("%s_camera %d" % (topic[1], msg.header.stamp.to_nsec()))
                image_filename = write_image(bridge, topic, outdir, msg, fmt=img_format)
                camera_dict["seq"].append(msg.header.seq)
                camera_dict["timestamp"].append(msg.header.stamp.to_nsec())
                try:
                    camera_dict["width"].append(msg.width)
                    camera_dict["height"].append(msg.height)
                except:
                    camera_dict["width"].append("")
                    camera_dict["height"].append("")
                camera_dict["frame_id"].append(msg.header.frame_id)
                camera_dict["filename"].append(os.path.relpath(image_filename, dataset_dir))
            elif topic == STEERING_TOPIC:
                if debug_print:
                    print("steering %d %f" % (msg.header.stamp.to_nsec(), msg.steering_wheel_angle))
                steering_dict["seq"].append(msg.header.seq)
                steering_dict["timestamp"].append(msg.header.stamp.to_nsec())
                steering_dict["angle"].append(msg.steering_wheel_angle)
                steering_dict["torque"].append(msg.steering_wheel_torque)
                steering_dict["speed"].append(msg.speed)
            elif topic in GPS_FIX_TOPIC:
                if debug_print:
                    print("gps lat %d %f" % (msg.header.stamp.to_nsec(), msg.latitude))
                gps_dict["seq"].append(msg.header.seq)
                gps_dict["timestamp"].append(msg.header.stamp.to_nsec())
                gps_dict["latitude"].append(msg.latitude)
                gps_dict["longitude"].append(msg.longitude)
    camera_csv_path = os.path.join(dataset_dir, 'camera.csv')
    camera_df = pd.DataFrame(data=camera_dict, columns=camera_cols)
    camera_df.to_csv(camera_csv_path, index=False)
    steering_csv_path = os.path.join(dataset_dir, 'steering.csv')
    steering_df = pd.DataFrame(data=steering_dict, columns=steering_cols)
    steering_df.to_csv(steering_csv_path, index=False)
    gps_csv_path = os.path.join(dataset_dir, 'gps.csv')
    gps_df = pd.DataFrame(data=gps_dict, columns=gps_cols)
    gps_df.to_csv(gps_csv_path, index=False)
