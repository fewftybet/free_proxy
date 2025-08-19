'''
初始化数据库
'''

import pymysql

# 数据库连接配置
def connect_to_database():
    """连接数据库"""
    try:
        conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            passwd='123456',
            db='freeproxy',
            charset='utf8'
        )
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def create_tables():
    """创建数据库表"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 创建HTTP代理表
        http_table_sql = """
        CREATE TABLE IF NOT EXISTS http_proxies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip VARCHAR(50) NOT NULL,
            port INT NOT NULL,
            addr VARCHAR(100),
            count INT DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_proxy (ip)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        """
        
        # 创建HTTPS代理表
        https_table_sql = """
        CREATE TABLE IF NOT EXISTS https_proxies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip VARCHAR(50) NOT NULL,
            port INT NOT NULL,
            addr VARCHAR(100),
            count INT DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_proxy (ip)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        """
        
        cursor.execute(http_table_sql)
        cursor.execute(https_table_sql)
        conn.commit()
        
        print("数据库表创建成功")
        return True
        
    except Exception as e:
        print(f"创建表失败: {e}")
        return False
    finally:
        conn.close()

def get_proxy_statistics():
    """获取代理统计信息"""
    conn = connect_to_database()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # 获取HTTP代理统计
        http_sql = "SELECT COUNT(*) as total FROM http_proxies"
        cursor.execute(http_sql)
        http_stats = cursor.fetchone()
        
        # 获取HTTPS代理统计
        https_sql = "SELECT COUNT(*) as total FROM https_proxies"
        cursor.execute(https_sql)
        https_stats = cursor.fetchone()
        
        return {
            'http': {
                'unique_proxies': http_stats[0] if http_stats[0] else 0
            },
            'https': {
                'unique_proxies': https_stats[0] if https_stats[0] else 0
            }
        }
        
    except Exception as e:
        print(f"获取统计信息失败: {e}")
        return None
    finally:
        conn.close()

def display_proxy_statistics():
    """显示代理统计信息"""
    stats = get_proxy_statistics()
    if not stats:
        print("无法获取统计信息")
        return
    
    print(f"HTTP代理: {stats['http']['unique_proxies']}个")
    print(f"HTTPS代理: {stats['https']['unique_proxies']}个")

if __name__ == "__main__":
    # 测试数据库连接和表创建
    print("测试数据库连接...")
    if create_tables():
        print("数据库连接和表创建成功")
        display_proxy_statistics()
    else:
        print("数据库连接或表创建失败") 