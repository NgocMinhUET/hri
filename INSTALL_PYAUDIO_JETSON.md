# Cài đặt PyAudio trên Jetson Nano

PyAudio cần compile từ source trên Jetson Nano (ARM64). Làm theo các bước sau:

## Bước 1: Cài đặt System Dependencies

```bash
# Cài đặt portaudio development libraries
sudo apt update
sudo apt install -y portaudio19-dev python3-pyaudio libportaudio2 libportaudiocpp0

# Cài đặt build tools (nếu chưa có)
sudo apt install -y build-essential python3-dev
```

## Bước 2: Cài đặt PyAudio

### Cách 1: Cài từ pip (sau khi có dependencies)

```bash
# Đảm bảo đang trong conda environment
conda activate hri

# Cài PyAudio
pip install pyaudio==0.2.13
```

### Cách 2: Nếu vẫn lỗi, thử build với verbose

```bash
pip install pyaudio==0.2.13 --verbose --no-cache-dir
```

### Cách 3: Cài từ source (nếu pip vẫn lỗi)

```bash
# Tải source code
cd /tmp
wget http://people.csail.mit.edu/hubert/pyaudio/packages/pyaudio-0.2.13.tar.gz
tar -xzf pyaudio-0.2.13.tar.gz
cd pyaudio-0.2.13

# Build và cài
python setup.py build
python setup.py install
```

## Bước 3: Kiểm tra

```bash
python -c "import pyaudio; print('PyAudio version:', pyaudio.__version__)"
```

## Troubleshooting

### Lỗi: "portaudio.h: No such file or directory"

```bash
# Cài lại portaudio-dev
sudo apt install --reinstall portaudio19-dev
```

### Lỗi: "error: command 'aarch64-linux-gnu-gcc' failed"

```bash
# Cài build essentials
sudo apt install -y build-essential gcc g++ make
```

### Lỗi: "fatal error: Python.h: No such file or directory"

```bash
# Cài Python development headers
sudo apt install -y python3-dev
```

## Alternative: Sử dụng system PyAudio

Nếu vẫn không build được, có thể dùng system PyAudio:

```bash
# Cài system package
sudo apt install -y python3-pyaudio

# Kiểm tra
python3 -c "import pyaudio; print('OK')"
```

Tuy nhiên, cách này có thể không tương thích với conda environment.

