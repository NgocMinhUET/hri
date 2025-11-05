"""
Speech-to-Text Engine - Chuyển giọng nói thành văn bản
Sử dụng Vosk (offline, nhanh) cho độ trễ thấp
"""
import json
import wave
from vosk import Model, KaldiRecognizer
from utils.logger import setup_logger
from utils.config_loader import get_config
from utils.audio_utils import AudioRecorder
from typing import Optional

class STTEngine:
    """Speech-to-Text với độ trễ thấp"""
    
    def __init__(self, config=None):
        """
        Args:
            config: ConfigLoader instance
        """
        self.config = config or get_config()
        self.logger = setup_logger("STT")
        
        # Load cấu hình
        self.sample_rate = self.config.get('stt.sample_rate', 16000)
        self.silence_duration = self.config.get('stt.silence_duration', 1.5)
        
        # Load Vosk model
        model_path = self.config.get('stt.model_path', 'models/vosk-model-small-vi-0.4')
        self.logger.info(f"Đang load Vosk model từ {model_path}...")
        
        try:
            self.model = Model(model_path)
            self.logger.info("Vosk model đã được load thành công!")
        except Exception as e:
            self.logger.error(f"Không thể load Vosk model: {e}")
            self.logger.error("Hãy tải model tại: https://alphacephei.com/vosk/models")
            raise
        
        # Audio recorder
        self.recorder = AudioRecorder(
            sample_rate=self.sample_rate,
            silence_duration=self.silence_duration
        )
    
    def transcribe_audio_data(self, audio_data: bytes) -> str:
        """
        Chuyển audio data thành văn bản
        
        Args:
            audio_data: Audio data dạng bytes (16-bit PCM)
        
        Returns:
            Văn bản nhận dạng được
        """
        recognizer = KaldiRecognizer(self.model, self.sample_rate)
        recognizer.SetWords(True)
        
        # Process audio
        if recognizer.AcceptWaveform(audio_data):
            result = json.loads(recognizer.Result())
        else:
            result = json.loads(recognizer.FinalResult())
        
        text = result.get('text', '')
        return text.strip()
    
    def transcribe_from_mic(self, mic_index: Optional[int] = None) -> str:
        """
        Ghi âm từ mic và chuyển thành văn bản
        
        Args:
            mic_index: Index của microphone (None = default)
        
        Returns:
            Văn bản nhận dạng được
        """
        self.logger.info("🎤 Đang ghi âm...")
        
        # Ghi âm
        audio_data = self.recorder.record(device_index=mic_index)
        
        # Transcribe
        self.logger.info("📝 Đang nhận dạng giọng nói...")
        text = self.transcribe_audio_data(audio_data)
        
        if text:
            self.logger.info(f"✅ Nhận dạng: '{text}'")
        else:
            self.logger.warning("⚠️ Không nhận dạng được gì.")
        
        return text
    
    def transcribe_from_file(self, wav_file: str) -> str:
        """
        Nhận dạng giọng nói từ file WAV
        
        Args:
            wav_file: Đường dẫn file WAV
        
        Returns:
            Văn bản nhận dạng được
        """
        self.logger.info(f"Đang nhận dạng từ file: {wav_file}")
        
        with wave.open(wav_file, 'rb') as wf:
            # Kiểm tra format
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != self.sample_rate:
                self.logger.error(f"File WAV phải là: mono, 16-bit, {self.sample_rate}Hz")
                return ""
            
            # Đọc audio data
            audio_data = wf.readframes(wf.getnframes())
        
        # Transcribe
        text = self.transcribe_audio_data(audio_data)
        
        if text:
            self.logger.info(f"✅ Nhận dạng: '{text}'")
        else:
            self.logger.warning("⚠️ Không nhận dạng được gì.")
        
        return text
    
    def listen_and_transcribe(self, mic_index: Optional[int] = None) -> str:
        """
        Alias cho transcribe_from_mic() - tên rõ nghĩa hơn
        """
        return self.transcribe_from_mic(mic_index)

# Test standalone
if __name__ == "__main__":
    import sys
    
    try:
        stt = STTEngine()
        
        print("\n🎤 STT Engine Test")
        print("=" * 50)
        print("Hãy nói gì đó...")
        print("(Dừng nói 1.5 giây để kết thúc)\n")
        
        text = stt.transcribe_from_mic()
        
        print("\n" + "=" * 50)
        print(f"📝 Kết quả: {text if text else '(không nhận dạng được)'}")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\nThoát chương trình.")
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

