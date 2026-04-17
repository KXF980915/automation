import pytest
from common.base_api import TestExecutor as te
import sys
import io
import pytest
#
def pytest_configure(config):
    """配置 pytest 使用 UTF-8 输出"""
    # 设置控制台编码为 UTF-8
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def pytest_collection_modifyitems(items):
    """修改测试项显示，确保中文正确显示"""
    for item in items:
        # 处理参数化测试的 ID 显示
        if hasattr(item, 'callspec'):
            params = item.callspec.params
            if 'data' in params and isinstance(params['data'], dict):
                name = params['data'].get('name', '')
                if name:
                    # 替换 nodeid 中的 Unicode 转义
                    if '[' in item.nodeid and ']' in item.nodeid:
                        base = item.nodeid.split('[')[0]
                        item._nodeid = f"{base}[{name}]"

#银行间债券
GZ = "20国开10"
@pytest.fixture(scope="session")
def ebd_token():
    data = {'username': 'admin', 'password': 'GJqQ1c3wPgdBCQyG0QnZzA=='}
    res = te().case('login.yml', 'ebond登录', data)
    return res['response_data']['access_token']

def hentai_token():
    data = {'username': '17375770915', 'password': 'GJqQ1c3wPgdBCQyG0QnZzA=='}
    te().case('login.yml', 'ebond登录', data)
