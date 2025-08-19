import requests
import os
import time
from datetime import datetime
from lxml import etree
from Header import get_random_headers

def convert_time_to_timestamp(time_str, format_str="%Y-%m-%d %H:%M:%S"):
    """将时间字符串转换为时间戳"""
    try:
        time_obj = datetime.strptime(time_str, format_str)
        return time_obj.timestamp()
    except Exception as e:
        print(f"时间转换失败: {str(e)}")
        return None

def get_time_difference(timestamp):
    """计算与当前时间的差值（秒）"""
    if timestamp is None:
        return None
    
    current_timestamp = time.time()
    return current_timestamp - timestamp


def freeproxy1(skip_time_filter=False,protocol='http'):
    """ 
    爬取特定网站的代理信息
    这里需要根据具体网站配置相应的URL和XPath
    """
    # 网站配置信息
    base_url = "https://proxy.scdn.io/"  # 替换为实际网站URL
    max_pages = 2
    time_threshold = 3000  # 时间阈值（秒）
    
    # 该网站的XPath配置
    xpath_config = {
        'table_body': '//*[@id="proxyTableBody"]/tr',  # 代理表格主体
        'ip': 'td[1]/text()',           # IP地址
        'port': 'td[2]/text()',         # 端口
        'protocol': 'td[3]/span/text()', # 协议
        'location': 'td[4]/text()',     # 位置
        'time': 'td[6]/text()'          # 最后验证时间
    }
    
    def scrape_single_page(url, xpath_config):
        """爬取单个页面的代理信息"""
        try:
            headers = get_random_headers(use_fake_useragent=True)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            html = etree.HTML(response.text)
            page_proxies = []
            
            # 获取所有代理行
            proxy_rows = html.xpath(xpath_config['table_body'])
            
            for i, row in enumerate(proxy_rows, 1):
                proxy_info = {"行号": i}
                
                try:
                    # 使用配置的XPath提取信息
                    proxy_info['ip'] = row.xpath(xpath_config['ip'])[0].strip()
                    proxy_info['port'] = row.xpath(xpath_config['port'])[0].strip()
                    proxy_info['protocol'] = row.xpath(xpath_config['protocol'])[0].strip()
                    proxy_info['location'] = row.xpath(xpath_config['location'])[0].strip()
                    
                    # 只保留HTTP和HTTPS代理
                    protocol = proxy_info['protocol'].lower()
                    if protocol not in ['http', 'https']:
                        continue
                    
                    # 处理时间
                    time_str = row.xpath(xpath_config['time'])[0].strip()
                    proxy_info['last_verified_str'] = time_str
                    proxy_info['last_verified_timestamp'] = convert_time_to_timestamp(time_str)
                    
                    # 计算时间差
                    time_diff = get_time_difference(proxy_info['last_verified_timestamp'])
                    proxy_info['time_diff_seconds'] = time_diff
                    
                    page_proxies.append(proxy_info)
                    
                except IndexError:
                    continue
                except Exception as e:
                    print(f"提取第{i}行信息时出错: {str(e)}")
                    continue
            
            return page_proxies
            
        except requests.exceptions.RequestException as e:
            print(f"请求页面 {url} 失败: {e}")
            return None
    
    # 存储所有符合条件的代理
    valid_proxies = []
    if protocol=='http':
        add_url='?protocol=HTTP&country=&per_page=100'
    elif protocol=='https':
        add_url='?protocol=HTTPS&country=&per_page=100'
    
    # 遍历多个页面
    for page in range(1, max_pages + 1):
        print(f"\n----- 正在爬取第 {page} 页 -----")
        # 构建页面URL
        base_url = f"{base_url}{add_url}"
        url = f"{base_url}&page={page}"
        
        # 爬取当前页面
        page_proxies = scrape_single_page(url, xpath_config)
        
        if not page_proxies:
            print(f"第 {page} 页未获取到代理信息，可能已到达最后一页")
            break
        
        print(f"第 {page} 页共获取到 {len(page_proxies)} 条代理信息")
        
        # 筛选出时间差小于阈值的代理
        for proxy in page_proxies:
            time_diff = proxy.get('time_diff_seconds')
            if skip_time_filter or (time_diff is not None and 0 <= time_diff < time_threshold):
                valid_proxies.append(proxy)
                if not skip_time_filter:
                    print(f"已记录有效代理: {proxy['ip']}:{proxy['port']} (时间差: {time_diff:.2f}秒)")
                else:
                    print(f"已记录代理: {proxy['ip']}:{proxy['port']} (时间差: {time_diff:.2f}秒)")
    
    return valid_proxies

def freeproxy2(file_path='./files/https.txt'):
    """
    github汇总的https的代理
    """
    # 网站配置信息
    url = "https://raw.githubusercontent.com/FifzzSENZE/Master-Proxy/master/proxies/https.txt"  # 替换为实际网站URL
    
    valid_proxies = []
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return valid_proxies
    
    # 打开文件并读取内容
    with open(file_path, 'r', encoding='utf-8') as f:
        # 按行读取，跳过空行
        lines = [line.strip() for line in f if line.strip()]
        
        # 取前1000条有效数据（假设每行对应一条代理信息）
        for i, line in enumerate(lines[:1000], 1):
            # 假设文本中代理格式为 "ip:port:原协议"
            parts = line.split(':')
            if len(parts) >= 2:  # 至少包含ip和port
                proxy = {
                    'ip': parts[0].strip(),
                    'port': parts[1].strip(),
                    'protocol': 'https'  # 固定为https
                }
                valid_proxies.append(proxy)
            else:
                print(f"跳过格式错误的行 {i}: {line}")
    
    print(f"共提取 {len(valid_proxies)} 条代理数据（前1000条）")
    return valid_proxies
    

def main():
    """
    主函数，调用爬取函数并保存结果
    """
    # 爬取代理信息
    #proxies = freeproxy1(skip_time_filter=True,protocol='https')
    proxies = freeproxy2()
    http,https = 0,0
    print(f"已获取 {len(proxies)} 个代理")
    for(i, proxy) in enumerate(proxies[:100], 1):
        print(f"第 {i} 个代理: {proxy['ip']}:{proxy['port']}")
        if proxy['protocol'].lower() =="http":
            http =http+1
        elif proxy['protocol'].lower() =="https":
            https = https+1
    print(f"HTTP可用代理: {http} 个,HTTPS可用代理: {https} 个")

if __name__ == "__main__":
    main()

    
    


