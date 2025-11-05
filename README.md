# 🤖 AI Kiosk Bot - UETBot

Bot AI Tương tác thông minh cho môi trường indoor, chạy trên NVIDIA Jetson Nano.

## ✨ Tính năng

### 👁️ **Mắt** - Kích hoạt tự động
- Phát hiện người tự động qua camera IMX477 (YOLOv8)
- Đánh thức bằng giọng nói: "Hi UETBot"
- Xác định khu vực tương tác

### 🧠 **Não** - Khả năng hội thoại
- Sử dụng Gemini API (miễn phí) cho LLM
- Trả lời thông minh, tự nhiên
- Có thể tùy chỉnh system prompt

### 🗣️ **Tai & Miệng** - Giao tiếp giọng nói
- **STT**: Vosk (offline, nhanh, hỗ trợ tiếng Việt)
- **TTS**: pyttsx3 (offline, độ trễ thấp)
- Voice Activity Detection (VAD) thông minh

### 😊 **Mặt** - Giao diện biểu cảm
- Hiển thị khuôn mặt hoạt hình với biểu cảm
- Các trạng thái: idle, listening, thinking, speaking, happy, surprised
- Animation mượt mà với Pygame

## 🛠️ Phần cứng

- **Board**: NVIDIA Jetson Nano
- **Camera**: 2x IMX477
- **Màn hình**: HDMI display
- **Audio**: USB Microphone + Speaker

## 📦 Cài đặt

### 1. Chuẩn bị môi trường Jetson Nano

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-dev portaudio19-dev
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y espeak ffmpeg libespeak-dev

# Install PyTorch for Jetson (pre-built)
wget https://nvidia.box.com/shared/static/ssf2v7pf5i245fk4i0q926hy4imzs2ph.whl -O torch-1.13.0-cp38-cp38-linux_aarch64.whl
pip3 install torch-1.13.0-cp38-cp38-linux_aarch64.whl
```

### 2. Clone và cài đặt dependencies

```bash
cd ~/
git clone <your-repo-url>
cd HRI

# Install Python packages
pip3 install -r requirements.txt
```

### 3. Tải models

```bash
# Tải YOLOv8 model (tự động khi chạy lần đầu)
# hoặc download trước:
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -P models/

# Tải Vosk Vietnamese model
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-vi-0.4.zip
unzip vosk-model-small-vi-0.4.zip
cd ..
```

### 4. Cấu hình

```bash
# Copy và chỉnh sửa file .env
cp .env.example .env
nano .env  # Thêm GEMINI_API_KEY của bạn
```

Lấy Gemini API Key miễn phí tại: https://makersuite.google.com/app/apikey

### 5. Cấu hình camera IMX477

```bash
# Kiểm tra camera
ls /dev/video*

# Nếu cần, enable camera trong config
sudo nano /boot/config.txt
# Thêm: dtoverlay=imx477
```

## 🚀 Chạy Bot

```bash
# Chạy bot chính
python3 main.py

# Hoặc chạy với debug mode
python3 main.py --debug

# Test từng module riêng
python3 -m modules.person_detector  # Test person detection
python3 -m modules.wake_word        # Test wake word
python3 -m modules.stt_engine       # Test STT
python3 -m modules.tts_engine       # Test TTS
python3 -m modules.face_display     # Test face display
```

## 📁 Cấu trúc dự án

```
HRI/
├── main.py                 # Entry point chính
├── config.yaml            # Cấu hình hệ thống
├── requirements.txt       # Python dependencies
├── .env                   # API keys (không commit)
│
├── modules/               # Các module chức năng
│   ├── __init__.py
│   ├── person_detector.py    # Phát hiện người
│   ├── wake_word.py          # Wake word detection
│   ├── stt_engine.py         # Speech-to-Text
│   ├── tts_engine.py         # Text-to-Speech
│   ├── llm_client.py         # Gemini LLM client
│   └── face_display.py       # Giao diện mặt
│
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── audio_utils.py        # Audio processing
│   ├── config_loader.py      # Load config
│   └── logger.py             # Logging
│
├── assets/                # Resources
│   ├── faces/                # Face images
│   │   ├── idle.png
│   │   ├── listening.png
│   │   ├── thinking.png
│   │   ├── speaking.png
│   │   ├── happy.png
│   │   └── surprised.png
│   └── sounds/               # Sound effects
│
├── models/                # AI Models
│   ├── yolov8n.pt
│   └── vosk-model-small-vi-0.4/
│
└── logs/                  # Log files
```

## ⚙️ Tùy chỉnh

Chỉnh sửa `config.yaml` để:
- Điều chỉnh độ nhạy phát hiện người
- Thay đổi wake word
- Tùy chỉnh giọng nói TTS
- Cấu hình LLM system prompt
- Thay đổi khu vực detection zone

## 🔧 Tối ưu cho Jetson Nano

- Sử dụng YOLOv8n (nano) - model nhỏ nhất, nhanh nhất
- Vosk STT chạy hoàn toàn offline
- pyttsx3 TTS có độ trễ cực thấp
- Camera resolution 640x480 để tối ưu FPS
- Multithreading để xử lý song song các task

## 📝 Lưu ý

1. **Gemini API Free Tier**: 60 requests/phút
2. **Jetson Nano RAM**: 4GB - tối ưu model size
3. **Camera**: Đảm bảo IMX477 được cấu hình đúng
4. **Audio**: Test microphone và speaker trước khi chạy

## 🐛 Troubleshooting

### Camera không hoạt động
```bash
ls /dev/video*
v4l2-ctl --list-devices
```

### Audio không hoạt động
```bash
arecord -l  # List microphones
aplay -l    # List speakers
```

### TTS không có giọng Việt
```bash
# Cài đặt espeak-ng
sudo apt install espeak-ng
```

## 📄 License

MIT License

## 👥 Contributors

Dự án AI Kiosk cho UET - ĐHQGHN

