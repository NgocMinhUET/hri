"""
Config Loader - Load cấu hình từ config.yaml và .env
"""
import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

class ConfigLoader:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.config = None
        self.load()
        
    def load(self):
        """Load config từ YAML và environment variables"""
        # Load .env file
        load_dotenv()
        
        # Load YAML config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Inject environment variables
        if 'llm' in self.config:
            api_key_env = self.config['llm'].get('api_key_env', 'GEMINI_API_KEY')
            self.config['llm']['api_key'] = os.getenv(api_key_env)
    
    def get(self, key_path, default=None):
        """
        Lấy giá trị config theo đường dẫn
        Ví dụ: get('camera.resolution.width') -> 640
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def __getitem__(self, key):
        """Cho phép truy cập trực tiếp: config['camera']"""
        return self.config.get(key)

# Singleton instance
_config_instance = None

def get_config(config_path="config.yaml"):
    """Lấy config instance (singleton)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance

