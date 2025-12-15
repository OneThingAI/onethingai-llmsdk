"""
OneThing AI 文本生成资源
"""

from typing import Any, Dict, List, Optional
from onethingai.transport import Transport
from onethingai.types import TextJobType


class Text:
    """文本生成资源"""
    
    def __init__(self, transport: Transport):
        self._transport = transport

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any
    ) -> Any:
        """聊天完成功能"""
        data = {
            "model": model,
            "job_type": TextJobType.CHAT_COMPLETIONS,
            "messages": messages,
            **kwargs
        }
        
        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if top_p is not None:
            data["top_p"] = top_p
        if frequency_penalty is not None:
            data["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            data["presence_penalty"] = presence_penalty
        if stream:
            data["stream"] = stream
            
        if stream:
            return self._transport.post_stream("/generation", data)
        else:
            return self._transport.post("/generation", data)

    def completions(
        self,
        model: str,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any
    ) -> Any:
        """文本完成功能"""
        data = {
            "model": model,
            "job_type": TextJobType.COMPLETIONS,
            "prompt": prompt,
            **kwargs
        }
        
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p
        if frequency_penalty is not None:
            data["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            data["presence_penalty"] = presence_penalty
        if stream:
            data["stream"] = stream
            
        if stream:
            return self._transport.post_stream("/generation", data)
        else:
            return self._transport.post("/generation", data)

    def responses(
        self,
        model: str,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        repetition_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any
    ) -> Any:
        """响应生成功能"""
        data = {
            "model": model,
            "job_type": TextJobType.RESPONSES,
            "prompt": prompt,
            **kwargs
        }
        
        if max_length is not None:
            data["max_length"] = max_length
        if temperature is not None:
            data["temperature"] = temperature
        if top_k is not None:
            data["top_k"] = top_k
        if top_p is not None:
            data["top_p"] = top_p
        if repetition_penalty is not None:
            data["repetition_penalty"] = repetition_penalty
        if stream:
            data["stream"] = stream
            
        if stream:
            return self._transport.post_stream("/generation", data)
        else:
            return self._transport.post("/generation", data)

