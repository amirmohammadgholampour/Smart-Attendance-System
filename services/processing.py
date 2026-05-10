import datetime 
import cv2 as cv 
import numpy as np 

def process_frame(frame, face_detector, face_recognizer, student_features, l2_threshold, logged_today, attendance_log):
    """Processes a single frame for face detection, recognition, and attendance logging."""
    
    capture_height, capture_width = frame.shape[:2]
    
    # Set input size for the detector
    face_detector.setInputSize((capture_width, capture_height))
    
    # Detect faces
    faces_info = face_detector.detect(frame)
    
    current_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now()
    timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    log_time_obj = current_time.date()

    if faces_info[1] is not None: # Check if any faces were detected
        for face in faces_info[1]:
            coordinates = face[:-1].astype(np.int32)
            x, y, w, h = coordinates[0], coordinates[1], coordinates[2], coordinates[3]

            # Extract and recognize face
            try:
                frame_align_crop = face_recognizer.alignCrop(frame, face)
                frame_feature = face_recognizer.feature(frame_align_crop)
            except Exception as e:
                print(f"Error extracting face features: {e}")
                continue

            best_match_name = "Unknown"
            min_l2_score = float('inf')

            # Match against known student features
            for student_name, student_feature in student_features.items():
                l2_score = face_recognizer.match(frame_feature, student_feature, cv.FACE_RECOGNIZER_SF_FR_NORM_L2)
                if l2_score < min_l2_score:
                    min_l2_score = l2_score
                    if l2_score <= l2_threshold:
                        best_match_name = student_name
                    else:
                        best_match_name = "Unknown" # Ensure it resets if no good match found

            # Determine color for bounding box
            color = (0, 255, 0) if best_match_name != "Unknown" else (0, 0, 255)

            # Log attendance if a known person is detected and not logged recently
            if best_match_name != "Unknown":
                # Check if already logged today to prevent multiple entries within a short time
                is_logged_recently = False
                if best_match_name in logged_today and logged_today[best_match_name] == current_date_str:
                    # Check if this specific entry is too close to a previous one in the log
                    for entry in attendance_log:
                        # Make sure the entry is for the same student and not too old
                        if entry["Name"] == best_match_name:
                           try:
                               log_time = datetime.datetime.strptime(entry["Timestamp"], "%Y-%m-%d %H:%M:%S")
                               if (current_time - log_time).total_seconds() < 10: # Within 10 seconds
                                   is_logged_recently = True
                                   break
                           except ValueError: # Handle potential timestamp format errors in log
                                print(f"Warning: Invalid timestamp format in attendance log: {entry.get('Timestamp')}")
                                continue # Skip this entry if timestamp is invalid

                if not is_logged_recently:
                    attendance_log.append({
                        "Name": best_match_name,
                        "Status": "Present",
                        "Date": log_time_obj,
                        "Timestamp": timestamp_str,
                    })
                    logged_today[best_match_name] = current_date_str # Mark as logged today
                    print(f"Logged: {best_match_name} at {timestamp_str}")

            # Draw bounding box and name on the frame
            cv.rectangle(frame, (x, y), (x + w, y + h), color, 3)
            cv.putText(frame, best_match_name, (x, y - 10), cv.FONT_ITALIC, 0.8, color, 2, cv.LINE_AA)

    return frame 