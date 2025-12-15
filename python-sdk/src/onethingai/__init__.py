"""
OneThing AI Python SDK

用于访问 OneThing AI 平台的综合 SDK，支持文本、图片和视频生成。
文本生成基于 OpenAI 客户端构建，以保持兼容性。
"""

from onethingai.client import AsyncOnethingAI, OnethingAI
from onethingai.types import (
    ImageDataResponse,
    ImageExtra,
    ImageJobType,
    ImageOutputConfig,
    ImageRequest,
    ImageResult,
    InputImage,
    InputVideo,
    ResponseFormat,
    Status,
    StreamDataResponse,
    StreamEventType,
    SyncMode,
    VideoDataResponse,
    VideoExtra,
    VideoJobType,
    VideoOutputConfig,
    VideoRequest,
    VideoResult,
)
from onethingai.errors import (
    OnethingAIError,
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)

__version__ = "1.0.0"

__all__ = [
    # 客户端
    "OnethingAI",
    "AsyncOnethingAI",
    # 类型定义
    "SyncMode",
    "InputImage",
    "InputVideo",
    "ResponseFormat",
    "ImageJobType",
    "VideoJobType",
    "ImageOutputConfig",
    "VideoOutputConfig",
    "ImageExtra",
    "VideoExtra",
    "ImageRequest",
    "VideoRequest",
    "Status",
    "ImageResult",
    "VideoResult",
    "ImageDataResponse",
    "VideoDataResponse",
    "StreamEventType",
    "StreamDataResponse",
    # 错误类型
    "OnethingAIError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
]
