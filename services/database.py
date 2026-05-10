import os 
import pandas as pd 
import cv2 as cv 

def load_images_from_db(database_path: str, detection_model, recognition_model):
    """Loads images from the database directory and extracts features."""
    print("========================================================")
    student_features = {} 

    if not os.path.isdir(database_path): 
        print(f"Error: Database path '{database_path}' not found.")
        return None 

    print(f"Loading images and extracting features from: {database_path}")
    for filename in os.listdir(database_path):
        if filename.lower().endswith(".jpg"): 
            student_name = os.path.splitext(filename)[0]
            image_path = os.path.join(database_path, filename)
            image = cv.imread(image_path) 

            if image is None:
                print(f"Could not read image {image_path}") 
                continue
            
            try:
                # Preprocess image for detection
                detection_model.setInputSize((image.shape[1], image.shape[0]))
                faces = detection_model.detect(image)

                if faces[1] is not None and len(faces[1]) > 0:
                    face = faces[1][0]
                    frame_align_crop = recognition_model.alignCrop(image, face)
                    feature = recognition_model.feature(frame_align_crop)
                    student_features[student_name] = feature
                    print(f"Loaded: {student_name}")
                else:
                    print(f"Warning: No face detected in {filename}. Skipping.")
            except Exception as error: 
                print(f"Error processing {filename}: {error}")
    print(f"Database loaded with {len(student_features)} students.")
    print("========================================================")
    return student_features


def save_attendance_log(attendance_log, existing_file_path, output_file_path):

    """Saves the attendance log to an Excel file, handling existing data and duplicates."""
    if not attendance_log:
        print("No attendance data to save.")
        return

    print(f"Saving attendance log to {output_file_path}...")
    df_new = pd.DataFrame(attendance_log)
    
    # Ensure 'Date' column is correctly formatted as date objects
    df_new['Date'] = pd.to_datetime(df_new['Date']).dt.date
    
    # Reorder columns for clarity
    df_new = df_new[["Name", "Status", "Date", "Timestamp"]]

    try:
        # Try to load existing data
        if os.path.exists(existing_file_path):
            df_existing = pd.read_excel(existing_file_path)
            # Ensure date format consistency in existing data
            df_existing['Date'] = pd.to_datetime(df_existing['Date']).dt.date
            
            # Combine new and existing logs
            combined_df = pd.concat([df_existing, df_new])
            print("Loaded existing attendance data.")
        else:
            combined_df = df_new # If file doesn't exist, use only the current log
            print(f"'{existing_file_path}' not found. Creating a new attendance file.")
        
        # Remove duplicates: keep the earliest entry for each student per day
        # Sort by Timestamp to ensure the earliest is kept when duplicates are found
        combined_df = combined_df.sort_values(by="Timestamp")
        # Drop duplicates based on student name and date, keeping the first occurrence
        combined_df = combined_df.drop_duplicates(subset=["Name", "Date"], keep="first") 
        
        # Save the processed data
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_file_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
            
        combined_df.to_excel(output_file_path, index=False)
        print("Attendance log saved successfully.")
        
    except FileNotFoundError:
         # This case is now handled by the os.path.exists check above, but kept for safety.
        print(f"File not found error during save, assuming new file: {existing_file_path}")
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_file_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        df_new.to_excel(output_file_path, index=False)
        print("Attendance log saved successfully as a new file.")

    except Exception as e:
        print(f"Error saving attendance log to Excel: {e}")