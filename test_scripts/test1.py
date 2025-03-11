import cv2

# Change this if needed: Try 0, 1, 2, etc., if the camera isn't detected
VIDEO_SOURCE = 0 

# Open the video stream
cap = cv2.VideoCapture(VIDEO_SOURCE)

# Set resolution (depends on Boson model; try different values if needed)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # Convert to grayscale (Boson outputs 8-bit grayscale)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply colormap to enhance visibility (optional)
    colored_frame = cv2.applyColorMap(gray_frame, cv2.COLORMAP_HOT)

    # Display the frame
    cv2.imshow("Boson IR Camera Feed", colored_frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
