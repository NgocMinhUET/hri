"""
Person Detector - Phát hiện người trong vùng tương tác
Sử dụng YOLOv8 trên camera IMX477
"""
import cv2
import numpy as np
from ultralytics import YOLO
import time
from typing import Optional, Tuple
from utils.logger import setup_logger
from utils.config_loader import get_config

class PersonDetector:
    """Phát hiện người xuất hiện trong vùng tương tác"""
    
    def __init__(self, config=None):
        """
        Args:
            config: ConfigLoader instance
        """
        self.config = config or get_config()
        self.logger = setup_logger("PersonDetector")
        
        # Load cấu hình
        self.camera_id = self.config.get('camera.device_id', 0)
        self.resolution = (
            self.config.get('camera.resolution.width', 640),
            self.config.get('camera.resolution.height', 480)
        )
        self.fps = self.config.get('camera.fps', 30)
        
        # Detection zone
        self.zone_x = self.config.get('camera.detection_zone.x', 160)
        self.zone_y = self.config.get('camera.detection_zone.y', 120)
        self.zone_w = self.config.get('camera.detection_zone.width', 320)
        self.zone_h = self.config.get('camera.detection_zone.height', 240)
        
        # Person detection settings
        model_path = self.config.get('person_detection.model', 'yolov8n.pt')
        self.confidence_threshold = self.config.get('person_detection.confidence_threshold', 0.5)
        self.cooldown = self.config.get('person_detection.cooldown_seconds', 3)
        
        # Load YOLO model
        self.logger.info(f"Đang load model {model_path}...")
        self.model = YOLO(model_path)
        
        # Camera
        self.cap = None
        self.last_detection_time = 0
        
        self.logger.info("PersonDetector đã sẵn sàng!")
    
    def start_camera(self):
        """Khởi động camera"""
        if self.cap is not None:
            self.logger.warning("Camera đã được khởi động rồi!")
            return
        
        self.logger.info(f"Đang khởi động camera {self.camera_id}...")
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            self.logger.error(f"Không thể mở camera {self.camera_id}")
            self.logger.error("Hãy chạy: python test_camera.py để tìm device ID đúng")
            raise RuntimeError(f"Không thể mở camera {self.camera_id}")
        
        # Set resolution (sau khi mở thành công)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        # Kiểm tra thực tế resolution đã set
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        self.logger.info(f"Camera đã sẵn sàng! Resolution: {actual_width}x{actual_height} @ {actual_fps:.1f}fps")
        
        # Test đọc frame đầu tiên
        ret, test_frame = self.cap.read()
        if not ret:
            self.logger.warning("Cảnh báo: Camera mở được nhưng chưa đọc được frame. Đợi vài giây...")
            import time
            time.sleep(2)
            ret, test_frame = self.cap.read()
            if ret:
                self.logger.info("✅ Camera đã sẵn sàng sau khi đợi!")
            else:
                self.logger.error("❌ Vẫn không đọc được frame. Kiểm tra camera!")
    
    def stop_camera(self):
        """Dừng camera"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.logger.info("Đã dừng camera.")
    
    def detect_person_in_zone(self) -> bool:
        """
        Kiểm tra xem có người trong vùng detection không
        
        Returns:
            True nếu phát hiện người trong zone
        """
        if self.cap is None:
            self.logger.error("Camera chưa được khởi động!")
            return False
        
        # Kiểm tra cooldown
        current_time = time.time()
        if current_time - self.last_detection_time < self.cooldown:
            return False
        
        # Đọc frame
        ret, frame = self.cap.read()
        if not ret:
            self.logger.error(f"Không thể đọc frame từ camera {self.camera_id}!")
            self.logger.error("Có thể do:")
            self.logger.error("  1. Camera device ID sai (kiểm tra: python test_camera.py)")
            self.logger.error("  2. Camera đang bị process khác sử dụng")
            self.logger.error("  3. Camera cần thời gian khởi động (thử đợi vài giây)")
            self.logger.error("  4. Permissions (thử: sudo chmod 666 /dev/video*)")
            return False
        
        # Run detection
        results = self.model(frame, verbose=False)
        
        # Kiểm tra từng detection
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Class 0 là 'person' trong COCO dataset
                if int(box.cls[0]) == 0 and float(box.conf[0]) >= self.confidence_threshold:
                    # Lấy bounding box
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Tính center của bounding box
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    
                    # Kiểm tra xem center có trong zone không
                    if (self.zone_x <= center_x <= self.zone_x + self.zone_w and
                        self.zone_y <= center_y <= self.zone_y + self.zone_h):
                        
                        self.logger.info(f"✅ Phát hiện người trong zone! (confidence: {box.conf[0]:.2f})")
                        self.last_detection_time = current_time
                        return True
        
        return False
    
    def get_frame_with_visualization(self) -> Optional[np.ndarray]:
        """
        Lấy frame với visualization (boxes và zone)
        Dùng cho debug/display
        
        Returns:
            Frame với visualization hoặc None
        """
        if self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Vẽ detection zone
        cv2.rectangle(
            frame,
            (self.zone_x, self.zone_y),
            (self.zone_x + self.zone_w, self.zone_y + self.zone_h),
            (0, 255, 0), 2
        )
        
        # Run detection và vẽ boxes
        results = self.model(frame, verbose=False)
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                if int(box.cls[0]) == 0:  # person
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    
                    # Màu: xanh nếu trong zone, đỏ nếu ngoài zone
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    in_zone = (self.zone_x <= center_x <= self.zone_x + self.zone_w and
                              self.zone_y <= center_y <= self.zone_y + self.zone_h)
                    
                    color = (0, 255, 0) if in_zone else (0, 0, 255)
                    
                    # Vẽ box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    cv2.putText(frame, f"Person {conf:.2f}", (int(x1), int(y1)-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def run_detection_loop(self, callback=None, show_preview=True):
        """
        Chạy detection loop liên tục
        
        Args:
            callback: Hàm được gọi khi phát hiện người (optional)
            show_preview: Hiển thị preview window (default: True)
        """
        self.logger.info("Bắt đầu detection loop...")
        
        try:
            while True:
                # Phát hiện người
                detected = self.detect_person_in_zone()
                
                if detected and callback:
                    callback()
                
                # Hiển thị preview
                if show_preview:
                    frame = self.get_frame_with_visualization()
                    if frame is not None:
                        cv2.imshow('Person Detection', frame)
                    
                    # Nhấn 'q' để thoát
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            self.logger.info("Dừng detection loop.")
        finally:
            if show_preview:
                cv2.destroyAllWindows()
    
    def __del__(self):
        """Cleanup"""
        self.stop_camera()

# Test standalone
if __name__ == "__main__":
    detector = PersonDetector()
    detector.start_camera()
    
    def on_person_detected():
        print("🚶 Có người trong vùng tương tác!")
    
    detector.run_detection_loop(callback=on_person_detected, show_preview=True)

