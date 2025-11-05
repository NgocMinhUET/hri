# 🏗️ Kiến trúc Hệ thống UETBot

Tài liệu chi tiết về kiến trúc và luồng hoạt động của UETBot.

---

## 📊 Tổng quan Kiến trúc

```
┌─────────────────────────────────────────────────────────────────┐
│                         UETBot System                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         Main Controller (main.py)        │
        │  • State Management                      │
        │  • Module Orchestration                  │
        │  • Conversation Flow Control             │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┴───────────────────────┐
        │                                             │
        ▼                                             ▼
┌─────────────────┐                         ┌─────────────────┐
│  INPUT MODULES  │                         │ OUTPUT MODULES  │
└─────────────────┘                         └─────────────────┘
        │                                             │
        ├─► 👁️ Person Detector                      ├─► 🔊 TTS Engine
        │    (Camera IMX477)                          │    (pyttsx3)
        │                                             │
        ├─► 🎤 Wake Word Detector                   ├─► 😊 Face Display
        │    (Vosk)                                  │    (Pygame)
        │                                             │
        └─► 🎙️ STT Engine                           └────────────────
             (Vosk)
                              │
                              ▼
                    ┌──────────────────┐
                    │  🧠 LLM Client    │
                    │  (Gemini API)     │
                    └──────────────────┘
```

---

## 🔄 Luồng Hoạt động (State Flow)

### State Diagram

```
     ┌──────────┐
     │  IDLE    │ ◄────────────────────────┐
     └──────────┘                          │
          │                                │
          │ [Person Detected OR           │
          │  Wake Word Heard]             │
          ▼                                │
  ┌──────────────┐                        │
  │  SPEAKING    │                        │
  │ (Greeting)   │                        │
  └──────────────┘                        │
          │                                │
          ▼                                │
  ┌──────────────┐                        │
  │  LISTENING   │                        │
  │  (STT)       │                        │
  └──────────────┘                        │
          │                                │
          ▼                                │
  ┌──────────────┐                        │
  │  THINKING    │                        │
  │  (LLM)       │                        │
  └──────────────┘                        │
          │                                │
          ▼                                │
  ┌──────────────┐                        │
  │  SPEAKING    │                        │
  │ (Response)   │                        │
  └──────────────┘                        │
          │                                │
          │ [Conversation Timeout]        │
          └────────────────────────────────┘
```

### Chi tiết từng State

#### 1. **IDLE** (Chờ kích hoạt)
- **Emotion**: Idle face
- **Hoạt động**:
  - Person Detector: Quét vùng detection liên tục
  - Wake Word Detector: Lắng nghe keyword "Hi UETBot"
- **Chuyển state**: Khi phát hiện người HOẶC nghe wake word → SPEAKING

#### 2. **SPEAKING** (Chào hỏi)
- **Emotion**: Speaking face (animated)
- **Hoạt động**:
  - TTS: "Xin chào! Tôi có thể giúp gì cho bạn?"
- **Chuyển state**: Sau khi nói xong → LISTENING

#### 3. **LISTENING** (Lắng nghe)
- **Emotion**: Listening face (với gợn sóng)
- **Hoạt động**:
  - STT: Ghi âm và chuyển đổi giọng nói thành text
  - Voice Activity Detection: Tự động kết thúc khi im lặng
- **Chuyển state**: Sau khi có text → THINKING

#### 4. **THINKING** (Suy nghĩ)
- **Emotion**: Thinking face (với dots animation)
- **Hoạt động**:
  - LLM Client: Gửi request tới Gemini API
  - Xử lý response
- **Chuyển state**: Sau khi có response → SPEAKING

#### 5. **SPEAKING** (Trả lời)
- **Emotion**: Speaking face (animated)
- **Hoạt động**:
  - TTS: Đọc response từ LLM
- **Chuyển state**: 
  - Sau khi nói xong → HAPPY (1s) → IDLE

---

## 🧩 Chi tiết Module

### 1. 👁️ Person Detector (`modules/person_detector.py`)

**Công nghệ**: YOLOv8 Nano

**Chức năng**:
- Phát hiện người trong frame camera
- Xác định vị trí center của bounding box
- Kiểm tra xem center có trong detection zone không
- Cooldown mechanism để tránh trigger liên tục

**Pipeline**:
```
Camera → Frame → YOLOv8 → Bounding Boxes → 
Filter (class=person, conf>threshold) → 
Check center in zone → Trigger (with cooldown)
```

**Tối ưu cho Jetson Nano**:
- YOLOv8n (nano): ~6MB, nhanh nhất
- Resolution 640x480
- Có thể giảm xuống 320x240 nếu cần

