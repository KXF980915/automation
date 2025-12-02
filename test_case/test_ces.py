import pytest

from common.base_api import TestExecutor as te
from common.csv_decorator import csv
from test_case.conftest import login

class TestUser:

    def test_login(self):
        data = {'username': '17375770915','password':'GJqQ1c3wPgdBCQyG0QnZzA=='}
        te().case('login.yml', 'ebond登录', data)

    def test_query_curve_info(self):
        te().case('partition_table.yml','扣除外部资金成本累计盈利接口')

    @csv(r'D:\automation\csv\login.csv')
    def test_xiao_e(self,data):
        print(data)
        te().case('e_push.yml','维护债券',data)
