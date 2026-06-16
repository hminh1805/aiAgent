import urllib.parse

tool_list = ["calculator", "weather", "chat", "search", "image"]

def weather_tool(input_data):
    # Giả sử đây là hàm gọi API thời tiết
    return f"Thời tiết {input_data} là nắng 25 độ C."

def chat_tool(input_data):
    # Hàm chat đơn giản
    return f" {input_data}"

def calculator_tool(input_data):
    # Hàm tính toán đơn giản
    try:
        result = eval(input_data)
        return f"Kết quả của {input_data} là {result}."
    except Exception as e:
        return f"Lỗi trong phép tính: {str(e)}."


def search_tool(input_data):
    """Search thật bằng DuckDuckGo (free, không cần key). Dùng query tiếng Anh + region US."""
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
                    # Cắt xuống câu đầu
                    first = snippet.split(". ")[0] + "."
                    lines.append(f"{title}: {first}")
                elif title:
                    lines.append(title)
            return " | ".join(lines)
        except ImportError:
            return "Lỗi: cần cài `pip install ddgs` (hoặc `pip install duckduckgo-search`)"
        except Exception as e:
            return f"Lỗi search: {str(e)}"


def image_tool(input_data):
    """Sinh ảnh từ prompt bằng Pollinations.ai (free, không cần token)."""
    prompt = urllib.parse.quote(input_data)
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    return url















def call_API(tool_name, input_data):
    if tool_name == "weather":
        return weather_tool(input_data)
    elif tool_name == "chat":
        return chat_tool(input_data)
    elif tool_name == "calculator":
        return calculator_tool(input_data)
    elif tool_name == "search":
        return search_tool(input_data)
    elif tool_name == "image":
        return image_tool(input_data)

    return f"Tool {tool_name} chưa được hỗ trợ."