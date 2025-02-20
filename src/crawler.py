"""
AI工具导航网站爬虫
主要爬虫逻辑和命令行接口
"""

import asyncio
import aiohttp
import argparse
import sys
from typing import List, Dict, Optional
from datetime import datetime
import random
import logging
from pathlib import Path

from .parser import AIToolParser
from .utils import get_random_headers, save_data, get_retry_delay

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 修改为DEBUG级别以获取更多信息
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('crawler.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class AICrawler:
    """AI工具导航网站爬虫类"""
    
    def __init__(self, base_url: str = "https://ai-bot.cn/ai-app-store/", max_retries: int = 3):
        self.base_url = base_url.rstrip('/')  # 移除末尾的斜杠
        self.max_retries = max_retries
        self.tools: List[Dict[str, str]] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 添加默认请求头
        self.default_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://ai-bot.cn/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str, retry_count: int = 0) -> Optional[str]:
        """
        获取页面内容
        
        Args:
            url: 页面URL
            retry_count: 当前重试次数
            
        Returns:
            Optional[str]: 页面内容，失败返回None
        """
        try:
            if not self.session:
                raise RuntimeError("Session not initialized")
            
            # 合并默认请求头和随机User-Agent
            headers = {**self.default_headers, **get_random_headers()}
            logger.debug(f"请求头: {headers}")
            
            async with self.session.get(url, headers=headers, ssl=False) as response:
                if response.status == 200:
                    html_content = await response.text()
                    logger.debug(f"成功获取页面内容，长度: {len(html_content)}")
                    # 保存HTML内容到文件以供调试
                    with open('debug_page.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    logger.debug("页面内容已保存到debug_page.html")
                    return html_content
                else:
                    logger.error(f"请求失败: {url}, 状态码: {response.status}")
                    
        except Exception as e:
            logger.error(f"获取页面出错: {url}, 错误: {str(e)}")
            
            if retry_count < self.max_retries:
                delay = get_retry_delay(retry_count)
                logger.info(f"等待 {delay} 秒后重试...")
                await asyncio.sleep(delay)
                return await self.fetch_page(url, retry_count + 1)
        
        return None
    
    async def crawl_page(self, page: int = 1) -> bool:
        """
        爬取指定页面的工具信息
        
        Args:
            page: 页码
            
        Returns:
            bool: 是否成功
        """
        # 构建URL
        if page > 1:
            url = f"{self.base_url}page/{page}"
        else:
            url = self.base_url
            
        logger.info(f"正在爬取第 {page} 页: {url}")
        
        # 添加随机延迟，避免请求过快
        await asyncio.sleep(random.uniform(2, 5))
        
        html_content = await self.fetch_page(url)
        if not html_content:
            return False
            
        if not AIToolParser.is_valid_page(html_content):
            logger.error(f"页面 {url} 格式无效")
            return False
            
        # 解析工具信息
        page_tools = AIToolParser.parse_tool_list(html_content)
        if page_tools:
            self.tools.extend(page_tools)
            logger.info(f"成功解析 {len(page_tools)} 个工具")
            return True
        else:
            logger.debug("未找到任何工具信息")
            return False
    
    async def crawl_all(self) -> None:
        """爬取所有页面"""
        # 获取第一页以确定总页数
        html_content = await self.fetch_page(self.base_url)
        if not html_content:
            logger.error("无法获取首页内容")
            return
            
        # 先尝试解析第一页
        if AIToolParser.is_valid_page(html_content):
            logger.debug("首页格式有效")
            page_tools = AIToolParser.parse_tool_list(html_content)
            if page_tools:
                self.tools.extend(page_tools)
                logger.info(f"成功解析首页 {len(page_tools)} 个工具")
            else:
                logger.debug("首页未找到工具信息")
        else:
            logger.debug("首页格式无效")
        
        pagination_info = AIToolParser.extract_pagination_info(html_content)
        total_pages = pagination_info['total_pages']
        logger.info(f"总页数: {total_pages}")
        
        # 创建剩余页面的任务（从第2页开始）
        if total_pages > 1:
            tasks = []
            for page in range(2, total_pages + 1):
                # 添加随机延迟，避免请求过于密集
                await asyncio.sleep(random.uniform(1, 3))
                tasks.append(self.crawl_page(page))
            
            # 并发执行任务
            results = await asyncio.gather(*tasks)
            successful_pages = sum(1 for r in results if r)
            logger.info(f"成功爬取额外的 {successful_pages}/{total_pages-1} 页")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI工具导航网站爬虫')
    parser.add_argument('--output', type=str, choices=['json', 'csv'],
                      default='json', help='输出格式 (默认: json)')
    args = parser.parse_args()
    
    async def run_crawler():
        async with AICrawler() as crawler:
            await crawler.crawl_all()
            
            if crawler.tools:
                # 保存数据
                output_file = save_data(crawler.tools, args.output)
                logger.info(f"数据已保存到: {output_file}")
                logger.info(f"共收集了 {len(crawler.tools)} 个AI工具信息")
            else:
                logger.error("未获取到任何工具信息")
    
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(run_crawler())
    except KeyboardInterrupt:
        logger.info("爬虫已手动停止")
    except Exception as e:
        logger.error(f"爬虫运行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()