import allure

from common.allure_utils import allure_testcase
from common.base_api import TestExecutor as te
from common.csv_decorator import csv

@allure.feature('登录模块')
class TestUser:

    @allure_testcase("用户登录成功测试", story="登录成功")
    def test_login(self):
        data = {'username': '17375770915','password':'GJqQ1c3wPgdBCQyG0QnZzA=='}
        te().case('login.yml', 'ebond登录', data)

    @allure_testcase("扣除外部资金成本累计盈利接口", feature="分仓表", story="查询盈利接口")
    def test_query_curve_info(self):
        te().case('partition_table.yml','扣除外部资金成本累计盈利接口')

    @allure_testcase("维护债券接口", feature="新发页面", story="债券维护")
    @csv(r'D:\automation\csv\login.csv')
    def test_xiao_e(self,data):
        print(data)
        te().case('e_push.yml','维护债券',data)
