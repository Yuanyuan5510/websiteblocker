# 自签名证书生成功能使用指南

## 功能概述

本模块实现了完整的自签名证书PFX文件生成功能，基于Windows工具链（makecert.exe、pvk2pfx.exe、cert2spc.exe），为应用程序提供代码签名证书。

## 主要功能

### 1. 证书生成配置
- **工具路径配置**: 支持自定义证书制作工具路径
- **证书参数配置**: 主题信息、有效期、签名算法等
- **输出目录管理**: 自动创建和管理证书输出目录

### 2. 核心生成功能
- **PVK和CER生成**: 使用makecert.exe生成私钥和证书文件
- **SPC转换**: 使用cert2spc.exe将CER转换为SPC格式
- **PFX合并**: 使用pvk2pfx.exe合并PVK和SPC为PFX文件
- **临时文件清理**: 自动清理中间文件，仅保留最终PFX文件

### 3. 工具验证
- **工具存在性检查**: 验证所有必需工具是否可用
- **路径有效性验证**: 确保工具路径正确且可执行

## 使用方法

### 命令行接口

```bash
# 生成自签名证书（使用默认配置）
python certificate_config.py --generate

# 验证工具是否可用
python certificate_config.py --validate-tools

# 显示帮助信息
python certificate_config.py --help

# 验证配置（默认行为）
python certificate_config.py
```

### 编程接口

```python
from certificate_config import quick_generate_certificate, generate_self_signed_certificate

# 快速生成（使用默认配置）
success, message, pfx_path = quick_generate_certificate()

# 自定义参数生成
config = {
    "country": "CN",
    "state": "Beijing",
    "locality": "Beijing",
    "organization": "MyCompany",
    "organizational_unit": "IT Department",
    "common_name": "MyApplication",
    "validity_years": 5,
    "password": "my_password"
}

success, message, pfx_path = generate_self_signed_certificate(config)
```

## 配置参数说明

### SELF_SIGNED_CONFIG 配置块

```python
SELF_SIGNED_CONFIG = {
    # 工具路径配置
    "makecert_tool_path": r"E:\wang\代码签名证书制作工具\代码签名证书制作工具\makecert.exe",
    "pvk2pfx_tool_path": r"E:\wang\代码签名证书制作工具\代码签名证书制作工具\pvk2pfx.exe",
    "cert2spc_tool_path": r"E:\wang\代码签名证书制作工具\代码签名证书制作工具\cert2spc.exe",
    
    # 输出配置
    "output_directory": "certificates",
    "output_filename": "certificate.pfx",
    
    # 证书参数
    "key_type": "signature",
    "signature_algorithm": "sha256",
    "validity_years": 5,
    
    # 默认主题信息
    "default_subject": {
        "country": "CN",
        "state": "Beijing",
        "locality": "Beijing",
        "organization": "wang.station",
        "organizational_unit": "wang.station",
        "common_name": "WebsiteBlocker"
    }
}
```

### 证书主题信息

- **country (C)**: 国家代码，如 "CN"
- **state (S)**: 省份/州，如 "Beijing"
- **locality (L)**: 城市，如 "Beijing"
- **organization (O)**: 组织名称，如 "wang.station"
- **organizational_unit (OU)**: 组织单位，如 "wang.station"
- **common_name (CN)**: 证书通用名称，通常是应用程序名称

### 生成参数

- **key_type**: 密钥类型，通常为 "signature"
- **signature_algorithm**: 签名算法，推荐 "sha256"
- **validity_years**: 证书有效期（年），默认5年
- **password**: PFX文件密码，默认从CERTIFICATE_CONFIG获取

## 输出文件

### 生成过程
1. **临时文件**:
   - `{filename}.pvk`: 私钥文件
   - `{filename}.cer`: 证书文件
   - `{filename}.spc`: 软件发布者证书文件

2. **最终文件**:
   - `{filename}.pfx`: 个人信息交换文件（包含证书和私钥）

### 文件位置
- 默认输出目录: `certificates/`
- 默认文件名: `certificate.pfx`
- 完整路径: `certificates/certificate.pfx`

## 集成到项目

### 1. 更新setup.py配置
```python
# 在setup.py中使用生成的证书
from certificate_config import get_certificate_config

cert_config = get_certificate_config()

class BuildAndSignExe(PyInstaller):
    def run(self):
        # ... 构建代码 ...
        
        # 签名可执行文件
        if os.path.exists(cert_config["certificate_file"]):
            sign_cmd = [
                cert_config["signtool_path"],
                "sign", "/f", cert_config["certificate_file"],
                "/p", cert_config["certificate_password"],
                "/t", cert_config["timestamp_server"],
                exe_path
            ]
            subprocess.run(sign_cmd)
```

### 2. 构建流程集成
```bash
# 1. 生成证书
python certificate_config.py --generate

# 2. 构建并签名应用程序
python setup.py build_exe

# 3. 或使用一键脚本
python setup_digital_signature.py
```

## 错误处理

### 常见错误及解决方案

1. **工具未找到**:
   ```
   ❌ makecert工具未找到: E:\path\to\makecert.exe
   ```
   **解决**: 检查工具路径配置，确保文件存在且可执行

2. **权限问题**:
   ```
   ❌ makecert执行失败: Access denied
   ```
   **解决**: 以管理员权限运行，或检查输出目录权限

3. **参数错误**:
   ```
   ❌ makecert执行失败: Invalid parameter
   ```
   **解决**: 检查证书主题格式，确保符合X.509标准

### 调试模式
```python
# 启用详细输出查看具体错误信息
success, message, pfx_path = generate_self_signed_certificate(config)
if not success:
    print(f"错误详情: {message}")
```

## 安全注意事项

1. **私钥保护**: PFX文件包含私钥，请妥善保管
2. **密码强度**: 使用强密码保护PFX文件
3. **证书分发**: 仅在可信环境中使用自签名证书
4. **有效期管理**: 及时更新即将过期的证书

## 工具依赖

### 必需工具
- **makecert.exe**: 证书生成工具
- **pvk2pfx.exe**: PFX文件转换工具
- **cert2spc.exe**: SPC文件转换工具

### 获取方式
1. Windows SDK
2. Visual Studio 开发工具
3. 或从现有证书制作工具包获取

## 技术实现细节

### 证书生成流程
1. **参数验证**: 检查输入参数和工具可用性
2. **X.509主题构建**: 格式化证书主题字符串
3. **有效期计算**: 根据年数计算过期日期
4. **多步骤生成**: PVK→CER→SPC→PFX
5. **文件清理**: 自动删除临时中间文件

### 错误恢复机制
- 工具调用失败时提供详细错误信息
- 支持空密码输入的备选方案
- 临时文件异常时的清理机制

## 扩展功能

### 自定义扩展
```python
# 添加自定义证书属性
custom_config = {
    "extended_key_usage": ["codeSigning"],
    "key_usage": ["digitalSignature"],
    "basic_constraints": {"ca": False}
}
```

### 批量生成
```python
# 为多个环境生成证书
environments = ["dev", "test", "prod"]
for env in environments:
    config["common_name"] = f"MyApp_{env}"
    generate_self_signed_certificate(config)
```

---

通过本功能，您可以快速生成符合项目需求的自签名证书，解决应用程序代码签名问题，提升用户信任度和安全性。