import math
import cv2
import time
import numpy as np
import HandTrackingModule as htm
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cap = cv2.VideoCapture(0)
cap.set(3, 360)
cap.set(4, 240)

detector = htm.HandDetector()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# volume.GetMute()
# volume.GetMasterVolumeLevel()
VolRange = volume.GetVolumeRange()
minVol = VolRange[0]
maxVol = VolRange[1]
vol = 0
volPerc = 0
volBar = 400
p_time = 0

while True:
    success, img = cap.read()
    img = detector.find_hands(img)
    lm_list = detector.find_position(img, draw = False)
    if len(lm_list) != 0:
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]

        cv2.circle(img, (x1, y1), 7, (110, 140, 20), cv2.FILLED)
        cv2.circle(img, (x2, y2), 7, (110, 140, 20), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (103, 40, 60), 3)
        cv2.line(img, (x2, y2), (lm_list[12][1],lm_list[12][2]), (255,0,0), 2)

        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) //2
        cv2.circle(img, (mid_x, mid_y), 5, (110, 140, 20), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)
        lengthToStop = math.hypot(lm_list[12][1] - x2, lm_list[12][2] - y2)
        # print(lengthToStop)
        vol = np.interp(length, [50, 150], [minVol, maxVol])
        # volBar = np.interp(length, [30, 200], [400, 150])
        # volPerc = np.interp(length, [30, 200], [0, 100])
        if lengthToStop < 60:
            cv2.line(img, (x2, y2), (lm_list[12][1], lm_list[12][2]), (0, 0, 255), 2)
        else:
            volume.SetMasterVolumeLevel(vol, None)


        if length < 40:
            cv2.circle(img, (mid_x, mid_y), 5, (10, 240, 20), cv2.FILLED)

    # cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    # cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    # cv2.putText(img, f'{int(volPerc)}%', (50, 450), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0))

    # FPS
    c_time = time.time()
    fps = 1/ (c_time-p_time)
    p_time = c_time
    cv2.putText(img, 'FPS: ' + str(int(fps)), (15,50), cv2.FONT_HERSHEY_PLAIN, 3, (224, 220, 240))

    cv2.imshow("Volume Control By Gesture", img)
    cv2.waitKey(1)