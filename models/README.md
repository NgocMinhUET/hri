# Models

Thư mục chứa các AI models cho UETBot.

## Models cần thiết

### 1. YOLOv8 Model (Person Detection)

**File**: `yolov8n.pt`  
**Kích thước**: ~6 MB  
**Tải về**:
```bash
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

Hoặc model sẽ tự động tải khi chạy lần đầu.

**Các variants khác**:
- `yolov8n.pt` - Nano (nhanh nhất, khuyến nghị cho Jetson Nano)
- `yolov8s.pt` - Small (chính xác hơn nhưng chậm hơn)
- `yolov8m.pt` - Medium (cần GPU mạnh)

### 2. Vosk Vietnamese Model (Speech-to-Text)

**Thư mục**: `vosk-model-small-vi-0.4/`  
**Kích thước**: ~40 MB  
**Tải về**:
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-vi-0.4.zip
unzip vosk-model-small-vi-0.4.zip
rm vosk-model-small-vi-0.4.zip
```

**Các models khác**:
- **vosk-model-small-vi-0.4** (khuyến nghị): Nhỏ, nhanh, độ chính xác tốt
- **vosk-model-vi-0.4**: Lớn hơn (~1GB), chính xác hơn nhưng chậm hơn

Link tải: https://alphacephei.com/vosk/models

## Cấu trúc sau khi tải xong

```
models/
├── README.md
├── yolov8n.pt                          # YOLOv8 model
└── vosk-model-small-vi-0.4/           # Vosk Vietnamese model
    ├── am/
    ├── conf/
    ├── graph/
    ├── ivector/
    └── ...
```

## Kiểm tra

Chạy test để kiểm tra models đã được cài đặt đúng:

```bash
python3 test_all.py
```

## Tối ưu Model

### YOLOv8 INT8 Quantization (Advanced)

Nếu muốn tăng tốc độ inference:

```python
from ultralytics import YOLO

# Load model
model = YOLO('yolov8n.pt')

# Export sang INT8
model.export(format='engine', int8=True)
```

### Vosk Custom Model

Nếu muốn train model riêng cho domain cụ thể, xem:
https://alphacephei.com/vosk/adaptation

## Lưu ý

- File `.pt` và thư mục `vosk-model-*` đã được thêm vào `.gitignore`
- Không commit models vào Git (quá lớn)
- Tải models riêng trên mỗi Jetson Nano

