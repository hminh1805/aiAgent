from openai import OpenAI
import json
import re
from tool_api import call_API, tool_list

client = OpenAI(
    base_url="http://172.16.12.230:8000/v1",
    api_key="ollama"
)


PLANER = (
    "Bạn là PLANNER. Phân tích câu hỏi người dùng, chọn tool cần dùng.\n"
    "Tool có sẵn:\n"
    "- calculator: tính toán (name=calculator, input=biểu thức)\n"
    "- weather: thời tiết (name=weather, input=tên địa điểm)\n"
    "- search: tìm kiếm (name=search, input=từ khóa tiếng Anh)\n"
    "- image: sinh ảnh (name=image, input=mô tả ảnh tiếng Anh)\n"
    "- date: lấy ngày hôm nay (name=date, input='today')\n"
    "- time: lấy giờ (name=time, input='now')\n"
    "Nếu là chào hỏi, hỏi đáp chung → tools=[], answer=viết câu trả lời.\n"
    "Nếu cần nhiều tool → liệt kê hết vào tools.\n"
    "KHÔNG giải thích. TRẢ VỀ JSON:\n"
    "{\"answer\": \"lời nhắn\", \"numtools\": số_tool, \"tools\": [{\"name\": \"tên\", \"input\": \"dữ liệu\"}]}"
)

messages = [{"role": "system", "content": PLANER}]


while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the agent.")
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="Qwen/Qwen3.6-35B-A3B-FP8",
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "agent_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "answer": {"type": "string"},
                        "numtools": {"type": "integer"},
                        "tools": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "input": {"type": "string"}
                                },
                                "required": ["name", "input"]
                            }
                        }
                    },
                    "required": ["answer", "tools"]
                }
            }
        },
        extra_body={
            "enable_thinking": False
        },
        timeout=120
    )

    answer = response.choices[0].message.content

    # Parse JSON response
    try:
        data = json.loads(answer)
        final_answer = data.get("answer", "")
        numtools = data.get("numtools", 0)
        tools = data.get("tools", [])
    except json.JSONDecodeError:
        print(f"Agent: (lỗi parse JSON: {answer[:100]})")
        messages.append({"role": "assistant", "content": answer})
        continue

    # Gọi các tool (kéo dài kết quả từ tool trước cho tool sau)
    tool_results = []
    tool_values = {}  # {tool_name: kết_quả_số}
    if tools:
        print(f"  → Đang gọi {len(tools)} tool...")
        for tool in tools:
            tool_name = tool.get("name")
            tool_input = tool.get("input")
            # Thay thế tên tool bằng kết quả thực tế (vd "weather" → "25")
            for prev_name, prev_val in tool_values.items():
                # Lấy số từ kết quả trước (vd "25 độ C" → "25")
                if prev_name in tool_input:
                    nums = re.findall(r'\d+', prev_val)
                    if nums:
                        tool_input = tool_input.replace(prev_name, nums[0])
            if tool_name and tool_input:
                r = call_API(tool_name, tool_input)
                tool_results.append(f"[{tool_name}] {r}")
                print(f"  Tool '{tool_name}' trả về: {r}")
                # Lưu kết quả số để tool sau dùng
                nums = re.findall(r'\d+', r)
                if nums:
                    tool_values[tool_name] = nums[0]
            else:
                print(f"  Tool không hợp lệ: {tool}")
    else:
        # Không có tool → dùng answer của LLM
        print(f"Agent: {final_answer}\n")
        messages.append({"role": "assistant", "content": answer})
        if len(messages) > 17:
            messages = [messages[0]] + messages[-16:]
        continue

    # Gửi kết quả tool cho LLM2 sinh câu trả lời cuối
    tool_summary = "\n".join(tool_results)
    llm2_messages = [
        {"role": "system", "content": "Bạn là người trả lời. Dựa vào kết quả tool bên dưới, viết 1 câu trả lời ngắn gọn.\nKHÔNG giải thích, KHÔNG suy nghĩ dài dòng.\nTRẢ VỀ JSON: {\"answer\": \"câu trả lời\"}\nKHÔNG thêm text khác ngoài JSON."},
        {"role": "user", "content": (
            f"Câu hỏi: {user_input}\n"
            f"KẾT QUẢ TOOL:\n{tool_summary}"
        )}
    ]
    final_resp = client.chat.completions.create(
        model="Qwen/Qwen3.6-35B-A3B-FP8",
        messages=llm2_messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "final_answer",
                "schema": {
                    "type": "object",
                    "properties": {
                        "answer": {"type": "string"}
                    },
                    "required": ["answer"]
                }
            }
        },
        extra_body={"enable_thinking": False},
        timeout=120
    )
    final_answer = final_resp.choices[0].message.content
    try:
        final_data = json.loads(final_answer)
        final_text = final_data.get("answer", final_answer)
    except json.JSONDecodeError:
        final_text = final_answer

    print(f"Agent: {final_text}\n")

    # Thêm vào messages để giữ context cho lần hỏi tiếp
    messages.append({"role": "assistant", "content": f"Planner: {answer}"})
    messages.append({"role": "assistant", "content": f"Final Answer: {final_text}"})

    # Giữ chỉ 16 tin cuối để context không phình to
    if len(messages) > 17:
        messages = [messages[0]] + messages[-16:]

