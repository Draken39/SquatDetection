import cv2
import pygame
from pose_detector import PoseDetector
from gui import GUI

def main():
    try:
        print("Initializing Squat Form Analyzer...")
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        pose_detector = PoseDetector()
        gui = GUI()
        
        print("\nControls:")
        print("SPACE - Start")
        print("Q     - Quit")
        
        running = True
        while running:
            result = gui.handle_events()
            if result == "SHOW_SUMMARY":
                # Show summary before resetting
                gui.show_summary = True
                gui.show_session_summary(pose_detector.squat_history)
            elif result == "RESET":
                pose_detector = PoseDetector()  # Create new detector
                running = True
            elif result == False:
                running = False
            
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            
            if gui.recording:
                metrics = pose_detector.detect_pose(frame)
            else:
                metrics = {
                    'knee_angle': 180,
                    'depth_percentage': 0,
                    'squat_count': pose_detector.squat_count,
                    'frame': frame
                }
            
            gui.update_display(frame, metrics)
            pygame.time.wait(10)
        
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        if 'cap' in locals():
            cap.release()
        pygame.quit()

if __name__ == "__main__":
    main()