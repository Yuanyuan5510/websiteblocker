#!/usr/bin/env python3
"""
数字签名一键配置脚本
运行此脚本快速配置WebsiteBlocker的数字签名功能
"""

import os
import sys
import shutil
from pathlib import Path

def print_banner():
    """打印配置向导横幅"""
    print("=" * 60)
    print("🔐 WebsiteBlocker 数字签名配置向导")
    print("=" * 60)
    print("此脚本将帮助您配置应用程序的数字签名功能")
    print("解决'未知发布者'问题，提高应用程序可信度")
    print("=" * 60)
    print()

def check_prerequisites():
    """检查前置条件"""
    print("🔍 检查系统环境...")
    
    issues = []
    
    # 检查操作系统
    if os.name != 'nt':
        issues.append("数字签名功能仅支持Windows系统")
    
    # 检查signtool
    signtool_path = shutil.which("signtool.exe")
    if not signtool_path:
        # 检查常见路径
        common_paths = [
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe",
        ]
        
        signtool_found = False
        for path in common_paths:
            if Path(path).exists():
                signtool_found = True
                break
        
        if not signtool_found:
            issues.append("未找到signtool.exe，请安装Windows SDK")
    
    # 检查Python环境
    try:
        import cx_Freeze
        print(f"✓ cx_Freeze已安装 (版本: {cx_Freeze.__version__})")
    except ImportError:
        issues.append("未安装cx_Freeze，请运行: pip install cx_Freeze")
    
    if issues:
        print("\n❌ 发现以下问题:")
        for issue in issues:
            print(f"  • {issue}")
        print("\n请解决上述问题后重新运行此脚本")
        return False
    
    print("✓ 系统环境检查通过")
    return True

def get_user_input():
    """获取用户输入的配置信息"""
    print("\n📝 请输入配置信息:")
    print("-" * 40)
    
    config = {}
    
    # 公司信息
    config['company_name'] = input("公司名称 [Your Company Name]: ").strip() or "Your Company Name"
    config['support_email'] = input("支持邮箱 [support@yourcompany.com]: ").strip() or "support@yourcompany.com"
    config['website_url'] = input("官方网站 [https://www.yourcompany.com]: ").strip() or "https://www.yourcompany.com"
    
    print()
    
    # 证书信息
    print("证书配置:")
    cert_path = input("证书文件路径 [certificate.pfx]: ").strip() or "certificate.pfx"
    config['certificate_path'] = cert_path
    
    # 检查证书文件是否存在
    if not Path(cert_path).exists():
        print(f"⚠️  警告: 证书文件 '{cert_path}' 不存在")
        create_placeholder = input("是否创建占位符文件? (y/N): ").strip().lower()
        if create_placeholder in ['y', 'yes']:
            Path(cert_path).touch()
            print(f"✓ 已创建占位符文件: {cert_path}")
    
    config['certificate_password'] = input("证书密码: ").strip()
    if not config['certificate_password']:
        print("⚠️  警告: 证书密码为空，后续需要手动配置")
    
    print()
    
    # 时间戳服务器
    timestamp_servers = [
        "http://timestamp.digicert.com",
        "http://timestamp.sectigo.com", 
        "http://timestamp.globalsign.com"
    ]
    
    print("选择时间戳服务器:")
    for i, server in enumerate(timestamp_servers, 1):
        print(f"  {i}. {server}")
    
    timestamp_choice = input(f"选择服务器 [1-{len(timestamp_servers)}]: ").strip()
    try:
        choice_idx = int(timestamp_choice) - 1
        if 0 <= choice_idx < len(timestamp_servers):
            config['timestamp_server'] = timestamp_servers[choice_idx]
        else:
            config['timestamp_server'] = timestamp_servers[0]
    except ValueError:
        config['timestamp_server'] = timestamp_servers[0]
    
    print(f"✓ 选择时间戳服务器: {config['timestamp_server']}")
    
    return config

