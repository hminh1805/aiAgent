from openclaw import tool, Agent
from datetime import datetime
import urllib.parse


# ——— Define tools with @tool decorator ———

@tool(description="Tính toán biểu thức toán học")
def calculator(input_data):
    try:
        result = eval(input_data)
        return f"Kết quả của {input_data} là {result}."
    except Exception as e:
        return f"Lỗi trong phép tính: {str(e)}."


@tool(description="Xem thời tiết theo địa điểm")
def weather(input_data):
    return f"Thời tiết {input_data} là nắng 25 độ C."


@tool(description="Tìm kiếm thông tin trên internet")
def search(input_data):
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            from duckduckgo_search import DDGS
            results = DDGS().text(input_data, max_results=3, region="us-en")
            if not results:
                return "Không tìm thấy kết quả."
            lines = []
            for r in results[:3]:
                title = r.get("title", "")
                snippet = r.get("body", "")
                if snippet:
                    first = snippet.split(". ")[0] + "."
                    lines.append(f"{title}: {first}")
                elif title:
                    lines.append(title)
            return " | ".join(lines)
        except ImportError:
            return "Lỗi: cần cài ddgs"
        except Exception as e:
            return f"Lỗi search: {str(e)}"


@tool(description="Sinh ảnh từ mô tả")
def image(input_data):
    prompt = urllib.parse.quote(input_data)
    url = f"https://image.pollinations.ai/prompt/{prompt}?model=flux-realism&nologo=true"
    return f"Ảnh sinh tại: {url}"


@tool(description="Lấy ngày hôm nay")
def get_date(_):
    now = datetime.now()
    return f"Hôm nay là ngày {now.day}/{now.month}/{now.year}, thứ {now.strftime('%A')}."


@tool(description="Lấy giờ hiện tại")
def get_time(_):
    now = datetime.now()
    return f"Giờ hiện tại là {now.hour}:{now.minute:02d} (UTC+7)."


# ——— Create agent and register tools ———

agent = Agent(
    model="Qwen/Qwen3.6-35B-A3B-FP8",
    base_url="http://172.16.12.230:8000/v1",
    api_key="ollama"
)

agent.add_tool(calculator)
agent.add_tool(weather)
agent.add_tool(search)
agent.add_tool(image)
agent.add_tool(get_date)
agent.add_tool(get_time)

SYSTEM_PROMPT = """Bạn là trợ lý AI đa năng. Người dùng sẽ hỏi bạn đủ thứ.
Hãy tự quyết định dùng tool nào (hoặc không dùng) để trả lời.
Tool có sẵn: calculator, weather, search, image, get_date, get_time."""

print("=" * 50)
print("  OpenClaw Agent — Web Chat Backend Demo")
print("  Gõ 'exit' hoặc 'quit' để thoát")
print("=" * 50)

while True:
    user_input = input("\nYou: ").strip()
    if user_input.lower() in ["exit", "quit"]:
        print("Bye!")
        break
    if not user_input:
        continue

    agent.run(user_input, system_prompt=SYSTEM_PROMPT)
