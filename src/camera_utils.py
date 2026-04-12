# Import required packages 
import cv2 as cv 

def initialize_camera(width=640, height=480):
    """Initializes the video capture device."""
    capture = cv.VideoCapture(0)
    if not capture.isOpened():
        print("Error: Could not open video device.")
        return None
    
    capture.set(cv.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv.CAP_PROP_FRAME_HEIGHT, height)
    
    print(f"Camera initialized. Resolution: {int(capture.get(cv.CAP_PROP_FRAME_WIDTH))}x{int(capture.get(cv.CAP_PROP_FRAME_HEIGHT))}")
    return capture