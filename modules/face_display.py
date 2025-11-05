"""
Face Display - Giao diện hiển thị khuôn mặt với biểu cảm
Sử dụng Pygame để vẽ khuôn mặt hoạt hình
"""
import pygame
import math
import time
from enum import Enum
from typing import Tuple, Optional
from utils.logger import setup_logger
from utils.config_loader import get_config

class Emotion(Enum):
    """Các trạng thái biểu cảm"""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    HAPPY = "happy"
    SURPRISED = "surprised"

class FaceDisplay:
    """Hiển thị khuôn mặt với biểu cảm động"""
    
    # Colors
    BG_COLOR = (30, 30, 40)  # Background
    FACE_COLOR = (255, 255, 255)  # Màu mặt (trắng)
    EYE_COLOR = (50, 50, 50)  # Màu mắt (xám đen)
    MOUTH_COLOR = (50, 50, 50)  # Màu miệng
    ACCENT_COLOR = (100, 200, 255)  # Màu nhấn (xanh dương nhạt)
    
    def __init__(self, config=None):
        """
        Args:
            config: ConfigLoader instance
        """
        self.config = config or get_config()
        self.logger = setup_logger("FaceDisplay")
        
        # Load cấu hình
        self.width = self.config.get('face.window_width', 800)
        self.height = self.config.get('face.window_height', 600)
        self.fullscreen = self.config.get('face.fullscreen', False)
        self.fps = self.config.get('face.fps', 30)
        
        # Khởi tạo Pygame
        pygame.init()
        
        # Tạo window
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.width, self.height = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))
        
        pygame.display.set_caption("UETBot Face")
        self.clock = pygame.time.Clock()
        
        # State
        self.current_emotion = Emotion.IDLE
        self.is_running = False
        
        # Animation parameters
        self.blink_timer = 0
        self.blink_duration = 0.2
        self.blink_interval = 3.0
        self.is_blinking = False
        
        self.mouth_animation_offset = 0
        self.animation_time = 0
        
        # Center point
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        self.logger.info("FaceDisplay đã sẵn sàng!")
    
    def set_emotion(self, emotion: Emotion):
        """Đặt biểu cảm hiện tại"""
        if self.current_emotion != emotion:
            self.current_emotion = emotion
            self.logger.info(f"Emotion: {emotion.value}")
    
    def _draw_face_base(self):
        """Vẽ khuôn mặt cơ bản (hình tròn)"""
        face_radius = min(self.width, self.height) // 3
        
        # Vẽ mặt (hình tròn trắng)
        pygame.draw.circle(
            self.screen,
            self.FACE_COLOR,
            (self.center_x, self.center_y),
            face_radius
        )
        
        # Viền
        pygame.draw.circle(
            self.screen,
            self.ACCENT_COLOR,
            (self.center_x, self.center_y),
            face_radius,
            5
        )
        
        return face_radius
    
    def _draw_eyes(self, face_radius: int):
        """Vẽ mắt"""
        eye_offset_x = face_radius // 3
        eye_offset_y = -face_radius // 6
        
        left_eye_pos = (self.center_x - eye_offset_x, self.center_y + eye_offset_y)
        right_eye_pos = (self.center_x + eye_offset_x, self.center_y + eye_offset_y)
        
        # Emotion-specific eye size
        if self.current_emotion == Emotion.SURPRISED:
            eye_width = 40
            eye_height = 50
        elif self.is_blinking:
            eye_width = 40
            eye_height = 5
        else:
            eye_width = 40
            eye_height = 40
        
        # Vẽ mắt
        pygame.draw.ellipse(
            self.screen,
            self.EYE_COLOR,
            (*left_eye_pos, eye_width, eye_height)
        )
        pygame.draw.ellipse(
            self.screen,
            self.EYE_COLOR,
            (*right_eye_pos, eye_width, eye_height)
        )
        
        # Listening: thêm gợn sóng xung quanh mắt
        if self.current_emotion == Emotion.LISTENING:
            for i in range(3):
                offset = 10 + i * 8
                alpha = int(100 - i * 30)
                s = pygame.Surface((eye_width + offset*2, eye_height + offset*2), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (*self.ACCENT_COLOR, alpha), s.get_rect(), 2)
                self.screen.blit(s, (left_eye_pos[0] - offset, left_eye_pos[1] - offset))
                self.screen.blit(s, (right_eye_pos[0] - offset, right_eye_pos[1] - offset))
    
    def _draw_mouth(self, face_radius: int):
        """Vẽ miệng"""
        mouth_y = self.center_y + face_radius // 3
        
        if self.current_emotion == Emotion.IDLE:
            # Idle: đường thẳng
            pygame.draw.line(
                self.screen,
                self.MOUTH_COLOR,
                (self.center_x - 50, mouth_y),
                (self.center_x + 50, mouth_y),
                5
            )
        
        elif self.current_emotion == Emotion.HAPPY:
            # Happy: nụ cười
            mouth_rect = pygame.Rect(self.center_x - 60, mouth_y - 30, 120, 60)
            pygame.draw.arc(
                self.screen,
                self.MOUTH_COLOR,
                mouth_rect,
                0,
                math.pi,
                8
            )
        
        elif self.current_emotion == Emotion.SURPRISED:
            # Surprised: hình tròn
            pygame.draw.circle(
                self.screen,
                self.MOUTH_COLOR,
                (self.center_x, mouth_y + 10),
                25
            )
        
        elif self.current_emotion == Emotion.SPEAKING:
            # Speaking: animation lên xuống
            offset = int(math.sin(self.animation_time * 10) * 15)
            mouth_points = [
                (self.center_x - 40, mouth_y + offset),
                (self.center_x - 20, mouth_y - offset),
                (self.center_x, mouth_y + offset),
                (self.center_x + 20, mouth_y - offset),
                (self.center_x + 40, mouth_y + offset),
            ]
            pygame.draw.lines(
                self.screen,
                self.MOUTH_COLOR,
                False,
                mouth_points,
                6
            )
        
        elif self.current_emotion == Emotion.LISTENING:
            # Listening: đường nhỏ (đang chờ)
            pygame.draw.circle(
                self.screen,
                self.MOUTH_COLOR,
                (self.center_x, mouth_y),
                15,
                3
            )
        
        elif self.current_emotion == Emotion.THINKING:
            # Thinking: đường cong nhỏ
            mouth_rect = pygame.Rect(self.center_x - 40, mouth_y - 20, 80, 40)
            pygame.draw.arc(
                self.screen,
                self.MOUTH_COLOR,
                mouth_rect,
                math.pi,
                2 * math.pi,
                5
            )
            
            # Thêm "thinking dots"
            for i in range(3):
                x = self.center_x + face_radius + 20 + i * 20
                y = self.center_y - face_radius // 2 + int(math.sin(self.animation_time * 3 + i) * 5)
                pygame.draw.circle(self.screen, self.ACCENT_COLOR, (x, y), 8)
    
    def _draw_text(self, text: str, y_offset: int = -250):
        """Vẽ text trên màn hình"""
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, self.ACCENT_COLOR)
        text_rect = text_surface.get_rect(center=(self.center_x, self.center_y + y_offset))
        self.screen.blit(text_surface, text_rect)
    
    def update(self, dt: float):
        """
        Cập nhật animation
        
        Args:
            dt: Delta time (seconds)
        """
        self.animation_time += dt
        
        # Blink animation
        self.blink_timer += dt
        if self.blink_timer >= self.blink_interval:
            self.is_blinking = True
            self.blink_timer = 0
        
        if self.is_blinking:
            if self.blink_timer >= self.blink_duration:
                self.is_blinking = False
    
    def draw(self):
        """Vẽ toàn bộ khuôn mặt"""
        # Clear screen
        self.screen.fill(self.BG_COLOR)
        
        # Vẽ các phần của mặt
        face_radius = self._draw_face_base()
        self._draw_eyes(face_radius)
        self._draw_mouth(face_radius)
        
        # Vẽ status text
        emotion_text = f"🤖 {self.current_emotion.value.upper()}"
        self._draw_text(emotion_text)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Chạy display loop"""
        self.is_running = True
        self.logger.info("Bắt đầu face display loop...")
        
        try:
            while self.is_running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                            self.is_running = False
                        # Test emotions với phím số
                        elif event.key == pygame.K_1:
                            self.set_emotion(Emotion.IDLE)
                        elif event.key == pygame.K_2:
                            self.set_emotion(Emotion.LISTENING)
                        elif event.key == pygame.K_3:
                            self.set_emotion(Emotion.THINKING)
                        elif event.key == pygame.K_4:
                            self.set_emotion(Emotion.SPEAKING)
                        elif event.key == pygame.K_5:
                            self.set_emotion(Emotion.HAPPY)
                        elif event.key == pygame.K_6:
                            self.set_emotion(Emotion.SURPRISED)
                
                # Update animation
                dt = self.clock.tick(self.fps) / 1000.0
                self.update(dt)
                
                # Draw
                self.draw()
                
        except KeyboardInterrupt:
            self.logger.info("Dừng face display loop.")
        finally:
            self.stop()
    
    def stop(self):
        """Dừng display"""
        self.is_running = False
        pygame.quit()
        self.logger.info("Đã dừng face display.")

# Test standalone
if __name__ == "__main__":
    import sys
    
    try:
        face = FaceDisplay()
        
        print("\n😊 Face Display Test")
        print("=" * 50)
        print("Nhấn phím số để thay đổi emotion:")
        print("  1 = Idle")
        print("  2 = Listening")
        print("  3 = Thinking")
        print("  4 = Speaking")
        print("  5 = Happy")
        print("  6 = Surprised")
        print("\nNhấn ESC hoặc Q để thoát\n")
        
        face.run()
        
    except KeyboardInterrupt:
        print("\nThoát chương trình.")
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

