import cv2
import mediapipe as mp
import socket 

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddrPort = ("127.0.0.1", 5052)
cap = cv2.VideoCapture(0)
with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      continue
    
    fore_lower = -1
    fore_upper = 1
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:              
      for hand_landmarks in results.multi_hand_landmarks:
        for ids, landmrk in enumerate(hand_landmarks.landmark):
            if ids == 9:
              # print(landmrk.x)
              s.sendto(str.encode(str(landmrk.x)), serverAddrPort)
            if ids == 10:
              fore_lower = landmrk.y
            if ids == 12:
              fore_upper = landmrk.y
              if fore_upper > fore_lower:
                print("Jump")
                s.sendto(str.encode("jump"), serverAddrPort)
            
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
        
    # Flip the image horizontally for a selfie-view display.
    imS = cv2.resize(image, (180, 160))
    cv2.imshow('MediaPipe Hands', cv2.flip(imS, 1))
    cv2.setWindowProperty('MediaPipe Hands', cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow('MediaPipe Hands', 1180, 50)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()