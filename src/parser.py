"""
HTML解析模块
负责解析网页内容，提取AI工具信息
"""

from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from .utils import clean_text, create_tool_item

class AIToolParser:
    """AI工具网页解析器"""
    
    @staticmethod
    def parse_tool_list(html_content: str) -> List[Dict[str, str]]:
        """
        解析工具列表页面
        
        Args:
            html_content: HTML页面内容
            
        Returns:
            List[Dict]: 工具信息列表
        """
        soup = BeautifulSoup(html_content, 'lxml')
        tools = []
        
        # 查找所有工具卡片
        tool_cards = soup.find_all('div', class_='card-app')
        
        for card in tool_cards:
            tool_info = AIToolParser._parse_tool_card(card)
            if tool_info:
                tools.append(tool_info)
        
        return tools
    
    @staticmethod
    def _parse_tool_card(card_element: BeautifulSoup) -> Optional[Dict[str, str]]:
        """
        解析单个工具卡片
        
        Args:
            card_element: 工具卡片的BeautifulSoup元素
            
        Returns:
            Optional[Dict]: 工具信息字典，解析失败返回None
        """
        try:
            # 获取工具名称和链接
            card_body = card_element.find('div', class_='card-body')
            if not card_body:
                return None
                
            app_content = card_body.find('div', class_='app-content')
            if not app_content:
                return None
                
            title_element = app_content.find('a')
            if not title_element:
                return None
                
            name = title_element.get_text().strip()
            url = title_element.get('href', '')
            
            # 获取工具描述
            description_element = app_content.find('div', class_='text-muted')
            description = description_element.get_text().strip() if description_element else ""
            
            # 获取分类
            category = "未分类"
            tga_element = app_content.find('div', class_='tga')
            if tga_element:
                category_link = tga_element.find('a')
                if category_link:
                    category = category_link.get_text().strip()
            
            # 获取统计信息（浏览量和点赞数）
            views = likes = "0"
            meta_info = app_content.find('div', class_='text-muted', recursive=False)
            if meta_info:
                spans = meta_info.find_all('span')
                for span in spans:
                    if 'down' in span.get('class', []):
                        views = span.get_text().replace('down', '').strip()
                    elif 'home-like' in span.get('class', []):
                        likes = span.get_text().strip()
            
            # 获取图标URL
            icon_url = ""
            media_content = card_body.find('a', class_='media-content')
            if media_content:
                icon_url = media_content.get('data-bg', '').replace('url(', '').replace(')', '').strip()
            
            # 创建标准格式的工具项
            tool_info = create_tool_item(
                name=name,
                description=description,
                url=url,
                category=category
            )
            
            # 添加额外信息
            tool_info.update({
                'views': clean_text(views),
                'likes': clean_text(likes),
                'icon_url': icon_url
            })
            
            return tool_info
            
        except Exception as e:
            print(f"解析工具卡片时出错: {str(e)}")
            return None
    
    @staticmethod
    def extract_pagination_info(html_content: str) -> Dict[str, int]:
        """
        提取分页信息
        
        Args:
            html_content: HTML页面内容
            
        Returns:
            Dict: 包含当前页码和总页数的字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        pagination = soup.find('div', class_='pagination')
        
        current_page = 1
        total_pages = 1
        
        if pagination:
            # 查找当前页码
            current = pagination.find('span', class_='current')
            if current:
                try:
                    current_page = int(current.get_text())
                except ValueError:
                    pass
            
            # 查找最后一个页码链接
            page_links = pagination.find_all('a', class_='page-numbers')
            if page_links:
                try:
                    # 过滤掉非数字的页码
                    page_numbers = [int(link.get_text()) for link in page_links 
                                  if link.get_text().isdigit()]
                    if page_numbers:
                        total_pages = max(page_numbers)
                except (ValueError, IndexError):
                    pass
        
        return {
            'current_page': current_page,
            'total_pages': total_pages
        }
    
    @staticmethod
    def is_valid_page(html_content: str) -> bool:
        """
        验证页面是否有效（是否包含预期的内容结构）
        
        Args:
            html_content: HTML页面内容
            
        Returns:
            bool: 页面是否有效
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 检查是否存在工具列表容器
        content_area = soup.find('div', class_='content')
        if not content_area:
            return False
            
        # 检查是否存在工具卡片
        tool_cards = soup.find_all('div', class_='card-app')
        if not tool_cards:
            return False
            
        return True