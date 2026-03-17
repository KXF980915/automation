import pytest
from common.base_api import TestExecutor as te

#银行间债券
GZ = "20国开10"
@pytest.fixture(scope="session")
def ebd_token():
    data = {'username': '17375770915', 'password': 'GJqQ1c3wPgdBCQyG0QnZzA=='}
    res = te().case('login.yml', 'ebond登录', data)
    return res['response_data']['access_token']

def hentai_token():
    data = {'username': '17375770915', 'password': 'GJqQ1c3wPgdBCQyG0QnZzA=='}
    te().case('login.yml', 'ebond登录', data)
