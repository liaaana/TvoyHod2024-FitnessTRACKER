import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from app import db
from flask_login import  current_user

def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def gen_curl():
    counter = 0
    stage = None
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark

            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            # if (0 < shoulder[0] < frame.shape[1] and 0 < shoulder[1] < frame.shape[0] and \
            #    0 < elbow[0] < frame.shape[1] and 0 < elbow[1] < frame.shape[0] and \
            #    0 < wrist[0] < frame.shape[1] and 0 < wrist[1] < frame.shape[0]):
            angle = calculate_angle(shoulder, elbow, wrist)

            if angle > 170:
                stage = "down"
            if angle < 30 and stage == 'down':
                stage = "up"
                counter += 1
                # sound.play()
                current_user.crunches_counter += 1
                db.session.add(current_user)
                db.session.commit()

            cv2.rectangle(image, (0, 0), (225, 73), (22, 163, 74), -1)

            cv2.putText(image, 'REPS', (25, 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter),
                        (30, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.putText(image, 'STAGE', (145, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, stage, (130, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0, 40, 0), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(22, 163, 74), thickness=2, circle_radius=2)
                                  )

        frame = cv2.imencode('.jpg', image)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        key = cv2.waitKey(20)
        if key == 27:
            break

    return counter


def gen_push_up():
    counter = 0
    stage = None
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark

            nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,
                    landmarks[mp_pose.PoseLandmark.NOSE.value].y]
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

            shoulder_angle = calculate_angle(shoulder, elbow, wrist)
            back_angle = calculate_angle(shoulder, hip, knee)
            # and nose[1] > shoulder[1]
            if shoulder_angle <= 100 and nose[1] > shoulder[1]:
                stage = "down"
            if shoulder_angle >= 160 and stage == 'down':
                stage = "up"
                counter += 1
                # sound.play()
                current_user.push_ups_counter += 1
                db.session.add(current_user)
                db.session.commit()

            if back_angle < 170:
                cv2.putText(image, 'BAD BACK', (25, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5,
                            cv2.LINE_AA)

        cv2.rectangle(image, (0, 0), (225, 73), (22, 163, 74), -1)

        cv2.putText(image, 'REPS', (25, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter),
                    (30, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(image, 'STAGE', (145, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, stage, (130, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0, 40, 0), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(22, 163, 74), thickness=2, circle_radius=2)
                                  )

        frame = cv2.imencode('.jpg', image)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        key = cv2.waitKey(20)
        if key == 27:
            break

    return counter

def gen_squat():
    counter = 0
    stage = None
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.9, min_tracking_confidence=0.9)

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark

            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            hip_knee_ankle_angle = calculate_angle(hip, knee, ankle)

            if hip_knee_ankle_angle >= 160:
                stage = "up"
            if hip_knee_ankle_angle <= 90 and stage == 'up':
                stage = "down"
                counter += 1
                current_user.squats_counter += 1
                db.session.add(current_user)
                db.session.commit()


        cv2.rectangle(image, (0, 0), (225, 73), (230, 37, 69), -1)

        cv2.putText(image, 'REPS', (25, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter),
                    (30, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(image, 'STAGE', (145, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, stage, (130, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        # cv2.putText(image, 'TOO LOW', (25, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5,
                            # cv2.LINE_AA)

        mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0, 40, 0), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(230, 37, 69), thickness=2, circle_radius=2)
                                  )

        frame = cv2.imencode('.jpg', image)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        key = cv2.waitKey(20)
        if key == 27:
            break

    return counter

