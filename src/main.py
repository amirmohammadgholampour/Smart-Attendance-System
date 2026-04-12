# Import required packages 
from camera_utils import initialize_camera
from config import * 
from database import load_images_from_db, save_attendance_log 
from models import load_detection_model, load_recognition_model
from processing import process_frame
import cv2 as cv 

# -------------------------
# Main Execution
# -------------------------
attendance_log = []
logged_today = {}

def main():
    # --- Initialization ---
    face_detector = load_detection_model(FACE_DETECTOR_MODEL_PATH)
    face_recognizer = load_recognition_model(FACE_RECOGNIZER_MODEL_PATH)
    student_features = load_images_from_db(STUDENT_DB_PATH, face_detector, face_recognizer)
    capture = initialize_camera()

    if not capture or not face_detector or not face_recognizer:
        print("Initialization failed. Exiting.")
        return

    # Set up display window
    cv.namedWindow(WINDOW_NAME, cv.WINDOW_NORMAL)

    # --- Main Loop ---
    print("Starting attendance system. Press 'q' to quit.")
    while True:
        ret, frame = capture.read()
        if not ret:
            print("Failed to grab frame, exiting.")
            break

        # Flip frame horizontally (for mirror effect)
        frame = cv.flip(frame, 1)

        # Process the frame
        processed_frame = process_frame(frame, face_detector, face_recognizer, student_features, 1.128, logged_today, attendance_log)

        # Display the resulting frame
        cv.imshow(WINDOW_NAME, processed_frame)

        # Exit loop on 'q' key press
        key = cv.waitKey(1) & 0xFF
        if key == ord("q"):
            print("Quitting...")
            break

    # --- Cleanup ---
    capture.release()
    cv.destroyAllWindows()
    print("Resources released.")

    # --- Save Log ---
    save_attendance_log(attendance_log, EXISTING_ATTENDANCE_FILE, ATTENDANCE_LOG_FILE)
    print("Process finished.")

if __name__ == "__main__":
    main()