"""
Wake Word Detection - Phát hiện từ khóa "Hi UETBot"
Sử dụng Vosk cho nhận dạng giọng nói liên tục
"""
import pyaudio
import json
import time
from vosk import Model, KaldiRecognizer
from utils.logger import setup_logger
from utils.config_loader import get_config
from typing import Optional, Callable

class WakeWordDetector:
    """Phát hiện wake word để đánh thức bot"""
    
    def __init__(self, config=None):
        """
        Args:
            config: ConfigLoader instance
        """
        self.config = config or get_config()
        self.logger = setup_logger("WakeWord")
        
        # Load cấu hình
        self.keyword = self.config.get('wake_word.keyword', 'hi uetbot').lower()
        self.sample_rate = self.config.get('audio.sample_rate', 16000)
        self.chunk_size = self.config.get('audio.chunk_size', 1024)
        
        # Load Vosk model
        model_path = self.config.get('stt.model_path', 'models/vosk-model-small-vi-0.4')
        self.logger.info(f"Đang load Vosk model từ {model_path}...")
        
        try:
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)
        except Exception as e:
            self.logger.error(f"Không thể load Vosk model: {e}")
            raise
        
        # Audio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_listening = False
        
        self.logger.info(f"WakeWordDetector đã sẵn sàng! Keyword: '{self.keyword}'")
    
    def start_listening(self, mic_index: Optional[int] = None):
        """Bắt đầu lắng nghe wake word"""
        if self.is_listening:
            self.logger.warning("Đã đang lắng nghe rồi!")
            return
        
        self.logger.info("Bắt đầu lắng nghe wake word...")
        
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=mic_index,
                frames_per_buffer=self.chunk_size
            )
            self.is_listening = True
            self.logger.info(f"🎤 Đang lắng nghe '{self.keyword}'...")
            
        except Exception as e:
            self.logger.error(f"Không thể mở microphone: {e}")
            raise
    
    def stop_listening(self):
        """Dừng lắng nghe"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        self.is_listening = False
        self.logger.info("Đã dừng lắng nghe.")
    
    def check_for_wake_word(self) -> bool:
        """
        Kiểm tra xem có phát hiện wake word không
        
        Returns:
            True nếu phát hiện wake word
        """
        if not self.is_listening or not self.stream:
            return False
        
        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '').lower()
                
                if text:
                    self.logger.debug(f"Nhận dạng: '{text}'")
                    
                    # Kiểm tra wake word
                    if self.keyword in text:
                        self.logger.info(f"✅ Phát hiện wake word: '{text}'")
                        return True
            
        except Exception as e:
            self.logger.error(f"Lỗi khi đọc audio: {e}")
        
        return False
    
    def wait_for_wake_word(self, timeout: Optional[float] = None) -> bool:
        """
        Đợi cho đến khi phát hiện wake word
        
        Args:
            timeout: Thời gian chờ tối đa (giây), None = vô hạn
        
        Returns:
            True nếu phát hiện wake word, False nếu timeout
        """
        start_time = time.time()
        
        while True:
            if self.check_for_wake_word():
                return True
            
            # Kiểm tra timeout
            if timeout and (time.time() - start_time) > timeout:
                self.logger.info("⏱️ Timeout chờ wake word.")
                return False
            
            time.sleep(0.01)  # Tránh CPU 100%
    
    def run_loop(self, callback: Callable):
        """
        Chạy loop liên tục, gọi callback khi phát hiện wake word
        
        Args:
            callback: Hàm được gọi khi phát hiện wake word
        """
        self.logger.info("Bắt đầu wake word detection loop...")
        
        try:
            while self.is_listening:
                if self.check_for_wake_word():
                    callback()
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            self.logger.info("Dừng wake word detection loop.")
    
    def __del__(self):
        """Cleanup"""
        self.stop_listening()
        if hasattr(self, 'audio'):
            self.audio.terminate()

# Test standalone
if __name__ == "__main__":
    import sys
    
    def on_wake_word_detected():
        print("\n🔔 Wake word detected! Bot đã được đánh thức!\n")
    
    try:
        detector = WakeWordDetector()
        detector.start_listening()
        
        print(f"💡 Hãy nói: '{detector.keyword}'")
        print("   (Nhấn Ctrl+C để thoát)")
        
        detector.run_loop(callback=on_wake_word_detected)
        
    except KeyboardInterrupt:
        print("\nThoát chương trình.")
    except Exception as e:
        print(f"Lỗi: {e}")
        sys.exit(1)

