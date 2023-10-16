from base64 import encode
from pydoc import classname
from sre_constants import SUCCESS
from time import time
import cv2
import numpy as np
import face_recognition
import os
from datetime import date, datetime
from os import listdir
import pandas as pd
from os.path import isfile, join
from sendsms import sendSMS


path = "ImageAttendance"
images = []
classname = []
mylist = os.listdir(path)
print(mylist)

for cls in mylist:
    currentImage = cv2.imread(f'{path}/{cls}')
    images.append(currentImage)
    classname.append(os.path.splitext(cls)[0])
print(classname)

def findEncoding(images):
    EncodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        EncodeList.append(encode)
    return EncodeList

#print(datetoday)

def markAttendance(name):
    today = date.today()
    datetoday = today.strftime("%d-%m-%y")
    if not isfile(f'csvattendance/{datetoday}.csv'):
        print("file not exists")
        f = open(f'csvattendance/{datetoday}.csv','w+')
        f.close()

    with open(f'csvattendance/{datetoday}.csv', 'r+') as f:
        myDataList = f.readlines()
        namelist = []
        outtimelist = []
        #datelist = []
        #print(namelist, datelist)
        for line in myDataList:
            entry = line.split(',', 2)
            #datelist.append(entry[0])
            namelist.append(entry[0].replace(' ',''))
            now1 = datetime.now()
            outtime = now1.strftime('%H:%M:%S')
            # outtimelist.append(entry[2])
            print(outtime)
            #print(namelist, "-- name list", name, "-- name")

        # if(name in namelist and outtime not in outtimelist):
            # outtime = pd.read_csv('csvattendance/{datetoday}.csv')
            # print(outtime)

        if(name in namelist):
            #if name not in namelist:
            print("Entered name: ", name)
            now = datetime.now()
            time = now.strftime('%H:%M:%S')
            f.writelines(f' {name}, {time}\n')

encodelistKnown = findEncoding(images)
print("Encode done")

capture = cv2.VideoCapture(0)

#to get frame by frame
while True:
    success, img = capture.read()
    imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    facelocCurFrame = face_recognition.face_locations(imgSmall)
    encodeCurFrame = face_recognition.face_encodings(imgSmall, facelocCurFrame)

    for encodeFace, faceLoc in zip(encodeCurFrame, facelocCurFrame):
        matches = face_recognition.compare_faces(encodelistKnown, encodeFace)
        faceDist = face_recognition.face_distance(encodelistKnown, encodeFace)
        #print(faceDist)
        matchIndex = np.argmin(faceDist)

        if matches[matchIndex]:
            name = classname[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1,(255, 255, 255), 2)            
            markAttendance(name)
            sendSMS(name)

    cv2.imshow('webcam', img)
    cv2.waitKey(1)