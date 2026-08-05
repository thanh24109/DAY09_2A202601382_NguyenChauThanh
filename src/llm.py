import os
import time
from dotenv import load_dotenv

# Nạp file .env
load_dotenv()

# Biến toàn cục để lưu mốc thời gian của cuộc gọi cuối cùng để tính khoảng chờ tối ưu
_LAST_CALL_TIME = 0.0

def call_llm(prompt: str, system_instruction: str = "") -> str:
    """Gọi LLM sử dụng API Key từ .env.
    Hỗ trợ cả Gemini API và OpenAI API (hoặc các provider tương thích).
    Nếu không có API Key, tự động fallback về phản hồi giả định (deterministic fallback).
    """
    global _LAST_CALL_TIME
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    dashscope_base = os.getenv("DASHSCOPE_BASE_URL")
    qwen_model = os.getenv("QWEN_MODEL", "qwen-plus")
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if dashscope_key:
        max_retries = 3
        backoff_delay = 2.0
        
        now = time.time()
        elapsed = now - _LAST_CALL_TIME
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        _LAST_CALL_TIME = time.time()

        for attempt in range(max_retries):
            try:
                from openai import OpenAI
                base_url = dashscope_base or "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
                model_name = qwen_model or "qwen-plus"
                
                client = OpenAI(api_key=dashscope_key, base_url=base_url)
                
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.0
                )
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower() or "limit" in err_str.lower() or "rate" in err_str.lower():
                    if attempt < max_retries - 1:
                        print(f"[LLM WARNING] DashScope/Qwen quá giới hạn request (429). Thử lại sau {backoff_delay}s... (Lần {attempt + 1}/{max_retries})")
                        time.sleep(backoff_delay)
                        backoff_delay *= 2
                        continue
                print(f"[LLM WARNING] Lỗi khi call DashScope/Qwen API: {e}. Sử dụng fallback.")
                break

    elif gemini_key:
        # Cơ chế tránh vượt ngưỡng 15 RPM (4.1 giây giữa các cuộc gọi) của Free Tier
        now = time.time()
        elapsed = now - _LAST_CALL_TIME
        if elapsed < 4.2:
            time.sleep(4.2 - elapsed)
        _LAST_CALL_TIME = time.time()

        max_retries = 3
        backoff_delay = 5.0
        
        for attempt in range(max_retries):
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                
                model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
                
                if system_instruction:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=system_instruction
                    )
                else:
                    model = genai.GenerativeModel(model_name=model_name)
                    
                response = model.generate_content(prompt)
                return response.text.strip()
                
            except Exception as e:
                err_str = str(e)
                # Nếu bị Rate Limit (429) hoặc vượt Quota, thực hiện retry
                if "429" in err_str or "quota" in err_str.lower() or "limit" in err_str.lower():
                    if attempt < max_retries - 1:
                        print(f"[LLM WARNING] Quá giới hạn request (429). Thử lại sau {backoff_delay}s... (Lần {attempt + 1}/{max_retries})")
                        time.sleep(backoff_delay)
                        backoff_delay *= 2
                        continue
                print(f"[LLM WARNING] Lỗi khi call Gemini API: {e}. Sử dụng fallback.")
                break
            
    elif openai_key:
        max_retries = 3
        backoff_delay = 5.0
        
        # Nhẹ nhàng cách khoảng giữa các cuộc gọi để không spam OpenRouter Free Tier
        now = time.time()
        elapsed = now - _LAST_CALL_TIME
        if elapsed < 2.0:
            time.sleep(2.0 - elapsed)
        _LAST_CALL_TIME = time.time()

        for attempt in range(max_retries):
            try:
                from openai import OpenAI
                base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE")
                model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
                
                # Cấu hình headers tùy chọn cho OpenRouter
                extra_headers = {}
                if "openrouter.ai" in (base_url or "").lower():
                    extra_headers = {
                        "HTTP-Referer": "https://github.com/thanh24109/DAY09_2A202601382_NguyenChauThanh",
                        "X-Title": "Olist Dispute Multi-Agent"
                    }

                client = OpenAI(api_key=openai_key, base_url=base_url, default_headers=extra_headers)
                
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.0
                )
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower() or "limit" in err_str.lower() or "rate" in err_str.lower():
                    if attempt < max_retries - 1:
                        print(f"[LLM WARNING] OpenRouter/OpenAI quá giới hạn request (429). Thử lại sau {backoff_delay}s... (Lần {attempt + 1}/{max_retries})")
                        time.sleep(backoff_delay)
                        backoff_delay *= 2
                        continue
                print(f"[LLM WARNING] Lỗi khi call OpenAI/OpenRouter API: {e}. Sử dụng fallback.")
                break

    # Fallback nếu không có API Key hoặc gặp lỗi call
    return "[FALLBACK] API Key không khả dụng hoặc cấu hình sai. Trả về phân tích cục bộ."
