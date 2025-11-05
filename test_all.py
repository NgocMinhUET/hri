#!/usr/bin/env python3
"""
Test tất cả modules của UETBot
Script này sẽ test từng module một cách tuần tự
"""
import sys
import time
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def print_header(text):
    print("\n" + "=" * 70)
    print(Fore.CYAN + Style.BRIGHT + text)
    print("=" * 70)

def print_success(text):
    print(Fore.GREEN + "✅ " + text)

def print_error(text):
    print(Fore.RED + "❌ " + text)

def print_warning(text):
    print(Fore.YELLOW + "⚠️  " + text)

def print_info(text):
    print(Fore.BLUE + "ℹ️  " + text)

def test_imports():
    """Test import các thư viện cần thiết"""
    print_header("TEST 1: Import Dependencies")
    
    modules = [
        ("numpy", "numpy"),
        ("opencv-python", "cv2"),
        ("torch", "torch"),
        ("ultralytics", "ultralytics"),
        ("vosk", "vosk"),
        ("pyaudio", "pyaudio"),
        ("pyttsx3", "pyttsx3"),
        ("google.generativeai", "google.generativeai"),
        ("pygame", "pygame"),
        ("yaml", "yaml"),
        ("dotenv", "dotenv"),
    ]
    
    failed = []
    for package_name, import_name in modules:
        try:
            __import__(import_name)
            print_success(f"{package_name}")
        except ImportError as e:
            print_error(f"{package_name}: {e}")
            failed.append(package_name)
    
    if failed:
        print_warning(f"Thiếu {len(failed)} package(s): {', '.join(failed)}")
        print_info("Chạy: pip3 install -r requirements.txt")
        return False
    else:
        print_success("Tất cả dependencies đã được cài đặt!")
        return True

def test_config():
    """Test config loader"""
    print_header("TEST 2: Config Loader")
    
    try:
        from utils.config_loader import get_config
        
        config = get_config()
        print_success("Config loaded thành công")
        
        # Kiểm tra một số key quan trọng
        tests = [
            ("camera.device_id", config.get('camera.device_id')),
            ("person_detection.model", config.get('person_detection.model')),
            ("llm.api_key", config.get('llm.api_key')),
        ]
        
        for key, value in tests:
            if value is not None:
                print_success(f"{key}: {value if key != 'llm.api_key' else '***'}")
            else:
                print_warning(f"{key}: Not set")
        
        # Check API key
        if config.get('llm.api_key'):
            print_success("Gemini API key đã được cấu hình")
        else:
            print_warning("Chưa cấu hình Gemini API key trong .env")
        
        return True
        
    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def test_camera():
    """Test camera"""
    print_header("TEST 3: Camera")
    
    try:
        import cv2
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print_error("Không thể mở camera")
            return False
        
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            print_success(f"Camera OK - Resolution: {w}x{h}")
            cap.release()
            return True
        else:
            print_error("Không thể đọc frame từ camera")
            cap.release()
            return False
            
    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def test_yolo():
    """Test YOLOv8 model"""
    print_header("TEST 4: YOLOv8 Model")
    
    try:
        from ultralytics import YOLO
        import os
        
        model_path = "models/yolov8n.pt"
        
        if not os.path.exists(model_path):
            print_warning(f"Model không tồn tại: {model_path}")
            print_info("Model sẽ tự động tải khi chạy lần đầu")
            return True
        
        model = YOLO(model_path)
        print_success(f"YOLOv8 model loaded: {model_path}")
        return True
        
    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def test_vosk():
    """Test Vosk model"""
    print_header("TEST 5: Vosk STT Model")
    
    try:
        from vosk import Model
        from utils.config_loader import get_config
        import os
        
        # Đọc model_path từ config thay vì hardcode
        config = get_config()
        model_path = config.get('stt.model_path', 'models/vosk-model-small-vn-0.4')
        
        if not os.path.exists(model_path):
            print_error(f"Vosk model không tồn tại: {model_path}")
            print_info(f"Kiểm tra config.yaml: stt.model_path = {model_path}")
            print_info("Tải tại: https://alphacephei.com/vosk/models")
            return False
        
        model = Model(model_path)
        print_success(f"Vosk model loaded: {model_path}")
        return True
        
    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def test_audio():
    """Test audio devices"""
    print_header("TEST 6: Audio Devices")
    
    try:
        import pyaudio
        
        audio = pyaudio.PyAudio()
        
        # List input devices
        print_info("Microphones:")
        mic_found = False
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  [{i}] {info['name']}")
                mic_found = True
        
        if not mic_found:
            print_error("Không tìm thấy microphone")
        
        # List output devices
        print_info("Speakers:")
        speaker_found = False
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0:
                print(f"  [{i}] {info['name']}")
                speaker_found = True
        
        if not speaker_found:
            print_error("Không tìm thấy speaker")
        
        audio.terminate()
        
        if mic_found and speaker_found:
            print_success("Audio devices OK")
            return True
        else:
            return False
            
    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def test_gemini_api():
    """Test Gemini API"""
    print_header("TEST 7: Gemini API")
    
    try:
        import google.generativeai as genai
        from utils.config_loader import get_config
        
        config = get_config()
        api_key = config.get('llm.api_key')
        
        if not api_key:
            print_warning("Chưa cấu hình API key")
            print_info("Thêm GEMINI_API_KEY vào file .env")
            return False
        
        genai.configure(api_key=api_key)
        
        # Thử list available models trước
        print_info("Đang lấy danh sách models có sẵn...")
        available_models = []
        try:
            models = genai.list_models()
            for m in models:
                if 'generateContent' in m.supported_generation_methods:
                    model_name_short = m.name.split('/')[-1] if '/' in m.name else m.name
                    available_models.append(model_name_short)
            if available_models:
                print_info(f"Models có sẵn: {', '.join(available_models[:5])}...")
        except Exception as e:
            print_warning(f"Không thể list models: {e}")
        
        # Danh sách model names để thử (theo thứ tự ưu tiên)
        model_names_to_try = [
            config.get('llm.model', 'gemini-1.5-flash'),  # Model từ config
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash-001',
            'gemini-1.5-pro-latest',
            'gemini-1.5-pro-001',
            'gemini-pro',
            'gemini-2.0-flash-exp',
        ]
        
        # Thêm các models từ available_models nếu có
        for avail_model in available_models[:3]:  # Thử 3 models đầu tiên
            if avail_model not in model_names_to_try:
                model_names_to_try.append(avail_model)
        
        model = None
        working_model = None
        
        # Thử từng model
        for model_name in model_names_to_try:
            try:
                print_info(f"Thử model: {model_name}...")
                test_model = genai.GenerativeModel(model_name)
                response = test_model.generate_content("Hello")
                # Nếu đến đây thì model hoạt động
                model = test_model
                working_model = model_name
                print_success(f"✅ Model {model_name} hoạt động!")
                break
            except Exception as e:
                error_msg = str(e)[:80]
                if "404" in error_msg or "not found" in error_msg.lower():
                    continue  # Model không tồn tại, thử model tiếp theo
                else:
                    # Lỗi khác (có thể là API key hoặc network)
                    print_warning(f"Lỗi với {model_name}: {error_msg}")
                    raise  # Re-raise để xử lý ở ngoài
        
        if not model:
            print_error("Không tìm thấy model nào hoạt động")
            print_info("Các models đã thử: " + ", ".join(model_names_to_try[:5]))
            print_info("Kiểm tra API key tại: https://makersuite.google.com/app/apikey")
            return False
        
        # Test với model đã tìm được
        print_info(f"Đang test với model: {working_model}...")
        response = model.generate_content("Say hello in Vietnamese")
        
        print_success("Gemini API hoạt động!")
        print_info(f"Model sử dụng: {working_model}")
        print_info(f"Response: {response.text[:100]}...")
        
        # Cảnh báo nếu model khác với config
        config_model = config.get('llm.model', 'gemini-1.5-flash')
        if working_model != config_model:
            print_warning(f"Model trong config ({config_model}) không hoạt động")
            print_info(f"Đề xuất cập nhật config.yaml: model: \"{working_model}\"")
        
        return True
        
    except Exception as e:
        print_error(f"Lỗi: {e}")
        print_info("Kiểm tra API key tại: https://makersuite.google.com/app/apikey")
        return False

