import pygame
import cv2
import numpy as np

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.active = True
        
        # Add padding and minimum width based on text
        self.horizontal_padding = 40  # Increased padding
        self.vertical_padding = 20
        self.min_width = 200  # Minimum button width

    def draw(self, screen, font):
        # Ensure minimum width based on text
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_width = text_surface.get_width() + (self.horizontal_padding * 2)
        self.rect.width = max(self.min_width, text_width)
        
        # Draw shadow
        shadow_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, 
                                self.rect.width, self.rect.height)
        pygame.draw.rect(screen, (0, 0, 0, 40), shadow_rect, border_radius=12)
        
        # Draw main button with smoother gradient
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        
        # Add subtle top highlight
        highlight_rect = self.rect.copy()
        highlight_rect.height = self.rect.height // 2
        pygame.draw.rect(screen, (*color, 50), highlight_rect, border_radius=12)
        
        # Draw text with better positioning
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class GUI:
    def __init__(self, width=1280, height=720):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Squat Form Analyzer")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (239, 83, 80)
        self.GREEN = (102, 187, 106)
        self.BLUE = (66, 165, 245)
        self.LIGHT_BLUE = (227, 242, 253)
        self.GRAY = (158, 158, 158)
        
        # Fonts
        self.font_large = pygame.font.SysFont('Arial', 42, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 24)
        
        # States
        self.show_instructions = True
        self.recording = False
        self.show_summary = False
        self.summary_data = None
        self.scroll_y = 0
        
        # Button setup
        button_width = 220
        button_height = 60
        button_y = height - 100
        spacing = 40
        
        total_width = (button_width * 2) + spacing
        start_x = (width - total_width) // 2
        
        self.start_button = Button(
            start_x, button_y,
            button_width, button_height,
            "Start Squat",
            self.GREEN,
            (129, 199, 132)
        )
        
        self.stop_button = Button(
            start_x + button_width + spacing, button_y,
            button_width, button_height,
            "Stop Squat",
            self.RED,
            (229, 115, 115)
        )
        
        self.continue_button = Button(
            width//2 - 90, height - 100, 180, 50,
            "Continue", self.BLUE, (60, 60, 220)
        )

    def draw_metrics_panel(self):
        panel_height = 200  # Increased height for more metrics
        panel = pygame.Surface((self.width, panel_height))
        panel.fill(self.WHITE)
        pygame.draw.rect(panel, (240, 240, 240), panel.get_rect(), 3)  # Add border
        self.screen.blit(panel, (0, 0))

    def draw_feedback(self, metrics):
        # Draw metrics panel with gradient
        panel_height = 140
        panel = pygame.Surface((self.width, panel_height))
        self.draw_gradient(panel, (240, 247, 255), (227, 242, 253))
        self.screen.blit(panel, (0, 0))
        
        # Draw three main metric boxes
        box_width = 280
        box_height = 100
        spacing = 60
        total_width = (box_width * 3) + (spacing * 2)
        start_x = (self.width - total_width) // 2
        
        metrics_data = [
            {
                'label': 'REPS',
                'value': str(metrics['squat_count']),
                'unit': '',
                'color': self.BLUE
            },
            {
                'label': 'KNEE ANGLE',
                'value': f"{metrics['knee_angle']:.0f}",
                'unit': '°',
                'color': self.GREEN if 90 <= metrics['knee_angle'] <= 150 else self.BLUE
            },
            {
                'label': 'DEPTH',
                'value': f"{metrics['depth_percentage']:.0f}",
                'unit': '%',
                'color': self.GREEN if metrics['depth_percentage'] >= 60 else self.BLUE
            }
        ]
        
        for i, metric in enumerate(metrics_data):
            x = start_x + (i * (box_width + spacing))
            y = 20
            
            # Draw metric box with shadow
            shadow_rect = pygame.Rect(x + 3, y + 3, box_width, box_height)
            pygame.draw.rect(self.screen, self.GRAY, shadow_rect, border_radius=15)
            
            # Draw main box
            box_rect = pygame.Rect(x, y, box_width, box_height)
            pygame.draw.rect(self.screen, self.WHITE, box_rect, border_radius=15)
            pygame.draw.rect(self.screen, (220, 230, 240), box_rect, 2, border_radius=15)
            
            # Draw label
            label = self.font_small.render(metric['label'], True, self.BLACK)
            label_rect = label.get_rect(centerx=box_rect.centerx, top=y + 15)
            self.screen.blit(label, label_rect)
            
            # Draw value
            value_text = f"{metric['value']}{metric['unit']}"
            value = self.font_large.render(value_text, True, metric['color'])
            value_rect = value.get_rect(centerx=box_rect.centerx, top=label_rect.bottom + 10)
            self.screen.blit(value, value_rect)

    def get_depth_color(self, depth):
        if depth >= 90:
            return self.GREEN  # Perfect
        elif depth >= 75:
            return (50, 205, 50)  # Good
        elif depth >= 60:
            return self.BLUE  # Not Bad
        else:
            return self.RED  # Needs Improvement

    def draw_gradient(self, surface, color1, color2):
        """Draw a vertical gradient on the given surface."""
        height = surface.get_height()
        for i in range(height):
            factor = i / height
            color = [
                color1[j] + (color2[j] - color1[j]) * factor
                for j in range(3)
            ]
            pygame.draw.line(surface, color, (0, i), (surface.get_width(), i))

    def draw_instructions(self):
        if not self.show_instructions:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill(self.BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        instructions = [
            "Squat Form Analyzer",
            "",
            "1. Stand sideways to the camera",
            "2. Keep your full body visible",
            "3. Press 'Start Squat' to begin",
            "4. Squat until parallel",
            "5. Keep your back straight",
            "",
            "Press SPACE to begin"
        ]
        
        y_pos = self.height // 4
        for i, text in enumerate(instructions):
            if text == "":
                y_pos += 30
                continue
                
            if i == 0:  # Title
                rendered_text = self.font_large.render(text, True, self.WHITE)
            else:
                rendered_text = self.font_medium.render(text, True, self.WHITE)
            
            text_rect = rendered_text.get_rect(center=(self.width//2, y_pos))
            self.screen.blit(rendered_text, text_rect)
            y_pos += 50

    def show_session_summary(self, squat_history):
        if not squat_history:
            return
            
        self.show_summary = True
        self.summary_data = {
            'total_reps': len(squat_history),
            'avg_depth': sum(rep['max_depth'] for rep in squat_history) / len(squat_history),
            'avg_knee_angle': sum(rep['lowest_angle'] for rep in squat_history) / len(squat_history),
            'best_depth': max((rep['max_depth'] for rep in squat_history), default=0),
            'worst_depth': min((rep['max_depth'] for rep in squat_history), default=0),
            'reps': squat_history
        }

    def draw_summary_screen(self):
        # Fill background
        self.screen.fill(self.LIGHT_BLUE)
        
        # Draw title
        title = self.font_large.render("Squat Session Summary", True, self.BLUE)
        title_rect = title.get_rect(center=(self.width//2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw main stats box
        stats_box = pygame.Rect(40, 100, self.width - 80, 550)
        pygame.draw.rect(self.screen, self.WHITE, stats_box, border_radius=15)
        pygame.draw.rect(self.screen, self.GRAY, stats_box, 3, border_radius=15)
        
        # Draw statistics
        stats_x = 60
        y_pos = 130
        
        # Overall Performance Section
        section_title = self.font_medium.render("Overall Performance", True, self.BLUE)
        self.screen.blit(section_title, (stats_x, y_pos))
        y_pos += 50
        
        # Calculate average depth
        avg_depth = self.summary_data['avg_depth']
        total_reps = self.summary_data['total_reps']
        
        # Overall grade based on average depth
        if avg_depth >= 90:
            grade = "PERFECT!"
            grade_color = self.GREEN
        elif avg_depth >= 75:
            grade = "GOOD"
            grade_color = (50, 205, 50)  # Lighter green
        elif avg_depth >= 60:
            grade = "NOT BAD"
            grade_color = self.BLUE
        else:
            grade = "NEEDS IMPROVEMENT"
            grade_color = self.RED
            
        # Display total reps
        reps_text = self.font_medium.render(f"Total Squats: {total_reps}", True, self.BLACK)
        self.screen.blit(reps_text, (stats_x + 20, y_pos))
        
        # Display average depth
        y_pos += 50
        depth_text = self.font_medium.render(f"Average Depth: {avg_depth:.1f}%", True, self.BLACK)
        self.screen.blit(depth_text, (stats_x + 20, y_pos))
        
        # Display grade
        y_pos += 80
        grade_text = self.font_large.render(f"Overall Grade: {grade}", True, grade_color)
        self.screen.blit(grade_text, (stats_x + 20, y_pos))
        
        # Individual Reps Section
        y_pos += 80
        section_title = self.font_medium.render("Individual Rep Details", True, self.BLUE)
        self.screen.blit(section_title, (stats_x, y_pos))
        y_pos += 40
        
        # Headers
        header_x = stats_x + 20
        headers = ["Rep #", "Depth", "Grade"]
        header_positions = [
            (header_x, headers[0]),
            (header_x + 120, headers[1]),
            (header_x + 270, headers[2])
        ]
        
        for x_pos, header in header_positions:
            header_text = self.font_small.render(header, True, self.BLUE)
            self.screen.blit(header_text, (x_pos, y_pos))
        
        y_pos += 30
        
        # Draw individual rep data
        for i, rep in enumerate(self.summary_data['reps']):
            row_y = y_pos + (i * 30)
            depth = rep['max_depth']
            
            # Rep number
            rep_num = self.font_small.render(f"#{i+1}", True, self.BLACK)
            self.screen.blit(rep_num, (header_x, row_y))
            
            # Depth
            depth_text = self.font_small.render(f"{depth:.1f}%", True, self.BLACK)
            self.screen.blit(depth_text, (header_x + 120, row_y))
            
            # Grade for individual rep
            if depth >= 90:
                rep_grade = "PERFECT!"
                grade_color = self.GREEN
            elif depth >= 75:
                rep_grade = "GOOD"
                grade_color = (50, 205, 50)
            elif depth >= 60:
                rep_grade = "NOT BAD"
                grade_color = self.BLUE
            else:
                rep_grade = "NEEDS IMPROVEMENT"
                grade_color = self.RED
            
            grade = self.font_small.render(rep_grade, True, grade_color)
            self.screen.blit(grade, (header_x + 270, row_y))
        
        # Draw continue button
        self.continue_button = Button(
            self.width//2 - 90,
            stats_box.bottom + 20,
            180, 50,
            "Continue",
            self.BLUE,
            (100, 181, 246)
        )
        self.continue_button.draw(self.screen, self.font_medium)

    def calculate_depth_consistency(self):
        depths = [rep['max_depth'] for rep in self.summary_data['reps']]
        if not depths:
            return 0
        avg_depth = sum(depths) / len(depths)
        variations = [abs(d - avg_depth) for d in depths]
        avg_variation = sum(variations) / len(variations)
        return max(0, 100 - (avg_variation * 2))  # Convert to percentage

    def calculate_angle_consistency(self):
        angles = [rep['lowest_angle'] for rep in self.summary_data['reps']]
        if not angles:
            return 0
        avg_angle = sum(angles) / len(angles)
        variations = [abs(a - avg_angle) for a in angles]
        avg_variation = sum(variations) / len(variations)
        return max(0, 100 - (avg_variation * 2))  # Convert to percentage

    def get_most_common_issue(self):
        all_issues = []
        for rep in self.summary_data['reps']:
            all_issues.extend(rep['form_issues'])
        if not all_issues:
            return "None"
        from collections import Counter
        return Counter(all_issues).most_common(1)[0][0]

    def update_display(self, frame, metrics):
        try:
            if self.show_summary:
                self.draw_summary_screen()
            else:
                self.screen.fill(self.LIGHT_BLUE)
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = cv2.resize(frame_rgb, (800, 600))
                frame_surface = pygame.surfarray.make_surface(np.rot90(frame_rgb))
                
                frame_x = (self.width - frame_surface.get_width()) // 2
                frame_y = (self.height - frame_surface.get_height()) // 2
                self.screen.blit(frame_surface, (frame_x, frame_y))
                
                if not self.show_instructions:
                    self.draw_feedback(metrics)
                    self.start_button.draw(self.screen, self.font_medium)
                    self.stop_button.draw(self.screen, self.font_medium)
                else:
                    self.draw_instructions()
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Display update error: {e}")

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        self.start_button.is_hovered = self.start_button.rect.collidepoint(mouse_pos)
        self.stop_button.is_hovered = self.stop_button.rect.collidepoint(mouse_pos)
        
        if self.show_summary:
            self.continue_button.is_hovered = self.continue_button.rect.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.show_instructions = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.show_summary:
                    if self.continue_button.rect.collidepoint(event.pos):
                        self.show_summary = False
                        return "RESET"
                elif not self.show_instructions:
                    if self.start_button.rect.collidepoint(event.pos):
                        self.recording = True
                    elif self.stop_button.rect.collidepoint(event.pos):
                        self.recording = False
                        return "SHOW_SUMMARY"
        return True

def rate_score(rate):
    if rate is None or not isinstance(rate, (int, float)):
        return 0
    if 100 <= rate <= 120:
        return 100
    else:
        return max(0, 100 - abs(110 - rate) * 2) 