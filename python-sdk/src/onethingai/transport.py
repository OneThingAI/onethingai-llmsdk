"""
OneThing AI SDK HTTP 传输层模块

处理与 API 服务器的 HTTP 通信，包括请求重试和流式响应。
"""

import json
import time
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Union

import httpx

from onethingai.errors import APIError, raise_for_status


class Transport:
    """同步 HTTP 传输类"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 60.0,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.custom_headers = headers or {}
        
        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout),
            headers=self._build_headers(),
        )

    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "onethingai-python-sdk/1.0.0",
        }
        headers.update(self.custom_headers)
        return headers

    def _build_stream_headers(self) -> Dict[str, str]:
        """构建流式请求头"""
        headers = self._build_headers()
        headers.update({
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        })
        return headers

    def request(
        self,
        method: str,
        path: str,
        body: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """执行 HTTP 请求，支持重试逻辑"""
        url = f"{self.base_url}{path}"
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                # 指数退避
                time.sleep(attempt)

            try:
                response = self._request_once(method, url, body)
                return response
            except APIError as e:
                # 客户端错误 (4xx) 不重试，除了 429
                if 400 <= e.status_code < 500 and e.status_code != 429:
                    raise
                last_error = e
            except httpx.RequestError as e:
                last_error = APIError(str(e), 0)

        raise APIError(
            f"已达到最大重试次数: {last_error}",
            getattr(last_error, "status_code", 0),
        )

    def _request_once(
        self,
        method: str,
        url: str,
        body: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """执行单次 HTTP 请求"""
        json_body = None
        if body is not None:
            if hasattr(body, "model_dump"):
                json_body = body.model_dump(exclude_none=True)
            elif isinstance(body, dict):
                json_body = body
            else:
                json_body = body

        response = self._client.request(
            method=method,
            url=url,
            json=json_body,
        )

        if response.status_code >= 400:
            raise_for_status(
                response.status_code,
                response.text,
                response.headers.get("X-Request-Id"),
            )

        return response.json()

    def stream_request(
        self,
        method: str,
        path: str,
        body: Optional[Any] = None,
    ) -> Iterator[str]:
        """执行流式 HTTP 请求"""
        url = f"{self.base_url}{path}"
        
        json_body = None
        if body is not None:
            if hasattr(body, "model_dump"):
                json_body = body.model_dump(exclude_none=True)
            elif isinstance(body, dict):
                json_body = body
            else:
                json_body = body

        with self._client.stream(
            method=method,
            url=url,
            json=json_body,
            headers=self._build_stream_headers(),
        ) as response:
            if response.status_code >= 400:
                body_text = response.read().decode()
                raise_for_status(
                    response.status_code,
                    body_text,
                    response.headers.get("X-Request-Id"),
                )

            for line in response.iter_lines():
                if line:
                    yield line

    def post(self, path: str, body: Optional[Any] = None) -> Dict[str, Any]:
        """执行 POST 请求"""
        return self.request("POST", path, body)

    def post_stream(self, path: str, body: Optional[Any] = None) -> Iterator[str]:
        """执行流式 POST 请求"""
        return self.stream_request("POST", path, body)

    def close(self) -> None:
        """关闭 HTTP 客户端"""
        self._client.close()


class AsyncTransport:
    """异步 HTTP 传输类"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 60.0,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.custom_headers = headers or {}
        
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=self._build_headers(),
        )

    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "onethingai-python-sdk/1.0.0",
        }
        headers.update(self.custom_headers)
        return headers

    def _build_stream_headers(self) -> Dict[str, str]:
        """构建流式请求头"""
        headers = self._build_headers()
        headers.update({
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        })
        return headers

    async def request(
        self,
        method: str,
        path: str,
        body: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """执行 HTTP 请求，支持重试逻辑"""
        url = f"{self.base_url}{path}"
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                import asyncio
                await asyncio.sleep(attempt)

            try:
                response = await self._request_once(method, url, body)
                return response
            except APIError as e:
                if 400 <= e.status_code < 500 and e.status_code != 429:
                    raise
                last_error = e
            except httpx.RequestError as e:
                last_error = APIError(str(e), 0)

        raise APIError(
            f"已达到最大重试次数: {last_error}",
            getattr(last_error, "status_code", 0),
        )

    async def _request_once(
        self,
        method: str,
        url: str,
        body: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """执行单次 HTTP 请求"""
        json_body = None
        if body is not None:
            if hasattr(body, "model_dump"):
                json_body = body.model_dump(exclude_none=True)
            elif isinstance(body, dict):
                json_body = body
            else:
                json_body = body

        response = await self._client.request(
            method=method,
            url=url,
            json=json_body,
        )

        if response.status_code >= 400:
            raise_for_status(
                response.status_code,
                response.text,
                response.headers.get("X-Request-Id"),
            )

        return response.json()

    async def stream_request(
        self,
        method: str,
        path: str,
        body: Optional[Any] = None,
    ) -> AsyncIterator[str]:
        """执行流式 HTTP 请求"""
        url = f"{self.base_url}{path}"
        
        json_body = None
        if body is not None:
            if hasattr(body, "model_dump"):
                json_body = body.model_dump(exclude_none=True)
            elif isinstance(body, dict):
                json_body = body
            else:
                json_body = body

        async with self._client.stream(
            method=method,
            url=url,
            json=json_body,
            headers=self._build_stream_headers(),
        ) as response:
            if response.status_code >= 400:
                body_text = (await response.aread()).decode()
                raise_for_status(
                    response.status_code,
                    body_text,
                    response.headers.get("X-Request-Id"),
                )

            async for line in response.aiter_lines():
                if line:
                    yield line

    async def post(self, path: str, body: Optional[Any] = None) -> Dict[str, Any]:
        """执行 POST 请求"""
        return await self.request("POST", path, body)

    async def post_stream(self, path: str, body: Optional[Any] = None) -> AsyncIterator[str]:
        """执行流式 POST 请求"""
        async for item in self.stream_request("POST", path, body):
            yield item

    async def close(self) -> None:
        """关闭 HTTP 客户端"""
        await self._client.aclose()
