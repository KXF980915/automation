@echo off
setlocal enabledelayedexpansion

REM 参数设置
set TEST_ENV=test
set TEST_MARK=
set TEST_DIR=test_case
set WORKERS=1

REM 解析命令行参数
:parse_args
if "%1"=="" goto run_tests
if "%1"=="--env" set TEST_ENV=%2& shift& shift& goto parse_args
if "%1"=="--mark" set TEST_MARK=%2& shift& shift& goto parse_args
if "%1"=="--dir" set TEST_DIR=%2& shift& shift& goto parse_args
if "%1"=="--workers" set WORKERS=%2& shift& shift& goto parse_args
if "%1"=="--help" goto show_help
shift
goto parse_args

:show_help
echo 用法: run_with_params.bat [参数]
echo.
echo 参数:
echo   --env [dev^|test^|prod]   设置测试环境 (默认: test)
echo   --mark [marker]           运行指定标记的测试
echo   --dir [directory]         指定测试目录 (默认: test_case)
echo   --workers [num]           并行进程数 (默认: 1)
echo   --help                    显示帮助
echo.
pause
exit /b 0

:run_tests
echo ========================================
echo   接口自动化测试 - 参数化运行
echo ========================================
echo 环境: %TEST_ENV%
echo 测试目录: %TEST_DIR%
if not "%TEST_MARK%"=="" echo 测试标记: %TEST_MARK%
echo 工作进程: %WORKERS%
echo ========================================

REM 设置环境变量
set WORKDIR=%~dp0
cd /d "%WORKDIR%"
set PYTHONPATH=%WORKDIR%
set ALLURE_RESULTS=%WORKDIR%\allure-results

REM 清理历史数据
if exist %ALLURE_RESULTS% rmdir /s /q %ALLURE_RESULTS%
mkdir %ALLURE_RESULTS%

REM 构建pytest命令
set PYTEST_CMD=python -m pytest %TEST_DIR% -v --tb=short --alluredir=%ALLURE_RESULTS% --clean-alluredir

if not "%TEST_MARK%"=="" set PYTEST_CMD=!PYTEST_CMD! -m "%TEST_MARK%"
if %WORKERS% gtr 1 set PYTEST_CMD=!PYTEST_CMD! -n %WORKERS%

REM 运行测试
echo 执行命令: %PYTEST_CMD%
echo.
%PYTEST_CMD%
set TEST_RESULT=%errorlevel%

REM 生成报告
if exist %ALLURE_RESULTS% (
    echo.
    echo 生成Allure报告...
    allure generate %ALLURE_RESULTS% -o allure-report --clean
)

echo.
echo 测试完成，退出码: %TEST_RESULT%
endlocal
pause