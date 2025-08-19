# IP代理管理工具

一个功能完整的IP代理爬取、验证、存储和应用的Python工具集，支持HTTP/HTTPS协议，可自动筛选有效代理并实现轮询切换访问目标网站。

## 功能概述

- 从多个来源爬取免费代理IP（网站爬取+本地文件导入）
- 自动验证代理有效性，过滤无效节点
- 将有效代理存储到MySQL数据库进行管理
- 按协议类型（HTTP/HTTPS）分类管理代理
- 提供代理轮询功能，实现自动切换IP访问目标网站
- 批量处理与并发验证，提升代理处理效率

## 环境要求

- Python 3.6+
- 依赖包：
  - requests
  - fake_useragent
  - pymysql
  - lxml

## 安装步骤

1. 克隆或下载项目代码到本地
2. 安装依赖包：
```bash
pip install requests fake_useragent pymysql lxml
```
3. 数据库配置：
   - 创建MySQL数据库`freeproxy`
   - 修改`init_sql.py`中的数据库连接信息（host、port、user、passwd）
   - 初始化数据库表结构：
```bash
python init_sql.py
```

## 核心模块说明

| 模块文件 | 主要功能 |
|---------|---------|
| `init_sql.py` | 数据库连接管理、表结构初始化、代理统计信息 |
| `Url2ip.py` | 从网络来源爬取代理IP（支持HTTP/HTTPS） |
| `Check.py` | 代理有效性验证核心逻辑、测试网站列表管理 |
| `check_web.py` | 验证从网页爬取的代理并存储到数据库 |
| `check_sql.py` | 验证数据库中已存储的代理有效性 |
| `storage_sql.py` | 代理数据的数据库存储与更新逻辑 |
| `Header.py` | 生成随机请求头，模拟不同浏览器环境 |
| `url_apply.py` | 代理应用模块，实现轮询切换与URL访问 |
| `test_proxy.py` | 单个代理的快速测试工具 |
| `apply1.py` | 使用代理访问指定URL的示例脚本 |

## 使用指南

### 1. 爬取并存储代理

#### 爬取HTTPS代理（默认）
```bash
python check_web.py
```
> 注：默认使用`freeproxy2()`从本地文件爬取HTTPS代理，文件路径为`./files/https.txt`

#### 爬取HTTP代理
修改`check_web.py`，取消`process_http_proxies()`函数的注释，然后运行：
```bash
python check_web.py
```

### 2. 验证数据库中的代理

定期验证数据库中存储的代理有效性：
```bash
python check_sql.py
```
程序会批量验证所有代理，输出可用代理列表及响应时间等信息。

### 3. 使用代理访问目标网站

通过示例脚本`apply1.py`使用代理访问指定URL：
```bash
python apply1.py
```

修改目标URL和协议类型：
```python
# 在apply1.py中修改
url = "https://目标网站地址"  # 要访问的目标URL
protocol = 'https'  # 协议类型，可选'http'或'https'
timeout = 3  # 超时时间（秒）
```

## 代理来源说明

1. **网站爬取**：通过`Url2ip.py`中的`freeproxy1()`函数从指定网站爬取
   - 支持HTTP和HTTPS协议筛选
   - 可配置爬取页数和时间阈值

2. **本地文件导入**：通过`Url2ip.py`中的`freeproxy2()`函数从本地文件读取
   - 默认路径：`./files/https.txt`
   - 文件格式：每行一个代理，格式为`ip:port`

## 自定义配置

1. **验证网站列表**：修改`Check.py`中的`HTTP_TEST_SITES`和`HTTPS_TEST_SITES`列表
2. **批量处理参数**：在各模块中调整`BATCH_SIZE`（批量大小）和`timeout`（超时时间）
3. **代理有效性阈值**：在`Check.py`的`check_proxy_validity()`函数中调整成功率阈值
4. **请求头配置**：在`Header.py`中添加或修改用户代理字符串

## 注意事项

- 免费代理时效性较短，建议定期运行`check_sql.py`更新有效代理
- 爬取第三方网站代理时请遵守其robots协议和使用规范
- 频繁请求可能导致本地IP被目标网站临时封禁，建议合理设置请求间隔
- 数据库连接信息请根据实际环境修改，确保安全性

## 许可证

本项目采用MIT许可证，详情参见LICENSE文件。