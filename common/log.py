import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any
import colorlog

from common.os_path import get_object_path


class TestLogger:
    """测试用例执行日志处理器"""

    def __init__(self, log_level: str = "INFO", log_dir: str = get_object_path()+"\logs",
                 console_output: bool = True, file_output: bool = True):
        """
        初始化日志处理器

        :param log_level: 日志级别
        :param log_dir: 日志目录
        :param console_output: 是否输出到控制台
        :param file_output: 是否输出到文件
        """
        self.log_level = log_level
        self.log_dir = log_dir
        self.console_output = console_output
        self.file_output = file_output
        self.loggers = {}

        # 创建日志目录
        if file_output and not os.path.exists(log_dir):
            os.makedirs(log_dir)

    logging.getLogger().handlers = []
    logging.getLogger().propagate = False

    def get_logger(self, test_case_name: str = "执行日志") -> logging.Logger:
        """
        获取指定测试用例的日志器

        :param test_case_name: 测试用例名称
        :return: 日志器实例
        """
        if test_case_name in self.loggers:
            return self.loggers[test_case_name]

        # 创建日志器
        logger = logging.getLogger(test_case_name)
        logger.setLevel(getattr(logging, self.log_level.upper()))
        logger.handlers = []  # 清除已有处理器
        logger.propagate = False  # 关键：禁止传播到根日志器

        # 设置日志格式
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )

        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台处理器
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # 文件处理器
        if self.file_output:
            timestamp = datetime.now().strftime("%Y%m%d")
            log_filename = f"{test_case_name}_{timestamp}.log"
            log_filepath = os.path.join(self.log_dir, log_filename)

            file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        self.loggers[test_case_name] = logger
        return logger

    def log_test_start(self, test_case_name: str):
        """记录测试开始"""
        logger = self.get_logger(test_case_name)
        logger.info(f"开始执行测试用例: {test_case_name}")

    def log_request_details(self, test_case_name: str, request_details: Dict[str, Any]):
        """记录请求详情"""
        logger = self.get_logger(test_case_name)
        logger.info("请求详情:")
        logger.info(f"  URL: {request_details.get('url')}")
        logger.info(f"  方法: {request_details.get('method')}")
        logger.info(f"  请求头: {request_details.get('headers', {})}")
        logger.info(f"  参数: {request_details.get('params', {})}")
        logger.info(f"  数据: {request_details.get('data', {})}")

    def log_response_details(self, test_case_name: str, response_result: Dict[str, Any]):
        """记录响应详情"""
        logger = self.get_logger(test_case_name)
        logger.info("响应详情:")
        logger.info(f"  状态码: {response_result.get('status_code')}")
        logger.info(f"  响应时间: {response_result.get('response_time')}秒")

        # 记录响应数据（截断长内容）
        response_data = response_result.get('response_data', {})
        json_res = json.dumps(response_data,indent=4,ensure_ascii=False)
        logger.info(f"  响应数据: \n{json_res}")

    def log_validation_results(self, test_case_name: str, validation_results: list):
        """记录验证结果"""
        logger = self.get_logger(test_case_name)

        if not validation_results:
            logger.info("无验证项")
            return

        logger.info("验证结果:")
        for result in validation_results:
            field = result.get('field', '')
            expected = result.get('expected', '')
            actual = result.get('actual', '')
            comparator = result.get('comparator', '')
            is_pass = result.get('pass', False)
            message = result.get('message', '')

            status_icon = "✅" if is_pass else "❌"
            status_text = "通过" if is_pass else "失败"

            log_message = f"  {status_icon} {field} {comparator} {expected} -> 实际: {actual}"
            if message:
                log_message += f" ({message})"

            if is_pass:
                logger.info(log_message)
            else:
                logger.error(log_message)

    def log_variable_extraction(self, test_case_name: str, extracted_variables: Dict[str, Any]):
        """记录变量提取结果"""
        logger = self.get_logger(test_case_name)
        if extracted_variables:
            logger.info("变量提取:")
            for var_name, var_value in extracted_variables.items():
                logger.info(f"  {var_name}: {var_value}")
        else:
            logger.debug("无变量提取")

    def log_test_end(self, test_case_name: str, success: bool, execution_time: float = None):
        """记录测试结束"""
        logger = self.get_logger(test_case_name)

        result_text = "成功" if success else "失败"
        result_icon = "🎉" if success else "💥"

        logger.info("-" * 40)
        if execution_time is not None:
            logger.info(f"测试用例执行{result_text} {result_icon} - 耗时: {execution_time:.2f}秒")
        else:
            logger.info(f"测试用例执行{result_text} {result_icon}")
        logger.info("=" * 60)
        logger.info("")  # 空行分隔

    def log_error(self, test_case_name: str, error_message: str, exception: Exception = None):
        """记录错误信息"""
        logger = self.get_logger(test_case_name)
        logger.error(f"执行错误: {error_message}")
        if exception:
            logger.exception(exception)

    def log_warning(self, test_case_name: str, warning_message: str):
        """记录警告信息"""
        logger = self.get_logger(test_case_name)
        logger.warning(warning_message)

    def log_debug_info(self, test_case_name: str, debug_message: str):
        """记录调试信息"""
        logger = self.get_logger(test_case_name)
        logger.debug(debug_message)


# 全局日志处理器实例
test_logger = TestLogger()


def setup_logger(level: str = "INFO", log_dir: str = ".\logs",
                 console: bool = True, file: bool = True) -> TestLogger:
    """
    设置全局日志处理器

    :param level: 日志级别
    :param log_dir: 日志目录
    :param console: 是否控制台输出
    :param file: 是否文件输出
    :return: 日志处理器实例
    """
    global test_logger
    test_logger = TestLogger(level, log_dir, console, file)
    return test_logger


def get_logger() -> TestLogger:
    """获取全局日志处理器"""
    return test_logger