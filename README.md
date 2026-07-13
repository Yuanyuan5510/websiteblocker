# Website Blocker v1.9

A simple and efficient website blocking tool for Windows.

## Features

- Block unwanted websites by modifying hosts file
- User-friendly GUI interface
- Configuration management tool included
- Support for both 32-bit and 64-bit systems
- Multi-language support (English/Chinese)

## Requirements

- Windows 10 or later
- Administrator privileges (required for modifying hosts file)

## Installation

1. Download the latest release from [Download Page](https://websiteblocker.wangstation.dpdns.org/download.html)
2. Run `WebsiteBlocker_Setup_v1.9.exe`
3. Follow the installation wizard

## Usage

### Main Application
Run `Website Blocker.exe` to:
- Add websites to block list
- Remove websites from block list
- View current blocked websites

### Configuration Tool
Run `Website Blocker Config.exe` to:
- Manage default block list
- Configure program settings

## Configuration

Configuration files are stored in:
```
%APPDATA%\WebsiteBlocker\
├── config.json          # Main configuration
└── logs/                # Application logs
```

## Build from Source

### Prerequisites
- Python 3.11+
- cx_Freeze

### Build Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
python setup.py build

# Output will be in dist/ directory
```

## License

This project is licensed under **CC BY-NC 4.0** - see [LICENSE.txt](LICENSE.txt) for details.

Copyright (c) 2025-2026 Yuanyuan5510

## Support

- Website: https://websiteblocker.wangstation.dpdns.org/
- Download: https://websiteblocker.wangstation.dpdns.org/download.html

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.9 | 2025 | Initial release |