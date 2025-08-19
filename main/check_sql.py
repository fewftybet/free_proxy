'''
检查数据库中的代理是否可用
'''

import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from Header import get_random_headers
from init_sql import connect_to_database, display_proxy_statistics
# 引用Check.py中的测试网站列表
from Check import HTTP_TEST_SITES, HTTPS_TEST_SITES

def get_proxies_from_database():
    """从数据库获取所有代理"""
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # 获取HTTP代理
        http_sql = "SELECT id, ip, port, addr FROM http_proxies"
        cursor.execute(http_sql)
        http_proxies = cursor.fetchall()
        
        # 获取HTTPS代理
        https_sql = "SELECT id, ip, port, addr FROM https_proxies"
        cursor.execute(https_sql)
        https_proxies = cursor.fetchall()
        
        proxies = []
        for proxy in http_proxies:
            proxies.append({
                'id': proxy[0],
                'ip': proxy[1],
                'port': proxy[2],
                'addr': proxy[3],
                'protocol': 'http',
                'table': 'http_proxies'
            })
        
        for proxy in https_proxies:
            proxies.append({
                'id': proxy[0],
                'ip': proxy[1],
                'port': proxy[2],
                'addr': proxy[3],
                'protocol': 'https',
                'table': 'https_proxies'
            })
        
        return proxies
        
    except Exception as e:
        print(f"获取代理列表失败: {e}")
        return []
    finally:
        conn.close()


