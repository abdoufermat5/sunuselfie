from random import randint
import cv2
import sys
import os
import traceback


def detect_faces(image_path, display=False, output_path="temp/Extracted"):
    # Load the cascade classifier for face detection
    face_cascade_path = "Face_cascade.xml"  # Update with correct path
    FACE_CASCADE = cv2.CascadeClassifier(face_cascade_path)

    if FACE_CASCADE.empty():
        print("Error: Cascade classifier not loaded.")
        return []

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    image = cv2.imread(image_path)
    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = FACE_CASCADE.detectMultiScale(image_grey, scaleFactor=1.16, minNeighbors=5, minSize=(25, 25), flags=0)

    for x, y, w, h in faces:
        sub_img = image[y - 10:y + h + 10, x - 10:x + w + 10]
        current_path = os.getcwd()
        os.chdir(output_path)
        cv2.imwrite(str(randint(0, 10000)) + ".jpg", sub_img)
        os.chdir(current_path)
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)

    if display:
        cv2.imshow("Faces Found", image)
    # if (cv2.waitKey(0) & 0xFF == ord('q')) or (cv2.waitKey(0) & 0xFF == ord('Q')):
    # 	cv2.destroyAllWindows()
    out_files = os.listdir(output_path)
    print(f"Extracted {len(out_files)} faces from {image_path}")
    return out_files
