#!/usr/bin/env python3
"""
Windows环境检查与设置脚本
"""
import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python():
    """检查Python环境"""
    print("=" * 50)
    print("检查Python环境...")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"系统平台: {platform.platform()}")

    if sys.version_info < (3, 7):
        print("警告: Python版本低于3.7，建议升级")
        return False
    return True


def check_dependencies():
    """检查依赖"""
    print("\n检查依赖包...")
    required_packages = [
        "pytest",
        "allure-pytest",
        "requests",
        "PyYAML",
        "colorlog"
    ]

    try:
        import pkg_resources
        installed = {pkg.key for pkg in pkg_resources.working_set}

        missing = []
        for pkg in required_packages:
            if pkg.lower() not in installed:
                missing.append(pkg)

        if missing:
            print(f"缺失的包: {', '.join(missing)}")
            print("运行: pip install -r requirements.txt")
            return False
        else:
            print("✓ 所有依赖包已安装")
            return True
    except:
        print("无法检查依赖包，请手动安装")
        return False


def check_allure():
    """检查Allure命令行工具"""
    print("\n检查Allure命令行工具...")
    try:
        result = subprocess.run(
            ["allure", "--version"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            print(f"✓ Allure已安装: {result.stdout.strip()}")
            return True
    except:
        pass

    print("! Allure命令行工具未找到")
    print("请从以下地址下载安装:")
    print("https://github.com/allure-framework/allure2/releases")
    print("安装后需将allure/bin添加到PATH环境变量")
    return False


def setup_directories():
    """创建必要的目录"""
    print("\n创建目录结构...")
    directories = [
        "allure-results",
        "allure-report",
        "logs",
        "reports",
        "data/csv",
        "case_data"
    ]

    for dir_path in directories:
        full_path = Path.cwd() / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  {dir_path}/")

    print("✓ 目录创建完成")
    return True


def test_pytest():
    """测试pytest是否能正常工作"""
    print("\n测试pytest...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            print(f"✓ pytest正常: {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"✗ pytest测试失败: {e}")
        return False


def main():
    """主函数"""
    print("接口自动化测试 - Windows环境设置")
    print("=" * 50)

    # 检查项目结构
    required_files = ["requirements.txt", "pytest.ini", "test_case"]
    for file in required_files:
        if not Path(file).exists():
            print(f"✗ 缺失必要文件/目录: {file}")
            return False

    # 执行各项检查
    checks = [
        ("Python环境", check_python),
        ("依赖包", check_dependencies),
        ("Allure工具", check_allure),
        ("目录结构", setup_directories),
        ("Pytest", test_pytest)
    ]

    results = []
    for name, check_func in checks:
        try:
            success = check_func()
            results.append((name, success))
        except Exception as e:
            print(f"检查{name}时出错: {e}")
            results.append((name, False))

    # 显示结果
    print("\n" + "=" * 50)
    print("环境检查结果:")
    print("-" * 50)

    all_passed = True
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {name}")
        if not success:
            all_passed = False

    print("-" * 50)

    if all_passed:
        print("🎉 环境检查通过！可以开始运行测试。")
        print("\n运行方式:")
        print("  1. 双击 run.bat")
        print("  2. 命令行运行: python -m pytest test_case")
    else:
        print("⚠️  环境检查未通过，请解决上述问题。")

    return all_passed


if __name__ == "__main__":
    success = main()
    input("\n按Enter键退出...")
    sys.exit(0 if success else 1)