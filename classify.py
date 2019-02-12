import tensorflow as tf
import sys
import os
import cv2
import math
import numpy as np
import pyrealsense2 as rs
import grip
# speicherorte fuer trainierten graph und labels in train.sh festlegen ##

# Disable tensorflow compilation warnings
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf

grip_pipe = grip.HatchPipeline()
pipe = rs.pipeline()
config = rs.config()

WIDTH = 640
HEIGHT = 480

config.enable_stream(rs.stream.color, int(WIDTH), int(HEIGHT), rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, int(WIDTH), int(HEIGHT), rs.format.z16, 30)
pipe.start(config)

# holt labels aus file in array
label_lines = [line.rstrip() for line in tf.gfile.GFile("tf_files/retrained_labels.txt")]
# !! labels befinden sich jeweils in eigenen lines -> keine aenderung in retrain.py noetig -> falsche darstellung im windows editor !!

# graph einlesen, wurde in train.sh -> call retrain.py trainiert
with tf.gfile.FastGFile("tf_files/retrained_graph.pb", 'rb') as f:

	graph_def = tf.GraphDef()	## The graph-graph_def is a saved copy of a TensorFlow graph; objektinitialisierung
	graph_def.ParseFromString(f.read())	#Parse serialized protocol buffer data into variable
	_ = tf.import_graph_def(graph_def, name='')	# import a serialized TensorFlow GraphDef protocol buffer, extract objects in the GraphDef as tf.Tensor

	#https://github.com/Hvass-Labs/TensorFlow-Tutorials/blob/master/inception.py ; ab zeile 276
with tf.Session() as sess:

	i = 0
	while True:  # fps._numFrames < 120
		frames = pipe.wait_for_frames()
		depth = frames.get_depth_frame()

		if not depth: #skip if there are no new frames
			continue

		# the technique we used to generate the original training images
		depth_data = np.asanyarray(depth.get_data())
		depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_data, alpha=0.03), cv2.COLORMAP_JET)
		grip_pipeline.process(depth_colormap)

		final_depth_image = grip_pipeline.hsl_threshold_output

		if (0 == 0):
			i = i + 1
			cv2.imwrite(filename="screens/"+str(i)+"alpha.png", img=final_depth_image);
			image_data = tf.gfile.FastGFile("screens/"+str(i)+"alpha.png", 'rb').read()
			softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
			predictions = sess.run(softmax_tensor, \
					 {'DecodeJpeg/contents:0': image_data})
			top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

			for node_id in top_k:
				human_string = label_lines[node_id]
				score = predictions[0][node_id]
				print('%s (score = %.5f)' % (human_string, score))
			print ("\n\n")

			os.remove("screens/"+str(i)+"alpha.png") # Deletes the image after processing so there's not a buildup of processed images
			# have to write to the images so the model can access them

			cv2.imshow("image", final_depth_image)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				print("leave")
				break

	pipe.stop()
	cv2.destroyAllWindows()
