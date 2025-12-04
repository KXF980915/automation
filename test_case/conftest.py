import os
import sys
import pytest
from pathlib import Path


def pytest_addoption(parser):
    """添加自定义命令行选项"""
    parser.addoption(
        "--allure-results-dir",
        action="store",
        default="allure-results",
        help="Allure结果目录"
    )
    parser.addoption(
        "--env",
        action="store",
        default="test",
        help="测试环境: dev/test/prod"
    )


def pytest_configure(config):
    """配置pytest"""
    # 设置Allure结果目录
    allure_dir = config.getoption("--allure-results-dir")

    # 转换为绝对路径
    if not os.path.isabs(allure_dir):
        # 获取项目根目录
        root_dir = Path(__file__).parent.parent
        allure_dir = str(root_dir / allure_dir)

    # 创建目录
    os.makedirs(allure_dir, exist_ok=True)

    # 设置环境变量
    env = config.getoption("--env")
    os.environ["TEST_ENV"] = env

    # 动态添加pytest选项
    config.option.alluredir = allure_dir
    config.option.clean_alluredir = True

    print(f"Allure结果目录: {allure_dir}")
    print(f"测试环境: {env}")


@pytest.fixture(scope="session")
def allure_results_dir(pytestconfig):
    """提供Allure结果目录的fixture"""
    return pytestconfig.getoption("--allure-results-dir")


@pytest.fixture(scope="session")
def test_env(pytestconfig):
    """提供测试环境的fixture"""
    return pytestconfig.getoption("--env")