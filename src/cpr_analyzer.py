import time
import numpy as np
from collections import deque

class CPRAnalyzer:
    def __init__(self):
        self.last_peak_time = None
        self.is_compression = False
        self.compression_count = 0
        self.current_rate = 0
        self.recent_intervals = deque(maxlen=3)  # Smaller window for more responsive rate
        self.last_depth = 0
        self.peak_threshold = 10  # More sensitive threshold
        
    def analyze_compression(self, depth):
        if depth is None:
            return 0, 0
            
        current_time = time.time()
        
        # Detect peaks in motion
        if not self.is_compression and depth > self.peak_threshold:
            self.is_compression = True
            if self.last_peak_time is not None:
                interval = current_time - self.last_peak_time
                if 0.1 <= interval <= 2.0:  # More permissive interval range
                    self.recent_intervals.append(interval)
                    
            self.last_peak_time = current_time
            self.compression_count += 1
            
        # Reset compression state
        elif self.is_compression and depth < self.peak_threshold/2:
            self.is_compression = False
        
        # Calculate rate
        if len(self.recent_intervals) > 0:
            avg_interval = np.mean(self.recent_intervals)
            self.current_rate = 60.0 / avg_interval
        
        # Reset rate if no recent compressions
        if self.last_peak_time and (current_time - self.last_peak_time) > 2.0:
            self.current_rate = 0
            self.recent_intervals.clear()
        
        # Calculate depth score
        depth_score = self.calculate_depth_score(abs(depth))
        
        # Debug output
        print(f"Depth: {depth:.1f}, Rate: {self.current_rate:.1f}, Count: {self.compression_count}")
        
        return self.current_rate, depth_score
    
    def calculate_depth_score(self, depth):
        # More lenient depth scoring
        if 15 <= depth <= 30:  # Wider acceptable range
            return 100
        elif depth > 30:
            return max(0, 100 - (depth - 30) * 3)
        else:
            return max(0, 100 - (15 - depth) * 3)