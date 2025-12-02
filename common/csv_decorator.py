import os
import csv as csv_module
import inspect
import pytest


def csv(csv_file_path: str, **kwargs):
    """
    CSV 参数化装饰器 - 使用第一列作为测试用例名称

    用法：
    @csv('test_data.csv')
    def test_example(data):
        pass

    假设 CSV 文件第一列是测试用例的标识符（如用例ID、名称等）
    """

    def decorator(test_func):
        # 获取 CSV 数据
        test_cases, first_column_name = _read_csv_file(csv_file_path)

        if not test_cases:
            test_cases = [{}]

        # 生成测试用例 IDs - 使用第一列的值
        ids = []
        for i, case in enumerate(test_cases):
            # 优先使用自定义 IDs 函数
            if 'ids' in kwargs and callable(kwargs['ids']):
                ids.append(kwargs['ids'](case, i))
            # 使用第一列的值作为 ID
            elif first_column_name and first_column_name in case and case[first_column_name]:
                ids.append(str(case[first_column_name]))
            # 如果第一列没有值，使用 row_{i+1}
            elif 'id' in case and case['id']:
                ids.append(str(case['id']))
            else:
                ids.append(f"case_{i + 1}")

        # 直接传递字典数据，不要包装在元组中
        argvalues = test_cases

        # 创建参数化装饰器
        parametrize_kwargs = {
            'argnames': 'data',
            'argvalues': argvalues,
            'ids': ids,
        }

        # 添加其他参数
        for key, value in kwargs.items():
            if key != 'ids':
                parametrize_kwargs[key] = value

        return pytest.mark.parametrize(**parametrize_kwargs)(test_func)

    return decorator


def _read_csv_file(file_path: str):
    """读取 CSV 文件，返回数据列表和第一列的名称"""

    # 处理文件路径
    if not os.path.exists(file_path):
        # 尝试从调用者目录查找
        stack = inspect.stack()
        for frame in stack:
            if 'decorator' in frame.function or frame.function == 'csv':
                caller_file = frame.filename
                caller_dir = os.path.dirname(caller_file)

                possible_paths = [
                    os.path.join(caller_dir, file_path),
                    os.path.join(caller_dir, 'data', file_path),
                    os.path.join(caller_dir, 'test_data', file_path),
                    file_path
                ]

                for path in possible_paths:
                    if os.path.exists(path):
                        file_path = path
                        break
                break

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV 文件不存在: {file_path}")

    cases = []
    first_column_name = None

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv_module.DictReader(f)

        # 获取第一列的名称
        if reader.fieldnames:
            first_column_name = reader.fieldnames[0]

        for i, row in enumerate(reader):
            clean_row = {}

            # 处理每一列
            for j, (key, value) in enumerate(row.items()):
                if not key or not key.strip():
                    continue

                key = key.strip()

                # 第一列特别处理（确保有值）
                if j == 0 and (value is None or value == ''):
                    # 如果第一列为空，使用默认值
                    value = f"test_case_{i + 1}"

                # 类型转换
                if value is None or value == '':
                    clean_row[key] = None
                elif value.lower() == 'true':
                    clean_row[key] = True
                elif value.lower() == 'false':
                    clean_row[key] = False
                elif value.lower() == 'null' or value.lower() == 'none':
                    clean_row[key] = None
                else:
                    # 尝试转换为数字
                    try:
                        if '.' in value:
                            clean_row[key] = float(value)
                        else:
                            clean_row[key] = int(value)
                    except ValueError:
                        clean_row[key] = value

            # 添加元数据
            clean_row['_csv_row'] = i + 1
            clean_row['_csv_file'] = os.path.basename(file_path)

            # 记录第一列的名称
            if first_column_name:
                clean_row['_first_column'] = first_column_name

            cases.append(clean_row)

    return cases, first_column_name