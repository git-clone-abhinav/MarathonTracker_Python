import cv2
import numpy as np
from pyzbar.pyzbar import decode

cap = cv2.VideoCapture(1)
cap.set(3, 640)
cap.set(4, 480)

while True:
    success,img = cap.read()
    for barcode in decode(img):
        mydata = barcode.data.decode("utf-8")
        print(mydata)
    cv2.imshow('Result', img)
    cv2.waitKey(1)