def create_certificate_config(config):
    """创建证书配置文件"""
    print("\n📄 创建证书配置文件...")
    
    config_content = f'''"""
数字签名配置文件
由配置向导自动生成
"""

# 证书文件配置
CERTIFICATE_CONFIG = {{
    "certificate_path": "{config['certificate_path']}",
    "certificate_password": "{config['certificate_password']}",
    "certificate_thumbprint": None,
    "timestamp_server": "{config['timestamp_server']}",
    "fallback_timestamp_servers": [
        "http://timestamp.sectigo.com",
        "http://timestamp.globalsign.com",
        "http://timestamp.comodoca.com"
    ]
}}

# 发布者信息配置
PUBLISHER_INFO = {{
    "company_name": "{config['company_name']}",
    "publisher_name": "{config['company_name']}",
    "support_email": "{config['support_email']}",
    "website_url": "{config['website_url']}",
    "support_url": "{config['website_url']}/support",
    "update_url": "{config['website_url']}/updates",
    "privacy_url": "{config['website_url']}/privacy",
    "terms_url": "{config['website_url']}/terms"
}}

# 应用程序信息
APP_INFO = {{
    "app_name": "WebsiteBlocker",
    "app_version": "3.9",
    "app_description": "Website Blocker - 专注工作和学习的网站访问控制工具",
    "app_detailed_description": """
    Website Blocker 是一款专业的网站访问控制工具，帮助用户：
    • 阻止访问分散注意力的网站
    • 提高工作和学习效率
    • 设置灵活的访问时间规则
    • 保护儿童免受不当内容影响
    • 支持白名单和黑名单模式
    """,
    "copyright": "Copyright © 2024 {config['company_name']}. All rights reserved.",
    "app_icon": "resources/icon.ico"
}}

# 构建配置
BUILD_CONFIG = {{
    "enable_signature": True,
    "signature_algorithm": "sha256",
    "include_cert_chain": True,
    "verify_signature": True,
    "auto_verify_after_build": True,
    "output_directory": "dist",
    "build_directory": "build"
}}

# 环境变量配置
ENVIRONMENT_CONFIG = {{
    "use_env_password": False,
    "password_env_var": "CERT_PASSWORD",
    "use_env_cert_path": False,
    "cert_path_env_var": "CERT_PATH",
    "use_env_timestamp": False,
    "timestamp_env_var": "TIMESTAMP_SERVER"
}}

# 验证配置
VALIDATION_CONFIG = {{
    "validate_cert_expiry": True,
    "validate_cert_usage": True,
    "expiry_warning_days": 30,
    "validate_timestamp_server": True,
    "timestamp_timeout": 30
}}

def get_certificate_config():
    return CERTIFICATE_CONFIG

def get_publisher_info():
    return PUBLISHER_INFO

def get_app_info():
    return APP_INFO

def get_build_config():
    return BUILD_CONFIG

def get_environment_config():
    return ENVIRONMENT_CONFIG

def get_validation_config():
    return VALIDATION_CONFIG

def merge_config_with_env():
    import os
    config = CERTIFICATE_CONFIG.copy()
    
    if ENVIRONMENT_CONFIG["use_env_password"]:
        password = os.getenv(ENVIRONMENT_CONFIG["password_env_var"])
        if password:
            config["certificate_password"] = password
    
    if ENVIRONMENT_CONFIG["use_env_cert_path"]:
        cert_path = os.getenv(ENVIRONMENT_CONFIG["cert_path_env_var"])
        if cert_path:
            config["certificate_path"] = cert_path
    
    if ENVIRONMENT_CONFIG["use_env_timestamp"]:
        timestamp = os.getenv(ENVIRONMENT_CONFIG["timestamp_env_var"])
        if timestamp:
            config["timestamp_server"] = timestamp
    
    return config

def validate_config():
    errors = []
    warnings = []
    
    if not CERTIFICATE_CONFIG["certificate_path"]:
        errors.append("证书文件路径未配置")
    
    if not CERTIFICATE_CONFIG["certificate_password"]:
        warnings.append("证书密码未配置")
    
    if not PUBLISHER_INFO["company_name"]:
        errors.append("公司名称未配置")
    
    if not APP_INFO["app_description"]:
        errors.append("应用程序描述未配置")
    
    return errors, warnings

if __name__ == "__main__":
    errors, warnings = validate_config()
    
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"  • {{error}}")
    
    if warnings:
        print("⚠️  配置警告:")
        for warning in warnings:
            print(f"  • {{warning}}")
    
    if not errors and not warnings:
        print("✅ 配置验证通过")
    
    print(f"\\n当前配置概览:")
    print(f"  证书路径: {{CERTIFICATE_CONFIG['certificate_path']}}")
    print(f"  发布者: {{PUBLISHER_INFO['company_name']}}")
    print(f"  应用程序: {{APP_INFO['app_name']}} v{{APP_INFO['app_version']}}")
    print(f"  签名算法: {{BUILD_CONFIG['signature_algorithm']}}")
'''
    
    config_file = Path("certificate_config.py")
    
    # 备份现有配置文件
    if config_file.exists():
        backup_file = config_file.with_suffix('.py.backup')
        shutil.copy2(config_file, backup_file)
        print(f"✓ 已备份现有配置文件: {backup_file}")
    
    # 写入新配置
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✓ 已创建配置文件: {config_file}")
    return True

