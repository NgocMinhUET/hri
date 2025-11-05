# 📋 Tổng Kết Dự Án UETBot

## 🎯 Mô tả Dự án

**UETBot** là một AI Kiosk Bot tương tác thông minh được thiết kế để hoạt động trong môi trường indoor. Bot có khả năng:

- 👁️ **Phát hiện người** tự động qua camera
- 🎤 **Đánh thức bằng giọng nói** với keyword "Hi UETBot"
- 💬 **Hội thoại thông minh** sử dụng Gemini LLM
- 🗣️ **Giao tiếp bằng giọng nói** (STT + TTS)
- 😊 **Hiển thị biểu cảm** trên màn hình

## 🛠️ Công nghệ Sử dụng

### Phần cứng
- **Board**: NVIDIA Jetson Nano (4GB RAM)
- **Camera**: IMX477 (dual camera support)
- **Audio**: USB Microphone + Speaker
- **Display**: HDMI Monitor

### Phần mềm

| Component | Technology | Why? |
|-----------|-----------|------|
| **Person Detection** | YOLOv8 Nano | Nhanh, nhẹ, phù hợp Jetson Nano |
| **Wake Word** | Vosk | Offline, độ trễ thấp, hỗ trợ tiếng Việt |
| **STT** | Vosk | Offline, nhanh, miễn phí |
| **LLM** | Gemini API | Free tier, chất lượng tốt |
| **TTS** | pyttsx3 | Offline, độ trễ cực thấp |
| **Face Display** | Pygame | Lightweight, dễ custom |

### Ngôn ngữ & Framework
- **Python 3.8+**
- **PyTorch** (optimized cho Jetson)
- **OpenCV** (computer vision)
- **PyAudio** (audio I/O)

## 📁 Cấu trúc Dự án

```
HRI/
│
├── main.py                      # Entry point chính
├── config.yaml                  # Cấu hình hệ thống
├── requirements.txt             # Python dependencies
├── .env                         # API keys (không commit)
├── .gitignore                   # Git ignore rules
│
├── modules/                     # Core modules
│   ├── person_detector.py       # YOLOv8 person detection
│   ├── wake_word.py             # Wake word detection
│   ├── stt_engine.py            # Speech-to-Text
│   ├── tts_engine.py            # Text-to-Speech
│   ├── llm_client.py            # Gemini LLM client
│   └── face_display.py          # Pygame face display
│
├── utils/                       # Utilities
│   ├── config_loader.py         # YAML + .env loader
│   ├── logger.py                # Logging setup
│   └── audio_utils.py           # Audio recording/playback
│
├── models/                      # AI models
│   ├── yolov8n.pt              # YOLO model
│   └── vosk-model-small-vi-0.4/ # Vosk Vietnamese model
│
├── assets/                      # Resources
│   ├── faces/                   # Face images (optional)
│   └── sounds/                  # Sound effects (optional)
│
├── logs/                        # Log files
│   └── uetbot.log              # Runtime logs
│
└── docs/                        # Documentation
    ├── README.md                # Project overview
    ├── QUICKSTART.md            # Quick start guide
    ├── SETUP_JETSON.md          # Jetson setup guide
    ├── ARCHITECTURE.md          # System architecture
    └── PROJECT_SUMMARY.md       # This file
```

## 🔄 Workflow

### 1. Activation Phase (Kích hoạt)
```
IDLE → [Person Detected OR Wake Word] → Activated
```

### 2. Conversation Phase (Hội thoại)
```
Greeting (TTS) → 
Listen (STT) → 
Process (LLM) → 
Respond (TTS) → 
Return to IDLE
```

### 3. State Management
```
IDLE → SPEAKING → LISTENING → THINKING → SPEAKING → IDLE
```

## 📊 Performance

### Latency Breakdown (trên Jetson Nano)

| Operation | Latency | Notes |
|-----------|---------|-------|
| Person Detection | ~100ms | Per frame @ 640x480 |
| Wake Word Detection | <100ms | Real-time streaming |
| STT (2s audio) | ~500ms | Vosk offline |
| LLM Response | 1-3s | Gemini API (network) |
| TTS Synthesis | ~50ms | pyttsx3 offline |
| **Total per turn** | **2-5s** | Acceptable for kiosk |

### Resource Usage

- **CPU**: 50-70% (during inference)
- **GPU**: 20-40% (YOLOv8)
- **RAM**: ~2GB (with swap)
- **Network**: ~10KB/request (Gemini API)

## ✅ Features Implemented

