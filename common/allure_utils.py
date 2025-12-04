import allure
import json
from typing import Dict, Any, Callable
from functools import wraps


class AllureReport:
    """Allure报告增强工具类"""

    @staticmethod
    def attach_request_response(request_details: Dict, response_result: Dict):
        """附加请求响应信息到Allure报告"""
        # 请求信息
        request_info = {
            "URL": request_details.get('url'),
            "Method": request_details.get('method'),
            "Headers": request_details.get('headers', {}),
            "Params": request_details.get('params', {}),
            "Data": request_details.get('data', {})
        }

        allure.attach(
            body=json.dumps(request_info, indent=2, ensure_ascii=False),
            name="请求详情",
            attachment_type=allure.attachment_type.JSON
        )

        # 响应信息
        response_info = {
            "Status Code": response_result.get('status_code'),
            "Response Time": f"{response_result.get('response_time', 0):.3f}s",
            "Response Data": response_result.get('response_data', {})
        }

        allure.attach(
            body=json.dumps(response_info, indent=2, ensure_ascii=False),
            name="响应详情",
            attachment_type=allure.attachment_type.JSON
        )

    @staticmethod
    def attach_variables(extracted_vars: Dict[str, Any], title: str = "提取的变量"):
        """附加变量信息"""
        if extracted_vars:
            var_text = "\n".join([f"{k}: {v}" for k, v in extracted_vars.items()])
            allure.attach(
                body=var_text,
                name=title,
                attachment_type=allure.attachment_type.TEXT
            )

    @staticmethod
    def attach_validation_results(validation_results: list):
        """附加验证结果"""
        if validation_results:
            results_text = []
            for vr in validation_results:
                status = "✅ PASS" if vr.get('pass') else "❌ FAIL"
                results_text.append(
                    f"{status} | {vr.get('field')} | "
                    f"期望: {vr.get('expected')} | 实际: {vr.get('actual')}"
                )

            allure.attach(
                body="\n".join(results_text),
                name="验证结果",
                attachment_type=allure.attachment_type.TEXT
            )

    @staticmethod
    def allure_step(step_name: str = None):
        """
        装饰器：将函数调用作为Allure步骤
        用法：
        @AllureReport.allure_step("执行登录操作")
        def login(username, password):
            ...
        """

        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                step_title = step_name or f"{func.__name__}"
                with allure.step(step_title):
                    # 记录参数
                    if args or kwargs:
                        params = {}
                        if args:
                            params['args'] = args
                        if kwargs:
                            params['kwargs'] = kwargs

                        allure.attach(
                            body=json.dumps(params, indent=2),
                            name="函数参数",
                            attachment_type=allure.attachment_type.JSON
                        )

                    # 执行函数
                    result = func(*args, **kwargs)

                    # 记录返回值
                    if result is not None:
                        allure.attach(
                            body=str(result),
                            name="返回值",
                            attachment_type=allure.attachment_type.TEXT
                        )

                    return result

            return wrapper

        return decorator


def allure_testcase(name=None, feature=None, story=None):
    """
    测试用例装饰器 - 简化Allure标记使用
    用法：
    @allure_testcase("用户登录测试", feature="登录模块", story="登录成功")
    def test_login():
        ...
    """

    def decorator(func):
        @allure.title(name or func.__name__)
        @allure.feature(feature or "未分类")
        @allure.story(story or func.__name__)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator