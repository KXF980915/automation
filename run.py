import subprocess


def run():
    # # 运行 pytest
    # result = subprocess.run(["pytest", "--alluredir=./allure-results"])

    # 只有当 pytest 成功时才生成报告
    # if result.returncode:
        subprocess.run(
            [r"D:\allure-2.35.1\bin\allure.bat", "generate", "./allure-results", "-o", "./allure-report", "--clean"])


if __name__ == "__main__":
    # run()
    subprocess.run(
        [r"D:\allure-2.35.1\bin\allure.bat", "generate", "./allure-results", "-o", "./allure-report", "--clean"])

    subprocess.run([r"D:\allure-2.35.1\bin\allure.bat", 'open','./allure-report'])
