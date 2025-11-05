#!/usr/bin/env python3
"""
Script test camera - Tìm device ID đúng cho camera
"""
import cv2
import sys

def list_video_devices():
    """Liệt kê tất cả video devices"""
    print("🔍 Đang tìm camera devices...")
    print("=" * 60)
    
    available_devices = []
    
    # Thử từ 0 đến 10
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Lấy thông tin camera
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            backend = cap.getBackendName()
            
            # Thử đọc frame
            ret, frame = cap.read()
            if ret:
                print(f"✅ Device {i}: {width}x{height} @ {fps:.1f}fps [{backend}]")
                print(f"   Frame shape: {frame.shape if frame is not None else 'None'}")
                available_devices.append(i)
            else:
                print(f"⚠️  Device {i}: Mở được nhưng không đọc được frame")
            
            cap.release()
        else:
            # Không có device tại index này
            pass
    
    print("=" * 60)
    
    if available_devices:
        print(f"\n✅ Tìm thấy {len(available_devices)} camera(s): {available_devices}")
        print(f"\n💡 Khuyến nghị: Sử dụng device_id = {available_devices[0]}")
        print(f"\n   Cập nhật config.yaml:")
        print(f"   camera:")
        print(f"     device_id: {available_devices[0]}")
    else:
        print("\n❌ Không tìm thấy camera nào!")
        print("\n🔧 Kiểm tra:")
        print("   1. Camera đã được cắm chưa?")
        print("   2. Kiểm tra: ls /dev/video*")
        print("   3. Kiểm tra permissions: sudo chmod 666 /dev/video*")
    
    return available_devices

def test_camera(device_id):
    """Test camera cụ thể"""
    print(f"\n🧪 Test camera device {device_id}...")
    
    cap = cv2.VideoCapture(device_id)
    
    if not cap.isOpened():
        print(f"❌ Không thể mở camera {device_id}")
        return False
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Đọc vài frame
    success_count = 0
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            success_count += 1
            print(f"   Frame {i+1}: OK - {frame.shape}")
        else:
            print(f"   Frame {i+1}: FAIL")
    
    cap.release()
    
    if success_count > 0:
        print(f"✅ Camera {device_id} hoạt động! ({success_count}/10 frames)")
        return True
    else:
        print(f"❌ Camera {device_id} không đọc được frame")
        return False

if __name__ == "__main__":
    print("📷 Camera Test Script")
    print("=" * 60)
    
    # List devices
    devices = list_video_devices()
    
    # Test từng device
    if devices:
        print("\n" + "=" * 60)
        for dev_id in devices:
            test_camera(dev_id)
            print()
    
    # Test với device_id từ config
    try:
        from utils.config_loader import get_config
        config = get_config()
        config_device = config.get('camera.device_id', 0)
        print(f"\n📋 Device ID trong config.yaml: {config_device}")
        
        if config_device not in devices:
            print(f"⚠️  Device {config_device} không có trong danh sách devices tìm được!")
            if devices:
                print(f"💡 Đề xuất: Đổi device_id thành {devices[0]}")
    except:
        pass

