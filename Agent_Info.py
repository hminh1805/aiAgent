import argparse
import json
import sys

# Fix Windows console encoding for Vietnamese characters
sys.stdout.reconfigure(encoding='utf-8')

def MyName(agent_name):
    return f"{agent_name} không nói tên của mình là {agent_name} đâu 🤭"
def MyAge(agent_name, age):
    return f"Tuổi của {agent_name} là {age} phút"

def MyHome(agent_name):
    return f"{agent_name} sống ở trong máy tính của bạn"

def Encourage(agent_name):
    return f"{agent_name} luôn ở bên bạn, hãy cố gắng lên nhé!"

parser = argparse.ArgumentParser()
parser.add_argument("--action", required=True, choices=["1", "2", "3", "4"])
parser.add_argument("--agent_name", required=True)
parser.add_argument("--name", default=None)
parser.add_argument("--age", type=int, default=None)

args = parser.parse_args()

if args.action == "1":
    result = MyName(args.agent_name)
elif args.action == "2":
    result = MyAge(args.agent_name, args.age or 0)
elif args.action == "3":
    result = MyHome(args.agent_name)
elif args.action == "4":
    result = Encourage(args.agent_name)



print(json.dumps({
    "ok": True,
    "action": args.action,
    "result": result
}, ensure_ascii=False))