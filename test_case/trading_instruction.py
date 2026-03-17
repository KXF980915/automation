import allure
import conftest
from common.allure_utils import allure_testcase
from common.base_api import TestExecutor as te

@allure.feature('交易指令')
class TestUser:
    def test_search_bond(self,ebd_token):
        gz = conftest.GZ
        te().case('trading_instruction.yml','获取债券信息',data={'keyword':gz})
    def test_trade_calc(self,ebd_token):
        te().case('trading_instruction.yml','获取到期行权收益率',data={'netPrice':100})

