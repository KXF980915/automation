import json
import os.path
from typing import Dict, Any
import re
import yaml

from common.log import test_logger
from common.os_path import get_object_path


class YamlUtils:
    """yaml文件工具类"""

    def __init__(self):
        self.logger = test_logger.get_logger()

    def read_yaml(self, file_path: str, default_file='case_data') -> Dict[str, Any]:
        """
        获取yaml数据
        :param file_path: 文件路径（支持相对/绝对）
        :param default_file: yaml文件默认存放路径
        :return:
        """
        try:
            if os.path.isabs(file_path):
                path = file_path
            else:
                path = os.path.join(get_object_path(), default_file, file_path)
            if not os.path.isabs(path):
                raise FileNotFoundError(f"YAML文件不存在: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                print(data)
            return data if data is not None else {}
        except FileNotFoundError:
            raise
        except yaml.YAMLError as e:
            raise ValueError(f"YAML文件解析错误: {e}")
        except Exception as e:
            raise RuntimeError(f"读取YAML文件失败: {e}")

    def replace_yaml(self, data, replacements: Dict):
        """
        替换数据结构中的 ${key} 格式变量

        Args:
            data: 从YAML读取的数据
            replacements: 变量替换字典，如 {'admin': 'value'}

        Returns:
            替换变量后的数据
        """
        # 处理字典类型
        if isinstance(data, dict):
            return {key: self.replace_yaml(value, replacements) for key, value in data.items()}

        # 处理列表类型
        elif isinstance(data, list):
            return [self.replace_yaml(item, replacements) for item in data]

        # 处理字符串类型 - 进行变量替换
        elif isinstance(data, str):
            pattern = r'\$\{(\w+)\}'

            def replace_match(match):
                var_name = match.group(1)
                if var_name in replacements:
                    return str(replacements[var_name])
                else:
                    print(f"警告: 未定义的变量 ${{{var_name}}}")
                    return match.group(0)

            return re.sub(pattern, replace_match, data)

        # 其他类型直接返回
        else:
            return data

    def get_yaml_case(self, file_path, case_name: str):
        """
        获取yml文件中的用例
        :param file_path 路径（支持全局/局部）
        :param case_name: 用例名
        :return: 没找到返回None
        """
        try:
            yml_data = self.read_yaml(file_path)

            # yaml文件中必须有test_cases
            if 'test_cases' not in yml_data:
                self.logger.error(f"YAML文件中必须存在'test_cases'键 - {file_path}")
                return None
            cases = yml_data['test_cases']

            # 一个yaml文件中禁止有重复的用例名
            name = [case['case_name'] for case in cases]
            repeat_name = [repeat_name for repeat_name in name if name.count(repeat_name) > 1]
            if repeat_name:
                self.logger.error(f'case_name用例名称禁止重复，重复case_name:{set(repeat_name)}')
                return None

            # 提取用例
            for case in cases:
                if case['case_name'] == case_name:
                    self.logger.debug(f'提取用例成功:{case_name}')
                    return case
            self.logger.warning(f"未找到对应用例：{case_name} - 在文件 {file_path} 中")
            return None
        except Exception as e:
            self.logger.error(f"获取用例失败：{str(e)} - 文件：{file_path}, 用例：{case_name}")
            return None

    def read_extract(self, node_name=None):
        """
        读取extract.yml文件(存放提取的变量)
        :param node_name: 节点名
        :return:
        """
        try:
            with open(get_object_path() + 'extract.yml', 'r', encoding='utf-8') as f:
                var = yaml.load(stream=f, Loader=yaml.FullLoader) or {}
            if node_name is None:
                return var
            return var.get(node_name)
        except FileNotFoundError:
            return {} if node_name is None else None

    def write_extract(self, data):
        """
        写入extract.yml文件(以追加形式写入)
        :param data:
        :return:
        """
        existing_data = self.read_extract() or {}
        existing_data.update(data)
        # 写入完整数据
        with open(get_object_path() + 'extract.yml', mode='w', encoding='utf-8') as f:
            yaml.dump(existing_data, stream=f, allow_unicode=True, default_flow_style=False)

    def read_config(self, one_node, two_node=None):
        """
        读取config.yml文件
        :param one_node: 第一节点名
        :param two_node: 第二节点名
        :return:
        """
        with open(get_object_path() + 'config.yml', encoding='utf-8') as f:
            value = yaml.load(stream=f, Loader=yaml.FullLoader)
            if two_node == None:
                return value[one_node]
            else:
                return value[one_node][two_node]

    def clean_extract(self):
        """
        清空extract.yml文件
        :return:
        """
        with open(get_object_path() + 'extract.yml', encoding='utf-8', mode='w') as f:
            f.truncate()


if __name__ == '__main__':
    path_yam = 'login.yml'
    yu = YamlUtils()

    a = yu.get_yaml_case(path_yam, '用户登录成功')
    print(json.dumps(a, indent=4, ensure_ascii=False))
