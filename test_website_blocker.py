#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网站访问限制工具测试脚本
用于验证程序的各项功能是否正常工作
"""

import os
import sys
import time
import subprocess
import json
import shutil
from datetime import datetime

# 配置文件路径
USER_HOME = os.path.expanduser("~")
CONFIG_DIR = os.path.join(USER_HOME, ".website_blocker")
# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 配置文件现在位于程序同目录下
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
HOSTS_PATH = "C:\\Windows\\System32\\drivers\\etc\\hosts" if os.name == 'nt' else "/etc/hosts"
HOSTS_BACKUP = HOSTS_PATH + ".test_backup"

print("=== 网站访问限制工具测试脚本 ===")
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*50)

def test_admin_rights():
    """测试是否有管理员权限"""
    print("\n[测试 1] 检查管理员权限...")
    try:
        if os.name == 'nt':
            # Windows系统检查
            is_admin = subprocess.check_output(['net', 'session'], 
                                             stderr=subprocess.STDOUT)
            print("✓ 当前有管理员权限")
            return True
        else:
            # Linux/Mac系统检查
            is_admin = os.geteuid() == 0
            if is_admin:
                print("✓ 当前有管理员权限")
                return True
            else:
                print("✗ 当前没有管理员权限")
                return False
    except:
        print("✗ 当前没有管理员权限")
        return False

def backup_hosts():
    """备份hosts文件"""
    print("\n[测试 2] 备份hosts文件...")
    try:
        if os.path.exists(HOSTS_PATH):
            shutil.copy2(HOSTS_PATH, HOSTS_BACKUP)
            print(f"✓ hosts文件已备份到: {HOSTS_BACKUP}")
            return True
        else:
            print("✗ hosts文件不存在")
            return False
    except Exception as e:
        print(f"✗ 备份失败: {e}")
        return False

def restore_hosts():
    """恢复hosts文件"""
    print("\n[测试 99] 恢复hosts文件...")
    try:
        if os.path.exists(HOSTS_BACKUP):
            shutil.copy2(HOSTS_BACKUP, HOSTS_PATH)
            os.remove(HOSTS_BACKUP)
            print(f"✓ hosts文件已恢复")
            return True
        else:
            print("✗ 备份文件不存在")
            return False
    except Exception as e:
        print(f"✗ 恢复失败: {e}")
        return False

def test_config_management():
    """测试配置管理功能"""
    print("\n[测试 3] 测试配置管理...")
    try:
        # 获取脚本所在目录，即程序目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 检查配置文件（现在位于程序同目录下）
        config_file = os.path.join(script_dir, "config.json")
        if os.path.exists(config_file):
            print(f"✓ 配置文件存在: {config_file}")
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print("✓ 配置文件格式正确")
                print(f"  - blocked_websites: {config.get('blocked_websites', [])}")
                print(f"  - auto_clear_on_exit: {config.get('auto_clear_on_exit', True)}")
                print(f"  - external_storage_enabled: {config.get('external_storage_enabled', False)}")
                return True
        else:
            print(f"⚠️  配置文件不存在: {config_file}")
            return False
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        return False

def test_program_launch():
    """测试程序启动"""
    print("\n[测试 4] 测试程序启动...")
    try:
        # 获取当前脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建正确的程序路径
        program_path = os.path.join(script_dir, "website_blocker_ui.py")
        # 启动程序并等待1秒后关闭
        print(f"启动程序测试 (将在3秒后自动关闭)...")
        print(f"程序路径: {program_path}")
        process = subprocess.Popen([sys.executable, program_path])
        time.sleep(3)
        process.terminate()
        process.wait(timeout=2)
        print("✓ 程序启动测试完成")
        return True
    except Exception as e:
        print(f"✗ 程序启动测试失败: {e}")
        return False

def test_domain_cleaning():
    """测试域名清理功能"""
    print("\n[测试 5] 测试域名清理功能...")
    try:
        # 直接实现域名清理逻辑用于测试
        import re
        
        def clean_domain_test(url):
            """简化版的域名清理函数，复制自主程序的逻辑"""
            # 移除协议部分
            url = re.sub(r'^https?://', '', url)
            # 移除路径部分
            url = re.sub(r'/(.*)$', '', url)
            # 移除端口号
            url = re.sub(r':\d+$', '', url)
            # 移除www前缀
            url = re.sub(r'^www\.', '', url)
            # 只保留主域名（移除子域名）
            parts = url.split('.')
            if len(parts) >= 3:
                # 常见顶级域名特殊处理
                if parts[-1] in ['com', 'net', 'org', 'edu', 'gov', 'mil', 'int'] and len(parts[-2]) > 2:
                    return '.'.join(parts[-2:])
                # 国家顶级域名（如.cn, .uk等）
                elif len(parts[-1]) == 2:
                    return '.'.join(parts[-2:])
                # 其他情况，返回最后三个部分（如.co.uk）
                else:
                    return '.'.join(parts[-3:])
            return url
        
        # 测试用例
        test_cases = [
            ("https://www.example.com", "example.com"),
            ("http://test.example.org/path?query=123", "example.org"),
            ("subdomain.site.net:8080", "site.net"),
            ("example.com", "example.com"),
            ("www.php.cn/faq/1294533.html", "php.cn")
        ]
        
        all_passed = True
        for input_url, expected in test_cases:
            try:
                result = clean_domain_test(input_url)
                if result == expected:
                    print(f"✓ 清理成功: {input_url} -> {result}")
                else:
                    print(f"✗ 清理失败: {input_url} -> {result} (应为 {expected})")
                    all_passed = False
            except Exception as e:
                print(f"✗ 处理 {input_url} 时出错: {e}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"✗ 域名清理测试失败: {e}")
        return False

def main():
    """主测试函数"""
    try:
        # 首先检查管理员权限
        if not test_admin_rights():
            print("\n错误: 需要管理员权限才能完整测试所有功能")
            print("请以管理员身份运行此测试脚本")
            return
        
        # 备份hosts文件
        if not backup_hosts():
            return
        
        # 运行各项测试
        tests = [
            test_config_management,
            test_program_launch,
            test_domain_cleaning
        ]
        
        passed_count = 0
        total_count = len(tests)
        
        for test_func in tests:
            if test_func():
                passed_count += 1
        
        # 打印测试结果汇总
        print("\n" + "="*50)
        print(f"测试结果汇总: {passed_count}/{total_count} 测试通过")
        if passed_count == total_count:
            print("🎉 所有测试通过！")
        else:
            print(f"⚠️  有 {total_count - passed_count} 项测试失败")
            
    finally:
        # 恢复hosts文件
        restore_hosts()
        
        print("\n" + "="*50)
        print("测试完成！")
        input("按回车键退出...")

if __name__ == "__main__":
    main()