def test_modules():
    """Test các module của bot"""
    print_header("TEST 8: Bot Modules")
    
    modules_to_test = [
        ("Person Detector", "modules.person_detector", "PersonDetector"),
        ("Wake Word Detector", "modules.wake_word", "WakeWordDetector"),
        ("STT Engine", "modules.stt_engine", "STTEngine"),
        ("LLM Client", "modules.llm_client", "LLMClient"),
        ("TTS Engine", "modules.tts_engine", "TTSEngine"),
        ("Face Display", "modules.face_display", "FaceDisplay"),
    ]
    
    failed = []
    for name, module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print_success(f"{name}")
        except Exception as e:
            print_error(f"{name}: {e}")
            failed.append(name)
    
    if failed:
        print_warning(f"Một số module bị lỗi: {', '.join(failed)}")
        return False
    else:
        print_success("Tất cả module OK!")
        return True

def main():
    """Chạy tất cả tests"""
    print(Fore.CYAN + Style.BRIGHT + """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                  UETBot System Test Suite                     ║
    ║                                                               ║
    ║  Test toàn bộ dependencies và modules trước khi chạy bot     ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Dependencies", test_imports),
        ("Config", test_config),
        ("Camera", test_camera),
        ("YOLO Model", test_yolo),
        ("Vosk Model", test_vosk),
        ("Audio Devices", test_audio),
        ("Gemini API", test_gemini_api),
        ("Bot Modules", test_modules),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = result
        except KeyboardInterrupt:
            print("\n\nTest bị dừng bởi user.")
            sys.exit(0)
        except Exception as e:
            print_error(f"Unexpected error in {name}: {e}")
            results[name] = False
        
        time.sleep(0.5)
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for name, result in results.items():
        if result:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
    
    print("\n" + "=" * 70)
    if passed == total:
        print_success(f"ALL TESTS PASSED ({passed}/{total})")
        print(Fore.GREEN + Style.BRIGHT + "\n🎉 Bot sẵn sàng hoạt động!")
        print(Fore.CYAN + "\nChạy bot: python3 main.py\n")
        return 0
    else:
        print_warning(f"SOME TESTS FAILED ({passed}/{total})")
        print(Fore.YELLOW + "\n⚠️  Hãy khắc phục các lỗi trước khi chạy bot.\n")
        return 1

if __name__ == "__main__":
    try:
        # Install colorama nếu chưa có
        try:
            import colorama
        except ImportError:
            print("Installing colorama...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
            import colorama
        
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nThoát.")
        sys.exit(0)

