import mediapipe as mp
import cv2
import numpy as np
from collections import deque
import time

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.reset_tracking()
        self.squat_start_time = None
        self.initial_ankle_distance = None
        self.initial_knee_position = None
        
    def reset_tracking(self):
        self.initial_hip_height = None
        self.squat_count = 0
        self.in_squat = False
        self.squat_history = []
        self.current_squat = None
        
    def calculate_angle(self, p1, p2, p3):
        # Convert points to numpy arrays
        a = np.array([p1.x, p1.y])
        b = np.array([p2.x, p2.y])
        c = np.array([p3.x, p3.y])
        
        # Calculate vectors
        ba = a - b
        bc = c - b
        
        # Calculate angle
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        
        return np.degrees(angle)

    def calculate_foot_distance(self, landmarks):
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
        # Convert to real-world units (approximate)
        distance = np.sqrt((left_ankle.x - right_ankle.x)**2 + (left_ankle.y - right_ankle.y)**2) * 100
        return distance
    
    def calculate_knee_balance(self, landmarks):
        left_knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE]
        right_knee = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE]
        # Calculate percentage of weight on left side (based on knee position)
        total_width = abs(left_knee.x - right_knee.x)
        if total_width == 0:
            return 50  # Centered
        left_percentage = (left_knee.x / total_width) * 100
        return left_percentage
    
    def calculate_forward_shift(self, landmarks):
        # Use ankle and hip position to calculate forward lean
        ankle_mid_x = (landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].x + 
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].x) / 2
        hip_mid_x = (landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].x + 
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].x) / 2
        # Convert to approximate centimeters
        forward_shift = abs(hip_mid_x - ankle_mid_x) * 100
        return forward_shift

    def detect_pose(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)
        
        metrics = {
            'knee_angle': 180,
            'depth_percentage': 0,
            'squat_count': self.squat_count,
            'frame': frame
        }
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE]
            ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE]
            
            knee_angle = self.calculate_angle(hip, knee, ankle)
            hip_height = hip.y * frame.shape[0]
            
            if knee_angle > 160:  # Standing position
                self.initial_hip_height = hip_height
            
            if self.initial_hip_height:
                current_drop = hip_height - self.initial_hip_height
                max_drop = self.initial_hip_height * 0.4
                depth_percentage = min(100, (current_drop / max_drop) * 100)
                
                metrics['knee_angle'] = knee_angle
                metrics['depth_percentage'] = depth_percentage
                
                # Draw guide lines
                h, w, _ = frame.shape
                
                # Standing position line (green)
                y_stand = int(self.initial_hip_height)
                cv2.line(frame, (0, y_stand), (w, y_stand), (0, 255, 0), 2)
                
                # Target depth line (red)
                y_target = int(self.initial_hip_height + (self.initial_hip_height * 0.4))
                cv2.line(frame, (0, y_target), (w, y_target), (0, 0, 255), 2)
                
                # Current hip position line (blue)
                y_current = int(hip_height)
                cv2.line(frame, (0, y_current), (w, y_current), (255, 0, 0), 1)
                
                if not self.in_squat and knee_angle < 140:
                    self.in_squat = True
                    self.current_squat = {
                        'lowest_angle': knee_angle,
                        'max_depth': depth_percentage,
                        'back_angle': 0,
                        'form_issues': []
                    }
                elif self.in_squat:
                    self.current_squat['lowest_angle'] = min(self.current_squat['lowest_angle'], knee_angle)
                    self.current_squat['max_depth'] = max(self.current_squat['max_depth'], depth_percentage)
                    
                    if knee_angle > 160:  # Completed rep
                        self.in_squat = False
                        self.squat_count += 1
                        self.squat_history.append(self.current_squat)
                        metrics['squat_count'] = self.squat_count
            
            # Draw skeleton
            self.mp_draw.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
        metrics['frame'] = frame
        return metrics

    def draw_guides(self, frame, current_hip_height):
        if self.initial_hip_height:
            h, w, _ = frame.shape
            
            # Draw standing position line
            y_stand = int(self.initial_hip_height)
            cv2.line(frame, (0, y_stand), (w, y_stand), (0, 255, 0), 1)
            
            # Draw target depth line
            y_target = int(self.initial_hip_height + (self.initial_hip_height * 0.4))
            cv2.line(frame, (0, y_target), (w, y_target), (0, 0, 255), 1)

    def draw_measurement_guides(self, frame, landmarks):
        h, w, _ = frame.shape
        
        # Draw foot distance line
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
        cv2.line(frame, 
                 (int(left_ankle.x * w), int(left_ankle.y * h)),
                 (int(right_ankle.x * w), int(right_ankle.y * h)),
                 (0, 255, 0), 2)
        
        # Draw knee balance indicator
        left_knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE]
        right_knee = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE]
        knee_mid_x = (left_knee.x + right_knee.x) / 2
        knee_y = (left_knee.y + right_knee.y) / 2
        cv2.circle(frame, 
                  (int(knee_mid_x * w), int(knee_y * h)),
                  5, (0, 0, 255), -1)
        
        # Draw forward shift line
        ankle_mid_x = (left_ankle.x + right_ankle.x) / 2
        hip_mid_x = (landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].x + 
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].x) / 2
        hip_y = (landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].y + 
                landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].y) / 2
        cv2.line(frame,
                 (int(ankle_mid_x * w), int(knee_y * h)),
                 (int(hip_mid_x * w), int(hip_y * h)),
                 (255, 0, 0), 2) 