"""
Audio Utils - Các hàm tiện ích xử lý audio
"""
import pyaudio
import wave
import numpy as np
from typing import Optional
import webrtcvad

class AudioRecorder:
    """Ghi âm với Voice Activity Detection"""
    
    def __init__(self, 
                 sample_rate=16000,
                 channels=1,
                 chunk_size=1024,
                 silence_duration=1.5):
        """
        Args:
            sample_rate: Tần số mẫu (Hz)
            channels: Số kênh audio (1=mono, 2=stereo)
            chunk_size: Kích thước chunk
            silence_duration: Thời gian im lặng để kết thúc (giây)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.silence_duration = silence_duration
        
        self.audio = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad(2)  # Aggressiveness: 0-3
        
    def record(self, device_index: Optional[int] = None) -> bytes:
        """
        Ghi âm cho đến khi phát hiện im lặng
        
        Returns:
            Audio data dạng bytes
        """
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.chunk_size
        )
        
        frames = []
        silence_chunks = 0
        silence_threshold = int(self.silence_duration * self.sample_rate / self.chunk_size)
        
        print("🎤 Đang lắng nghe...")
        
        try:
            while True:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Voice Activity Detection
                is_speech = self.vad.is_speech(data, self.sample_rate)
                
                if not is_speech:
                    silence_chunks += 1
                    if silence_chunks > silence_threshold:
                        print("🔇 Phát hiện im lặng, kết thúc ghi âm.")
                        break
                else:
                    silence_chunks = 0
                    
        except KeyboardInterrupt:
            print("\n⏹️ Dừng ghi âm.")
        finally:
            stream.stop_stream()
            stream.close()
        
        return b''.join(frames)
    
    def save_wav(self, data: bytes, filename: str):
        """Lưu audio data ra file WAV"""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(data)
    
    def play(self, data: bytes, device_index: Optional[int] = None):
        """Phát audio"""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
            output_device_index=device_index
        )
        
        stream.write(data)
        stream.stop_stream()
        stream.close()
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'audio'):
            self.audio.terminate()

def list_audio_devices():
    """Liệt kê tất cả audio devices"""
    audio = pyaudio.PyAudio()
    
    print("\n🎧 Danh sách Microphones:")
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"  [{i}] {info['name']}")
    
    print("\n🔊 Danh sách Speakers:")
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxOutputChannels'] > 0:
            print(f"  [{i}] {info['name']}")
    
    audio.terminate()

if __name__ == "__main__":
    # Test audio devices
    list_audio_devices()

