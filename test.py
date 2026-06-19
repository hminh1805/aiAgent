# import requests

# # Thay bằng Token trong file openclaw.json của ông
# TOKEN = "ac87d4c6299c42661353386ba0763b69d21081a2f8e25916"
# URL = "http://127.0.0.1:18789/api/v1/admin/rpc"

# headers = {
#     "Authorization": f"Bearer {TOKEN}",
#     "Content-Type": "application/json"
# }

# # Gói tin test chuẩn theo document
# # payload = {
# #     "method": "hello",
# #     "params": {}
# # }


# payload = {
#     "method": "chat.completions",
#     # "model": "google/gemini-3.1-pro-preview", # Lấy đúng tên model trong file config của ông
#     "messages": [
#         {"role": "user", "content": "Hello MiMi, test hệ thống nghe rõ trả lời!"}
#     ]
# }


# print("Đang gõ cửa OpenClaw...")
# response = requests.post(URL, headers=headers, json=payload)

# if response.status_code == 200:
#     print("🎉 THÀNH CÔNG! Cửa đã mở, OpenClaw phản hồi:")
#     print(response.json())
# else:
#     print(f"❌ THẤT BẠI (Mã lỗi: {response.status_code})")
#     print(response.text)

import asyncio
import websockets
import json

WS_URL = "ws://127.0.0.1:18789/ws" 
TOKEN = "ac87d4c6299c42661353386ba0763b69d21081a2f8e25916"

async def chat_with_mimi():
    async with websockets.connect(
        WS_URL, 
        additional_headers={"Authorization": f"Bearer {TOKEN}"}
    ) as websocket:
        
        # 1. Bắn lệnh vào đường ống
        payload = {
            "type": "chat_message", # (Lưu ý: Nếu không chạy, có thể doc của nó dùng chữ "message" thay vì "chat_message")
            "agentId": "main",
            "message": "Hello MiMi"
        }
        await websocket.send(json.dumps(payload))
        print("Đã gửi lệnh cho MiMi, đang chờ xử lý...\n")
        
        # 2. Ngồi kiên nhẫn hứng từng gói tin server trả về
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                
                # In ra để ông xem luồng sự kiện hệ thống chạy ngầm như thế nào
                event_type = data.get("type") or data.get("event")
                print(f"[Log] Server nhả ra gói tin: {event_type}")
                
                # Kiểm tra nếu gói tin có chứa câu trả lời thật của AI thì in ra
                # (Chúng ta in tạm toàn bộ chuỗi JSON để dò xem nó giấu text ở biến nào)
                if event_type not in ["connect.challenge", "ping", "pong"]:
                    print("\n🎉 DỮ LIỆU CỦA MiMi NÈ:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # Tạm ngắt vòng lặp sau khi nhận tin nhắn đầu tiên (ông có thể bỏ break để chat liên tục)
                    # break 
                    
            except websockets.exceptions.ConnectionClosed:
                print("Đường ống đã đóng.")
                break

asyncio.run(chat_with_mimi())