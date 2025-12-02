# 内部库
from common.log import test_logger
from common.os_path import get_object_path
from common.request_encapsulation import ApiRequest, ApiResponse
from common.yaml_utils import YamlUtils
from common.csv_utils import DataReplaceUtils


# 外部库
from typing import Dict, Any, List


class TestExecutor:
    """测试执行器 - 协调请求和响应处理"""

    def __init__(self):
        self.request_api = ApiRequest()
        self.response_api = ApiResponse()
        self.logger = test_logger.get_logger()
        # 初始化时清空extract文件，确保每次执行都是干净的
        # clean_extract()

    def case(self, path: str, case_name: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行测试用例
        :param path: 路径
        :param case_name: 用例名
        :param data: yaml文件中需要替换的变量
        :return: 执行结果
        """
        try:
            yaml_data = YamlUtils().get_yaml_case(path, case_name)
            all_variables = self._merge_variables(data)

            # 变量替换
            if all_variables:
                case_data = DataReplaceUtils().replace_variables(yaml_data, all_variables)
            else:
                case_data = yaml_data

            # 获取请求配置
            request_config = case_data.get('request', {})

            # 发送请求
            response = self.request_api.send_request(
                request_config,
                all_variables,
                case_name
            )

            # 处理响应
            result = self.response_api.process_response(response, case_data, case_name)

            # 保存提取的变量到extract.yml文件
            self._save_extracted_variables(result.get('extracted_variables', {}))

            # 执行teardown
            self._execute_teardown(case_data.get('teardown', []))

            return result
        except Exception as e:
            self.logger.error(f"用例执行失败: {str(e)}")
            raise {
                'success': False,
                'error': str(e)
            }


    def _merge_variables(self, external_variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        合并变量，按照优先级: 提取的变量 > 传入的variables

        Args:
            external_variables: 外部传入的变量

        Returns:
            合并后的变量字典
        """
        merged_variables = {}

        # 第一优先级: 当前响应处理器中的变量 (最近提取的变量)
        response_variables = self.response_api.get_all_variables()
        merged_variables.update(response_variables)

        # 第二优先级: extract.yml文件中的变量 (历史提取的变量)
        try:
            # 读取extract.yml中的所有变量
            extract_variables = self._read_all_extract_variables()
            # extract.yml中的变量会覆盖response_variables中的同名变量
            merged_variables.update(extract_variables)
        except Exception as e:
            self.logger.warning(f"读取extract.yml文件失败: {e}")

        # 第三优先级: 外部传入的变量 (最低优先级)
        if external_variables:
            # 外部传入的变量不会覆盖已存在的变量
            for key, value in external_variables.items():
                if key not in merged_variables:
                    merged_variables[key] = value

        return merged_variables

    def _read_all_extract_variables(self) -> Dict[str, Any]:
        """
        读取extract.yml文件中的所有变量

        Returns:
            变量字典
        """
        try:
            # 由于yaml_loader中的read_extract只能读取单个节点，需要改进
            with open(get_object_path() + 'extract.yml', 'r', encoding='utf-8') as f:
                import yaml
                data = yaml.safe_load(f)
                return data if data else {}
        except FileNotFoundError:
            return {}
        except Exception as e:
            self.logger.warning(f"读取extract.yml失败: {e}")
            return {}

    def _save_extracted_variables(self, extracted_variables: Dict[str, Any]):
        """
        保存提取的变量到extract.yml文件

        Args:
            extracted_variables: 提取的变量字典
        """
        if not extracted_variables:
            return

        try:
            # 读取现有的变量
            existing_variables = self._read_all_extract_variables()
            # 合并变量（新变量会覆盖旧变量）
            existing_variables.update(extracted_variables)
            # 写回文件
            with open(get_object_path() + 'extract.yml', 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(existing_variables, f, allow_unicode=True, default_flow_style=False)

            self.logger.info(f"成功保存变量到extract.yml: {list(extracted_variables.keys())}")
        except Exception as e:
            self.logger.error(f"保存变量到extract.yml失败: {e}")

    def _execute_teardown(self, teardown_config: list):
        """执行teardown操作"""
        if not teardown_config:
            return

        for action in teardown_config:
            try:
                action_type = action.get('action')
                params = action.get('params', {})

                if action_type == 'logout':
                    self._logout(params)
                elif action_type == 'clear_variables':
                    self._clear_specific_variables(params.get('variables', []))
                elif action_type == 'clean_extract_file':
                    # 清空extract.yml文件
                    YamlUtils().clean_extract()
                    self.logger.info("已清空extract.yml文件")

            except Exception as e:
                self.logger.error(f"Teardown操作执行失败: {str(e)}")

    def _logout(self, params: Dict[str, Any]):
        """登出操作"""
        token = params.get('token', '')
        self.logger.info(f"执行登出操作，token: {token}")
        # 实际登出逻辑

    def _clear_specific_variables(self, variables: List[str]):
        """清理特定变量"""
        for var_name in variables:
            if var_name in self.response_api.variables:
                del self.response_api.variables[var_name]
                self.logger.info(f"清理变量: {var_name}")

    def set_variable(self, name: str, value: Any):
        """设置变量"""
        self.response_api.set_variable(name, value)

    def get_variable(self, name: str) -> Any:
        """获取变量"""
        return self.response_api.get_variable(name)

    def get_all_variables(self) -> Dict[str, Any]:
        """获取所有变量"""
        return self.response_api.get_all_variables()

    def clear_variables(self):
        """清空所有变量"""
        self.response_api.clear_variables()

    def close(self):
        """关闭资源"""
        self.request_api.close()
        # 关闭时清空extract文件
        YamlUtils().clean_extract()


# if __name__ == '__main__':
#     te = TestExecutor()
#     sk = te.case('login.yml', '用户登录成功')