---

### 2. 🎤 Wake Word Detector (`modules/wake_word.py`)

**Công nghệ**: Vosk (offline speech recognition)

**Chức năng**:
- Lắng nghe audio stream liên tục
- Nhận dạng giọng nói real-time
- Phát hiện keyword "Hi UETBot"

**Pipeline**:
```
Microphone → Audio Stream → Vosk Recognizer → 
Text → Keyword Matching → Trigger
```

**Ưu điểm**:
- Hoàn toàn offline
- Độ trễ thấp (<100ms)
- Hỗ trợ tiếng Việt

---

### 3. 🎙️ STT Engine (`modules/stt_engine.py`)

**Công nghệ**: Vosk + Voice Activity Detection (VAD)

**Chức năng**:
- Ghi âm từ microphone
- Phát hiện im lặng để auto-stop
- Chuyển đổi audio thành text

**Pipeline**:
```
Microphone → Audio Recording → 
VAD (detect silence) → Stop Recording → 
Vosk Transcription → Text
```

**Tối ưu**:
- Sample rate: 16kHz (đủ cho giọng nói)
- Silence duration: 1.5s (có thể tune)
- WebRTC VAD: Aggressiveness level 2

---

### 4. 🧠 LLM Client (`modules/llm_client.py`)

**Công nghệ**: Google Gemini API

**Chức năng**:
- Gửi user message tới Gemini
- Duy trì conversation history
- Xử lý response

**Pipeline**:
```
User Text → [System Prompt +] Message → 
Gemini API → Response → 
Save to History → Return Text
```

**Features**:
- System prompt: Tùy chỉnh tính cách bot
- Temperature: 0.7 (cân bằng creativity/coherence)
- Max tokens: 150 (response ngắn gọn)
- Conversation reset sau mỗi session

**API Free Tier**:
- 60 requests/phút
- Đủ cho use case kiosk

---

### 5. 🔊 TTS Engine (`modules/tts_engine.py`)

**Công nghệ**: pyttsx3 (offline TTS)

**Chức năng**:
- Chuyển text thành giọng nói
- Điều chỉnh rate, volume
- Chọn voice (ưu tiên Vietnamese nếu có)

**Pipeline**:
```
Text → pyttsx3 Engine → 
Audio Synthesis → Speaker Output
```

**Ưu điểm**:
- Hoàn toàn offline
- Độ trễ cực thấp (~50ms)
- Không cần network

**Nhược điểm**:
- Chất lượng giọng không tự nhiên như cloud TTS
- Hỗ trợ tiếng Việt hạn chế (phụ thuộc espeak)

**Alternative**: 
- gTTS (Google TTS) - online, chất lượng tốt hơn nhưng có độ trễ

---

### 6. 😊 Face Display (`modules/face_display.py`)

**Công nghệ**: Pygame

**Chức năng**:
- Hiển thị khuôn mặt hoạt hình
- 6 emotions: idle, listening, thinking, speaking, happy, surprised
- Animation: blink, mouth movement, thinking dots

**Emotions**:

| Emotion | Mô tả | Animation |
|---------|-------|-----------|
| **Idle** | Trạng thái chờ | Blink định kỳ, miệng thẳng |
| **Listening** | Đang lắng nghe | Gợn sóng xung quanh mắt |
| **Thinking** | Đang suy nghĩ | Thinking dots bay lên xuống |
| **Speaking** | Đang nói | Miệng chuyển động sóng |
| **Happy** | Vui vẻ | Nụ cười (arc curve) |
| **Surprised** | Ngạc nhiên | Mắt to, miệng tròn |

**Drawing Pipeline**:
```
Clear Screen → Draw Face Base (circle) → 
Draw Eyes (emotion-specific) → 
Draw Mouth (emotion-specific) → 
Draw Text → Flip Display
```

**Animation Loop**:
- FPS: 30
- Blink interval: 3s
- Blink duration: 0.2s

---

## 🔧 Utilities

### Config Loader (`utils/config_loader.py`)
- Load `config.yaml`
- Inject environment variables từ `.env`
- Singleton pattern
- Hỗ trợ nested key access: `config.get('camera.resolution.width')`

### Logger (`utils/logger.py`)
- Consistent logging format
- Console + file output
- Level: DEBUG, INFO, WARNING, ERROR

### Audio Utils (`utils/audio_utils.py`)
- AudioRecorder với VAD
- List audio devices
- Save/load WAV files

---

## 📊 Luồng Dữ liệu Chi tiết

