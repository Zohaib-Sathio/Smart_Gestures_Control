import time
import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self, img_mode=False, max_hands=2, model_complexity=1, detection_conf=0.5, track_conf=0.5):
        self.imgMode = img_mode
        self.maxHands = max_hands
        self.model_complexity = model_complexity
        self.detectionConf = detection_conf
        self.trackConf = track_conf
        self.mpHands = mp.solutions.hands
        self.mpDraw = mp.solutions.drawing_utils
        self.hands = self.mpHands.Hands(self.imgMode, self.maxHands, self.model_complexity, self.detectionConf,
                                        self.trackConf)


    def find_hands(self, img, draw = True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks:
            for handLMs in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLMs, self.mpHands.HAND_CONNECTIONS)
        return img


    def find_position(self, img, hand_no = 0, draw = True):
        lm_list = []
        if self.results.multi_hand_landmarks:
            h, w, c = img.shape
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(my_hand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (103, 70, 110), cv2.FILLED)

        return lm_list



def main():
    cap = cv2.VideoCapture(0)
    # For showing FPS
    pTime = 0
    cTime = 0
    detector = HandDetector()

    while True:
        success, img = cap.read()
        img = detector.find_hands(img)

        # Find cords of positions in list
        lm_list = detector.find_position(img, draw=False)
        if len(lm_list) != 0:
            print(lm_list[8])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, 'FPS: ' + str(int(fps)), (10, 60), cv2.FONT_HERSHEY_PLAIN, 4, (30, 200, 30))
        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()