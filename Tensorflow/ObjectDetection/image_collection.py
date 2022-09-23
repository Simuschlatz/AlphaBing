import tensorflow as tf
# OpenCV
import cv2
import uuid
import os
import time

labels = ['thumbsup', 'thumbsdown', 'peace']
num_images = 5

# Set up the folders
IMAGES_PATH = os.path.join("Tensorflow/ObjectDetection", "Images")
if not os.path.exists(IMAGES_PATH):
    os.mkdir(IMAGES_PATH)
    for label in labels:
        path = os.path.join(IMAGES_PATH, label)
        os.mkdir(path)

# Collecting data and labelling
for label in labels:
    label_path = os.path.join(IMAGES_PATH, label)
    if len(os.listdir(label_path)):
        print("not empty")
        continue
    # Webcam capturing
    cap = cv2.VideoCapture(0)
    print(f"Collecting images for {label}...")
    time.sleep(4)
    for imageid in range(num_images):
        ret, frame = cap.read()
        img_name = f"{label}.{str(uuid.uuid1())}.jpg"
        img_path = os.path.join(label_path, img_name)
        cv2.imwrite(img_path, frame)
        cv2.imshow("frame", frame)
        cv2.waitKey(1)
        time.sleep(1)  
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()

os.open("main.py", 0, 0)

