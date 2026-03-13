from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mind_salon.llm.siliconflow import SiliconFlowLLM


class TestSiliconFlowApiStyle(unittest.TestCase):
    def test_auto_detects_anthropic(self) -> None:
        llm = SiliconFlowLLM(api_key="k", model="m", base_url="https://dashscope.aliyuncs.com/apps/anthropic", api_style="auto")
        self.assertEqual(llm._resolve_style(), "anthropic")
        self.assertEqual(llm._resolve_url("anthropic"), "https://dashscope.aliyuncs.com/apps/anthropic/v1/messages")

    def test_openai_url_and_payload(self) -> None:
        llm = SiliconFlowLLM(api_key="k", model="m", base_url="https://api.example.com", api_style="openai")
        self.assertEqual(llm._resolve_url("openai"), "https://api.example.com/v1/chat/completions")
        payload = llm._build_payload("openai", system_prompt="s", user_prompt="u")
        self.assertEqual(payload["model"], "m")
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertEqual(payload["messages"][1]["role"], "user")

    def test_anthropic_payload_and_extract(self) -> None:
        llm = SiliconFlowLLM(api_key="k", model="m", base_url="https://api.example.com/v1/messages", api_style="anthropic")
        payload = llm._build_payload("anthropic", system_prompt="s", user_prompt="u")
        self.assertEqual(payload["system"], "s")
        self.assertEqual(payload["messages"][0]["role"], "user")
        self.assertEqual(payload["max_tokens"], 1024)

        content = llm._extract_content("anthropic", {"content": [{"type": "text", "text": "hello"}]})
        self.assertEqual(content, "hello")


if __name__ == "__main__":
    unittest.main()