def create_build_script():
    """创建一键构建脚本"""
    print("\n🔨 创建一键构建脚本...")
    
    script_content = '''@echo off
echo ========================================
echo WebsiteBlocker 一键构建脚本
echo ========================================
echo.

echo 正在清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo 清理完成

echo.
echo 正在构建应用程序...
python setup.py build_exe

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 构建成功！
    echo ========================================
    echo.
    echo 可执行文件位置: dist\\WebsiteBlocker.exe
    echo.
    
    if exist "dist\\WebsiteBlocker.exe" (
        echo 正在验证数字签名...
        signtool verify /pa /v "dist\\WebsiteBlocker.exe"
        if %ERRORLEVEL% EQU 0 (
            echo ✓ 数字签名验证成功
        ) else (
            echo ⚠️ 数字签名验证失败或未签名
        )
    )
    
    echo.
    echo 构建完成！按任意键退出...
    pause >nul
) else (
    echo.
    echo ❌ 构建失败，请检查错误信息
    echo.
    pause
)
'''
    
    script_file = Path("build_signed.bat")
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✓ 已创建构建脚本: {script_file}")
    return True

def run_tests():
    """运行配置测试"""
    print("\n🧪 运行配置测试...")
    
    try:
        # 运行简化测试脚本
        result = os.system("python test_signature_simple.py")
        if result == 0:
            print("✓ 配置测试通过")
            return True
        else:
            print("⚠️ 配置测试发现问题，请查看测试结果")
            return False
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return False

def print_final_instructions():
    """打印最终说明"""
    print("\n" + "=" * 60)
    print("🎉 配置完成！")
    print("=" * 60)
    print()
    print("📋 下一步操作:")
    print()
    print("1. 📁 准备证书文件")
    print("   • 将有效的代码签名证书(.pfx)放在项目根目录")
    print("   • 确保证书密码正确配置")
    print()
    print("2. 🔨 构建应用程序")
    print("   • 运行 build_signed.bat 进行一键构建")
    print("   • 或手动运行: python setup.py build_exe")
    print()
    print("3. ✅ 验证签名")
    print("   • 右键点击生成的exe文件查看数字签名")
    print("   • 运行 signtool verify /pa /v dist\\WebsiteBlocker.exe")
    print()
    print("4. 📚 参考文档")
    print("   • 查看 digital_signature_guide.md 获取详细指南")
    print("   • 查看 certificate_config.py 自定义配置")
    print()
    print("🔧 故障排除:")
    print("   • signtool未找到 → 安装Windows SDK")
    print("   • 证书错误 → 检查证书文件和密码")
    print("   • 签名失败 → 检查网络和时间戳服务器")
    print()
    print("=" * 60)

def main():
    """主函数"""
    print_banner()
    
    # 检查前置条件
    if not check_prerequisites():
        return False
    
    # 获取用户配置
    config = get_user_input()
    
    # 创建配置文件
    if not create_certificate_config(config):
        print("❌ 配置文件创建失败")
        return False
    
    # 创建构建脚本
    if not create_build_script():
        print("❌ 构建脚本创建失败")
        return False
    
    # 运行测试
    run_tests()
    
    # 打印最终说明
    print_final_instructions()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 配置被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 配置过程中发生错误: {e}")
        sys.exit(1)