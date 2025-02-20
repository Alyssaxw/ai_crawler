"""
工具函数模块
提供通用功能如请求头生成、数据保存等
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Union
from fake_useragent import UserAgent

def get_random_headers() -> Dict[str, str]:
    """
    生成随机User-Agent的请求头
    """
    ua = UserAgent()
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }

def save_data(data: List[Dict], output_format: str = 'json', output_dir: str = 'data/output') -> str:
    """
    保存爬取的数据
    
    Args:
        data: 要保存的数据列表
        output_format: 输出格式（json或csv）
        output_dir: 输出目录
    
    Returns:
        str: 保存的文件路径
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_format.lower() == 'json':
        filename = f'ai_tools_{timestamp}.json'
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'tools': data}, f, ensure_ascii=False, indent=2)
    else:
        filename = f'ai_tools_{timestamp}.csv'
        filepath = os.path.join(output_dir, filename)
        if data:
            fieldnames = data[0].keys()
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
    
    return filepath

def format_timestamp() -> str:
    """
    生成格式化的时间戳
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def clean_text(text: str) -> str:
    """
    清理文本数据
    """
    if not text:
        return ""
    return text.strip().replace('\n', ' ').replace('\r', '').replace('\t', ' ')

def create_tool_item(
    name: str,
    description: str,
    url: str,
    category: str = "未分类"
) -> Dict[str, str]:
    """
    创建标准格式的工具项
    """
    return {
        "name": clean_text(name),
        "description": clean_text(description),
        "url": url.strip(),
        "category": clean_text(category),
        "crawl_time": format_timestamp()
    }

def get_retry_delay(attempt: int, base_delay: float = 1.0) -> float:
    """
    获取重试延迟时间（指数退避）
    """
    return min(base_delay * (2 ** attempt), 60)  # 最大延迟60秒