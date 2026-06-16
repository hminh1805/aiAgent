from openai import OpenAI
import json
from tool_api import call_API, tool_list

client = OpenAI(
    base_url="http://172.16.12.230:8000/v1",
    api_key="ollama"
)





messages = [{
    "role": "system",
    "content": (
        "Bạn là AGENT. Chọn tool hoặc tự trả lời tùy tình huống.\n"
        "Nếu là chào hỏi, hỏi đáp chung, hỏi bạn là ai → tool='chat', answer: tự viết câu trả lời.\n"
        "Nếu là tính toán → tool='calculator', input='biểu thức'.\n"
        "Nếu hỏi thời tiết → tool='weather', input='tên địa điểm'.\n"
        "Nếu cần tìm kiếm thông tin (sự kiện hiện tại, chính trị, kinh tế, ranking, điểm chuẩn, giá cả) → tool='search', input='từ khóa tiếng Anh'.\n"
        "Nếu cần sinh ảnh → tool='image', input='mô tả ảnh bằng tiếng Anh'.\n"
        "Training data chỉ đến đầu 2025 — nếu không chắc câu trả lời → search.\n"
        "Nếu đã có kết quả tool trong context → giữ nguyên tool đó, KHÔNG đổi sang 'chat'.\n"
        "KHÔNG giải thích trước JSON. LUÔN viết answer (dù chat cũng phải có nội dung).\n"
        "TRẢ VỀ JSON: {\"answer\": \"lời nhắn\", \"tool\": \"tên_tool\", \"input\": \"dữ_liệu\"}"
    )
}]

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
                        "tool": {"type": "string"},
                        "input": {"type": "string"}
                    },
                    "required": ["answer", "tool", "input"]
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
        result_tool = data.get("tool", "chat")
        result_input = data.get("input", "")
    except json.JSONDecodeError:
        print(f"Agent: (lỗi parse JSON: {answer[:100]})")
        messages.append({"role": "assistant", "content": answer})
        continue

    tool_result = call_API(result_tool, result_input)

    if result_tool == "chat":
        # chat không cần gọi thêm, in answer đã parse
        print(f"Agent: {result_input if result_input else data.get('answer', '')}")
    else:
        # # Gửi kết quả tool cho model sinh câu trả lời cuối
        # tool_msg = {
        #     "role": "user",
        #     "content": f"""[TOOL_USED]: {result_tool}
        #     [TOOL_RESULT]: {tool_result}

        #     Hãy trả lời người dùng dựa trên kết quả tool ở trên.
        #     BẮT BUỘC: "tool" trong JSON phải là "{result_tool}".
        #     KHÔNG dùng "chat" khi đã có tool.
        #     KHÔNG giải thích trước JSON."""
        # }
        # messages.append(tool_msg)
        
        # final_resp = client.chat.completions.create(
        #     model="Qwen/Qwen3.6-35B-A3B-FP8",
        #     messages=messages,
        #     extra_body={"enable_thinking": False},
        #     timeout=120
        # )
        # final_answer = final_resp.choices[0].message.content
        result_json = {
            "answer": tool_result,
            "tool": result_tool,
            "input": result_input
        }
        print(f"Agent: {result_json}")
        

    messages.append({"role": "assistant", "content": answer})

    # Giữ chỉ 16 tin cuối để context không phình to
    if len(messages) > 17:
        messages = [messages[0]] + messages[-16:]

