# ⚡ Quick Start Guide - UETBot

Hướng dẫn nhanh để chạy UETBot trong 5 phút!

---

## 🎯 Mục tiêu

Sau khi hoàn thành guide này, bạn sẽ có:
- ✅ Bot AI chạy trên Jetson Nano
- ✅ Phát hiện người tự động
- ✅ Đánh thức bằng giọng nói "Hi UETBot"
- ✅ Hội thoại bằng tiếng Việt
- ✅ Giao diện khuôn mặt biểu cảm

---

## 📝 Checklist Trước khi Bắt đầu

- [ ] NVIDIA Jetson Nano đã flash JetPack 4.6+
- [ ] Camera IMX477 đã kết nối
- [ ] USB Microphone đã kết nối
- [ ] Speaker/Headphone đã kết nối
- [ ] Màn hình HDMI đã kết nối
- [ ] Kết nối Internet (để tải models và sử dụng Gemini API)

---

## 🚀 Cài đặt Nhanh (5 bước)

### Bước 1: Update System (2 phút)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-dev git
```

### Bước 2: Clone Project (1 phút)

```bash
cd ~/
git clone <your-repo-url> HRI
cd HRI
```

### Bước 3: Cài đặt Dependencies (10 phút)

```bash
# System dependencies
sudo apt install -y libopencv-dev python3-opencv portaudio19-dev espeak ffmpeg

# Python packages
pip3 install -r requirements.txt --user

# PyTorch cho Jetson (nếu chưa có)
wget https://nvidia.box.com/shared/static/ssf2v7pf5i245fk4i0q926hy4imzs2ph.whl -O torch.whl
pip3 install torch.whl
```

### Bước 4: Tải Models (5 phút)

```bash
# Tạo thư mục models
mkdir -p models
cd models

# YOLOv8 (sẽ tự động tải khi chạy lần đầu, hoặc tải trước)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Vosk Vietnamese Model
wget https://alphacephei.com/vosk/models/vosk-model-small-vi-0.4.zip
unzip vosk-model-small-vi-0.4.zip
rm vosk-model-small-vi-0.4.zip

cd ..
```

### Bước 5: Cấu hình API Key (1 phút)

```bash
# Copy .env template
cp .env.example .env

# Edit .env
nano .env
```

Thêm Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

**Lấy API key miễn phí**: https://makersuite.google.com/app/apikey

**Lưu file**: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## ✅ Test Hệ thống

Chạy test suite để kiểm tra tất cả:

```bash
python3 test_all.py
```

Nếu tất cả test PASS → Bạn sẵn sàng! 🎉

Nếu có test FAIL → Xem phần [Troubleshooting](#troubleshooting) bên dưới.

---

## 🎮 Chạy Bot

### Chạy bot hoàn chỉnh

```bash
python3 main.py
```

### Hoặc test từng module riêng

```bash
# Test camera + person detection
python3 -m modules.person_detector

# Test wake word
python3 -m modules.wake_word

# Test speech-to-text
python3 -m modules.stt_engine

# Test text-to-speech
python3 -m modules.tts_engine

# Test LLM
python3 -m modules.llm_client

# Test face display
python3 -m modules.face_display
```

---

## 🎯 Cách Sử dụng

### Kịch bản 1: Kích hoạt bằng Person Detection

1. **Đứng trước camera** trong vùng detection (giữa màn hình)
2. Bot phát hiện bạn → Chào hỏi
3. Bot hỏi: "Tôi có thể giúp gì cho bạn?"
4. **Nói câu hỏi** của bạn
5. Bot suy nghĩ và trả lời
6. Hội thoại kết thúc → Bot về trạng thái chờ

### Kịch bản 2: Kích hoạt bằng Wake Word

1. **Nói**: "Hi UETBot"
2. Bot đánh thức → Chào hỏi
3. (Tiếp tục như Kịch bản 1)

---

## ⚙️ Tùy chỉnh

### Thay đổi cấu hình

Edit `config.yaml`:

```yaml
# Điều chỉnh detection zone
camera:
  detection_zone:
    x: 160
    y: 120
    width: 320
    height: 240

# Điều chỉnh độ nhạy person detection
person_detection:
  confidence_threshold: 0.5  # 0.0 - 1.0

# Thay đổi wake word
wake_word:
  keyword: "hi uetbot"  # Thay đổi thành keyword khác

# Tùy chỉnh tính cách bot
llm:
  system_prompt: "Bạn là UETBot, một trợ lý AI thân thiện..."
```

### Tắt Person Detection hoặc Wake Word

```bash
# Chỉ dùng wake word
python3 main.py --no-person-detection

# Chỉ dùng person detection
python3 main.py --no-wake-word
```

---

## 🐛 Troubleshooting

### ❌ Camera không hoạt động

```bash
# Kiểm tra camera
ls /dev/video*

# Nếu không có → enable camera
sudo nano /boot/config.txt
# Thêm: dtoverlay=imx477
sudo reboot
```

### ❌ Microphone không hoạt động

```bash
# List microphones
arecord -l

# Test ghi âm
arecord -d 3 test.wav
aplay test.wav
```

### ❌ "No module named 'torch'"

```bash
# Cài PyTorch cho Jetson
wget https://nvidia.box.com/shared/static/ssf2v7pf5i245fk4i0q926hy4imzs2ph.whl -O torch.whl
pip3 install torch.whl
```

### ❌ "No module named 'vosk'"

```bash
pip3 install vosk --user
```

### ❌ Gemini API Error

- Kiểm tra API key trong file `.env`
- Kiểm tra kết nối Internet
- Lấy API key mới tại: https://makersuite.google.com/app/apikey

### ❌ TTS không có giọng Việt

```bash
sudo apt install espeak-ng
```

### ❌ "Out of Memory"

```bash
# Tăng swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📚 Tài liệu Chi tiết

- **README.md**: Tổng quan dự án
- **ARCHITECTURE.md**: Kiến trúc hệ thống chi tiết
- **SETUP_JETSON.md**: Hướng dẫn cài đặt chi tiết cho Jetson Nano

---

## 🎉 Hoàn tất!

Bot của bạn đã sẵn sàng! 

**Cách dừng bot**: Nhấn `Ctrl+C`

**Cách chạy lại**: `python3 main.py`

---

## 💡 Tips

1. **Performance**: Set Jetson về max performance mode
   ```bash
   sudo nvpmodel -m 0
   sudo jetson_clocks
   ```

2. **Auto-start khi boot**: Xem hướng dẫn trong `SETUP_JETSON.md`

3. **Monitor resources**: 
   ```bash
   sudo pip3 install jetson-stats
   sudo jtop
   ```

4. **Xem logs**: 
   ```bash
   tail -f logs/uetbot.log
   ```

---

## 🆘 Cần Trợ giúp?

1. Chạy `python3 test_all.py` để xem component nào bị lỗi
2. Kiểm tra logs tại `logs/uetbot.log`
3. Xem troubleshooting chi tiết trong `SETUP_JETSON.md`

---

**Chúc bạn thành công!** 🚀

