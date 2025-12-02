import os


def get_object_path():
    """
    获取项目路径
    :return:
    """
    return os.path.realpath(__file__).split('common')[0]