import requests
from fake_useragent import UserAgent  # 需要安装：pip install fake_useragent

# 代理配置
proxies = {
    "http": "http://47.109.110.100:80",  # 替换为实际可用代理
    # "https": "https://代理IP:端口"  # 如需访问HTTPS可添加
}

# 生成随机User-Agent
try:
    ua = UserAgent()
    random_ua = ua.random  # 随机获取一个浏览器标识
except:
    # 异常时使用提供的默认UA
    random_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"

# 完整请求头（基于提供的信息）
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Host": "httpbin.org",  # 注意：该值应与请求的域名保持一致
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": random_ua
}

# 注意：如果访问其他域名，建议修改Host字段以匹配目标域名
url = "http://httpbin.org/get"  # 已修改为与Host匹配的域名

try:
    response = requests.get(
        url,
        headers=headers,
        proxies=proxies,
        timeout=10
    )
    response.raise_for_status()
    
    # 打印状态码和响应内容
    print(f"请求成功，状态码：{response.status_code}")
    print("响应内容：", response.text)
    
except requests.exceptions.HTTPError as e:
    print(f"HTTP错误: {e}")
except requests.exceptions.ProxyError:
    print("代理连接失败，请检查代理IP和端口是否有效")
except Exception as e:
    print(f"请求失败: {e}")
