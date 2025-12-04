@echo off
echo ========================================
echo   接口自动化测试启动脚本 (Windows版)
echo ========================================
echo.

REM 设置当前目录为工作目录
set WORKDIR=%~dp0
cd /d "%WORKDIR%"

REM 设置Python路径
set PYTHONPATH=%WORKDIR%

echo [1/4] 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo [2/4] 安装依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 警告: 依赖安装可能有问题，继续执行...
)

echo [3/4] 清理并创建目录...
if exist allure-results rmdir /s /q allure-results
mkdir allure-results
if exist allure-report rmdir /s /q allure-report

echo [4/4] 运行测试...
echo 开始执行测试用例...
echo.

REM 运行pytest测试
python -m pytest test_case -v --tb=short --clean-alluredir
set TEST_RESULT=%errorlevel%

echo.
echo ========================================
if %TEST_RESULT% equ 0 (
    echo ✓ 测试执行完成 (所有测试通过)
) else if %TEST_RESULT% equ 1 (
    echo ! 测试执行完成 (有测试失败)
) else (
    echo ✗ 测试执行错误 (代码: %TEST_RESULT%)
)
echo ========================================

REM 生成Allure报告
if exist allure-results (
    if not exist allure-report mkdir allure-report

    echo 正在生成Allure报告...
    allure generate allure-results -o allure-report --clean

    REM 检查是否有allure打开命令
    where allure >nul 2>nul
    if %errorlevel% equ 0 (
        echo.
        set /p OPEN_REPORT="是否打开Allure报告? (Y/N): "
        if /i "%OPEN_REPORT%"=="Y" (
            allure open allure-report
        )
    ) else (
        echo 提示: allure命令未找到，请安装Allure命令行工具
        echo 下载地址: https://github.com/allure-framework/allure2/releases
    )
)

echo.
echo 临时文件清理...
del /f /q extract.yml 2>nul
rmdir /s /q __pycache__ 2>nul
rmdir /s /q .pytest_cache 2>nul

echo.
echo 完成! 报告位置: %WORKDIR%\allure-report\index.html
pause