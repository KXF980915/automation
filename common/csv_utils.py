import logging
import os
import csv
import re
from typing import Any, Dict, List





class CsvUtils:
    """CSV文件操作工具类"""

    @staticmethod
    def read_csv(file_path: str) -> List[Dict[str, str]]:
        """
        读取CSV文件为字典列表

        Args:
            file_path: CSV文件路径

        Returns:
            List[Dict[str, str]]: CSV数据列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return [row for row in reader]
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV文件不存在: {file_path}")
        except Exception as e:
            raise ValueError(f"CSV文件读取失败: {e}")

    @staticmethod
    def get_csv_data(file_path: str, key: str = None) -> Any:
        """
        获取CSV数据，支持按key筛选

        Args:
            file_path: CSV文件路径
            key: 筛选的key

        Returns:
            Any: 返回的数据
        """
        data = CsvUtils.read_csv(file_path)
        if key and data:
            return [row.get(key) for row in data if key in row]
        return data


class DataReplaceUtils:
    """数据替换工具类"""

    @staticmethod
    def replace_variables(data: Any, variables: Dict[str, Any]) -> Any:
        """
        递归替换数据中的变量占位符 ${variable}

        Args:
            data: 原始数据
            variables: 变量字典

        Returns:
            Any: 替换后的数据
        """
        if isinstance(data, str):
            # 替换字符串中的 ${variable}
            for key, value in variables.items():
                placeholder = f"${{{key}}}"
                if placeholder in data:
                    data = data.replace(placeholder, str(value))
            return data
        elif isinstance(data, dict):
            # 递归处理字典
            return {k: DataReplaceUtils.replace_variables(v, variables) for k, v in data.items()}
        elif isinstance(data, list):
            # 递归处理列表
            return [DataReplaceUtils.replace_variables(item, variables) for item in data]
        else:
            return data

    @staticmethod
    def extract_variables(data: Any) -> List[str]:
        """
        从数据中提取所有变量占位符

        Args:
            data: 要提取的数据

        Returns:
            List[str]: 变量名列表
        """
        variables = set()

        def _extract(obj):
            if isinstance(obj, str):
                # 使用正则表达式匹配 ${variable} 格式
                matches = re.findall(r'\$\{([^}]+)\}', obj)
                variables.update(matches)
            elif isinstance(obj, dict):
                for value in obj.values():
                    _extract(value)
            elif isinstance(obj, list):
                for item in obj:
                    _extract(item)

        _extract(data)
        return list(variables)

    @staticmethod
    def replace_from_csv(data: Any, csv_file_path: str, key_column: str, value_column: str) -> Any:
        """
        从CSV文件中读取变量并进行替换

        Args:
            data: 原始数据
            csv_file_path: CSV文件路径
            key_column: 变量名列名
            value_column: 变量值列名

        Returns:
            Any: 替换后的数据
        """
        try:
            csv_data = CsvUtils.read_csv(csv_file_path)
            variables = {}
            for row in csv_data:
                if key_column in row and value_column in row:
                    variables[row[key_column]] = row[value_column]

            return DataReplaceUtils.replace_variables(data, variables)
        except Exception as e:
            logging.warning(f"CSV变量替换失败: {e}")
            return data