### Conversation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    ACTIVATION PHASE                          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
  ┌──────────────┐                    ┌──────────────┐
  │ Person Det.  │                    │  Wake Word   │
  │ (Camera)     │                    │  (Mic)       │
  └──────────────┘                    └──────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  CONVERSATION PHASE                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  Greeting    │
                    │  (TTS)       │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  Listen      │
                    │  (STT)       │
                    └──────────────┘
                            │
                            │ user_text
                            ▼
                    ┌──────────────┐
                    │  Process     │
                    │  (LLM)       │
                    └──────────────┘
                            │
                            │ response_text
                            ▼
                    ┌──────────────┐
                    │  Respond     │
                    │  (TTS)       │
                    └──────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     RESET PHASE                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Reset conversation
                            │ Return to IDLE
                            ▼
```

---

## 🔒 Thread Safety & Concurrency

### Threading Model

```
Main Thread
    ├─► Face Display Thread (daemon)
    │   └─► Pygame event loop
    │
    └─► Main Loop
        ├─► Person Detection (polling)
        ├─► Wake Word Detection (polling)
        └─► Conversation Handler
            ├─► STT (blocking)
            ├─► LLM (blocking)
            └─► TTS (blocking)
```

**Lưu ý**:
- Face Display chạy trong thread riêng để không block main loop
- STT, LLM, TTS đều blocking - chạy tuần tự trong main thread
- Person Detection và Wake Word polling mỗi 0.1s

---

## 📈 Performance Considerations

### Jetson Nano Specs
- CPU: Quad-core ARM A57 @ 1.43 GHz
- GPU: 128-core Maxwell
- RAM: 4GB LPDDR4
- Storage: microSD

### Bottlenecks & Solutions

| Component | Bottleneck | Solution |
|-----------|------------|----------|
| **YOLOv8** | GPU inference | Use YOLOv8n, lower resolution |
| **Vosk STT** | CPU processing | Use small model, 16kHz |
| **Gemini API** | Network latency | Keep response short (max_tokens=150) |
| **pyttsx3 TTS** | CPU synthesis | Already very fast (<50ms) |
| **Pygame** | Display rendering | 30 FPS is enough |

### Expected Latency

| Operation | Latency | Notes |
|-----------|---------|-------|
| Person Detection | ~100ms | Per frame (YOLOv8n @ 640x480) |
| Wake Word Detection | <100ms | Real-time with Vosk |
| STT Transcription | ~500ms | Depends on audio length |
| LLM Response | 1-3s | Network + API processing |
| TTS Synthesis | ~50ms | pyttsx3 is very fast |
| **Total (per turn)** | **2-5s** | Acceptable for kiosk |

---

## 🛡️ Error Handling

### Error Categories

1. **Hardware Errors**
   - Camera not found
   - Microphone not found
   - Speaker not found

2. **Model Errors**
   - YOLOv8 model not found
   - Vosk model not found

3. **API Errors**
   - Gemini API key invalid
   - Gemini API rate limit
   - Network timeout

4. **Runtime Errors**
   - Audio buffer overflow
   - Out of memory

### Error Handling Strategy

```python
try:
    # Main operation
except SpecificError as e:
    logger.error(f"Error: {e}")
    # Fallback behavior
    # User-friendly message via TTS
finally:
    # Cleanup
```

---

## 🎯 Future Improvements

### 1. Performance
- [ ] YOLOv8 INT8 quantization cho tốc độ nhanh hơn
- [ ] Cache Gemini responses cho câu hỏi thường gặp
- [ ] Parallel processing: STT + Face animation

### 2. Features
- [ ] Multi-language support
- [ ] Gesture recognition (từ camera)
- [ ] Context-aware responses (nhớ conversation dài hạn)
- [ ] Custom wake word training

### 3. UI/UX
- [ ] Touchscreen support
- [ ] QR code display cho thông tin
- [ ] Avatar 3D thay vì 2D face

### 4. Deployment
- [ ] Docker container
- [ ] Auto-update mechanism
- [ ] Remote monitoring dashboard
- [ ] Analytics & logging

---

## 📚 References

- **YOLOv8**: https://github.com/ultralytics/ultralytics
- **Vosk**: https://alphacephei.com/vosk/
- **Gemini API**: https://ai.google.dev/
- **pyttsx3**: https://github.com/nateshmbhat/pyttsx3
- **Pygame**: https://www.pygame.org/
- **Jetson Nano**: https://developer.nvidia.com/embedded/jetson-nano-developer-kit

---

**Ngày cập nhật**: 2025-01-05  
**Phiên bản**: 1.0

