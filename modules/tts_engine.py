"""
Text-to-Speech Engine - Chuyển văn bản thành giọng nói
Sử dụng pyttsx3 (offline, nhanh) cho độ trễ thấp
"""
import pyttsx3
from typing import Optional
from utils.logger import setup_logger
from utils.config_loader import get_config

class TTSEngine:
    """Text-to-Speech với độ trễ thấp"""
    
    def __init__(self, config=None):
        """
        Args:
            config: ConfigLoader instance
        """
        self.config = config or get_config()
        self.logger = setup_logger("TTS")
        
        # Khởi tạo pyttsx3
        self.engine = pyttsx3.init()
        
        # Load cấu hình
        rate = self.config.get('tts.rate', 150)
        volume = self.config.get('tts.volume', 0.9)
        
        # Cấu hình engine
        self.engine.setProperty('rate', rate)  # Tốc độ nói (words per minute)
        self.engine.setProperty('volume', volume)  # Volume (0.0 - 1.0)
        
        # Chọn voice (tìm Vietnamese voice nếu có)
        self._select_best_voice()
        
        self.logger.info("TTS Engine đã sẵn sàng!")
    
    def _select_best_voice(self):
        """Chọn voice tốt nhất (ưu tiên tiếng Việt nếu có)"""
        voices = self.engine.getProperty('voices')
        
        # Tìm Vietnamese voice
        vietnamese_voice = None
        for voice in voices:
            if 'vietnamese' in voice.name.lower() or 'vi' in voice.languages:
                vietnamese_voice = voice
                break
        
        if vietnamese_voice:
            self.engine.setProperty('voice', vietnamese_voice.id)
            self.logger.info(f"Đã chọn voice: {vietnamese_voice.name}")
        else:
            # Fallback: chọn voice đầu tiên
            if voices:
                self.engine.setProperty('voice', voices[0].id)
                self.logger.warning(f"Không tìm thấy Vietnamese voice, dùng: {voices[0].name}")
            else:
                self.logger.warning("Không tìm thấy voice nào!")
    
    def speak(self, text: str, block: bool = True):
        """
        Đọc văn bản
        
        Args:
            text: Văn bản cần đọc
            block: Đợi cho đến khi đọc xong (default: True)
        """
        if not text:
            self.logger.warning("Không có văn bản để đọc.")
            return
        
        self.logger.info(f"🔊 Đang nói: '{text}'")
        
        try:
            self.engine.say(text)
            
            if block:
                self.engine.runAndWait()
            
        except Exception as e:
            self.logger.error(f"Lỗi khi đọc văn bản: {e}")
    
    def speak_async(self, text: str):
        """
        Đọc văn bản không đồng bộ (không block)
        """
        self.speak(text, block=False)
    
    def stop(self):
        """Dừng đọc"""
        try:
            self.engine.stop()
            self.logger.info("Đã dừng TTS.")
        except Exception as e:
            self.logger.error(f"Lỗi khi dừng TTS: {e}")
    
    def set_rate(self, rate: int):
        """
        Đặt tốc độ nói
        
        Args:
            rate: Tốc độ (words per minute), thường 100-200
        """
        self.engine.setProperty('rate', rate)
        self.logger.info(f"Đã đặt tốc độ: {rate} WPM")
    
    def set_volume(self, volume: float):
        """
        Đặt âm lượng
        
        Args:
            volume: Âm lượng (0.0 - 1.0)
        """
        volume = max(0.0, min(1.0, volume))
        self.engine.setProperty('volume', volume)
        self.logger.info(f"Đã đặt âm lượng: {volume}")
    
    def list_voices(self):
        """Liệt kê tất cả voices có sẵn"""
        voices = self.engine.getProperty('voices')
        
        print("\n🔊 Danh sách Voices:")
        for i, voice in enumerate(voices):
            print(f"  [{i}] {voice.name}")
            print(f"      ID: {voice.id}")
            print(f"      Languages: {voice.languages}")
            print()

# Test standalone
if __name__ == "__main__":
    import sys
    
    try:
        tts = TTSEngine()
        
        print("\n🔊 TTS Engine Test")
        print("=" * 50)
        
        # List voices
        tts.list_voices()
        
        # Test speak
        print("\nTest 1: Tiếng Việt")
        tts.speak("Xin chào! Tôi là UET Bot, trợ lý AI thông minh của bạn.")
        
        print("\nTest 2: Tốc độ nhanh hơn")
        tts.set_rate(200)
        tts.speak("Đây là tốc độ nói nhanh hơn.")
        
        print("\nTest 3: Tốc độ chậm hơn")
        tts.set_rate(120)
        tts.speak("Và đây là tốc độ nói chậm hơn.")
        
        print("\n" + "=" * 50)
        print("✅ Test hoàn tất!")
        
    except KeyboardInterrupt:
        print("\nThoát chương trình.")
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

