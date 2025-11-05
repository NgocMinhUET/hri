"""
LLM Client - Tích hợp Gemini API cho khả năng hội thoại
"""
import google.generativeai as genai
from typing import List, Dict, Optional
from utils.logger import setup_logger
from utils.config_loader import get_config

class LLMClient:
    """Client để giao tiếp với Gemini LLM"""
    
    def __init__(self, config=None):
        """
        Args:
            config: ConfigLoader instance
        """
        self.config = config or get_config()
        self.logger = setup_logger("LLM")
        
        # Load cấu hình
        api_key = self.config.get('llm.api_key')
        if not api_key:
            raise ValueError("Chưa cấu hình GEMINI_API_KEY! Hãy thêm vào file .env")
        
        self.model_name = self.config.get('llm.model', 'gemini-1.5-flash')
        self.temperature = self.config.get('llm.temperature', 0.7)
        self.max_tokens = self.config.get('llm.max_tokens', 150)
        self.system_prompt = self.config.get('llm.system_prompt', '')
        
        # Cấu hình Gemini
        genai.configure(api_key=api_key)
        
        # Khởi tạo model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                'temperature': self.temperature,
                'max_output_tokens': self.max_tokens,
            }
        )
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
        # Bắt đầu chat session
        self.chat = self.model.start_chat(history=[])
        
        self.logger.info(f"LLM Client đã sẵn sàng! Model: {self.model_name}")
    
    def generate_response(self, user_message: str) -> str:
        """
        Tạo response từ user message
        
        Args:
            user_message: Tin nhắn từ người dùng
        
        Returns:
            Response từ LLM
        """
        try:
            # Thêm system prompt nếu đây là tin nhắn đầu tiên
            if not self.conversation_history and self.system_prompt:
                prompt = f"{self.system_prompt}\n\nUser: {user_message}"
            else:
                prompt = user_message
            
            self.logger.info(f"👤 User: {user_message}")
            
            # Gửi message
            response = self.chat.send_message(prompt)
            bot_response = response.text.strip()
            
            # Lưu history
            self.conversation_history.append({
                'role': 'user',
                'content': user_message
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': bot_response
            })
            
            self.logger.info(f"🤖 Bot: {bot_response}")
            
            return bot_response
            
        except Exception as e:
            self.logger.error(f"Lỗi khi gọi Gemini API: {e}")
            return "Xin lỗi, tôi đang gặp vấn đề kỹ thuật. Bạn có thể thử lại không?"
    
    def reset_conversation(self):
        """Reset cuộc hội thoại"""
        self.conversation_history = []
        self.chat = self.model.start_chat(history=[])
        self.logger.info("Đã reset cuộc hội thoại.")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Lấy lịch sử hội thoại"""
        return self.conversation_history.copy()
    
    def set_system_prompt(self, prompt: str):
        """Cập nhật system prompt"""
        self.system_prompt = prompt
        self.logger.info(f"Đã cập nhật system prompt: {prompt[:50]}...")

# Test standalone
if __name__ == "__main__":
    import sys
    
    try:
        llm = LLMClient()
        
        print("\n🤖 Gemini LLM Test")
        print("=" * 50)
        print("Hãy chat với bot!")
        print("(Gõ 'exit' hoặc 'quit' để thoát)")
        print("(Gõ 'reset' để reset cuộc hội thoại)\n")
        
        while True:
            user_input = input("👤 Bạn: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'thoát']:
                print("Tạm biệt!")
                break
            
            if user_input.lower() == 'reset':
                llm.reset_conversation()
                print("✅ Đã reset cuộc hội thoại.\n")
                continue
            
            response = llm.generate_response(user_input)
            print(f"🤖 Bot: {response}\n")
        
    except KeyboardInterrupt:
        print("\nThoát chương trình.")
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

