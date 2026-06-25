from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# 直接指定数据库路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'website_blocker.db')
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
