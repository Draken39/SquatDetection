import cv2
import yt_dlp
import os
from pose_detector import PoseDetector
from gui import GUI
import pygame

class VideoAnalyzer:
    def __init__(self):
        self.pose_detector = PoseDetector()
        self.gui = GUI()
        
    def download_youtube_video(self, url):
        try:
            print("Downloading video...")
            
            ydl_opts = {
                'format': 'mp4',
                'outtmpl': 'temp_squat.mp4',
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            print("Download complete!")
            return 'temp_squat.mp4'
            
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None

    def analyze_video(self, video_path):
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print("Error: Could not open video")
                return

            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            delay = int(1000/fps)

            running = True
            paused = False

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            running = False
                        elif event.key == pygame.K_SPACE:
                            paused = not paused

                if not paused:
                    ret, frame = cap.read()
                    if not ret:
                        # Loop back to start of video
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue

                    # Resize frame if too large
                    height, width = frame.shape[:2]
                    if width > 1280:
                        new_width = 1280
                        new_height = int(height * (new_width / width))
                        frame = cv2.resize(frame, (new_width, new_height))

                    # Analyze frame
                    knee_angle, depth_percentage, proper_form, annotated_frame = \
                        self.pose_detector.detect_pose(frame)

                    # Update display
                    self.gui.update_display(annotated_frame, knee_angle, depth_percentage, proper_form)

                pygame.time.wait(delay)

            cap.release()

        except Exception as e:
            print(f"Error analyzing video: {e}")
        finally:
            # Cleanup
            if os.path.exists('temp_squat.mp4'):
                try:
                    os.remove('temp_squat.mp4')
                except:
                    pass 