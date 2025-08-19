import requests
from Header import get_random_headers
from init_sql import connect_to_database

# 用于记录每个协议的当前代理索引，实现轮询切换
proxy_index = {
    'http': 0,
    'https': 0
}

def get_proxy_lists():
    """从数据库获取HTTP和HTTPS代理列表"""
    conn = connect_to_database()
    if not conn:
        return [], []
    
    try:
        cursor = conn.cursor()
        
        # 获取HTTP代理
        cursor.execute("SELECT id, ip, port FROM http_proxies")
        http_proxies = [{
            'id': p[0], 'ip': p[1], 'port': p[2], 
            'protocol': 'http'
        } for p in cursor.fetchall()]
        
        # 获取HTTPS代理
        cursor.execute("SELECT id, ip, port FROM https_proxies")
        https_proxies = [{
            'id': p[0], 'ip': p[1], 'port': p[2], 
            'protocol': 'https'
        } for p in cursor.fetchall()]
        
        return http_proxies, https_proxies
        
    except Exception as e:
        print(f"获取代理失败: {e}")
        return [], []
    finally:
        if conn:
            conn.close()

def get_next_proxy(protocol):
    """获取下一个可用代理（轮询方式）"""
    http_proxies, https_proxies = get_proxy_lists()
    proxies = http_proxies if protocol.lower() == 'http' else https_proxies
    
    if not proxies:
        return None
    
    # 获取当前索引并更新（实现轮询切换）
    current_index = proxy_index[protocol.lower()]
    proxy = proxies[current_index]
    
    # 更新索引，下次调用自动切换到下一个代理
    proxy_index[protocol.lower()] = (current_index + 1) % len(proxies)
    return proxy

def access_url_with_proxy(url, protocol):
    """
    每次调用自动切换IP访问URL，失败立即切换下一个代理
    timeout固定为3秒
    """
    timeout = 3
    protocol = protocol.lower()
    http_proxies, https_proxies = get_proxy_lists()
    total_proxies = len(http_proxies) if protocol == 'http' else len(https_proxies)
    
    if total_proxies == 0:
        return {'success': False, 'url': url, 'reason': f"无可用{protocol}代理"}
    
    # 尝试所有代理直到成功或全部失败
    for attempt in range(total_proxies):
        # 获取当前轮询到的代理
        proxy = get_next_proxy(protocol)
        if not proxy:
            continue
        
        try:
            print(f"尝试第{attempt+1}/{total_proxies}个代理: {proxy['ip']}:{proxy['port']}")
            
            # 构建代理格式
            proxy_str = f"{proxy['protocol']}://{proxy['ip']}:{proxy['port']}"
            proxies = {protocol: proxy_str}
            
            # 发送请求
            headers = get_random_headers()
            response = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=timeout,
                allow_redirects=False,
                verify=False
            )
            
            return {
                'success': True,
                'status_code': response.status_code,
                'proxy': proxy,
                'url': url,
                'reason': f"访问成功，状态码: {response.status_code}"
            }
            
        except requests.exceptions.Timeout:
            reason = f"代理{proxy['ip']}:{proxy['port']}超时"
        except Exception as e:
            reason = f"代理{proxy['ip']}:{proxy['port']}访问失败: {str(e)}"
        
        print(reason)
        # 失败不中断，继续尝试下一个代理
    
    return {
        'success': False,
        'url': url,
        'reason': f"所有{protocol}代理尝试完毕，均访问失败"
    }


# 示例调用
if __name__ == "__main__":
    # 第一次调用（使用第一个代理）
    print("第一次调用:")
    result1 = access_url_with_proxy("http://httpbin.org/get", "http")
    print(result1['reason'])
    
    # 第二次调用（自动切换到第二个代理）
    print("\n第二次调用:")
    result2 = access_url_with_proxy("http://httpbin.org/get", "http")
    print(result2['reason'])
    
    # 第三次调用（自动切换到第三个代理）
    print("\n第三次调用:")
    result3 = access_url_with_proxy("http://httpbin.org/get", "http")
    print(result3['reason'])