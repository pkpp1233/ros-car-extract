# Tutorial on Python Script and Rosbag Data Extraction


## Ros gotchas

* This tutorial assumes ros is installed on your machine.

* We get the definitions of our topics by using the following ros command for example: `rosbag info udacitiy_dataset_for_center_camera.bag`. Look through the list of topics and you should see a topic named `/left_camera/image_color/compressed` or `/left_camera/image_color` depending on which dataset you're using. See next point for more info.

* The camera images we not compressed the first time Udacity published the dataset.bag file. The newer datasets have compressed images so this script will use numpy to decompress the images: `cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)`

* After the images are decompressed, we can use cv2 to write them to our output directory: `cv2.imwrite(image_filename, cv_image)`


## Step 1 Import Dependencies and Setup definitions

First we import dependencies and define the ros topics we want to extract, ex: 

`CENTER_CAMERA_TOPIC_COMPRESSED = "/center_camera/image_color/compressed"`

 We got the names for the Ros topics as explained above. I will talk about the write_image function in a little bit

## Step 2 Grab all bagfiles and iterate through them

We use glob to get all the bag files and then do the rest of our work while looping through each bagfile:

For each bagfile, setup the output directories 
`left_outdir = get_outdir(dataset_dir, "left")` and define headers for our data 
`gps_cols = ["seq", "timestamp", "latitude", "longitude"]`

## Step 3 Iterate through topics in each bagfile

