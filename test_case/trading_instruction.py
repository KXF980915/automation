import allure
import conftest
from common.allure_utils import allure_testcase
from common.base_api import TestExecutor as te
from common.csv_decorator import csv


@allure.feature('交易指令')

class TestUser:
    # @csv(r'D:\automation\csv\trading_instruction.csv')
    @allure_testcase("提交上市交易指令", feature="交易指令", story="指令提交")
    def test_search_bond(self,ebd_token):
        gz = conftest.GZ
        te().case('trading_instruction.yml','获取债券信息',data={'keyword':gz})
        re = te().case('trading_instruction.yml','获取中债估值净价-中债估值收益率')
        print(re['response_data'])
        # te().case('trading_instruction.yml', '获取交易机构')
        # te().case('trading_instruction.yml', '提交上市交易指令',data)

    def test_trade_calc(self,ebd_token):
        te().case('trading_instruction.yml','获取到期行权收益率',data={'netPrice':100})

