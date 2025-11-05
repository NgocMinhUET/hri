# 🚀 Hướng dẫn Cài đặt UETBot trên NVIDIA Jetson Nano

Chi tiết từng bước để triển khai UETBot trên Jetson Nano.

## 📋 Mục lục
1. [Chuẩn bị Jetson Nano](#1-chuẩn-bị-jetson-nano)
2. [Cài đặt Dependencies](#2-cài-đặt-dependencies)
3. [Cài đặt PyTorch](#3-cài-đặt-pytorch)
4. [Cấu hình Camera IMX477](#4-cấu-hình-camera-imx477)
5. [Cài đặt UETBot](#5-cài-đặt-uetbot)
6. [Tải Models](#6-tải-models)
7. [Cấu hình Audio](#7-cấu-hình-audio)
8. [Chạy Bot](#8-chạy-bot)
9. [Tối ưu Performance](#9-tối-ưu-performance)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Chuẩn bị Jetson Nano

### 1.1. Flash JetPack SDK
- Download JetPack 4.6.1 (hoặc mới hơn): https://developer.nvidia.com/jetpack-sdk-461
- Flash lên SD card (32GB trở lên khuyến nghị)
- Boot Jetson Nano và hoàn tất setup ban đầu

### 1.2. Update System
```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

### 1.3. Tăng Swap Space (khuyến nghị cho Jetson Nano 4GB)
```bash
# Tạo 8GB swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Thêm vào /etc/fstab để tự động mount
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 2. Cài đặt Dependencies

### 2.1. System Dependencies
```bash
# Python và build tools
sudo apt install -y python3-pip python3-dev python3-setuptools
sudo apt install -y build-essential cmake pkg-config

# OpenCV dependencies
sudo apt install -y libopencv-dev python3-opencv

# Audio dependencies
sudo apt install -y portaudio19-dev libportaudio2 libportaudiocpp0
sudo apt install -y espeak espeak-ng ffmpeg libespeak-dev

# GUI dependencies (Pygame)
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt install -y libfreetype6-dev libjpeg-dev libpng-dev

# USB/Camera
sudo apt install -y v4l-utils
```

### 2.2. Upgrade pip
```bash
pip3 install --upgrade pip
```

---

## 3. Cài đặt PyTorch

### 3.1. Download PyTorch Wheel cho Jetson
```bash
# PyTorch 1.13.0 cho JetPack 4.6.1
cd ~/Downloads
wget https://nvidia.box.com/shared/static/ssf2v7pf5i245fk4i0q926hy4imzs2ph.whl \
  -O torch-1.13.0-cp38-cp38-linux_aarch64.whl
```

### 3.2. Install PyTorch
```bash
pip3 install torch-1.13.0-cp38-cp38-linux_aarch64.whl
```

### 3.3. Install Torchvision
```bash
sudo apt install -y libjpeg-dev zlib1g-dev
pip3 install torchvision==0.14.0
```

### 3.4. Verify
```bash
python3 -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
# Output: 1.13.0, True
```

---

## 4. Cấu hình Camera IMX477

### 4.1. Enable Camera
```bash
# Kiểm tra camera có được nhận diện không
ls /dev/video*

# Nếu không có, enable trong config
sudo nano /boot/config.txt
# Thêm dòng: dtoverlay=imx477
```

### 4.2. Test Camera
```bash
# Test với OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Error')"

# Hoặc dùng v4l2
v4l2-ctl --list-devices
```

### 4.3. Cấu hình múi giờ camera (nếu cần)
```bash
# Kiểm tra các video device
ls -la /dev/video*

# Cập nhật camera ID trong config.yaml nếu cần
# camera.device_id: 0  # hoặc 1, 2,...
```

---

## 5. Cài đặt UETBot

### 5.1. Clone Repository
```bash
cd ~/
git clone <your-repo-url> HRI
cd HRI
```

### 5.2. Install Python Dependencies
```bash
# Install từ requirements.txt
pip3 install -r requirements.txt --user

# Một số package có thể cần install riêng:
pip3 install vosk --user
pip3 install ultralytics --user
pip3 install google-generativeai --user
```

### 5.3. Tạo file .env
```bash
cp .env.example .env
nano .env
# Thêm GEMINI_API_KEY của bạn
```

**Lấy Gemini API Key miễn phí:**
- Truy cập: https://makersuite.google.com/app/apikey
- Tạo API key mới
- Copy và paste vào file .env

---

## 6. Tải Models

### 6.1. YOLOv8 Model
```bash
mkdir -p models
cd models

# Download YOLOv8 nano (nhẹ nhất, phù hợp Jetson Nano)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

cd ..
```

### 6.2. Vosk Vietnamese Model
```bash
cd models

# Download Vosk Vietnamese model (small)
wget https://alphacephei.com/vosk/models/vosk-model-small-vi-0.4.zip
unzip vosk-model-small-vi-0.4.zip
rm vosk-model-small-vi-0.4.zip

cd ..
```

### 6.3. Verify Models
```bash
ls -lh models/
# Nên thấy:
# - yolov8n.pt (~6MB)
# - vosk-model-small-vi-0.4/ (folder)
```

---

## 7. Cấu hình Audio

### 7.1. Kiểm tra Audio Devices
```bash
# List microphones
arecord -l

# List speakers
aplay -l
```

### 7.2. Test Microphone
```bash
# Record 5 giây
arecord -d 5 -f cd test.wav

# Play back
aplay test.wav
```

### 7.3. Test Speaker
```bash
speaker-test -t wav -c 2
```

### 7.4. Cấu hình Default Audio Device (nếu cần)
```bash
# Tạo file .asoundrc
nano ~/.asoundrc

# Thêm (thay số X bằng device index của bạn):
pcm.!default {
    type hw
    card 0
    device 0
}

ctl.!default {
    type hw
    card 0
}
```

---

## 8. Chạy Bot

### 8.1. Test Từng Module

#### Test Camera + Person Detection
```bash
python3 -m modules.person_detector
# Nhấn 'q' để thoát
```

#### Test Wake Word
```bash
python3 -m modules.wake_word
# Nói "Hi UETBot"
```

#### Test STT
```bash
python3 -m modules.stt_engine
# Nói gì đó, dừng 1.5s
```

#### Test LLM
```bash
python3 -m modules.llm_client
# Chat với bot
```

#### Test TTS
```bash
python3 -m modules.tts_engine
# Nghe bot nói
```

#### Test Face Display
```bash
python3 -m modules.face_display
# Nhấn 1-6 để thay đổi emotion
```

### 8.2. Chạy Bot Hoàn Chỉnh
```bash
python3 main.py
```

### 8.3. Chạy với Options
```bash
# Tắt person detection (chỉ dùng wake word)
python3 main.py --no-person-detection

# Tắt wake word (chỉ dùng person detection)
python3 main.py --no-wake-word

# Debug mode
python3 main.py --debug
```

---

## 9. Tối ưu Performance

### 9.1. Set Power Mode
```bash
# Max performance mode
sudo nvpmodel -m 0
sudo jetson_clocks
```

### 9.2. Monitor Resources
```bash
# CPU/GPU/RAM
sudo tegrastats

# Hoặc dùng jtop (cần cài đặt)
sudo pip3 install jetson-stats
sudo jtop
```

### 9.3. Tối ưu YOLO Inference
Trong `config.yaml`, điều chỉnh:
```yaml
person_detection:
  model: "yolov8n.pt"  # Dùng nano, nhẹ nhất
  confidence_threshold: 0.5  # Tăng lên nếu muốn ít false positive
```

### 9.4. Giảm Resolution Camera (nếu lag)
```yaml
camera:
  resolution:
    width: 320  # Thay vì 640
    height: 240  # Thay vì 480
```

---

## 10. Troubleshooting

### ❌ Camera không hoạt động
```bash
# Kiểm tra camera có được nhận diện
ls /dev/video*

# Kiểm tra driver
dmesg | grep -i imx477

# Reboot nếu cần
sudo reboot
```

### ❌ PyTorch không có CUDA
```bash
# Kiểm tra CUDA
nvcc --version

# Kiểm tra PyTorch
python3 -c "import torch; print(torch.cuda.is_available())"

# Nếu False, cài lại PyTorch wheel đúng phiên bản JetPack
```

### ❌ Vosk model không load được
```bash
# Kiểm tra đường dẫn
ls -la models/vosk-model-small-vi-0.4/

# Phải có các file: am/, conf/, graph/, ...
```

### ❌ TTS không có giọng Việt
```bash
# Cài thêm espeak-ng
sudo apt install espeak-ng

# Test
espeak-ng "Xin chào"
```

### ❌ Out of Memory
```bash
# Tăng swap
sudo swapoff -a
sudo fallocate -l 12G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Hoặc giảm resolution/model size
```

### ❌ Gemini API Error
```bash
# Kiểm tra API key
cat .env

# Test API key
python3 -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
print(model.generate_content('Hello').text)
"
```

---

## 🎉 Hoàn tất!

Bot của bạn đã sẵn sàng hoạt động trên Jetson Nano!

### Chạy tự động khi boot (optional)
```bash
# Tạo systemd service
sudo nano /etc/systemd/system/uetbot.service

# Thêm:
[Unit]
Description=UETBot AI Kiosk
After=network.target

[Service]
Type=simple
User=<your-username>
WorkingDirectory=/home/<your-username>/HRI
ExecStart=/usr/bin/python3 /home/<your-username>/HRI/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Enable
sudo systemctl enable uetbot.service
sudo systemctl start uetbot.service
```

---

## 📚 Tài liệu tham khảo
- Jetson Nano Developer Kit: https://developer.nvidia.com/embedded/jetson-nano-developer-kit
- IMX477 Camera: https://www.arducam.com/docs/camera-for-jetson-nano/
- PyTorch for Jetson: https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048

