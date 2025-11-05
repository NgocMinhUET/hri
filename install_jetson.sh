#!/bin/bash
# Script cài đặt tự động dependencies cho UETBot trên Jetson Nano
# Chạy: bash install_jetson.sh

set -e  # Exit on error

echo "🚀 Bắt đầu cài đặt dependencies cho Jetson Nano..."

# Kiểm tra conda environment
if ! command -v conda &> /dev/null; then
    echo "❌ Conda chưa được cài đặt. Hãy cài Miniconda trước."
    exit 1
fi

# Activate conda environment (nếu chưa active)
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "📦 Activating conda environment 'hri'..."
    source ~/miniforge3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null
    conda activate hri
fi

echo "✅ Conda environment: $CONDA_DEFAULT_ENV"

# 1. Cài system dependencies cho PyAudio
echo ""
echo "📚 Bước 1: Cài đặt system dependencies..."
sudo apt update
sudo apt install -y portaudio19-dev python3-dev build-essential
sudo apt install -y libportaudio2 libportaudiocpp0

# 2. Upgrade pip
echo ""
echo "⬆️  Bước 2: Upgrade pip..."
pip install --upgrade pip

# 3. Cài PyAudio trước (vì cần build)
echo ""
echo "🎤 Bước 3: Cài đặt PyAudio..."
pip install pyaudio==0.2.13 || {
    echo "⚠️  PyAudio build failed, trying alternative method..."
    # Thử cài system pyaudio
    sudo apt install -y python3-pyaudio || echo "⚠️  System PyAudio also failed"
}

# 4. Cài các package còn lại (trừ pyaudio)
echo ""
echo "📦 Bước 4: Cài đặt Python packages..."
pip install numpy>=1.22.2
pip install opencv-python==4.8.0.74
pip install Pillow pydub webrtcvad librosa
pip install vosk SpeechRecognition
pip install pyttsx3 gTTS
pip install google-generativeai requests
pip install pygame python-dotenv pyyaml
pip install ultralytics==8.0.196

# 5. Kiểm tra PyTorch
echo ""
echo "🔥 Bước 5: Kiểm tra PyTorch..."
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())" || {
    echo "⚠️  PyTorch chưa được cài. Hãy cài từ NVIDIA wheel:"
    echo "   wget https://nvidia.box.com/shared/static/ssf2v7pf5i245fk4i0q926hy4imzs2ph.whl -O torch.whl"
    echo "   pip install torch.whl"
}

# 6. Kiểm tra các package quan trọng
echo ""
echo "✅ Bước 6: Kiểm tra packages..."
python -c "import numpy; print('✅ numpy:', numpy.__version__)" || echo "❌ numpy failed"
python -c "import cv2; print('✅ opencv:', cv2.__version__)" || echo "❌ opencv failed"
python -c "import pyaudio; print('✅ pyaudio:', pyaudio.__version__)" || echo "❌ pyaudio failed"
python -c "import vosk; print('✅ vosk OK')" || echo "❌ vosk failed"
python -c "import ultralytics; print('✅ ultralytics OK')" || echo "❌ ultralytics failed"

echo ""
echo "🎉 Hoàn tất! Chạy 'python test_all.py' để kiểm tra toàn bộ hệ thống."

