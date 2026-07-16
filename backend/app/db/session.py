from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from pathlib import Path

# 导入统一路径获取函数
def get_appdata_path() -> str:
    """获取统一配置路径"""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    return os.path.join(appdata, 'WebsiteBlocker')


def get_database_path() -> str:
    """获取数据库路径"""
    config_dir = get_appdata_path()
    # 确保目录存在
    Path(config_dir).mkdir(parents=True, exist_ok=True)
    return os.path.join(config_dir, 'website_blocker.db')


# 获取数据库路径
db_path = get_database_path()
database_url = f"sqlite:///{db_path}"

# 创建数据库引擎
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False}  # SQLite特定设置
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 依赖函数，用于获取数据库会话
def get_db():
    """
    获取数据库会话
    
    Yields:
        db: 数据库会话实例
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()