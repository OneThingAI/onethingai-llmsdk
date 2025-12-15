"""
OneThing AI SDK 错误类型模块

定义了 SDK 中使用的所有异常类型。
"""

from typing import Any, Optional


class OnethingAIError(Exception):
    """OneThing AI SDK 基础错误类"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class APIError(OnethingAIError):
    """API 错误，包含状态码和响应体"""

    def __init__(
        self,
        message: str,
        status_code: int,
        body: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.request_id = request_id
        super().__init__(message)

    def __str__(self) -> str:
        base = f"HTTP {self.status_code}: {self.message}"
        if self.request_id:
            base += f" (request_id: {self.request_id})"
        return base


class AuthenticationError(APIError):
    """认证错误 (401/403)"""

    def __init__(
        self,
        message: str = "API Key 无效或缺失",
        status_code: int = 401,
        body: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, status_code, body, request_id)


class RateLimitError(APIError):
    """请求频率超限错误 (429)"""

    def __init__(
        self,
        message: str = "请求频率超限",
        status_code: int = 429,
        body: Optional[str] = None,
        request_id: Optional[str] = None,
        retry_after: Optional[float] = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, status_code, body, request_id)


class ValidationError(OnethingAIError):
    """请求参数验证错误"""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(f"字段 '{field}' 验证失败: {message}")


class JobError(OnethingAIError):
    """任务执行错误"""

    def __init__(
        self,
        message: str,
        job_id: Optional[str] = None,
        error_details: Optional[Any] = None,
    ) -> None:
        self.job_id = job_id
        self.error_details = error_details
        super().__init__(message)


class TimeoutError(OnethingAIError):
    """请求或轮询超时错误"""

    def __init__(self, message: str = "请求超时") -> None:
        super().__init__(message)


class StreamError(OnethingAIError):
    """流式处理错误"""

    def __init__(self, message: str, error_data: Optional[Any] = None) -> None:
        self.error_data = error_data
        super().__init__(message)


def raise_for_status(status_code: int, body: str, request_id: Optional[str] = None) -> None:
    """根据状态码抛出相应的错误"""
    if status_code < 400:
        return

    # 尝试从响应体解析错误信息
    message = body
    try:
        import json
        error_data = json.loads(body)
        if isinstance(error_data, dict):
            if "error" in error_data and isinstance(error_data["error"], dict):
                message = error_data["error"].get("message", body)
            elif "message" in error_data:
                message = error_data["message"]
    except (json.JSONDecodeError, KeyError):
        pass

    if status_code == 401 or status_code == 403:
        raise AuthenticationError(message, status_code, body, request_id)
    elif status_code == 429:
        raise RateLimitError(message, status_code, body, request_id)
    else:
        raise APIError(message, status_code, body, request_id)
