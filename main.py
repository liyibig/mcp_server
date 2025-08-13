"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
import re
import requests
from urllib.parse import urlparse



mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def get_bilibili_cover(video_url):
    "根据给出的视频网址获取哔哩哔哩视频封面URL"
    try:
        # 获取视频的BV号或av号
        parsed_url = urlparse(video_url)
        if 'b23.tv' in parsed_url.netloc:  # 处理短链接
            video_url = requests.head(video_url, allow_redirects=True).url
            parsed_url = urlparse(video_url)
        
        path = parsed_url.path
        bvid = None
        
        # 匹配BV号或av号
        if '/video/BV' in path:
            bvid = re.search(r'/video/(BV[0-9A-Za-z]+)', path).group(1)
        elif '/video/av' in path:
            aid = re.search(r'/video/av(\d+)', path).group(1)
            bvid = f"av{aid}"
        
        if not bvid:
            raise ValueError("无法从URL中提取视频ID")
        
        # 通过B站API获取视频信息
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}" if bvid.startswith('BV') else f"https://api.bilibili.com/x/web-interface/view?aid={bvid[2:]}"
        response = requests.get(api_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        data = response.json()
        
        if data['code'] != 0:
            raise ValueError(f"API错误: {data['message']}")
        
        # 获取封面URL
        cover_url = data['data']['pic']
        if not cover_url.startswith('http'):
            cover_url = f'https:{cover_url}' if cover_url.startswith('//') else f'https://{cover_url}'
        print(f"封面URL: {cover_url}")
        return cover_url
    
    except Exception as e:
        print(f"获取封面失败: {e}")
        return None


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
'''
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."
'''
def main() -> None:
    mcp.run(transport="stdio")