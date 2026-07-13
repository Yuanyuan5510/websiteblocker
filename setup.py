#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Blocker - 打包配置文件
用于cx_Freeze打包程序为可执行文件
"""

import os
import sys
import json
import subprocess
import shutil
import logging
from pathlib import Path
from datetime import datetime, timezone
from cx_Freeze import setup, Executable
from cx_Freeze.command.build_exe import build_exe
import platform

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 尝试导入证书配置
try:
    from certificate_config import (
        get_certificate_config, 
        get_publisher_info, 
        get_app_info, 
        get_build_config,
        merge_config_with_env
    )
    CERT_CONFIG_AVAILABLE = True
except ImportError:
    logger.warning("certificate_config.py 未找到，使用默认配置")
    CERT_CONFIG_AVAILABLE = False

# 基本信息配置
NAME = "WebsiteBlocker"
VERSION = "3.9"
DESCRIPTION = "一个简单高效的website blocking tool"
AUTHOR = "wang.station"
AUTHOR_EMAIL = "wang.station@hotmail.com"
SUPPORT_URL = "https://websiteblocker-zh.wangstation.ddns-ip.net/"
UPDATE_URL = "https://websiteblocker-zh.wangstation.ddns-ip.net/download.html"

# 获取当前目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

# 判断是否为Windows系统
if sys.platform == 'win32':
    base = "Win32GUI"  # 使用GUI模式，不显示控制台
    # 添加Windows特定的包含项以确保C++库兼容性
    os.environ['PATH'] = os.path.join(sys.base_exec_prefix, 'Lib', 'site-packages', 'cx_Freeze', 'bases') + ';' + os.environ['PATH']
else:
    base = None

# 设置图标路径
icon_path = os.path.join(PARENT_DIR, "app_icon.ico")

# 检查配置文件是否存在
config_path = os.path.join(BASE_DIR, "website_blocker_config.json")
if not os.path.exists(config_path):
    # 如果配置文件不存在，创建一个默认的
    default_config = {
        "blocked_websites": [],
        "auto_clear_on_exit": True,
        "external_storage_enabled": False
    }
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=4)

# 包含所有必需的文件
include_files = [
    icon_path,
    config_path
]

# 需要包含的包（基于PyQt6）
include_packages = [
    "PyQt6",
    "PyQt6.QtWidgets",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtNetwork",
    # 确保包含所有必要的标准库
    "os",
    "sys",
    "json",
    "shutil",
    "re",
    "ctypes",
    "logging",
    "platform",
    "time",
    "subprocess",
    "socket",
    "signal",
    "datetime",
    "atexit",
    "math",
    "cryptography"  # 新增：用于证书验证
]

# 数字签名配置类
class BuildAndSignExe(build_exe):
    """自定义构建命令，用于在构建后对可执行文件进行数字签名"""
    
    # 数字签名相关参数
    user_options = build_exe.user_options + [
        ('cert-path=', None, 'Path to the signing certificate (PFX/P12 file)'),
        ('cert-password=', None, 'Password for the signing certificate (use CERT_PASSWORD env var for security)'),
        ('timestamp-url=', None, 'URL for timestamp server'),
        ('publisher-name=', None, 'Publisher name to display in UAC dialog'),
        ('signtool-path=', None, 'Path to signtool.exe (if not in system PATH)'),
        ('cert-thumbprint=', None, 'Certificate thumbprint for verification'),
        ('description=', None, 'Detailed description of the application'),
        ('additional-cert=', None, 'Additional certificate chain file (CER/PEM)'),
    ]
    
    def __init__(self, dist):
        super().__init__(dist)
        # 默认值
        self.cert_path = None
        self.cert_password = None
        self.cert_thumbprint = None
        self.timestamp_url = "http://timestamp.digicert.com"  # 可靠的时间戳服务器
        self.publisher_name = "wang.station"
        self.description = "Website Blocker - 一个简单高效的website blocking tool"
        self.signtool_path = None
        self.additional_cert = None
        
        # 应用程序详细信息
        self.app_info = {
            "name": NAME,
            "version": VERSION,
            "description": DESCRIPTION,
            "author": AUTHOR,
            "author_email": AUTHOR_EMAIL,
            "support_url": SUPPORT_URL,
            "update_url": UPDATE_URL
        }
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """加载配置，优先级：命令行参数 > 环境变量 > 配置文件 > 默认值"""
        # 从环境变量加载
        env_cert_path = os.environ.get("CERT_PATH")
        env_cert_password = os.environ.get("CERT_PASSWORD")
        env_timestamp_url = os.environ.get("TIMESTAMP_URL")
        env_publisher_name = os.environ.get("PUBLISHER_NAME")
        env_signtool_path = os.environ.get("SIGNTOOL_PATH")
        env_cert_thumbprint = os.environ.get("CERT_THUMBPRINT")
        env_description = os.environ.get("APP_DESCRIPTION")
        env_additional_cert = os.environ.get("ADDITIONAL_CERT")
        
        # 设置默认值（环境变量优先）
        self.cert_path = env_cert_path if env_cert_path else self.cert_path
        self.cert_password = env_cert_password if env_cert_password else self.cert_password
        self.timestamp_url = env_timestamp_url if env_timestamp_url else self.timestamp_url
        self.publisher_name = env_publisher_name if env_publisher_name else self.publisher_name
        self.signtool_path = env_signtool_path if env_signtool_path else self.signtool_path
        self.cert_thumbprint = env_cert_thumbprint if env_cert_thumbprint else self.cert_thumbprint
        self.description = env_description if env_description else self.description
        self.additional_cert = env_additional_cert if env_additional_cert else self.additional_cert
        
        # 如果配置文件可用，使用配置文件中的值（不覆盖环境变量）
        if CERT_CONFIG_AVAILABLE:
            try:
                cert_config = merge_config_with_env()
                publisher_info = get_publisher_info()
                app_info = get_app_info()
                build_config = get_build_config()
                
                self.cert_path = self.cert_path or cert_config.get("certificate_path")
                self.timestamp_url = self.timestamp_url or cert_config.get("timestamp_server")
                self.publisher_name = self.publisher_name or publisher_info.get("publisher_name")
                self.description = self.description or app_info.get("app_description")
                self.cert_thumbprint = self.cert_thumbprint or cert_config.get("certificate_thumbprint")
            except Exception as e:
                logger.warning(f"加载证书配置失败: {e}")
    
    def initialize_options(self):
        build_exe.initialize_options(self)
    
    def finalize_options(self):
        build_exe.finalize_options(self)
    
    def _verify_certificate(self):
        """增强的证书验证，使用cryptography库验证证书有效性"""
        if not self.cert_path or not os.path.exists(self.cert_path):
            logger.warning("未指定证书文件路径或文件不存在")
            return False
        
        try:
            # 尝试导入cryptography库
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.serialization import pkcs12
            
            logger.info(f"正在验证证书: {self.cert_path}")
            
            # 读取证书文件
            with open(self.cert_path, 'rb') as f:
                cert_data = f.read()
            
            # 加载证书（不验证密码，仅验证文件格式）
            try:
                if self.cert_password:
                    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                        cert_data, self.cert_password.encode(), backend=default_backend()
                    )
                else:
                    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                        cert_data, None, backend=default_backend()
                    )
            except Exception as e:
                logger.error(f"证书密码错误或证书格式无效: {e}")
                return False
            
            # 验证证书有效性
            now = datetime.now(timezone.utc)
            if certificate.not_valid_before_utc > now:
                logger.error(f"证书尚未生效，生效日期: {certificate.not_valid_before_utc}")
                return False
            if certificate.not_valid_after_utc < now:
                logger.error(f"证书已过期，过期日期: {certificate.not_valid_after_utc}")
                return False
            
            # 验证证书用途包含代码签名
            key_usage = certificate.extensions.get_extension_for_class(x509.KeyUsage)
            if not key_usage.value.digital_signature:
                logger.error("证书不具备数字签名权限")
                return False
            
            # 检查扩展密钥用法
            try:
                ext_key_usage = certificate.extensions.get_extension_for_class(x509.ExtendedKeyUsage)
                has_code_signing = x509.OID_CODE_SIGNING in ext_key_usage.value.usages
                if not has_code_signing:
                    logger.warning("证书未明确指定代码签名用途，但具备数字签名权限")
            except x509.ExtensionNotFound:
                logger.warning("证书未包含扩展密钥用法，但具备数字签名权限")
            
            # 获取证书颁发者和主题
            issuer = certificate.issuer.rfc4514_string()
            subject = certificate.subject.rfc4514_string()
            logger.info(f"证书验证通过: {subject}")
            logger.info(f"  颁发者: {issuer}")
            logger.info(f"  有效期: {certificate.not_valid_before_utc} 至 {certificate.not_valid_after_utc}")
            
            # 验证证书指纹（如果提供）
            if self.cert_thumbprint:
                cert_hash = certificate.fingerprint(hashes.SHA256())
                cert_thumbprint_hex = cert_hash.hex().upper()
                if self.cert_thumbprint.replace(':', '').upper() != cert_thumbprint_hex:
                    logger.error(f"证书指纹不匹配: 预期 {self.cert_thumbprint}，实际 {cert_thumbprint_hex}")
                    return False
                logger.info(f"  指纹验证通过: {cert_thumbprint_hex}")
            
            logger.info("✓ 证书验证成功")
            return True
            
        except ImportError:
            logger.warning("cryptography库未安装，仅进行基本证书验证")
            # 回退到基本验证
            if os.path.getsize(self.cert_path) > 0:
                logger.info("✓ 证书文件基本验证通过")
                return True
            return False
        except Exception as e:
            logger.error(f"证书验证失败: {e}")
            return False
    
    def _find_signtool(self):
        """改进的Signtool检测，支持更多路径和环境变量"""
        # 检查用户提供的路径
        if self.signtool_path and os.path.exists(self.signtool_path):
            logger.info(f"使用用户指定的signtool: {self.signtool_path}")
            return self.signtool_path
        
        # 检查环境变量SIGNTOOL_PATH
        env_signtool = os.environ.get("SIGNTOOL_PATH")
        if env_signtool and os.path.exists(env_signtool):
            logger.info(f"使用环境变量指定的signtool: {env_signtool}")
            return env_signtool
        
        # 检查系统PATH
        signtool_in_path = shutil.which("signtool")
        if signtool_in_path:
            logger.info(f"在系统PATH中找到signtool: {signtool_in_path}")
            return signtool_in_path
        
        # 检查常见的Windows SDK安装路径（支持Windows 10/11）
        windows_kits_paths = []
        
        # 检查Program Files (x86)和Program Files
        for base_dir in ["C:\\Program Files (x86)", "C:\\Program Files"]:
            # 检查Windows Kits目录
            kits_base = os.path.join(base_dir, "Windows Kits")
            if os.path.exists(kits_base):
                # 获取所有Windows Kits版本（如10, 11）
                for kit_ver in os.listdir(kits_base):
                    kit_path = os.path.join(kits_base, kit_ver)
                    if os.path.isdir(kit_path):
                        # 获取bin目录下的所有架构
                        bin_path = os.path.join(kit_path, "bin")
                        if os.path.exists(bin_path):
                            # 获取所有版本目录（如10.0.19041.0）
                            for ver_dir in os.listdir(bin_path):
                                ver_path = os.path.join(bin_path, ver_dir)
                                if os.path.isdir(ver_path):
                                    # 检查x64和x86架构
                                    for arch in ["x64", "x86"]:
                                        signtool_path = os.path.join(ver_path, arch, "signtool.exe")
                                        windows_kits_paths.append(signtool_path)
        
        # 其他常见路径
        other_paths = [
            r"E:\wang\代码签名证书制作工具\代码签名证书制作工具\signtool.exe",
        ]
        windows_kits_paths.extend(other_paths)
        
        # 检查所有可能的路径
        for signtool_path in windows_kits_paths:
            if os.path.exists(signtool_path):
                logger.info(f"找到signtool: {signtool_path}")
                return signtool_path
        
        logger.error("未找到signtool.exe")
        logger.error("请确保已安装Windows SDK或通过SIGNTOOL_PATH环境变量指定路径")
        logger.error("Windows SDK下载地址: https://developer.microsoft.com/zh-cn/windows/downloads/windows-sdk/")
        return None
    
    def _build_sign_command(self, exe_path):
        """构建符合行业标准的数字签名命令"""
        signtool_path = self._find_signtool()
        if not signtool_path:
            return None
        
        # 基础签名参数（符合行业标准）
        sign_cmd = [
            signtool_path,
            "sign",
            "/fd", "sha256",  # 强制使用SHA256哈希算法
            "/tr", self.timestamp_url,  # 可靠的时间戳服务器
            "/td", "sha256",  # 时间戳哈希算法
            "/d", self.description,  # 详细描述
            "/du", self.app_info["support_url"],  # 支持URL
            "/n", self.publisher_name,  # 发布者名称
            "/sa",  # 附加签名（如果需要）
            "/debug",  # 调试输出
        ]
        
        # 添加证书信息
        if self.cert_path and os.path.exists(self.cert_path):
            sign_cmd.extend(["/f", self.cert_path])
            if self.cert_password:
                # 使用环境变量传递密码，避免命令行泄露
                os.environ["SIGNTOOL_PASSWORD"] = self.cert_password
                sign_cmd.extend(["/p", "$SIGNTOOL_PASSWORD"])
        
        # 添加额外证书链（如果有）
        if self.additional_cert and os.path.exists(self.additional_cert):
            sign_cmd.extend(["/ac", self.additional_cert])
        
        # 添加要签名的文件
        sign_cmd.append(exe_path)
        
        return sign_cmd
    
    def _verify_signature(self, exe_path):
        """验证签名是否成功应用"""
        signtool_path = self._find_signtool()
        if not signtool_path:
            return False
        
        try:
            verify_cmd = [
                signtool_path,
                "verify",
                "/pa",  # 使用默认认证策略
                "/v",   # 详细输出
                "/all", # 验证所有签名
                exe_path
            ]
            
            logger.info("\n正在验证签名...")
            result = subprocess.run(
                verify_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✓ 签名验证成功")
            if result.stdout:
                logger.debug(f"验证输出: {result.stdout}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ 签名验证失败: {e}")
            if e.stderr:
                logger.error(f"验证错误: {e.stderr}")
            return False
    
    def run(self):
        """运行构建和签名流程，确保可重复性"""
        logger.info("=" * 60)
        logger.info("Website Blocker - 构建和数字签名")
        logger.info("=" * 60)
        
        # 设置构建可重复性环境变量
        os.environ.setdefault("SOURCE_DATE_EPOCH", "1600000000")  # 固定时间戳，确保构建可重复
        
        # 执行标准构建
        logger.info("\n1. 执行标准构建...")
        build_exe.run(self)
        
        # 查找生成的可执行文件
        exe_name = NAME + "_Setup_" + VERSION + ".exe"
        exe_path = os.path.join(self.build_exe, exe_name)
        
        if not os.path.exists(exe_path):
            logger.error(f"✗ 未找到生成的可执行文件: {exe_path}")
            return
        
        logger.info(f"✓ 找到生成的可执行文件: {exe_path}")
        
        # 验证证书
        logger.info("\n2. 验证数字证书...")
        if not self._verify_certificate():
            logger.warning("✗ 证书验证失败，跳过签名步骤")
            return
        
        # 构建签名命令
        logger.info("\n3. 准备数字签名...")
        sign_cmd = self._build_sign_command(exe_path)
        if not sign_cmd:
            logger.error("✗ 无法构建签名命令")
            return
        
        # 执行签名
        logger.info("\n4. 执行数字签名...")
        logger.info(f"执行命令: {' '.join(sign_cmd[:-1])} <exe_path>")  # 隐藏密码和完整路径
        
        try:
            result = subprocess.run(
                sign_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✓ 数字签名成功!")
            if result.stdout:
                logger.debug(f"签名输出: {result.stdout}")
            if result.stderr:
                logger.debug(f"签名信息: {result.stderr}")
            
            # 验证签名
            logger.info("\n5. 验证签名结果...")
            if self._verify_signature(exe_path):
                logger.info("\n" + "=" * 60)
                logger.info("✓ 构建和签名流程完成!")
                logger.info(f"✓ 可执行文件: {exe_path}")
                logger.info(f"✓ 发布者: {self.publisher_name}")
                logger.info(f"✓ 描述: {self.description}")
                logger.info(f"✓ 版本: {VERSION}")
                logger.info("=" * 60)
            else:
                logger.warning("✗ 签名验证失败，但文件已生成")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ 数字签名失败: {e}")
            if e.stderr:
                logger.error(f"签名错误: {e.stderr}")
            if e.stdout:
                logger.debug(f"签名输出: {e.stdout}")
            logger.warning("警告: 可执行文件已生成但未签名")
            logger.warning("建议: 请检查证书路径、密码和网络连接")
            
        except Exception as e:
            logger.error(f"✗ 签名过程中发生未知错误: {e}")
            logger.warning("警告: 可执行文件已生成但未签名")
        finally:
            # 清理环境变量中的密码
            if "SIGNTOOL_PASSWORD" in os.environ:
                del os.environ["SIGNTOOL_PASSWORD"]

# 动态配置元数据
if CERT_CONFIG_AVAILABLE:
    try:
        publisher_info = get_publisher_info()
        app_info = get_app_info()
        
        NAME = app_info.get("app_name", NAME)
        VERSION = app_info.get("app_version", VERSION)
        AUTHOR = publisher_info.get("company_name", AUTHOR)
        DESCRIPTION = app_info.get("app_description", DESCRIPTION)
        SUPPORT_URL = publisher_info.get("support_url", SUPPORT_URL)
        UPDATE_URL = publisher_info.get("update_url", UPDATE_URL)
    except Exception as e:
        logger.warning(f"加载动态配置失败: {e}")

# 打包配置
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL if not CERT_CONFIG_AVAILABLE else publisher_info.get("support_email", AUTHOR_EMAIL),
    url=SUPPORT_URL,
    project_urls={
        "Documentation": SUPPORT_URL,
        "Source": SUPPORT_URL,
        "Tracker": SUPPORT_URL,
        "Download": UPDATE_URL,
        "Bug Reports": SUPPORT_URL + "issues" if not CERT_CONFIG_AVAILABLE else publisher_info.get("support_url", SUPPORT_URL) + "/issues",
        "Changelog": SUPPORT_URL + "changelog",
        "Funding": SUPPORT_URL + "sponsor" if not CERT_CONFIG_AVAILABLE else publisher_info.get("website_url", SUPPORT_URL) + "/sponsor"
    },
    keywords="website blocker, parental control, productivity, security",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities"
    ],
    options={
        "build_exe": {
            "include_files": include_files,
            "packages": include_packages,
            "excludes": ["tkinter", "unittest", "email", "xml", "pydoc", "doctest"],
            "optimize": 2,
            "build_exe": "dist",
            "include_msvcr": True,  # 包含Microsoft Visual C++运行时库
            "zip_include_packages": "*",
            "zip_exclude_packages": "",
        },
        "build_and_sign_exe": {
            "cert_path": None,  # 可在命令行中指定证书路径
            "cert_password": None,  # 建议通过环境变量CERT_PASSWORD传递
            "cert_thumbprint": None,  # 证书指纹
            "timestamp_url": "http://timestamp.digicert.com",
            "publisher_name": "wang.station",
            "description": "Website Blocker - 一个简单高效的website blocking tool",
            "signtool_path": None,  # 可在命令行中指定signtool.exe路径
            "additional_cert": None  # 额外证书链文件
        }
    },
    executables=[
        # 主程序可执行文件
        Executable(
            script=os.path.join(BASE_DIR, "website_blocker_ui.py"),
            base=base,
            target_name=NAME + "_Setup_" + VERSION + ".exe",
            shortcut_name=NAME + " " + VERSION,
            shortcut_dir="DesktopFolder",
            icon=icon_path
        )
    ],
    cmdclass={
        'build_exe': BuildAndSignExe  # 使用自定义的构建命令
    }
)
