import time
import math
import cv2
import numpy as np
import pyautogui
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import HandTrackingModule as htm

########### Audio Control ###########
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# volume.GetMasterVolumeLevel()
VolRange = volume.GetVolumeRange()
minVol = VolRange[0]
maxVol = VolRange[1]
vol = 0
volPerc = 0
volBar = 400
########### Audio Control ##########

cam_width, cam_height = 720, 540
touch_frame = 40
smoothen_constant = 3

prev_X, prev_Y = 0, 0
cur_X, cur_Y = 0, 0

cap = cv2.VideoCapture(0)

screen_width, screen_height = pyautogui.size()
detector = htm.HandDetector(max_hands=1)
gesture_mouse = True
click_flag = True
right_click_flag = True
double_click = True
prev_time = 0

while True:
    success, img = cap.read()

    # 1 Find hand landmarks
    img = detector.find_hands(img)
    lm_list, bbox = detector.find_position(img, draw=False)

    # 2 Get the tip of index and middle finger
    if len(lm_list) != 0:
        if lm_list[8][1] < lm_list[20][1]:
            x1, y1 = lm_list[8][1:]
            x2, y2 = lm_list[12][1:]
            cv2.rectangle(img, (touch_frame + 120, touch_frame - 20), (cam_width - 110, cam_height - 250),
                          (0, 255, 255), 3)
            fingers = detector.fingersUp()
            if fingers.count(1) == 3:
                if fingers[1] and fingers[0] and fingers[4]:
                    gesture_mouse = not gesture_mouse
                    time.sleep(1)
            if gesture_mouse:
                # 3 Only index Finger: Moving Mode
                if fingers.count(1) == 1:
                    if fingers[1]:
                        # Convert Coordinates
                        x3 = np.interp(x1, (touch_frame + 120, cam_width - touch_frame - 110), (0, screen_width))
                        y3 = np.interp(y1, (touch_frame - 20, cam_height - touch_frame - 250), (0, screen_height))
                        cv2.circle(img, (x1, y1), 12, (255, 255, 0), cv2.FILLED)

                        # Smoothen the values
                        cur_X = prev_X + (x3 - prev_X) / smoothen_constant
                        cur_Y = prev_Y + (y3 - prev_Y) / smoothen_constant

                        # Move Mouse
                        pyautogui.moveTo(screen_width - cur_X, cur_Y)
                        prev_X = cur_X
                        prev_Y = cur_Y
                        click_flag = True
                        right_click_flag = True
                        double_click = True
                    if fingers[0]:
                        if double_click:
                            pyautogui.doubleClick()
                            double_click = False
                            click_flag = True
                            right_click_flag = True

                # 4 Both index and middle fingers are up: Clicking Mode
                if fingers.count(1) == 2 and fingers[1] and fingers[2]:
                    # Find distance between fingers
                    length, img, line_info = detector.findDistance(8, 12, img, r=7)
                    # print(length)
                    # Click mouse if distance is short
                    if length < 50:
                        cv2.circle(img, (line_info[4], line_info[5]), 10, (255, 0, 0), cv2.FILLED)
                        if click_flag:
                            pyautogui.click()
                            click_flag = False
                            right_click_flag = True
                            double_click = True

                # 5 For Right Click
                if fingers.count(1) == 3:
                    if fingers[1] and fingers[2] and fingers[4]:
                        if right_click_flag:
                            pyautogui.rightClick()
                            right_click_flag = False
                            click_flag = True
                            double_click = True
                    # if fingers[1] and fingers[2] and fingers[3]:
                    #     pyautogui.dragTo(100, 300)
        else:
            x1, y1 = lm_list[4][1], lm_list[4][2]
            x2, y2 = lm_list[8][1], lm_list[8][2]

            cv2.circle(img, (x1, y1), 7, (110, 140, 20), cv2.FILLED)
            cv2.circle(img, (x2, y2), 7, (110, 140, 20), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (103, 40, 60), 3)
            cv2.line(img, (x2, y2), (lm_list[12][1], lm_list[12][2]), (255, 0, 0), 2)

            mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
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

    cur_time = time.time()
    fps = 1 / (cur_time - prev_time)
    prev_time = cur_time

    cv2.putText(img, str(int(fps)), (10, 50), cv2.FONT_HERSHEY_PLAIN, 4, (0, 255, 0))

    # cv2.namedWindow("Virtual Mouse", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Virtual Mouse", 1160, 960)
    cv2.imshow("Virtual Mouse", img)
    cv2.waitKey(1)