def test_proxy_connectivity(proxy, test_sites, max_workers=3):
    """测试代理连接性 - 引用Check.py中的函数逻辑"""
    timeout = 10
    proxy_str = f"{proxy['protocol'].lower()}://{proxy['ip']}:{proxy['port']}"
    proxies = {
        "http": proxy_str,
        "https": proxy_str
    }
    
    # 随机选择5个网站进行测试
    selected_sites = random.sample(test_sites, 5)
    
    def test_single_site(site):
        """测试单个网站"""
        try:
            headers = get_random_headers()
            start_time = time.time()
            response = requests.get(
                site, 
                headers=headers, 
                proxies=proxies, 
                timeout=timeout,
                allow_redirects=False
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return True, response_time, site
            else:
                return False, response_time, site
                
        except Exception as e:
            return False, None, site
    
    # 并发测试选中的网站
    successful_tests = 0
    total_response_time = 0
    successful_sites = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_site = {executor.submit(test_single_site, site): site for site in selected_sites}
        
        for future in as_completed(future_to_site):
            is_valid, response_time, site = future.result()
            if is_valid:
                successful_tests += 1
                total_response_time += response_time
                successful_sites.append(site)
    
    # 计算成功率
    success_rate = successful_tests / len(selected_sites)
    avg_response_time = total_response_time / successful_tests if successful_tests > 0 else None
    
    return success_rate >= 0.6, avg_response_time, successful_sites  # 60%成功率阈值

def validate_database_proxies_batch(proxy_list, test_sites, protocol_type, batch_size=50):
    """批量验证数据库中的代理"""
    working_proxies = []
    
    print(f"\n----- 开始验证数据库中的 {protocol_type} 代理 -----")
    print(f"共需要验证 {len(proxy_list)} 个 {protocol_type} 代理")
    print(f"批量验证，每批 {batch_size} 个代理")
    
    # 分批处理代理
    for batch_start in range(0, len(proxy_list), batch_size):
        batch_end = min(batch_start + batch_size, len(proxy_list))
        current_batch = proxy_list[batch_start:batch_end]
        
        print(f"\n----- 验证第 {batch_start//batch_size + 1} 批 ({batch_start+1}-{batch_end}) -----")
        
        # 并发验证当前批次的代理
        batch_working_proxies = validate_single_database_batch(current_batch, test_sites, protocol_type)
        working_proxies.extend(batch_working_proxies)
        
        # 批次间延迟
        if batch_end < len(proxy_list):
            delay = random.uniform(2, 5)
            print(f"等待 {delay:.1f} 秒后继续下一批...")
            time.sleep(delay)
    
    return working_proxies

def validate_single_database_batch(proxy_batch, test_sites, protocol_type):
    """验证单个批次的数据库代理"""
    working_proxies = []
    
    def validate_single_database_proxy(proxy):
        """验证单个数据库代理"""
        print(f"验证代理: {proxy['ip']}:{proxy['port']} ({proxy['protocol']})")
        
        # 随机延迟
        time.sleep(random.uniform(0.5, 1.5))
        
        # 选择测试网站
        if proxy['protocol'].lower() == 'http':
            test_sites_for_proxy = HTTP_TEST_SITES
        else:
            test_sites_for_proxy = HTTPS_TEST_SITES
        
        # 检查代理有效性
        is_valid, response_time, successful_sites = test_proxy_connectivity(proxy, test_sites_for_proxy)
        
        
        
        if is_valid:
            print(f"✓ 代理有效！平均响应时间: {response_time:.2f}秒")
            print(f"  成功访问: {len(successful_sites)}/5 个网站")
            proxy['response_time'] = response_time
            proxy['successful_sites'] = successful_sites
            return proxy
        else:
            print(f"✗ 代理无效")
            return None
    
    # 并发验证当前批次的代理
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_proxy = {executor.submit(validate_single_database_proxy, proxy): proxy for proxy in proxy_batch}
        
        for future in as_completed(future_to_proxy):
            result = future.result()
            if result:
                working_proxies.append(result)
    
    print(f"当前批次验证完成: {len(working_proxies)}/{len(proxy_batch)} 个代理有效")
    return working_proxies

def filter_database_proxies_by_protocol(proxies):
    """按协议类型过滤数据库代理"""
    http_proxies = []
    https_proxies = []
    
    for proxy in proxies:
        protocol = proxy['protocol'].lower()
        if protocol == 'http':
            http_proxies.append(proxy)
        elif protocol == 'https':
            https_proxies.append(proxy)
    
    return http_proxies, https_proxies

def main():
    print("开始检查数据库中的代理存活状态...")
    
    # 获取数据库中的所有代理
    all_proxies = get_proxies_from_database()
    
    if not all_proxies:
        print("数据库中没有代理数据")
        return
    
    print(f"数据库中共有 {len(all_proxies)} 个代理")
    
    # 按协议类型过滤代理
    http_proxies, https_proxies = filter_database_proxies_by_protocol(all_proxies)
    
    print(f"HTTP代理: {len(http_proxies)} 个")
    print(f"HTTPS代理: {len(https_proxies)} 个")
    
    # 批量验证HTTP代理
    working_http_proxies = validate_database_proxies_batch(http_proxies, HTTP_TEST_SITES, "HTTP", batch_size=50)
    
    # 批量验证HTTPS代理
    working_https_proxies = validate_database_proxies_batch(https_proxies, HTTPS_TEST_SITES, "HTTPS", batch_size=50)
    
    # 合并结果
    all_working_proxies = working_http_proxies + working_https_proxies
    
    # 按响应时间排序
    all_working_proxies.sort(key=lambda x: x['response_time'])
    
    # 输出最终结果
    print(f"\n----- 数据库代理验证完成 -----")
    print(f"HTTP可用代理: {len(working_http_proxies)} 个")
    print(f"HTTPS可用代理: {len(working_https_proxies)} 个")
    print(f"总计可用代理: {len(all_working_proxies)} 个")
    
    # 显示详细结果
    for i, proxy in enumerate(all_working_proxies, 1):
        print(f"\n{i}. IP: {proxy['ip']}")
        print(f"   端口: {proxy['port']}")
        print(f"   协议: {proxy['protocol']}")
        print(f"   地址: {proxy['addr']}")
        print(f"   平均响应时间: {proxy['response_time']:.2f}秒")
        print(f"   成功访问网站: {len(proxy['successful_sites'])}/5")
    
    # 显示数据库统计信息
    display_proxy_statistics()

if __name__ == "__main__":
    main() 