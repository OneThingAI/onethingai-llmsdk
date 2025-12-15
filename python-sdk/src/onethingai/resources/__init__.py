"""
OneThing AI SDK 资源模块。
"""

from onethingai.resources.text import Text
from onethingai.resources.images import Images, AsyncImages
from onethingai.resources.videos import Videos, AsyncVideos

__all__ = [
    "Text",             # 文本生成资源（
    "Images",           # 同步图片生成资源
    "AsyncImages",      # 异步图片生成资源
    "Videos",           # 同步视频生成资源
    "AsyncVideos",      # 异步视频生成资源
]
