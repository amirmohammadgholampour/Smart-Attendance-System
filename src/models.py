import cv2 as cv 

def load_detection_model(model_path: str):
    """Loads the face detection model."""
    try: 
        detector = cv.FaceDetectorYN.create( 
            model_path, 
            "", 
            (320, 320), 
            0.9, 
            0.3, 
            5000
        )
        print("Face detector model loaded successfully.")
        return detector 
    except Exception as error: 
        return f"Error loading face detector model: {error}" 

def load_recognition_model(model_path):
    """Loads the face recognition model."""
    try:
        recognizer = cv.FaceRecognizerSF.create(model_path, "")
        print("Face recognizer model loaded successfully.")
        return recognizer
    except Exception as e:
        print(f"Error loading face recognizer model: {e}")
        return None
