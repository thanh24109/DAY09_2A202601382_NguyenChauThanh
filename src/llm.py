import os
import time

from dotenv import load_dotenv


load_dotenv()

_LAST_CALL_TIME = 0.0
_LAST_EXECUTION_MODE = None
_PROVIDER_DISABLED = False

# Single source of truth for both API calls and metadata.json. Every configured
# model is explicitly at or below the assignment's 10B-parameter limit.
DASHSCOPE_MODEL = "qwen3-8b"
OPENAI_MODEL = "meta-llama/llama-3-8b-instruct:free"


def get_active_model_metadata() -> dict:
    if os.getenv("LLM_DISABLED") == "1" or _LAST_EXECUTION_MODE == "fallback":
        return {
            "model": "deterministic-local-rules",
            "provider": "local",
            "parameter_size": "0 (no LLM)",
            "execution_mode": "fallback",
        }
    if os.getenv("DASHSCOPE_API_KEY"):
        return {
            "model": DASHSCOPE_MODEL,
            "provider": "Alibaba Cloud DashScope",
            "parameter_size": "8B",
            "execution_mode": "remote_llm",
        }
    if os.getenv("OPENAI_API_KEY"):
        return {
            "model": OPENAI_MODEL,
            "provider": "OpenAI-compatible API",
            "parameter_size": "8B",
            "execution_mode": "remote_llm",
        }
    return {
        "model": "deterministic-local-rules",
        "provider": "local",
        "parameter_size": "0 (no LLM)",
        "execution_mode": "fallback",
    }


def _chat_completion(api_key: str, base_url: str, model: str, prompt: str,
                     system_instruction: str, default_headers=None) -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers=default_headers or {},
    )
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        extra_body={"enable_thinking": False} if model == DASHSCOPE_MODEL else None,
    )
    return response.choices[0].message.content.strip()


def call_llm(prompt: str, system_instruction: str = "") -> str:
    """Call the configured <=10B model, or use a deterministic local fallback."""
    global _LAST_CALL_TIME, _LAST_EXECUTION_MODE, _PROVIDER_DISABLED

    if os.getenv("LLM_DISABLED") == "1" or _PROVIDER_DISABLED:
        _LAST_EXECUTION_MODE = "fallback"
        return "[FALLBACK] LLM disabled or unavailable; local confidence used."

    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if dashscope_key:
        provider = "DashScope/Qwen"
        api_key = dashscope_key
        base_url = os.getenv("DASHSCOPE_BASE_URL") or (
            "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )
        model = DASHSCOPE_MODEL
        interval = 1.0
        headers = None
    elif openai_key:
        provider = "OpenAI-compatible"
        api_key = openai_key
        base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE")
        model = OPENAI_MODEL
        interval = 2.0
        headers = {}
        if "openrouter.ai" in (base_url or "").lower():
            headers = {
                "HTTP-Referer": (
                    "https://github.com/thanh24109/"
                    "DAY09_2A202601382_NguyenChauThanh"
                ),
                "X-Title": "Olist Dispute Multi-Agent",
            }
    else:
        _LAST_EXECUTION_MODE = "fallback"
        return "[FALLBACK] No supported API key; local deterministic confidence used."

    elapsed = time.time() - _LAST_CALL_TIME
    if elapsed < interval:
        time.sleep(interval - elapsed)
    _LAST_CALL_TIME = time.time()

    backoff_delay = 2.0
    for attempt in range(3):
        try:
            result = _chat_completion(
                api_key,
                base_url,
                model,
                prompt,
                system_instruction,
                headers,
            )
            _LAST_EXECUTION_MODE = "remote_llm"
            return result
        except Exception as exc:
            message = str(exc)
            rate_limited = any(
                marker in message.lower()
                for marker in ("429", "quota", "limit", "rate")
            )
            if rate_limited and attempt < 2:
                print(
                    f"[LLM WARNING] {provider} rate limited; retrying in "
                    f"{backoff_delay:.0f}s ({attempt + 1}/3)."
                )
                time.sleep(backoff_delay)
                backoff_delay *= 2
                continue
            print(f"[LLM WARNING] {provider} call failed: {exc}. Using fallback.")
            _PROVIDER_DISABLED = True
            break

    _LAST_EXECUTION_MODE = "fallback"
    return "[FALLBACK] LLM unavailable; local deterministic confidence used."