### ✅ Core Features
- [x] Person detection với YOLOv8
- [x] Wake word detection "Hi UETBot"
- [x] Speech-to-Text (tiếng Việt)
- [x] LLM integration (Gemini)
- [x] Text-to-Speech (tiếng Việt)
- [x] Face display với 6 emotions
- [x] State management
- [x] Conversation flow control

### ✅ Advanced Features
- [x] Voice Activity Detection (VAD)
- [x] Cooldown mechanism (tránh trigger spam)
- [x] Conversation history
- [x] Configurable via YAML
- [x] Logging system
- [x] Error handling
- [x] Multi-threading (face display)

### ✅ Developer Tools
- [x] Test suite (`test_all.py`)
- [x] Standalone module tests
- [x] Comprehensive documentation
- [x] Quick start guide
- [x] Setup guide cho Jetson Nano

## 🚧 Future Improvements

### Performance
- [ ] YOLOv8 INT8 quantization
- [ ] Multi-language support
- [ ] Context-aware LLM (long-term memory)
- [ ] Edge TTS (local neural TTS)

### Features
- [ ] Gesture recognition
- [ ] Emotion detection (từ giọng nói)
- [ ] Touch screen support
- [ ] QR code display
- [ ] Analytics dashboard
- [ ] Custom wake word training

### Deployment
- [ ] Docker container
- [ ] Systemd service
- [ ] Auto-update mechanism
- [ ] Remote monitoring
- [ ] OTA updates

## 📚 Documentation

### Hướng dẫn Sử dụng
- **README.md**: Tổng quan dự án
- **QUICKSTART.md**: Bắt đầu nhanh trong 5 phút
- **SETUP_JETSON.md**: Hướng dẫn chi tiết cho Jetson Nano

### Tài liệu Kỹ thuật
- **ARCHITECTURE.md**: Kiến trúc hệ thống chi tiết
- **PROJECT_SUMMARY.md**: Tổng kết dự án (file này)

### Code Documentation
- Tất cả module đều có docstrings
- Inline comments cho logic phức tạp
- Type hints cho function parameters

## 🎓 Learning Resources

### Computer Vision
- YOLOv8: https://github.com/ultralytics/ultralytics
- Object Detection: https://learnopencv.com/

### Speech Processing
- Vosk: https://alphacephei.com/vosk/
- Speech Recognition: https://realpython.com/python-speech-recognition/

### LLM Integration
- Gemini API: https://ai.google.dev/
- Prompt Engineering: https://www.promptingguide.ai/

### Jetson Development
- Jetson Nano: https://developer.nvidia.com/embedded/jetson-nano-developer-kit
- Jetson AI Courses: https://courses.nvidia.com/courses/course-v1:DLI+S-RX-02+V2/

## 🤝 Contributing

### Cách Đóng góp

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

### Code Style

- **Python**: PEP 8
- **Docstrings**: Google style
- **Type hints**: Strongly encouraged
- **Comments**: Tiếng Việt hoặc English

### Testing

Trước khi commit, chạy:

```bash
# Test tất cả modules
python3 test_all.py

# Test từng module riêng
python3 -m modules.person_detector
python3 -m modules.wake_word
# ... etc
```

## 📄 License

MIT License - Xem file `LICENSE` để biết chi tiết.

## 👥 Team

**UETBot Team**  
Đại học Công nghệ - ĐHQGHN  
University of Engineering and Technology, VNU

## 🙏 Acknowledgments

### Open Source Projects
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Vosk Speech Recognition](https://alphacephei.com/vosk/)
- [Google Gemini](https://ai.google.dev/)
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3)
- [Pygame](https://www.pygame.org/)

### Communities
- NVIDIA Jetson Developer Community
- PyTorch Community
- Python Community

## 📧 Contact

Nếu có câu hỏi hoặc gặp vấn đề, vui lòng:
1. Tạo Issue trên GitHub
2. Xem phần Troubleshooting trong documentation
3. Liên hệ team

---

## 🎉 Kết luận

UETBot là một dự án AI Kiosk hoàn chỉnh, tối ưu cho NVIDIA Jetson Nano, với đầy đủ tính năng:

✅ Phát hiện người tự động  
✅ Wake word detection  
✅ Hội thoại bằng giọng nói (tiếng Việt)  
✅ LLM integration  
✅ Giao diện biểu cảm  
✅ Tài liệu đầy đủ  

Dự án sẵn sàng để:
- Deploy vào production
- Mở rộng thêm tính năng
- Tùy chỉnh cho use case cụ thể
- Sử dụng cho giáo dục và nghiên cứu

**Happy Coding!** 🚀

---

**Last Updated**: 2025-01-05  
**Version**: 1.0.0

