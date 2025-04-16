import face_recognition
import cv2
import numpy as np
import os
import pickle

video_capture = cv2.VideoCapture(0)

image_folder = "static/images"
encoding_file = "face_encodings.pkl"

if os.path.exists(encoding_file):
    with open(encoding_file, "rb") as f:
        known_face_encodings, known_face_names = pickle.load(f)
else:
    # If no encodings file, calculate
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(image_folder):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            image_path = os.path.join(image_folder, filename)
            person_image = face_recognition.load_image_file(image_path)

            person_face_encoding = face_recognition.face_encodings(person_image)

            if not person_face_encoding:
                print(f"[!] No face detected in {filename}")
            else:
                print(f"[✓] Face encoding successful for {filename}")
                known_face_encodings.append(person_face_encoding[0])
                known_face_names.append(os.path.splitext(filename)[0])


    # Save the encodings to the file for later use
    with open(encoding_file, "wb") as f:
        pickle.dump((known_face_encodings, known_face_names), f)

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
print(f"Loaded encodings: {known_face_names}")

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
        
        # Find all the faces in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)

        # Only process face encodings if faces are found
        if face_locations:
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # Use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

                if name != "Unknown":
                    print(f"{name} is Present!")

    process_this_frame = not process_this_frame

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
