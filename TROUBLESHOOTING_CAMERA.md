# 🔧 Troubleshooting Camera Issues

Hướng dẫn khắc phục các vấn đề với camera USB Logitech hoặc camera khác.

## ❌ Lỗi: "Không thể đọc frame từ camera"

### Bước 1: Tìm Device ID đúng

```bash
cd ~/HRI
conda activate hri

# Chạy script test camera
python test_camera.py
```

Script sẽ:
- Liệt kê tất cả camera devices
- Test từng device
- Đề xuất device_id đúng

### Bước 2: Kiểm tra camera có được nhận diện không

```bash
# Liệt kê video devices
ls -la /dev/video*

# Hoặc dùng v4l2
v4l2-ctl --list-devices
```

### Bước 3: Kiểm tra Permissions

```bash
# Kiểm tra permissions
ls -l /dev/video*

# Nếu permission bị từ chối, thử:
sudo chmod 666 /dev/video0
sudo chmod 666 /dev/video1
# ... cho tất cả video devices
```

Hoặc thêm user vào group video:
```bash
sudo usermod -a -G video $USER
# Logout và login lại
```

### Bước 4: Kiểm tra camera có bị process khác sử dụng

```bash
# Kiểm tra process nào đang dùng camera
lsof /dev/video0
# hoặc
fuser /dev/video0

# Nếu có, kill process đó
kill <PID>
```

### Bước 5: Cập nhật config.yaml

Sau khi tìm được device_id đúng, cập nhật:

```yaml
camera:
  device_id: 0  # Đổi thành device_id tìm được (ví dụ: 1, 2, ...)
  resolution:
    width: 640
    height: 480
```

### Bước 6: Test lại

```bash
# Test camera với device_id mới
python -c "import cv2; cap = cv2.VideoCapture(1); print('OK' if cap.isOpened() else 'FAIL'); cap.release()"
```

## 🔍 Các vấn đề thường gặp

### 1. Camera USB không được nhận diện

**Triệu chứng**: `ls /dev/video*` không hiển thị camera

**Giải pháp**:
```bash
# Kiểm tra USB devices
lsusb

# Kiểm tra dmesg
dmesg | tail -20

# Thử rút và cắm lại camera
# Hoặc:
sudo modprobe -r uvcvideo
sudo modprobe uvcvideo
```

### 2. Camera bị lỗi "Device busy"

**Triệu chứng**: Camera mở được nhưng không đọc được frame, hoặc báo "Device busy"

**Giải pháp**:
```bash
# Tìm và kill process đang dùng camera
sudo fuser -k /dev/video0

# Hoặc restart camera driver
sudo modprobe -r uvcvideo
sudo modprobe uvcvideo
```

### 3. Camera Logitech 720p không hoạt động

**Triệu chứng**: Camera mở được nhưng resolution/fps không đúng

**Giải pháp**:
```bash
# Kiểm tra supported formats
v4l2-ctl --device=/dev/video0 --list-formats-ext

# Test với resolution khác trong config.yaml
camera:
  resolution:
    width: 1280
    height: 720
```

### 4. Multiple cameras (USB + IMX477)

**Triệu chứng**: Có nhiều camera, không biết device_id nào

**Giải pháp**:
```bash
# Chạy test_camera.py để tìm device_id đúng
python test_camera.py

# Hoặc kiểm tra từng device:
for i in {0..5}; do
  echo "Testing device $i:"
  python -c "import cv2; cap = cv2.VideoCapture($i); print('OK' if cap.isOpened() else 'FAIL'); cap.release()"
done
```

## 📝 Checklist

- [ ] Camera đã được cắm vào USB
- [ ] Camera được nhận diện: `ls /dev/video*`
- [ ] Permissions OK: `ls -l /dev/video*`
- [ ] Không có process khác đang dùng camera
- [ ] Device ID đúng trong config.yaml
- [ ] Test camera: `python test_camera.py`

## 🚀 Quick Fix

```bash
# 1. Tìm device ID
python test_camera.py

# 2. Cập nhật config.yaml với device_id tìm được

# 3. Fix permissions
sudo chmod 666 /dev/video*

# 4. Test lại
python main.py
```

## 📞 Nếu vẫn không được

1. Kiểm tra camera có hoạt động trên máy khác không
2. Thử camera USB khác
3. Kiểm tra USB port có hoạt động không
4. Kiểm tra logs: `tail -f logs/uetbot.log`

