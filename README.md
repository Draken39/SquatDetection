# Squat Form Analyzer

A real-time computer vision application that helps users perfect their squat form by providing instant feedback on depth and rep counting.

## Features

- 📊 Real-time squat depth tracking
- 🎯 Visual guide lines for proper form
- 🔢 Automatic rep counting
- 📈 Performance metrics display
- 📋 Session summary with detailed statistics

## Installation

1. Clone the repository
```bash
git clone [repository-url]
cd squat-analyzer
```

2. Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scriptsctivate
```

3. Install required packages
```bash
pip install -r requirements.txt
```

## Usage

1. Run the program:
```bash
python src/main.py
```

2. Controls:
- Press `SPACE` to start
- Click "Start Squat" to begin tracking
- Click "Stop Squat" to end session and view summary
- Press `Q` to quit

## Requirements

- Python 3.7+
- Webcam
- Packages:
  - OpenCV
  - Mediapipe
  - Pygame
  - NumPy

## Setup Tips

- Ensure good lighting
- Position camera at hip height
- Stand sideways to the camera
- Keep your full body in frame

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
