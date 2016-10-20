import pandas
import numpy as np

gps_df = pandas.read_csv("./gps.csv")
camera_df = pandas.read_csv("./camera.csv")

gps_df['timestamp_camera'] = None
gps_df['filename'] = None
gps_df['seq_camera'] = None

for gps_index, gps_row in gps_df.iterrows():
  min_index = np.argmin(np.abs(camera_df.timestamp - gps_row.timestamp))
  gps_df.set_value(gps_index, "timestamp_camera", camera_df.timestamp[min_index])
  gps_df.set_value(gps_index, "filename", camera_df.filename[min_index])
  gps_df.set_value(gps_index, "seq_camera", camera_df.seq[min_index])

gps_df.to_csv("./interpolation.csv")