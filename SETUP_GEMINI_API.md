# 🔑 Hướng dẫn Cấu hình Gemini API Key

## Bước 1: Lấy Gemini API Key Miễn phí

### 1.1. Truy cập Google AI Studio

1. Mở trình duyệt và truy cập: **https://makersuite.google.com/app/apikey**
   - Hoặc: **https://aistudio.google.com/app/apikey**

2. **Đăng nhập** bằng tài khoản Google của bạn

3. Nếu lần đầu tiên, bạn sẽ thấy trang chào mừng → Click **"Get API Key"**

### 1.2. Tạo API Key

1. Click **"Create API Key"** hoặc **"Get API Key"**

2. Chọn một trong các options:
   - **Create API key in new project** (khuyến nghị cho lần đầu)
   - **Create API key in existing project** (nếu đã có project)

3. **Copy API Key** - Nó sẽ có dạng:
   ```
   AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

4. **Lưu lại API Key** này ở nơi an toàn (bạn sẽ không thấy lại được)

### 1.3. Kiểm tra API Key

- API Key bắt đầu bằng: `AIzaSy`
- Độ dài: khoảng 39 ký tự
- **Free tier**: 60 requests/phút, 1,500 requests/ngày

---

## Bước 2: Thêm API Key vào Project

### 2.1. Trên Windows (Development Machine)

```powershell
# Di chuyển vào thư mục project
cd D:\project\HRI

# Copy file template
copy .env.example .env

# Mở file .env bằng Notepad hoặc editor khác
notepad .env
```

**Hoặc dùng CMD:**
```cmd
cd D:\project\HRI
copy .env.example .env
notepad .env
```

**Hoặc dùng VS Code/Cursor:**
```powershell
# Mở file .env
code .env
# hoặc
cursor .env
```

### 2.2. Trên Jetson Nano

```bash
# Di chuyển vào thư mục project
cd ~/HRI

# Copy file template
cp .env.example .env

# Mở file .env bằng nano
nano .env
```

### 2.3. Thêm API Key

Trong file `.env`, thay thế:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Thành:
```
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Lưu file:**
- **Windows**: `Ctrl+S` hoặc `File → Save`
- **Jetson (nano)**: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## Bước 3: Kiểm tra Cấu hình

### 3.1. Test trên Windows

```powershell
# Chạy test
python test_all.py

# Hoặc test riêng LLM
python -c "from modules.llm_client import LLMClient; llm = LLMClient(); print('✅ Gemini API OK')"
```

### 3.2. Test trên Jetson Nano

```bash
# Chạy test
python test_all.py

# Hoặc test riêng LLM
python -c "from modules.llm_client import LLMClient; llm = LLMClient(); print('✅ Gemini API OK')"
```

---

## Bước 4: Troubleshooting

### ❌ Lỗi: "Chưa cấu hình GEMINI_API_KEY"

**Nguyên nhân:**
- File `.env` chưa được tạo
- API key chưa được thêm vào file `.env`
- Tên biến trong `.env` không đúng

**Giải pháp:**
```bash
# Kiểm tra file .env có tồn tại không
ls -la .env  # Trên Jetson
dir .env     # Trên Windows

# Kiểm tra nội dung file .env
cat .env     # Trên Jetson
type .env    # Trên Windows

# Đảm bảo format đúng:
# GEMINI_API_KEY=AIzaSy...
# (Không có khoảng trắng, không có quotes)
```

### ❌ Lỗi: "Invalid API Key"

**Nguyên nhân:**
- API key không đúng
- API key đã bị thu hồi
- API key bị copy thiếu ký tự

**Giải pháp:**
1. Kiểm tra lại API key trong file `.env`
2. Lấy API key mới từ Google AI Studio
3. Đảm bảo copy đầy đủ (không có khoảng trắng ở đầu/cuối)

### ❌ Lỗi: "API quota exceeded"

**Nguyên nhân:**
- Đã vượt quá giới hạn free tier (60 requests/phút)

**Giải pháp:**
- Đợi 1 phút rồi thử lại
- Hoặc upgrade lên paid tier

### ❌ Lỗi: "Network error"

**Nguyên nhân:**
- Jetson Nano không có kết nối Internet
- Firewall chặn

**Giải pháp:**
```bash
# Kiểm tra kết nối Internet
ping google.com

# Test API key trực tiếp
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

---

## Bước 5: Bảo mật API Key

### ⚠️ Quan trọng:

1. **Không commit file `.env` lên Git**
   - File `.env` đã được thêm vào `.gitignore`
   - Kiểm tra: `git status` không hiển thị `.env`

2. **Không chia sẻ API key**
   - Không gửi qua email, chat
   - Không đăng lên GitHub, forum

3. **Nếu API key bị lộ:**
   - Vào Google AI Studio ngay
   - Xóa API key cũ
   - Tạo API key mới
   - Cập nhật trong file `.env`

4. **Rotate API key định kỳ:**
   - Nên thay đổi API key mỗi 3-6 tháng

---

## Tóm tắt

```bash
# 1. Lấy API key từ: https://makersuite.google.com/app/apikey

# 2. Tạo file .env
cp .env.example .env

# 3. Thêm API key vào .env
nano .env  # hoặc notepad .env trên Windows

# 4. Kiểm tra
python test_all.py
```

---

## Tài liệu Tham khảo

- **Google AI Studio**: https://aistudio.google.com/
- **Gemini API Docs**: https://ai.google.dev/docs
- **API Key Management**: https://aistudio.google.com/app/apikey

---

**Chúc bạn thành công!** 🚀

