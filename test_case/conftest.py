import pytest

from common.base_api import TestExecutor

@pytest.fixture(scope='session')
def login():
    """登录fixture，返回TestExecutor实例"""
    executor = TestExecutor()
    result = executor.case('login.yml', '衡泰登录')
    yield executor  # 返回executor实例，可以在测试中使用
    executor.close()  # 测试结束后关闭资源

