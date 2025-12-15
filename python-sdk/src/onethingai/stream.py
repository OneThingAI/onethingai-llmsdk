"""
OneThing AI SDK 流式响应读取器模块

处理 SSE (Server-Sent Events) 流式响应。
"""

import json
from typing import Any, AsyncIterator, Dict, Generic, Iterator, Optional, TypeVar

from onethingai.types import (
    ImageResult,
    ImageStreamDataResponse,
    StreamDataResponse,
    StreamEventType,
    VideoResult,
    VideoStreamDataResponse,
)
from onethingai.errors import StreamError


T = TypeVar("T")


class StreamReader(Generic[T]):
    """SSE (Server-Sent Events) 流式读取器"""

    def __init__(self, lines: Iterator[str], result_type: type) -> None:
        self._lines = lines
        self._result_type = result_type
        self._closed = False

    def __iter__(self) -> "StreamReader[T]":
        return self

    def __next__(self) -> StreamDataResponse:
        return self.next()

    def next(self) -> StreamDataResponse:
        """读取流中的下一个事件"""
        if self._closed:
            raise StopIteration

        for line in self._lines:
            line = line.strip()

            # 跳过空行和注释
            if not line or line.startswith(":"):
                continue

            # 解析 SSE 格式: "data: {...}"
            if line.startswith("data: "):
                data = line[6:]  # 移除 "data: " 前缀

                # 处理 [DONE] 信号
                if data == "[DONE]":
                    self._closed = True
                    raise StopIteration

                # 解析 JSON 数据
                try:
                    event_data = json.loads(data)
                    return self._parse_event(event_data)
                except json.JSONDecodeError as e:
                    raise StreamError(f"解析流事件失败: {e}", data)

        self._closed = True
        raise StopIteration

    def _parse_event(self, event_data: Dict[str, Any]) -> StreamDataResponse:
        """将事件数据解析为类型化响应"""
        event_type = StreamEventType(event_data.get("type", "progress"))
        
        result_data = None
        if "data" in event_data and event_data["data"]:
            if self._result_type == ImageResult:
                result_data = ImageResult(**event_data["data"])
            elif self._result_type == VideoResult:
                result_data = VideoResult(**event_data["data"])
            else:
                result_data = event_data["data"]

        if self._result_type == ImageResult:
            return ImageStreamDataResponse(
                type=event_type,
                data=result_data,
                error=event_data.get("error"),
            )
        elif self._result_type == VideoResult:
            return VideoStreamDataResponse(
                type=event_type,
                data=result_data,
                error=event_data.get("error"),
            )
        else:
            return StreamDataResponse(
                type=event_type,
                data=result_data,
                error=event_data.get("error"),
            )

    def read_all(self) -> list:
        """读取流中的所有事件直到完成"""
        events = []
        for event in self:
            events.append(event)
            if event.is_done():
                break
        return events

    def close(self) -> None:
        """关闭流"""
        self._closed = True


class AsyncStreamReader(Generic[T]):
    """异步 SSE 流式读取器"""

    def __init__(self, lines: AsyncIterator[str], result_type: type) -> None:
        self._lines = lines
        self._result_type = result_type
        self._closed = False

    def __aiter__(self) -> "AsyncStreamReader[T]":
        return self

    async def __anext__(self) -> StreamDataResponse:
        return await self.next()

    async def next(self) -> StreamDataResponse:
        """读取流中的下一个事件"""
        if self._closed:
            raise StopAsyncIteration

        async for line in self._lines:
            line = line.strip()

            if not line or line.startswith(":"):
                continue

            if line.startswith("data: "):
                data = line[6:]

                if data == "[DONE]":
                    self._closed = True
                    raise StopAsyncIteration

                try:
                    event_data = json.loads(data)
                    return self._parse_event(event_data)
                except json.JSONDecodeError as e:
                    raise StreamError(f"解析流事件失败: {e}", data)

        self._closed = True
        raise StopAsyncIteration

    def _parse_event(self, event_data: Dict[str, Any]) -> StreamDataResponse:
        """将事件数据解析为类型化响应"""
        event_type = StreamEventType(event_data.get("type", "progress"))
        
        result_data = None
        if "data" in event_data and event_data["data"]:
            if self._result_type == ImageResult:
                result_data = ImageResult(**event_data["data"])
            elif self._result_type == VideoResult:
                result_data = VideoResult(**event_data["data"])
            else:
                result_data = event_data["data"]

        if self._result_type == ImageResult:
            return ImageStreamDataResponse(
                type=event_type,
                data=result_data,
                error=event_data.get("error"),
            )
        elif self._result_type == VideoResult:
            return VideoStreamDataResponse(
                type=event_type,
                data=result_data,
                error=event_data.get("error"),
            )
        else:
            return StreamDataResponse(
                type=event_type,
                data=result_data,
                error=event_data.get("error"),
            )

    async def read_all(self) -> list:
        """读取流中的所有事件直到完成"""
        events = []
        async for event in self:
            events.append(event)
            if event.is_done():
                break
        return events

    def close(self) -> None:
        """关闭流"""
        self._closed = True


class TextStreamReader:
    """文本流式响应读取器 (OpenAI 风格)"""

    def __init__(self, lines: Iterator[str]) -> None:
        self._lines = lines
        self._closed = False

    def __iter__(self) -> "TextStreamReader":
        return self

    def __next__(self) -> Dict[str, Any]:
        return self.next()

    def next(self) -> Dict[str, Any]:
        """读取文本流中的下一个数据块"""
        if self._closed:
            raise StopIteration

        data_buffer = ""

        for line in self._lines:
            line = line.strip()

            if not line:
                if data_buffer:
                    try:
                        result = json.loads(data_buffer)
                        return result
                    except json.JSONDecodeError as e:
                        raise StreamError(f"解析流数据失败: {e}", data_buffer)
                continue

            if line.startswith("data: "):
                data = line[6:]

                if data == "[DONE]":
                    self._closed = True
                    raise StopIteration

                data_buffer = data
            elif line.startswith(":"):
                continue

        self._closed = True
        raise StopIteration

    def close(self) -> None:
        """关闭流"""
        self._closed = True


class AsyncTextStreamReader:
    """异步文本流式响应读取器"""

    def __init__(self, lines: AsyncIterator[str]) -> None:
        self._lines = lines
        self._closed = False

    def __aiter__(self) -> "AsyncTextStreamReader":
        return self

    async def __anext__(self) -> Dict[str, Any]:
        return await self.next()

    async def next(self) -> Dict[str, Any]:
        """读取文本流中的下一个数据块"""
        if self._closed:
            raise StopAsyncIteration

        data_buffer = ""

        async for line in self._lines:
            line = line.strip()

            if not line:
                if data_buffer:
                    try:
                        result = json.loads(data_buffer)
                        return result
                    except json.JSONDecodeError as e:
                        raise StreamError(f"解析流数据失败: {e}", data_buffer)
                continue

            if line.startswith("data: "):
                data = line[6:]

                if data == "[DONE]":
                    self._closed = True
                    raise StopAsyncIteration

                data_buffer = data
            elif line.startswith(":"):
                continue

        self._closed = True
        raise StopAsyncIteration

    def close(self) -> None:
        """关闭流"""
        self._closed = True
