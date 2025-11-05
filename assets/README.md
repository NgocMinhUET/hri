# Assets

Thư mục chứa các tài nguyên cho UETBot.

## Cấu trúc

```
assets/
├── faces/          # Hình ảnh khuôn mặt (nếu sử dụng image-based face)
│   ├── idle.png
│   ├── listening.png
│   ├── thinking.png
│   ├── speaking.png
│   ├── happy.png
│   └── surprised.png
│
└── sounds/         # Sound effects (optional)
    ├── wake_sound.wav
    └── beep.wav
```

## Lưu ý

Hiện tại, Face Display sử dụng **Pygame để vẽ vector graphics** thay vì load hình ảnh, nên thư mục `faces/` không bắt buộc.

Nếu bạn muốn chuyển sang sử dụng pre-rendered face images, có thể thêm các file PNG vào đây và sửa `modules/face_display.py` để load images thay vì vẽ.

