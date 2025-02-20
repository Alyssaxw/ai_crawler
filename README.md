# AI工具导航网站爬虫

这是一个用于抓取AI工具导航网站(https://ai-bot.cn/)的Python爬虫项目。该爬虫可以自动获取网站上的AI工具信息，包括工具名称、描述、链接、分类等数据。

## 功能特点

- 支持抓取多种类型的AI工具信息：
  * AI聊天机器人
  * AI图像设计
  * AI视频制作
  * AI搜索引擎
  * AI写作助手
  * AI扫描识别
  * AI语音转录
  * AI语言翻译
  * AI教育学习

- 提取的信息包括：
  * 工具名称
  * 工具描述
  * 访问链接
  * 工具分类
  * 图标URL
  * 浏览量和点赞数
  * 数据抓取时间

## 项目结构

```
ai_crawler/
├── README.md           # 项目说明文档
├── requirements.txt    # 项目依赖
├── src/
│   ├── __init__.py    # 包初始化文件
│   ├── crawler.py     # 爬虫主程序
│   ├── parser.py      # HTML解析模块
│   └── utils.py       # 工具函数
└── data/
    └── output/        # 输出数据目录
```

## 依赖安装

```bash
pip install -r requirements.txt
```

## 使用方法

1. 克隆项目到本地：
```bash
git clone https://github.com/yourusername/ai_crawler.git
cd ai_crawler
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行爬虫：
```bash
python -m src.crawler
```

4. 输出数据将保存在 `data/output` 目录下，格式为JSON：
```json
{
  "tools": [
    {
      "name": "工具名称",
      "description": "工具描述",
      "url": "工具链接",
      "category": "工具分类",
      "icon_url": "图标URL",
      "views": "浏览量",
      "likes": "点赞数",
      "crawl_time": "抓取时间"
    }
  ]
}
```

## 主要模块说明

### crawler.py
- 爬虫主程序
- 负责发送HTTP请求获取页面内容
- 控制爬取流程和数据保存

### parser.py
- HTML解析模块
- 使用BeautifulSoup解析页面内容
- 提取工具信息和分页信息

### utils.py
- 工具函数模块
- 提供数据清洗、格式化等通用功能
- 处理文件保存等操作

## 注意事项

1. 遵守网站的robots.txt规则
2. 控制请求频率，避免对目标网站造成压力
3. 定期检查页面结构变化，及时更新解析规则
4. 建议添加请求头模拟浏览器行为
5. 处理网络异常和解析异常

## 开发计划

- [ ] 添加命令行参数支持
- [ ] 实现多线程抓取
- [ ] 添加数据库存储支持
- [ ] 优化错误处理机制
- [ ] 添加日志记录功能
- [ ] 支持导出为其他格式（CSV、Excel等）

## 许可证

MIT License