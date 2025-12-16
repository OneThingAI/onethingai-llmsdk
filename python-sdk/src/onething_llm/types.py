"""
OneThing AI SDK 类型定义模块

定义了所有请求和响应的数据类型。
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class SyncMode(str, Enum):
    """同步模式枚举"""
    SYNC = "sync"
    ASYNC = "async"


class ResponseFormat(str, Enum):
    """响应格式枚举"""
    URL = "url"
    B64_JSON = "b64_json"


class ImageJobType(str, Enum):
    """图片任务类型枚举"""
    GENERATION = "generation"
    EDIT = "edit"
    VARIATION = "variation"


class VideoJobType(str, Enum):
    """视频任务类型枚举"""
    TEXT2VIDEO = "text2video"
    IMAGE2VIDEO = "image2video"


class TextJobType(str, Enum):
    """文本任务类型枚举"""
    CHAT_COMPLETIONS = "chat/completions"
    COMPLETIONS = "completions"
    RESPONSES = "responses"


class Status(str, Enum):
    """任务状态枚举"""
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class StreamEventType(str, Enum):
    """流式事件类型枚举"""
    PROGRESS = "progress"
    PARTIAL_RESULT = "partial_result"
    ERROR = "error"
    DONE = "done"


class ImageStyle(str, Enum):
    """图片风格枚举"""
    VIVID = "vivid"
    NATURAL = "natural"


# Input Types

class InputImage(BaseModel):
    """输入图片结构"""
    url: Optional[str] = None
    b64_json: Optional[str] = None

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """序列化时排除 None 值"""
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class InputVideo(BaseModel):
    """输入视频结构"""
    url: Optional[str] = None

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


# Output Config Types

class ImageOutputConfig(BaseModel):
    """图片输出配置"""
    height: Optional[int] = None
    width: Optional[int] = None
    response_format: Optional[ResponseFormat] = None

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class VideoOutputConfig(BaseModel):
    """视频输出配置"""
    height: Optional[int] = None
    width: Optional[int] = None
    duration: Optional[int] = None
    fps: Optional[int] = None

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


# Extra Params

class ImageExtra(BaseModel):
    """图片额外参数"""
    seed: Optional[int] = None
    style: Optional[ImageStyle] = None

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class VideoExtra(BaseModel):
    """视频额外参数"""
    seed: Optional[int] = None
    audio_enabled: bool = False
    negative_prompt: Optional[str] = None

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


# Parameters

class ImageParameters(BaseModel):
    """图片参数配置"""
    input_images: Optional[List[InputImage]] = None
    input_videos: Optional[List[InputVideo]] = None
    output_config: Optional[ImageOutputConfig] = None

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class VideoParameters(BaseModel):
    """视频参数配置"""
    input_images: Optional[List[InputImage]] = None
    input_videos: Optional[List[InputVideo]] = None
    output_config: Optional[VideoOutputConfig] = None

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


# Request Types

class ImageRequest(BaseModel):
    """图片请求结构"""
    model: str
    job_type: ImageJobType = ImageJobType.GENERATION
    sync_mode: SyncMode = SyncMode.SYNC
    stream: Optional[bool] = None
    prompt: str
    n: Optional[int] = None
    parameters: Optional[ImageParameters] = None
    extra: Optional[ImageExtra] = None

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class VideoRequest(BaseModel):
    """视频请求结构"""
    model: str
    job_type: VideoJobType = VideoJobType.TEXT2VIDEO
    sync_mode: SyncMode = SyncMode.ASYNC
    stream: Optional[bool] = None
    prompt: str
    n: Optional[int] = None
    parameters: Optional[VideoParameters] = None
    extra: Optional[VideoExtra] = None

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


# Result Types

class ImageResult(BaseModel):
    """图片结果"""
    index: int = 0
    url: Optional[str] = None
    b64_json: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class VideoResult(BaseModel):
    """视频结果"""
    index: int = 0
    url: Optional[str] = None
    duration: Optional[int] = None
    fps: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


# Response Types

class Result(BaseModel):
    """任务结果容器"""
    data: List[Any] = Field(default_factory=list)


class ImageResultContainer(BaseModel):
    """图片结果容器"""
    data: List[ImageResult] = Field(default_factory=list)


class VideoResultContainer(BaseModel):
    """视频结果容器"""
    data: List[VideoResult] = Field(default_factory=list)


class ImageAndVideoDataResponse(BaseModel):
    """图片和视频数据响应结构"""
    job_id: str = ""
    status: str = "processing"  # processing, success, failed
    progress: float = 0.0
    created: int = 0
    result: Optional[Any] = None
    error: Optional[Any] = None

    def is_completed(self) -> bool:
        return self.status == "success"

    def is_failed(self) -> bool:
        return self.status == "failed"

    def is_processing(self) -> bool:
        return self.status == "processing"


class ImageDataResponse(ImageAndVideoDataResponse):
    """图片响应类型"""
    result: Optional[ImageResultContainer] = None


class VideoDataResponse(ImageAndVideoDataResponse):
    """视频响应类型"""
    result: Optional[VideoResultContainer] = None


# Stream Types

class StreamDataResponse(BaseModel):
    """流式响应结构"""
    type: StreamEventType
    data: Optional[Any] = None
    error: Optional[Any] = None

    def is_progress(self) -> bool:
        return self.type == StreamEventType.PROGRESS

    def is_partial_result(self) -> bool:
        return self.type == StreamEventType.PARTIAL_RESULT

    def is_error(self) -> bool:
        return self.type == StreamEventType.ERROR

    def is_done(self) -> bool:
        return self.type == StreamEventType.DONE


class ImageStreamDataResponse(StreamDataResponse):
    """图片流式响应类型"""
    data: Optional[ImageResult] = None


class VideoStreamDataResponse(StreamDataResponse):
    """视频流式响应类型"""
    data: Optional[VideoResult] = None


# API Response Wrapper

class APIResponse(BaseModel):
    """API 响应基础结构"""
    code: int = 0
    data: Any = None
    request_id: str = ""
    message: str = ""


class ImageResponse(APIResponse):
    """图片 API 响应
    
    响应格式：
    {
        "code": 0,
        "data": {
            "job_id": "string",
            "status": "processing",
            "progress": 0,
            "created": 0,
            "result": {
                "data": [
                    {
                        "index": 0,
                        "url": "string",
                        "b64_json": "string",
                        "metadata": {...}
                    }
                ]
            },
            "error": null
        },
        "request_id": "string", 
        "message": "string"
    }
    """
    data: ImageAndVideoDataResponse = Field(default_factory=ImageAndVideoDataResponse)
    
    @property
    def status(self) -> str:
        """获取任务状态"""
        return self.data.status
    
    @property
    def job_id(self) -> str:
        """获取任务ID"""
        return self.data.job_id
    
    @property
    def progress(self) -> float:
        """获取进度"""
        return self.data.progress
    
    @property
    def results(self) -> List[ImageResult]:
        """获取图片结果列表"""
        if (self.data.result and 
            isinstance(self.data.result, dict) and 
            'data' in self.data.result):
            return [ImageResult(**item) if isinstance(item, dict) else item 
                   for item in self.data.result['data']]
        return []
    
    @property
    def error(self) -> Optional[Any]:
        """获取错误信息"""
        return self.data.error


class VideoResponse(APIResponse):
    """视频 API 响应"""
    data: ImageAndVideoDataResponse = Field(default_factory=ImageAndVideoDataResponse)


class TextResponse(APIResponse):
    """文本 API 响应"""
    data: Dict[str, Any] = Field(default_factory=dict)


# Polling Options

class PollingOptions(BaseModel):
    """轮询配置选项"""
    max_attempts: int = 0  # 0 = 无限制
    interval: float = 2.0  # 秒
    timeout: float = 300.0  # 秒, 0 = 无超时

    class Config:
        arbitrary_types_allowed = True
