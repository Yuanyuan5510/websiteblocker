import sqlite3
import os

# 测试直接使用sqlite3连接数据库
db_path = r"j:\pyiadea312\限制网站访问\4.4\backend\website_blocker.db"

print(f"数据库文件路径: {db_path}")
print(f"目录是否存在: {os.path.exists(os.path.dirname(db_path))}")

try:
    # 尝试连接到数据库
    conn = sqlite3.connect(db_path)
    print("成功连接到SQLite数据库")
    
    # 尝试创建一个简单的表
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)''')
    print("成功创建测试表")
    
    # 插入测试数据
    cursor.execute("INSERT OR IGNORE INTO test_table (id, name) VALUES (1, 'Test Data')")
    conn.commit()
    print("成功插入测试数据")
    
    # 查询数据
    cursor.execute("SELECT * FROM test_table")
    data = cursor.fetchall()
    print(f"查询到的数据: {data}")
    
    conn.close()
    print("测试完成")
    
except Exception as e:
    print(f"错误: {e}")
    print(f"错误类型: {type(e)}")
