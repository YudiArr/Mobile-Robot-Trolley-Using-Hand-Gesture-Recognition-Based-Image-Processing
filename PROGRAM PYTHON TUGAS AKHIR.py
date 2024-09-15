import cv2
import mediapipe as mp
import time
import serial
import json

useSerial = False
if useSerial == True :
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1.11)
    time.sleep(2)

class dataObject():
    def __init__(self, mode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex, 
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True, flipType = True):
        xList = []
        yList = []
        bbox = []
        lmList = []
        b = []
        if self.results.multi_hand_landmarks:
            palm = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(palm.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                cv2.putText(img, str('Tangan Terdeteksi'), (10, 120), cv2.FONT_HERSHEY_PLAIN,1,
                    (0, 120, 205),2)
                lmList.append([id, cx, cy])
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax   
            bx, by = (bbox[0]-20 + bbox[2] + 20) //2, (bbox[3] + 20 + bbox[1] - 20)//2 
            b = [bx, by]
            b.append(0)
            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),
                              (255, 255, 255), 2)
                
        else:
            cv2.putText(img, str('Tidak Terdeteksi'), (10, 120), cv2.FONT_HERSHEY_PLAIN,1,
                    (0, 120, 205),2)
        return lmList,bbox,b
        
def main():
    mode = ''
    time.sleep(1)
    pTime = 0
    cTime = 0
    width, height = 640, 480
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, width)
    cap.set(4, height)
    detected = dataObject()
    k = 0
    while True:
        success, img = cap.read()
        img = detected.findHands(img)
        lmList,bbox,b = detected.findPosition(img)
        
        height, width = img.shape[:2]
        fingers=[]
        tipIds = [4, 8, 12, 16, 20]
        
        if len(lmList) != 0:
            x1, y1 = lmList[4][1:]
            x2, y2 = lmList[20][1:]
            gx = b[0] - width // 2
            gy = b[1] - height // 2

            cv2.line(img, (0, b[1]), (width, b[1]), (0, 0, 0), 1)
            cv2.line(img, (b[0], 0), (b[0], height), (0, 0, 0), 1)
            cv2.circle(img, (b[0], b[1]), 5, (0, 0, 0), cv2.FILLED)

            if lmList[tipIds[0]][1] > lmList[tipIds[0]-1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
            for id in range(1,5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            total=fingers.count(1)
                
            if total == 5:
                cv2.putText(img, str("Mundur"), (10, 90), cv2.FONT_HERSHEY_PLAIN,2,
                            (0, 170, 255),3)
                k = 66
                
            elif (fingers == [0,0,0,0,0] and fingers != [1,1,1,1,1] and x1 < x2):
                cv2.putText(img, str("Kanan"), (10, 90), cv2.FONT_HERSHEY_PLAIN,2,
                            (0, 0, 255),3)
                k = 55
            
            elif (fingers == [1,0,0,0,0] and fingers != [1,1,1,1,1] and x1 > x2):
                cv2.putText(img, str("Kiri"), (10, 90), cv2.FONT_HERSHEY_PLAIN,2,
                            (0, 0, 255),3)
                k = 44
            elif (fingers == [0,1,1,0,0]):
                cv2.putText(img, str("front"), (10, 90), cv2.FONT_HERSHEY_PLAIN,2,
                            (0, 0, 255),3)
                k = 33
            else:
                cv2.putText(img, str("Berhenti"), (10, 90), cv2.FONT_HERSHEY_PLAIN,2,
                            (0, 0, 255),3)
                k = 77

            cv2.putText(img, (str("x1: ") + str(x1)+','+str(" x2: ") + str(x2)), (10, 150), cv2.FONT_HERSHEY_PLAIN,1,
                            (255, 255, 255),2)
            cv2.putText(img, (str("Servo X: ") + str(gx)), (10, 180), cv2.FONT_HERSHEY_PLAIN,1,
                            (255, 255, 255),2)
            cv2.putText(img, (str("Servo Y: ") + str(gy)), (10, 200), cv2.FONT_HERSHEY_PLAIN,1,
                            (255, 255, 255),2)
                          
            dataOject ={
                "xc":gx,
                "yc":gy,
                "k":k
            } 
        else:    
            gx = 404
            gy = 404
            k = 404
            dataOject ={
                "xc":gx,
                "yc":gy,
                "k":k
            } 
        # print(data)
        if useSerial == True :
            dataJson = json.dumps(dataOject)
            print(dataJson)
            ser.write((dataJson + '\n').encode())

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img,str(int(fps)), (10,50), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,255), 3)

        # cv2.namedWindow("Image",cv2.WINDOW_NORMAL)
        # cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Image", img)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    main()