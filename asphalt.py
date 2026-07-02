import cv2
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller, Key
import time 

# Initialize vide o    capture and hand detector
video = cv2.VideoCapture(0)
cv2.namedWindow("Asphalt 8 Controller", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Asphalt 8 Controller", cv2.WND_PROP_TOPMOST, 1)
  
detector = HandDetector(detectionCon=0.8, maxHands=2)  # Increased detection confidence
keyboard = Controller()

# Initialize variables to track key press states (for long press control and pause)
steering_right = False 
steering_left = False
accelerating = False
braking = False
using_nitro = False   
paused = False
start_time = None

# Helper function for handling long press visual feedback
def long_press_feedback(img, action, color, y_pos):
    elapsed_time = time.time() - start_time if start_time else 0
    if elapsed_time >= 0.5:  # Long press threshold (0.5 seconds)
        action += " (Long Press)"
    cv2.putText(img, action, (45, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 5)

while True:
    # Capture frame from video
    _, img = video.read()
    img = cv2.flip(img, 1)  # Flip the image to act as a mirror
    hands, img = detector.findHands(img)  # Detect hands in the frame

    # Reset state for this frame (to determine which keys should be pressed)
    steer_right_active = False
    steer_left_active = False
    accelerate_active = False
    brake_active = False
    nitro_active = False
    pause_active = False
    gesture_detected = False

    if hands:
        if len(hands) == 2:  # Both hands are detected
            right_hand = hands[0] if hands[0]["type"] == "Right" else hands[1]
            left_hand = hands[1] if hands[0]["type"] == "Right" else hands[0]
            right_fingers = detector.fingersUp(right_hand)
            left_fingers = detector.fingersUp(left_hand)

            # Check for both hands fully open (all fingers up) to trigger pause
            if right_fingers == [1, 1, 1, 1, 1] and left_fingers == [1, 1, 1, 1, 1]:
                pause_active = True
                if not paused:
                    print("PAUSE")
                    keyboard.press('p')  # Pause the game
                    keyboard.release('p')
                    paused = True
                cv2.putText(img, "Pause", (45, 675), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 6)
            else:
                paused = False  # Reset pause state when not showing full hands open

        for hand in hands:
            fingers = detector.fingersUp(hand)
            gesture_detected = True 

            if hand["type"] == "Left":
                # Right hand: Steer left when the index finger is up (interchanged control)
                if fingers == [0, 1, 0 , 0, 0]:  # Index finger up
                    steer_left_active = True
                    if not steering_left:
                        start_time = time.time()  # Start timing for long press
                        keyboard.press(Key.left)
                        steering_left = True
                else:
                    if steering_left:
                        keyboard.release(Key.left)
                        steering_left = False

                # Right hand: Nitro when the thumb is up
                if fingers == [1, 0, 0, 0, 0]:  # Thumb up
                    nitro_active = True
                    if not using_nitro:
                        start_time = time.time()  # Start timing for long press
                        keyboard.press(Key.space)
                        using_nitro = True
                else:
                    if using_nitro:
                        keyboard.release(Key.space)
                        using_nitro = False

                # Right hand: Accelerate when two fingers (index and middle) are up
                if fingers == [0, 1, 1, 1,0]:  # Two fingers up (index and middle)
                    accelerate_active = True
                    if not accelerating:
                        start_time = time.time()  # Start timing for long press
                        keyboard.press(Key.up)
                        accelerating = True
                else:
                    if accelerating:
                        keyboard.release(Key.up)
                        accelerating = False

            if hand["type"] == "Left":
                # Left hand: Steer right when the index finger is up (interchanged control)
                if fingers == [0, 1, 1, 0, 0]:  # Index finger up
                    steer_right_active = True
                    if not steering_right:
                        start_time = time.time()  # Start timing for long press
                        keyboard.press(Key.right)
                        steering_right = True
                else:
                    if steering_right:
                        keyboard.release(Key.right)
                        steering_right = False

                # Left hand: Brake when two fingers (index and middle) are up
                if fingers == [1 , 1, 1, 1, 1]:  # Two fingers up (index and middle)
                    brake_active = True
                    if not braking:
                        start_time = time.time()  # Start timing for long press
                        keyboard.press(Key.down)  # Brake
                        braking = True
                else:
                    if braking:
                        keyboard.release(Key.down)
                        braking = False

    # Display visual feedback for active controls
    if steer_right_active:
        long_press_feedback(img, "Steer Right", (0, 255, 0), 275)
    
    if steer_left_active:
        long_press_feedback(img, "Steer Left", (0, 0, 255), 375)
    
    if accelerate_active:
        long_press_feedback(img, "Accelerate", (0, 255, 255), 475)

    if brake_active:
        long_press_feedback(img, "Brake", (255, 0, 0), 575)

    if nitro_active:
        long_press_feedback(img, "Nitro", (0, 0, 255), 675)

    if pause_active:
        long_press_feedback(img, "Pause", (255, 0, 0), 675)

    # If no gesture is detected, reset start time (for long press)
    if not gesture_detected:
        start_time = None

    # Display the image with hand detection
    cv2.imshow("Asphalt 8 Controller", img)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) == ord("q"):
                break

# Release video capture and close all windows
video.release()
cv2.destroyAllWindows()
