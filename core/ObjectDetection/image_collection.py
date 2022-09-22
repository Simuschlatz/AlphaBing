import tensorflow as tf
# OpenCV
import cv2
import uuid
import os
import time

labels = ['thumbsup', 'thumbsdown', 'peace']
num_images = 5

# Set up the folders
IMAGES_PATH = os.path.join("core/ObjectDetection", "Images")
if not os.path.exists(IMAGES_PATH):
    os.mkdir(IMAGES_PATH)
    for label in labels:
        path = os.path.join(IMAGES_PATH, label)
        os.mkdir(path)
    
