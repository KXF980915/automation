# 外部库
import json
import re

from requests import Response
import requests
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urljoin

# 内部库

from common.log import test_logger
from common.yaml_utils import YamlUtils


class ApiRequest:
    """接口请求封装"""

    def __init__(self, base_url: str = YamlUtils().read_config("base", "default_url")):
        self.base_url = base_url
        self.session = requests.session()
        self.logger = test_logger

    def send_request(self, request_config: Dict[str, Any], variables: Dict[str, Any] = None,
                     test_case_name: str = "unknown") -> requests.Response:
        """
        发送HTTP请求

        :param request_config: 请求配置
        :param variables: 变量字典
        :param test_case_name: 用例名称
        :return:
        """
        try:
            # 处理变量
            variables = variables or {}

            # 构建完整的URL
            url = request_config.get('url') or self.base_url
            url = url + request_config.get('path')

            # 准备请求参数
            method = request_config.get('method', 'GET').upper()
            headers = self._process_headers(request_config.get('headers', {}), variables)
            data = self._process_request_data(request_config, variables)
            params = self._process_params(request_config.get('params', {}), variables)
            cookies = self._process_cookies(request_config.get('cookies', {}), variables)
            auth = self._process_auth(request_config.get('auth'), variables)
            files = self._process_files(request_config.get('files'), variables)
            request_details = {
                'url': url,
                'method': method,
                'headers': headers,
                'params': params,
                'data': data
            }
            self.logger.log_request_details(test_case_name, request_details)
            # 设置超时
            timeout = request_config.get('timeout', 60)

            # 发送请求
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data if not self._is_json_content(headers) else None,
                json=data if self._is_json_content(headers) else None,
                cookies=cookies,
                auth=auth,
                files=files,
                timeout=timeout,
                allow_redirects=request_config.get('allow_redirects', True),
                verify=request_config.get('verify_ssl', False)
            )
            return response

        except Exception as e:
            self.logger.log_error(test_case_name, f"请求发送失败: {str(e)}", e)
            raise

    def _build_url(self, request_config: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """构建完整的URL"""
        base_url = self._replace_variables(request_config.get('url', '').strip(), variables) or self.base_url
        path = self._replace_variables(request_config.get('path', '').strip(), variables)

        if not base_url and not path:
            raise ValueError("URL和Path不能同时为空")

        if base_url and path:
            return urljoin(base_url, path)
        elif base_url:
            return base_url
        else:
            return path

    def _process_headers(self, headers: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, str]:
        """处理请求头"""
        processed_headers = {}
        for key, value in headers.items():
            if isinstance(value, str):
                processed_headers[key] = self._replace_variables(value, variables)
            else:
                processed_headers[key] = str(value)
        return processed_headers

    def _process_request_data(self, request_config: Dict[str, Any], variables: Dict[str, Any]) -> Any:
        """处理请求数据"""
        content_type = request_config.get('headers', {}).get('Content-Type', '').lower()

        # 根据Content-Type处理不同的数据格式
        if 'application/json' in content_type:
            data = request_config.get('json', request_config.get('data', {}))
            return self._process_nested_data(data, variables)
        elif 'application/x-www-form-urlencoded' in content_type:
            data = request_config.get('data', {})
            return self._process_form_data(data, variables)
        elif 'multipart/form-data' in content_type:
            data = request_config.get('data', {})
            return self._process_form_data(data, variables)
        else:
            # 默认处理为JSON
            data = request_config.get('json', request_config.get('data', {}))
            return self._process_nested_data(data, variables)

    def _process_params(self, params: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """处理URL参数"""
        return self._process_nested_data(params, variables)

    def _process_cookies(self, cookies: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """处理Cookies"""
        return self._process_nested_data(cookies, variables)

    def _process_form_data(self, data: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """处理表单数据"""
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                processed_data[key] = self._replace_variables(value, variables)
            elif isinstance(value, (dict, list)):
                processed_data[key] = str(value)
            else:
                processed_data[key] = value
        return processed_data

    def _process_auth(self, auth_config: Optional[Dict[str, Any]], variables: Dict[str, Any]) -> Optional[Tuple]:
        """处理认证信息"""
        if not auth_config:
            return None

        auth_type = auth_config.get('type', 'basic')
        if auth_type == 'basic':
            username = self._replace_variables(auth_config.get('username', ''), variables)
            password = self._replace_variables(auth_config.get('password', ''), variables)
            return (username, password)
        elif auth_type == 'bearer':
            token = self._replace_variables(auth_config.get('token', ''), variables)
            self.session.headers.update({'Authorization': f'Bearer {token}'})
            return None
        return None

    def _process_files(self, files_config: Optional[Dict[str, Any]], variables: Dict[str, Any]) -> Optional[
        Dict[str, Any]]:
        """处理文件上传"""
        if not files_config:
            return None

        files = {}
        for field_name, file_info in files_config.items():
            if isinstance(file_info, dict):
                file_path = self._replace_variables(file_info.get('path', ''), variables)
                # 实际文件处理逻辑
                # files[field_name] = (os.path.basename(file_path), open(file_path, 'rb'), file_info.get('content_type'))
            elif isinstance(file_info, str):
                file_path = self._replace_variables(file_info, variables)
                # files[field_name] = open(file_path, 'rb')

        return files

    def _is_json_content(self, headers: Dict[str, str]) -> bool:
        """判断是否为JSON内容类型"""
        content_type = headers.get('Content-Type', '').lower()
        return 'application/json' in content_type

    def _process_nested_data(self, data: Any, variables: Dict[str, Any]) -> Any:
        """处理嵌套的数据结构"""
        if isinstance(data, dict):
            return {k: self._process_nested_data(v, variables) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._process_nested_data(item, variables) for item in data]
        elif isinstance(data, str):
            return self._replace_variables(data, variables)
        else:
            return data

    def _replace_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """替换变量占位符"""
        if not isinstance(text, str) or '${' not in text:
            return text

        for var_name, var_value in variables.items():
            placeholder = f"${{{var_name}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(var_value))

        return text

    def close(self):
        """关闭会话"""
        self.session.close()


class ApiResponse:
    """响应处理器 - 专门处理HTTP响应的解析和验证"""

    def __init__(self):
        self.variables = {}
        self.logger = test_logger

    def process_response(self, response: Response, case_data: Dict[str, Any],
                         test_case_name: str = "unknown") -> Dict[str, Any]:
        """
        处理HTTP响应

        :param response: 响应对象
        :param case_data: 用例数据
        :param case_data: test_case_name 用例名称
        :return: 处理结果
        """
        try:
            # 解析响应数据
            response_data = self._parse_response_data(response)

            result = {
                'success': True,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'cookies': dict(response.cookies),
                'response_data': response_data,
                'response_time': response.elapsed.total_seconds(),
                'extracted_variables': {},
                'validation_results': []
            }
            # 响应日志
            self.logger.log_response_details(test_case_name, result)

            # 提取变量
            self._extract_variables(response, case_data.get('extract', {}), result)
            self.logger.log_variable_extraction(test_case_name, result['extracted_variables'])

            # 执行验证
            self._validate_response(response, response_data, case_data.get('validate', []), result)
            self.logger.log_validation_results(test_case_name, result['validation_results'])

            success = all(vr.get('pass', False) for vr in result['validation_results'])
            self.logger.log_test_end(test_case_name, success, result['response_time'])

            return result

        except Exception as e:
            self.logger.log_error(test_case_name, f"响应处理失败: {str(e)}", e)
            raise {
                'success': False,
                'error': str(e),
                'response': None
            }

    def _parse_response_data(self, response: Response) -> Any:
        """解析响应数据"""
        content_type = response.headers.get('Content-Type', '').lower()

        if 'application/json' in content_type:
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
        else:
            return response.text

    def _extract_variables(self, response: Any, extract_config: Dict[str, Any], result: Dict[str, Any]):
        """
        从响应中提取变量，支持从响应对象的不同部分提取
        :param response: 响应数据
        :param extract_config: 提取数据
        :param result:
        :return:
        """
        if not extract_config:
            return

        for var_name, var in extract_config.items():
            try:
                path = var
                save_as = var_name

                # 根据路径前缀确定提取来源
                if path.startswith('$.cookies'):
                    # 从 cookies 提取
                    cookie_path = path[10:]  # 去掉 '$.cookies'
                    variable_value = self._extract_from_cookies(response, cookie_path)

                elif path.startswith('$.headers'):
                    # 从 headers 提取
                    header_path = path[9:]  # 去掉 '$.headers'
                    variable_value = self._extract_from_headers(response, header_path)

                elif path.startswith('$.data'):
                    # 从响应体数据提取
                    data_path = path[6:]  # 去掉 '$.data'
                    response_data = getattr(response, 'json', lambda: {})() if hasattr(response, 'json') else {}
                    variable_value = self._extract_value_by_path(response_data, data_path)

                elif path.startswith('$.status'):
                    # 提取状态码
                    variable_value = response.status_code if hasattr(response, 'status_code') else None

                elif path.startswith('$.url'):
                    # 提取 URL
                    variable_value = response.url if hasattr(response, 'url') else None

                else:
                    # 默认从响应体提取
                    response_data = getattr(response, 'json', lambda: {})() if hasattr(response, 'json') else {}
                    variable_value = self._extract_value_by_path(response_data, path)

                if variable_value is not None:
                    # 保存变量
                    self.variables[save_as] = variable_value
                    result['extracted_variables'][save_as] = variable_value
                    self.logger.get_logger().info(f"提取变量成功: {save_as} = {variable_value}")
                else:
                    self.logger.get_logger().warning(f"提取变量失败: 路径 {path} 未找到数据")

            except Exception as e:
                self.logger.get_logger().warning(f"提取变量失败 {var_name}: {str(e)}")

    def _extract_from_cookies(self, response: Any, path: str) -> Any:
        """从 cookies 中提取数据"""
        if not hasattr(response, 'cookies'):
            return None

        cookies = response.cookies
        if not path or path == '.':
            return dict(cookies)

        # 去掉开头的 .
        if path.startswith('.'):
            path = path[1:]

        if not path:
            return dict(cookies)

        # 直接通过 cookie 名获取
        return cookies.get(path)

    def _extract_from_headers(self, response: Any, path: str) -> Any:
        """从 headers 中提取数据"""
        if not hasattr(response, 'headers'):
            return None

        headers = dict(response.headers)
        if not path or path == '.':
            return headers

        # 去掉开头的 .
        if path.startswith('.'):
            path = path[1:]

        if not path:
            return headers

        # 通过 header 名获取（不区分大小写）
        for header_name, value in headers.items():
            if header_name.lower() == path.lower():
                return value

        return None

    def _extract_from_cookies(self, response_obj: Any, cookie_name: str) -> Any:
        """从cookies中提取特定cookie值"""
        if not response_obj or not hasattr(response_obj, 'cookies'):
            return None

        # 获取特定cookie值
        return response_obj.cookies.get(cookie_name)

    def _extract_value_by_path(self, data: Any, path: str) -> Any:
        """根据路径提取值，支持 JSONPath 风格"""
        if not path or path == '.' or path == '$':
            return data

        # 标准化路径：去掉开头的 $ 和可能的 .
        if path.startswith('$'):
            path = path[1:]
        if path.startswith('.'):
            path = path[1:]

        # 如果路径为空，返回原始数据
        if not path:
            return data

        # 解析路径组件
        components = self._parse_jsonpath_components(path)
        current_data = data

        for component in components:
            if current_data is None:
                return None

            # 处理数组索引 [0], [1], ['key'], ["key"] 等
            if component.startswith('[') and component.endswith(']'):
                index_str = component[1:-1]  # 去掉方括号

                # 处理带引号的键 ['key'], ["key"]
                if (index_str.startswith("'") and index_str.endswith("'")) or \
                        (index_str.startswith('"') and index_str.endswith('"')):
                    key = index_str[1:-1]  # 去掉引号
                    if isinstance(current_data, dict):
                        current_data = current_data.get(key)
                    elif isinstance(current_data, list):
                        # 在列表中的每个元素中查找该键（如果元素是字典）
                        results = []
                        for item in current_data:
                            if isinstance(item, dict) and key in item:
                                results.append(item[key])
                        # 根据结果数量返回
                        if not results:
                            return None
                        current_data = results[0] if len(results) == 1 else results
                    else:
                        return None

                # 处理数字索引
                elif index_str.isdigit() or (index_str.startswith('-') and index_str[1:].isdigit()):
                    index = int(index_str)

                    if isinstance(current_data, list):
                        # 处理负索引
                        if index < 0:
                            index = len(current_data) + index

                        if 0 <= index < len(current_data):
                            current_data = current_data[index]
                        else:
                            return None
                    else:
                        return None

                # 处理不带引号的键 [key]（简写形式）
                else:
                    key = index_str
                    if isinstance(current_data, dict):
                        current_data = current_data.get(key)
                    elif isinstance(current_data, list):
                        # 尝试在列表元素中查找
                        results = []
                        for item in current_data:
                            if isinstance(item, dict) and key in item:
                                results.append(item[key])
                        if results:
                            current_data = results[0] if len(results) == 1 else results
                        else:
                            return None
                    else:
                        return None

            # 处理普通的键（无方括号）
            else:
                if isinstance(current_data, dict):
                    current_data = current_data.get(component)
                elif isinstance(current_data, list):
                    # 尝试将组件转换为索引
                    if component.isdigit():
                        index = int(component)
                        if 0 <= index < len(current_data):
                            current_data = current_data[index]
                        else:
                            return None
                    else:
                        # 在列表元素中查找键
                        results = []
                        for item in current_data:
                            if isinstance(item, dict) and component in item:
                                results.append(item[component])
                        if results:
                            current_data = results[0] if len(results) == 1 else results
                        else:
                            return None
                else:
                    return None

        return current_data

    def _parse_jsonpath_components(self, path: str) -> list:
        """解析 JSONPath 表达式为组件列表"""
        components = []
        i = 0
        length = len(path)

        while i < length:
            char = path[i]

            if char == '.':
                i += 1
                if i >= length:
                    break

                # 检查下一个字符是否是 [
                if path[i] == '[':
                    # 处理 .[ 的情况，跳过 . 直接处理 [
                    continue
                else:
                    # 处理 .key 的情况
                    start = i
                    while i < length and path[i] not in ['[', '.']:
                        i += 1
                    if start < i:
                        components.append(path[start:i])

            elif char == '[':
                # 找到匹配的 ]
                bracket_end = path.find(']', i)
                if bracket_end == -1:
                    raise ValueError(f"Unclosed bracket in path: {path}")

                components.append(path[i:bracket_end + 1])  # 包括方括号
                i = bracket_end + 1

            else:
                # 处理开头的键（没有 . 前缀）
                start = i
                while i < length and path[i] not in ['[', '.']:
                    i += 1
                if start < i:
                    components.append(path[start:i])

        return components

    def _validate_response(self, response: Response, response_data: Any,
                           validate_config: List, result: Dict[str, Any]):
        """验证响应"""
        if not validate_config:
            return

        for validation in validate_config:
            try:
                # 简化配置格式：[字段路径, 比较器, 期望值]
                if len(validation) >= 3:
                    field_path = validation[0]
                    comparator = validation[1]
                    expected = validation[2]
                    message = validation[3] if len(validation) > 3 else ''
                else:
                    self.logger.get_logger().error(f"验证配置格式错误: {validation}")
                    continue

                # 获取实际值
                actual_value = self._get_field_value(field_path, response, response_data)

                # 执行比较
                is_pass = self._compare_values(actual_value, expected, comparator)

                validation_result = {
                    'field': field_path,
                    'expected': expected,
                    'actual': actual_value,
                    'comparator': comparator,
                    'message': message,
                    'pass': is_pass
                }

                result['validation_results'].append(validation_result)

                if is_pass:
                    self.logger.get_logger().info(f"验证通过: {field_path} {comparator} {expected}")
                else:
                    error_msg = f"验证失败: {field_path} {comparator} {expected}, 实际值: {actual_value}"
                    if message:
                        error_msg = f"{message}: {error_msg}"
                    self.logger.get_logger().error(error_msg)
                    raise AssertionError(error_msg)

            except AssertionError as e:
                raise
            except Exception as e:
                self.logger.get_logger().error(f"验证执行失败: {str(e)}")
                result['validation_results'].append({
                    'field': field_path if 'field_path' in locals() else 'unknown',
                    'expected': expected if 'expected' in locals() else None,
                    'actual': None,
                    'comparator': comparator if 'comparator' in locals() else 'unknown',
                    'message': f"验证执行失败: {str(e)}",
                    'pass': False
                })
                raise AssertionError(f"验证执行失败: {str(e)}")

    def _get_field_value(self, field_path: str, response: Response, response_data: Any) -> Any:
        """根据路径表达式获取字段值"""
        # 所有路径都以$开头
        if not field_path.startswith('$'):
            # 如果不是路径表达式，返回整个响应数据
            return response_data

        # 移除开头的$符号
        path = field_path[1:]

        # 如果路径以.开头，去掉.
        if path.startswith('.'):
            path = path[1:]

        # 特殊字段处理
        if path == 'status_code':
            return response.status_code
        elif path == 'headers':
            return dict(response.headers)
        elif path == 'cookies':
            return dict(response.cookies)
        elif path == 'response_time':
            return response.elapsed.total_seconds()
        elif path == 'url':
            return response.url
        elif path == 'encoding':
            return response.encoding
        elif not path:  # 如果是"$"，返回整个响应数据
            return response_data

        # JSON响应数据路径提取（支持点号表示法）
        if '.' in path or '[' in path:
            return self._extract_json_path(response_data, path)

        # 直接键查找
        if isinstance(response_data, dict) and path in response_data:
            return response_data[path]

        # 尝试在响应数据中查找
        return self._extract_json_path(response_data, path)

    def _extract_json_path(self, data: Any, path: str) -> Any:
        """提取JSON路径的值"""
        if not path:
            return data

        # 支持多种路径格式
        if path == 'status_code':
            # 这里无法获取status_code，应该在_get_field_value中处理
            return None

        # 分割路径
        if '.' in path:
            parts = path.split('.')
        else:
            parts = [path]

        current = data

        for part in parts:
            if current is None:
                return None

            # 处理数组索引，如 items[0] 或 [0]
            if '[' in part and part.endswith(']'):
                # 处理两种情况：key[0] 和 [0]
                if part.startswith('['):
                    # 直接数组索引，如 [0]
                    index = int(part[1:-1])
                    if isinstance(current, list) and 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
                else:
                    # 带键名的数组索引，如 items[0]
                    key = part.split('[')[0]
                    index_str = part.split('[')[1][:-1]
                    index = int(index_str)

                    if isinstance(current, dict) and key in current:
                        current = current[key]
                        if isinstance(current, list) and 0 <= index < len(current):
                            current = current[index]
                        else:
                            return None
                    else:
                        return None
            else:
                # 普通键访问
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list):
                    # 如果是列表，可以按索引访问
                    try:
                        index = int(part)
                        if 0 <= index < len(current):
                            current = current[index]
                        else:
                            return None
                    except ValueError:
                        # 如果不是数字，尝试在列表元素中查找
                        found = False
                        for item in current:
                            if isinstance(item, dict) and part in item:
                                current = item[part]
                                found = True
                                break
                        if not found:
                            return None
                else:
                    return None

        return current

    def _compare_values(self, actual: Any, expected: Any, comparator: str) -> bool:
        """比较值，支持常用比较运算符"""
        try:
            # 处理None值
            if actual is None:
                return False

            # 处理比较器字符串
            comparator = str(comparator).strip()

            # 自动转换类型匹配（字符串和数字）
            if comparator in ['==', '!=', '>', '<', '>=', '<=']:
                # 尝试将actual和expected转换为相同类型
                try:
                    # 如果两者都是数字字符串，转换为数字比较
                    if isinstance(actual, (int, float)) or (
                            isinstance(actual, str) and actual.replace('.', '', 1).isdigit()):
                        if isinstance(expected, (int, float)) or (
                                isinstance(expected, str) and expected.replace('.', '', 1).isdigit()):
                            actual_float = float(actual)
                            expected_float = float(expected)

                            if comparator == '==':
                                return abs(actual_float - expected_float) < 0.000001  # 浮点数比较容差
                            elif comparator == '!=':
                                return abs(actual_float - expected_float) > 0.000001
                            elif comparator == '>':
                                return actual_float > expected_float
                            elif comparator == '<':
                                return actual_float < expected_float
                            elif comparator == '>=':
                                return actual_float >= expected_float
                            elif comparator == '<=':
                                return actual_float <= expected_float
                except:
                    pass  # 转换失败，按原样比较

            # 按原样比较
            if comparator == '==':
                return str(actual) == str(expected)
            elif comparator == '!=':
                return str(actual) != str(expected)
            elif comparator == '>':
                try:
                    return float(actual) > float(expected)
                except:
                    return False
            elif comparator == '<':
                try:
                    return float(actual) < float(expected)
                except:
                    return False
            elif comparator == '>=':
                try:
                    return float(actual) >= float(expected)
                except:
                    return False
            elif comparator == '<=':
                try:
                    return float(actual) <= float(expected)
                except:
                    return False
            elif comparator in ['in', '包含']:
                return str(expected) in str(actual)
            elif comparator in ['not in', '不包含']:
                return str(expected) not in str(actual)
            elif comparator in ['regex', '正则匹配']:
                return bool(re.search(str(expected), str(actual)))
            elif comparator in ['length', '长度']:
                try:
                    return len(actual) == int(expected)
                except:
                    return False
            elif comparator in ['startswith', '以开头']:
                return str(actual).startswith(str(expected))
            elif comparator in ['endswith', '以结尾']:
                return str(actual).endswith(str(expected))
            elif comparator in ['type', '类型']:
                return type(actual).__name__ == str(expected)
            elif comparator in ['exists', '存在']:
                return actual is not None
            elif comparator in ['not_exists', '不存在']:
                return actual is None
            else:
                self.logger.get_logger().warning(f"不支持的比较器: {comparator}")
                return False
        except Exception as e:
            self.logger.get_logger().error(
                f"比较失败: {e}, actual={actual}, expected={expected}, comparator={comparator}")
            return False

    def set_variable(self, name: str, value: Any):
        """设置变量"""
        self.variables[name] = value

    def get_variable(self, name: str) -> Any:
        """获取变量"""
        return self.variables.get(name)

    def clear_variables(self):
        """清空变量"""
        self.variables.clear()

    def get_all_variables(self) -> Dict[str, Any]:
        """获取所有变量"""
        return self.variables.copy()


# if __name__ == '__main__':
#     api = ApiRequest()
#     yu = YamlUtils()
#     a = yu.get_yaml_case('login.yml', '用户登录成功')
#     request = api.send_request(a.get('request'))
#     print(request.json())
#     res = ApiResponse()
#     s = res.process_response(request, a)
#     print(s)
