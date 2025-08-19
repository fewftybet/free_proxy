'''
为check_sql.py和
提供代理数据存储功能到数据库和文件的功能
'''

import pymysql
from init_sql import connect_to_database

def check_proxy_exists(conn, ip, port, protocol):
    """检查代理是否已存在"""
    try:
        cursor = conn.cursor()
        table_name = f"{protocol.lower()}_proxies"
        
        sql = f"SELECT id, count FROM {table_name} WHERE ip = %s AND port = %s"
        cursor.execute(sql, (ip, port))
        result = cursor.fetchone()
        
        return result
    except Exception as e:
        print(f"检查代理存在性失败: {e}")
        return None

def insert_or_update_proxy(conn, proxy, protocol):
    """插入或更新代理信息"""
    try:
        cursor = conn.cursor()
        table_name = f"{protocol.lower()}_proxies"
        
        ip = proxy['ip']
        port = int(proxy['port'])
        addr = proxy.get('location', '')
        
        # 检查代理是否已存在
        existing_proxy = check_proxy_exists(conn, ip, port, protocol)
        
        if existing_proxy:
            # 代理已存在，更新count
            proxy_id, current_count = existing_proxy
            new_count = current_count + 1
            
            update_sql = f"UPDATE {table_name} SET count = %s, updated_at = NOW() WHERE id = %s"
            cursor.execute(update_sql, (new_count, proxy_id))
            
            print(f"更新代理: {ip}:{port} (count: {current_count} -> {new_count})")
        else:
            # 代理不存在，插入新记录
            insert_sql = f"INSERT INTO {table_name} (ip, port, addr, count) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_sql, (ip, port, addr, 1))
            
            print(f"插入新代理: {ip}:{port}")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"插入/更新代理失败: {e}")
        conn.rollback()
        return False

def store_proxies_to_database(proxies,protocol):
    """将代理列表存储到数据库"""
    if not proxies:
        print("没有代理数据需要存储")
        return
    

    
    # 连接数据库
    conn = connect_to_database()
    if not conn:
        print("数据库连接失败")
        return
    
    try:
        http_count = 0
        https_count = 0
        
        for proxy in proxies:   
            if protocol == 'http':
                if insert_or_update_proxy(conn, proxy, 'http'):
                    http_count += 1
            elif protocol == 'https':
                if insert_or_update_proxy(conn, proxy, 'https'):
                    https_count += 1
        
        print(f"\n----- 数据库存储完成 -----")
        print(f"HTTP代理: {http_count} 个")
        print(f"HTTPS代理: {https_count} 个")
        print(f"总计: {http_count + https_count} 个")
        
    except Exception as e:
        print(f"存储代理数据时出错: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # 测试存储功能
    test_proxies = [
        {'ip': '192.168.1.1', 'port': 8080, 'protocol': 'http', 'location': '测试地址'},
        {'ip': '10.0.0.1', 'port': 3128, 'protocol': 'https', 'location': '测试地址2'}
    ]
    print("测试代理存储功能...")
    store_proxies_to_database(test_proxies,protocol='https') 