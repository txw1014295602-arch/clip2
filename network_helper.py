
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网络连接助手 - 处理网络错误和重试机制
"""

import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any
import socket

class RobustNetworkHelper:
    """健壮的网络连接助手"""
    
    def __init__(self):
        self.session = self._create_robust_session()
    
    def _create_robust_session(self) -> requests.Session:
        """创建带重试机制的会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,  # 最多重试3次
            backoff_factor=1,  # 重试间隔递增
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的状态码
            allowed_methods=["HEAD", "GET", "POST"],  # 允许重试的方法
        )
        
        # 配置适配器
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置超时
        session.timeout = (10, 30)  # 连接超时10秒，读取超时30秒
        
        return session
    
    def safe_api_call(self, url: str, headers: Dict[str, str], 
                     data: Dict[str, Any], max_retries: int = 3) -> Optional[Dict]:
        """安全的API调用，带重试机制"""
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 API调用尝试 {attempt + 1}/{max_retries}")
                
                response = self.session.post(
                    url, 
                    headers=headers, 
                    json=data,
                    timeout=(10, 30)
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # 速率限制，等待更长时间
                    wait_time = 2 ** attempt
                    print(f"⏰ 速率限制，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ HTTP错误: {response.status_code}")
                    if attempt == max_retries - 1:
                        return None
                    
            except requests.exceptions.ConnectionError as e:
                error_msg = str(e)
                if "10054" in error_msg or "远程主机" in error_msg:
                    print(f"🔌 连接被重置 (10054错误)，尝试 {attempt + 1}/{max_retries}")
                else:
                    print(f"🌐 连接错误: {error_msg}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⏰ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print("❌ 所有重试都失败了")
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"⏰ 请求超时，尝试 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    return None
                    
            except Exception as e:
                print(f"❓ 未知错误: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    return None
        
        return None
    
    def test_network_connectivity(self) -> bool:
        """测试网络连通性"""
        test_urls = [
            "https://www.baidu.com",
            "https://httpbin.org/get",
            "https://www.google.com"
        ]
        
        print("🔍 测试网络连通性...")
        
        for url in test_urls:
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ 网络正常: {url}")
                    return True
            except Exception as e:
                print(f"❌ 无法访问 {url}: {e}")
                continue
        
        print("❌ 网络连接异常")
        return False
    
    def get_network_info(self):
        """获取网络信息"""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"💻 本机信息: {hostname} ({local_ip})")
        except Exception as e:
            print(f"⚠️ 无法获取网络信息: {e}")

# 全局网络助手实例
network_helper = RobustNetworkHelper()
