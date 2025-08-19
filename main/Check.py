'''
测试代理检测的逻辑函数,无实际调用
'''
import requests
import time
import random

from concurrent.futures import ThreadPoolExecutor, as_completed
from Header import get_random_headers

# HTTP测试网站列表
HTTP_TEST_SITES = [
    "http://www.51cto.com/",
    "http://www.csdn.net/",
    "http://www.cnblogs.com/",
    "http://www.oschina.net/",
    "http://www.infoq.cn/",
    "http://www.iteye.com/",
    "http://www.jianshu.com/",
    "http://www.segmentfault.com/",
    "http://www.v2ex.com/",
    "http://www.zhihu.com/"
]

# HTTPS测试网站列表
HTTPS_TEST_SITES = [
    "https://www.baidu.com",
    "https://www.doubao.com/",
    "https://www.bilibili.com/",
    "https://www.tongyi.com/",
    "https://explinks.com/",
    "https://www.freebuf.com/",
    "https://www.douyin.com/",
    "https://buff.163.com/",
    "https://bot.n.cn/",
    "https://www.beqege.cc/"
]

def check_proxy_validity(proxy, test_sites, max_workers=3):
    """
    检查代理是否有效
    每个代理随机访问5个网站进行测试
    """
    timeout = 3
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
    
    return success_rate >= 0.2, avg_response_time, successful_sites  # 60%成功率阈值

def filter_proxies_by_protocol(proxies):
    """按协议类型过滤代理"""
    http_proxies = []
    https_proxies = []
    
    for proxy in proxies:
        protocol = proxy['protocol'].lower()
        if protocol == 'http':
            http_proxies.append(proxy)
        elif protocol == 'https':
            https_proxies.append(proxy)
        # 跳过其他类型的代理
    
    return http_proxies, https_proxies

def validate_proxy_batch(proxy_list, test_sites, protocol_type, batch_size=50):
    """批量验证代理，每次验证batch_size个代理"""
    working_proxies = []
    
    print(f"\n----- 开始验证 {protocol_type} 代理 -----")
    print(f"共需要验证 {len(proxy_list)} 个 {protocol_type} 代理")
    print(f"批量验证，每批 {batch_size} 个代理")
    
    # 分批处理代理
    for batch_start in range(0, len(proxy_list), batch_size):
        batch_end = min(batch_start + batch_size, len(proxy_list))
        current_batch = proxy_list[batch_start:batch_end]
        
        print(f"\n----- 验证第 {batch_start//batch_size + 1} 批 ({batch_start+1}-{batch_end}) -----")
        
        # 并发验证当前批次的代理
        batch_working_proxies = validate_single_batch(current_batch, test_sites, protocol_type)
        working_proxies.extend(batch_working_proxies)
        
        # 批次间延迟
        if batch_end < len(proxy_list):
            delay = random.uniform(2, 5)
            print(f"等待 {delay:.1f} 秒后继续下一批...")
            time.sleep(delay)
    
    return working_proxies

def validate_single_batch(proxy_batch, test_sites, protocol_type):
    """验证单个批次的代理"""
    working_proxies = []
    
    def validate_single_proxy(proxy):
        """验证单个代理"""
        print(f"验证代理: {proxy['ip']}:{proxy['port']} ({proxy['protocol']})")
        
        # 随机延迟
        time.sleep(random.uniform(0.1, 0.5))
        
        # 检查代理有效性
        is_valid, response_time, successful_sites = check_proxy_validity(proxy, test_sites)
        
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
        future_to_proxy = {executor.submit(validate_single_proxy, proxy): proxy for proxy in proxy_batch}
        
        for future in as_completed(future_to_proxy):
            result = future.result()
            if result:
                working_proxies.append(result)
    
    print(f"当前批次验证完成: {len(working_proxies)}/{len(proxy_batch)} 个代理有效")
    return working_proxies
