import os
from typing import Dict, Any


class Config:
    """配置管理类"""

    def __init__(self):
        # 基础路径配置
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATA_DIR = os.path.join(self.BASE_DIR, 'data')
        self.CASE_DATA_DIR = os.path.join(self.BASE_DIR, 'case_data')
        self.TESTS_DIR = os.path.join(self.BASE_DIR, 'tests')

        # 环境配置
        self.ENV = os.getenv('TEST_ENV', 'dev')

        # 不同环境的URL配置
        self.URLS = {
            'dev': 'http://dev.example.com',
            'test': 'http://test.example.com',
            'prod': 'http://api.example.com'
        }

        # 请求配置
        self.TIMEOUT = 30
        self.MAX_RETRIES = 3

        # 全局变量存储
        self.global_variables: Dict[str, Any] = {}

    @property
    def BASE_URL(self) -> str:
        """获取基础URL"""
        return self.URLS.get(self.ENV, self.URLS['dev'])

    def set_global_variable(self, key: str, value: Any) -> None:
        """设置全局变量"""
        self.global_variables[key] = value

    def get_global_variable(self, key: str, default: Any = None) -> Any:
        """获取全局变量"""
        return self.global_variables.get(key, default)


# 创建全局配置实例
config = Config()