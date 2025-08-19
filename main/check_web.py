'''
检测网站爬取的代理是否可用
'''

from Url2ip import *
from Check import validate_proxy_batch, filter_proxies_by_protocol
from storage_sql import store_proxies_to_database
from init_sql import display_proxy_statistics
from check_sql import get_proxies_from_database
# 引用Check.py中的测试网站列表
from Check import HTTP_TEST_SITES, HTTPS_TEST_SITES

def process_http_proxies():
    # 获取所有HTTP代理
    http_proxies = freeproxy1(skip_time_filter=True, protocol='http')
    
    if not http_proxies:
        print("未获取到任何HTTP代理信息")
        return
    
    print(f"共获取到HTTP的 {len(http_proxies)} 个代理")
    
    # 存储所有可用代理的列表
    working_http_proxies = []
    
    # 每批处理的数量
    BATCH_SIZE = 100
    
    # 分批验证HTTP代理
    print("开始验证HTTP代理...")
    for i in range(0, len(http_proxies), BATCH_SIZE):
        batch = http_proxies[i:i+BATCH_SIZE]
        print(f"验证第 {i//BATCH_SIZE + 1} 批HTTP代理,共 {len(batch)} 个")
        
        # 验证当前批次
        working_batch = validate_proxy_batch(batch, HTTP_TEST_SITES, "HTTP", batch_size=50)
        working_http_proxies.extend(working_batch)
        
        # 每验证100个就存储一次并清除当前批次数据
        print(f"已验证100个HTTP代理，开始存储到数据库...")
        store_proxies_to_database(working_http_proxies,protocol='https')
        working_http_proxies.clear()  # 清除当前数据列表
    
    # 处理剩余不足100个的HTTP代理
    if working_http_proxies:
        print(f"HTTP代理验证完毕，存储剩余 {len(working_http_proxies)} 个可用代理到数据库...")
        store_proxies_to_database(working_http_proxies,protocol='http')
        working_http_proxies.clear()


def process_https_proxies():
    # 获取HTTPS的所有代理
    #https_proxies = freeproxy1(skip_time_filter=True, protocol='https')
    https_proxies = freeproxy2()
    
    if not https_proxies:
        print("未获取到任何HTTPS代理信息")
        return
        
    print(f"共获取到HTTPS的 {len(https_proxies)} 个代理")

    # 存储所有可用代理的列表
    working_https_proxies = []
    # 每批处理的数量
    BATCH_SIZE = 100
    
    # 分批验证HTTPS代理
    print("开始验证HTTPS代理...")
    for i in range(0, len(https_proxies), BATCH_SIZE):
        batch = https_proxies[i:i+BATCH_SIZE]
        print(f"验证第 {i//BATCH_SIZE + 1} 批HTTPS代理,共 {len(batch)} 个")
        
        # 验证当前批次
        working_batch = validate_proxy_batch(batch, HTTPS_TEST_SITES, "HTTPS", batch_size=50)
        working_https_proxies.extend(working_batch)
        
        # 每验证100个就存储一次并清除当前批次数据
        print(f"已验证100个HTTPS代理，开始存储到数据库...")
        store_proxies_to_database(working_https_proxies,protocol='https')
        working_https_proxies.clear()  # 清除当前数据列表
    
    # 处理剩余不足100个的HTTPS代理
    if working_https_proxies:
        print(f"HTTPS代理验证完毕，存储剩余 {len(working_https_proxies)} 个可用代理到数据库...")
        store_proxies_to_database(working_https_proxies,protocol='https')
        working_https_proxies.clear()
    
    print(f"共获取到{len(https_proxies)} 个HTTPS代理")


def main():
    print("开始爬取并验证代理信息...")
    
    # 处理HTTP代理
    # process_http_proxies()
    
    # 处理HTTPS代理
    process_https_proxies()
    
    # 获取所有可用代理用于统计
    all_working_proxies = get_proxies_from_database()
    
    # 输出最终结果
    print(f"\n----- 验证完成 -----")
    # 统计HTTP和HTTPS代理数量
    http_count = sum(1 for p in all_working_proxies if p['protocol'] == 'HTTP')
    https_count = len(all_working_proxies) - http_count
    
    print(f"HTTP可用代理: {http_count} 个")
    print(f"HTTPS可用代理: {https_count} 个")
    print(f"总计可用代理: {len(all_working_proxies)} 个")
    
    # 显示详细结果
    for i, proxy in enumerate(all_working_proxies, 1):
        print(f"\n{i}. IP: {proxy['ip']}")
        print(f"   端口: {proxy['port']}")
        print(f"   协议: {proxy['protocol']}")
        print(f"   地址: {proxy['location']}")
        print(f"   平均响应时间: {proxy['response_time']:.2f}秒")
        print(f"   成功访问网站: {len(proxy['successful_sites'])}/5")
    
    # 显示数据库统计信息
    display_proxy_statistics()

if __name__ == "__main__":
    main()