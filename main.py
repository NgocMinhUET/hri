"""
UETBot - AI Kiosk Bot
Main entry point tích hợp tất cả module
"""
import argparse
import threading
import time
import sys
from enum import Enum

from utils.logger import setup_logger
from utils.config_loader import get_config
from modules.person_detector import PersonDetector
from modules.wake_word import WakeWordDetector
from modules.stt_engine import STTEngine
from modules.llm_client import LLMClient
from modules.tts_engine import TTSEngine
from modules.face_display import FaceDisplay, Emotion

class BotState(Enum):
    """Các trạng thái của bot"""
    IDLE = "idle"  # Đang chờ kích hoạt
    WAITING_WAKE_WORD = "waiting_wake_word"  # Đang chờ wake word
    LISTENING = "listening"  # Đang lắng nghe user
    THINKING = "thinking"  # Đang xử lý với LLM
    SPEAKING = "speaking"  # Đang nói
    ERROR = "error"  # Lỗi

class UETBot:
    """AI Kiosk Bot chính"""
    
    def __init__(self, config_path="config.yaml"):
        """
        Args:
            config_path: Đường dẫn file cấu hình
        """
        # Load config
        self.config = get_config(config_path)
        self.logger = setup_logger("UETBot", log_file="uetbot.log")
        
        self.logger.info("=" * 70)
        self.logger.info("🤖 Khởi động UETBot...")
        self.logger.info("=" * 70)
        
        # State
        self.state = BotState.IDLE
        self.is_running = False
        
        # Flags từ config
        self.enable_person_detection = self.config.get('person_detection.enable', True)
        self.enable_wake_word = self.config.get('wake_word.enable', True)
        self.conversation_timeout = self.config.get('general.conversation_timeout', 30)
        
        # Initialize modules
        self.logger.info("Đang khởi tạo các module...")
        
        try:
            # Face Display (chạy trong thread riêng)
            self.face = FaceDisplay(self.config)
            self.face_thread = None
            
            # Person Detector (optional)
            if self.enable_person_detection:
                self.person_detector = PersonDetector(self.config)
                self.person_detector.start_camera()
            else:
                self.person_detector = None
                self.logger.info("Person detection đã bị tắt.")
            
            # Wake Word Detector (optional)
            if self.enable_wake_word:
                self.wake_word_detector = WakeWordDetector(self.config)
                self.wake_word_detector.start_listening()
            else:
                self.wake_word_detector = None
                self.logger.info("Wake word detection đã bị tắt.")
            
            # STT
            self.stt = STTEngine(self.config)
            
            # LLM
            self.llm = LLMClient(self.config)
            
            # TTS
            self.tts = TTSEngine(self.config)
            
            self.logger.info("✅ Tất cả module đã sẵn sàng!")
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi khởi tạo module: {e}")
            raise
    
    def set_state(self, state: BotState):
        """Thay đổi trạng thái bot"""
        if self.state != state:
            self.logger.info(f"State: {self.state.value} -> {state.value}")
            self.state = state
            
            # Cập nhật face emotion theo state
            emotion_map = {
                BotState.IDLE: Emotion.IDLE,
                BotState.WAITING_WAKE_WORD: Emotion.IDLE,
                BotState.LISTENING: Emotion.LISTENING,
                BotState.THINKING: Emotion.THINKING,
                BotState.SPEAKING: Emotion.SPEAKING,
            }
            
            if state in emotion_map:
                self.face.set_emotion(emotion_map[state])
    
    def wait_for_activation(self) -> bool:
        """
        Đợi cho đến khi bot được kích hoạt
        (Qua person detection hoặc wake word)
        
        Returns:
            True nếu được kích hoạt thành công
        """
        self.set_state(BotState.IDLE)
        
        self.logger.info("👀 Đang chờ kích hoạt...")
        self.logger.info(f"   - Person detection: {'ON' if self.enable_person_detection else 'OFF'}")
        self.logger.info(f"   - Wake word: {'ON' if self.enable_wake_word else 'OFF'}")
        
        while self.is_running:
            # Kiểm tra person detection
            if self.enable_person_detection and self.person_detector:
                if self.person_detector.detect_person_in_zone():
                    self.logger.info("✅ Kích hoạt bởi: Person Detection")
                    self.face.set_emotion(Emotion.HAPPY)
                    time.sleep(0.5)  # Show happy emotion
                    return True
            
            # Kiểm tra wake word
            if self.enable_wake_word and self.wake_word_detector:
                if self.wake_word_detector.check_for_wake_word():
                    self.logger.info("✅ Kích hoạt bởi: Wake Word")
                    self.face.set_emotion(Emotion.HAPPY)
                    time.sleep(0.5)
                    return True
            
            time.sleep(0.1)
        
        return False
    
    def handle_conversation(self):
        """Xử lý một lượt hội thoại"""
        try:
            # 1. Chào hỏi
            self.set_state(BotState.SPEAKING)
            greeting = "Xin chào! Tôi có thể giúp gì cho bạn?"
            self.tts.speak(greeting)
            
            # 2. Lắng nghe user
            self.set_state(BotState.LISTENING)
            self.logger.info("🎤 Đang lắng nghe...")
            
            user_text = self.stt.transcribe_from_mic()
            
            if not user_text:
                self.logger.warning("Không nghe rõ, thử lại...")
                self.set_state(BotState.SPEAKING)
                self.tts.speak("Xin lỗi, tôi không nghe rõ. Bạn có thể nói lại không?")
                return
            
            self.logger.info(f"👤 User: {user_text}")
            
            # 3. Xử lý với LLM
            self.set_state(BotState.THINKING)
            self.logger.info("🧠 Đang suy nghĩ...")
            
            response = self.llm.generate_response(user_text)
            
            # 4. Trả lời
            self.set_state(BotState.SPEAKING)
            self.logger.info(f"🤖 Bot: {response}")
            
            self.tts.speak(response)
            
            # 5. Show happy emotion sau khi hoàn thành
            self.face.set_emotion(Emotion.HAPPY)
            time.sleep(1)
            
        except Exception as e:
            self.logger.error(f"Lỗi trong conversation: {e}")
            self.set_state(BotState.SPEAKING)
            self.tts.speak("Xin lỗi, tôi gặp sự cố kỹ thuật.")
    
    def run_face_display(self):
        """Chạy face display trong thread riêng"""
        self.face.run()
    
    def run(self):
        """Chạy main loop của bot"""
        self.is_running = True
        
        # Start face display thread
        self.face_thread = threading.Thread(target=self.run_face_display, daemon=True)
        self.face_thread.start()
        
        self.logger.info("🚀 UETBot đã sẵn sàng hoạt động!")
        self.logger.info("   (Nhấn Ctrl+C để dừng)")
        
        try:
            while self.is_running:
                # Đợi kích hoạt
                activated = self.wait_for_activation()
                
                if not activated:
                    continue
                
                # Xử lý hội thoại
                self.handle_conversation()
                
                # Reset conversation sau mỗi lượt
                self.llm.reset_conversation()
                
                # Chờ một chút trước khi về idle
                time.sleep(2)
                
        except KeyboardInterrupt:
            self.logger.info("\n⏹️ Dừng bot...")
        except Exception as e:
            self.logger.error(f"Lỗi không mong đợi: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()
    
    def stop(self):
        """Dừng bot và cleanup"""
        self.logger.info("Đang dừng tất cả module...")
        
        self.is_running = False
        
        # Stop modules
        if self.person_detector:
            self.person_detector.stop_camera()
        
        if self.wake_word_detector:
            self.wake_word_detector.stop_listening()
        
        self.face.stop()
        
        self.logger.info("✅ UETBot đã dừng.")
        self.logger.info("=" * 70)

def main():
    """Entry point"""
    parser = argparse.ArgumentParser(description="UETBot - AI Kiosk Bot")
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Đường dẫn file cấu hình (default: config.yaml)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Bật debug mode'
    )
    parser.add_argument(
        '--no-person-detection',
        action='store_true',
        help='Tắt person detection'
    )
    parser.add_argument(
        '--no-wake-word',
        action='store_true',
        help='Tắt wake word detection'
    )
    
    args = parser.parse_args()
    
    try:
        # Tạo bot
        bot = UETBot(config_path=args.config)
        
        # Override settings từ command line
        if args.no_person_detection:
            bot.enable_person_detection = False
            if bot.person_detector:
                bot.person_detector.stop_camera()
                bot.person_detector = None
        
        if args.no_wake_word:
            bot.enable_wake_word = False
            if bot.wake_word_detector:
                bot.wake_word_detector.stop_listening()
                bot.wake_word_detector = None
        
        # Chạy bot
        bot.run()
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

