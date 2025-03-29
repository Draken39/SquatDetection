import sys
import os
import pygame
import cv2
import mediapipe as mp
import numpy as np

def test_dependencies():
    print("\n1. Testing Dependencies...")
    
    # Dictionary of required packages and their minimum versions
    required_packages = {
        'pygame': ('pygame', '2.0.0'),
        'opencv-python': ('cv2', '4.0.0'),
        'mediapipe': ('mediapipe', '0.8.0'),
        'numpy': ('numpy', '1.19.0')
    }
    
    all_passed = True
    
    for package_name, (import_name, min_version) in required_packages.items():
        try:
            # Try to import the package
            if package_name == 'pygame':
                import pygame
                version = pygame.__version__
            elif package_name == 'opencv-python':
                import cv2
                version = cv2.__version__
            elif package_name == 'mediapipe':
                import mediapipe
                version = mediapipe.__version__
            elif package_name == 'numpy':
                import numpy
                version = numpy.__version__
            
            print(f"✓ {package_name} installed successfully - Version: {version}")
            
        except ImportError:
            print(f"✗ {package_name} is not installed. Please run:")
            print(f"  pip install {package_name}")
            all_passed = False
        except Exception as e:
            print(f"✗ Error checking {package_name}: {str(e)}")
            all_passed = False
    
    if all_passed:
        print("\n✓ All dependencies are properly installed!")
    else:
        print("\n✗ Some dependencies are missing. Please install them using:")
        print("pip install pygame opencv-python mediapipe numpy")
    
    return all_passed

def test_camera():
    print("\n2. Testing Camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("✗ Error: Could not open camera")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print("✗ Error: Could not read frame from camera")
        cap.release()
        return False
    
    print(f"✓ Camera working - Resolution: {frame.shape[1]}x{frame.shape[0]}")
    cap.release()
    return True

def test_directories():
    print("\n3. Testing Directory Structure...")
    required_dirs = [
        'src',
        'assets',
        'assets/sounds',
        'assets/images'
    ]
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_exist = True
    
    for dir_path in required_dirs:
        full_path = os.path.join(base_path, dir_path)
        if os.path.exists(full_path):
            print(f"✓ Found directory: {dir_path}")
        else:
            print(f"✗ Missing directory: {dir_path}")
            try:
                os.makedirs(full_path)
                print(f"  → Created directory: {dir_path}")
            except Exception as e:
                print(f"  → Error creating directory: {e}")
                all_exist = False
    
    return all_exist

def test_pygame():
    print("\n4. Testing Pygame...")
    try:
        pygame.init()
        pygame.mixer.init()
        
        # Test display
        test_display = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Test Window")
        test_display.fill((0, 0, 0))
        pygame.display.flip()
        
        print("✓ Pygame display initialized successfully")
        print("✓ Pygame mixer initialized successfully")
        
        pygame.time.wait(1000)  # Keep window open for 1 second
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"✗ Pygame error: {e}")
        return False

def test_mediapipe():
    print("\n5. Testing MediaPipe...")
    try:
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("✓ MediaPipe Pose model initialized successfully")
        return True
    except Exception as e:
        print(f"✗ MediaPipe error: {e}")
        return False

def main():
    print("=== CPR Trainer Setup Test ===")
    
    # Dictionary to store test results
    test_results = {
        "Dependencies": test_dependencies,
        "Camera": test_camera,
        "Directories": test_directories,
        "Pygame": test_pygame,
        "MediaPipe": test_mediapipe
    }
    
    failed_tests = []
    passed_tests = []
    
    # Run each test and track results
    for test_name, test_function in test_results.items():
        print(f"\nRunning {test_name} test...")
        try:
            if test_function():
                passed_tests.append(test_name)
            else:
                failed_tests.append(test_name)
        except Exception as e:
            print(f"✗ Unexpected error in {test_name}: {str(e)}")
            failed_tests.append(test_name)
    
    # Print summary
    print("\n=== Test Results Summary ===")
    print(f"\n✓ Passed Tests ({len(passed_tests)}):")
    for test in passed_tests:
        print(f"  • {test}")
        
    if failed_tests:
        print(f"\n✗ Failed Tests ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"  • {test}")
        print("\nPlease fix the failed tests before running the main application.")
    else:
        print("\n✓ All tests passed! You can run the main application.")
        print("\nTo run the main application, use:")
        print("python src/main.py")

if __name__ == "__main__":
    main()