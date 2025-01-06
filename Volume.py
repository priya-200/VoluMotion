import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import cv2
import time
import numpy as np
from HandTrackingModule import handDetector
from comtypes import CLSCTX_ALL

width_cam, height_cam = 620, 720
pTime = 0

cap = cv2.VideoCapture(0)
cap.set(3, width_cam)
cap.set(4, height_cam)

hand = handDetector()

# Audio volume control setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volumeRange = volume.GetVolumeRange()
print(volumeRange)
minVol = volumeRange[0]  # Minimum volume level
maxVol = volumeRange[1]  # Maximum volume level
vol = 0
volBar = 400

while True:
    success, img = cap.read()

    img = hand.findHands(img)
    lmList = hand.findPosition(img, draw=False)
    if len(lmList) != 0:
        # Thumb and index finger coordinates
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw visual elements for debugging
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        # Calculate the distance between thumb and index finger
        length = math.hypot(x2 - x1, y2 - y1)

        # Map the distance to volume range
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])

        # Set the system volume
        volume.SetMasterVolumeLevel(vol, None)
        print(f"Volume Level: {vol}")

        # Visual feedback for minimal distance
        if length <= 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    # Draw volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)

    # Display FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS : {int(fps)}', (40, 70), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    # Show the image
    cv2.imshow("Image", img)

    # Quit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
