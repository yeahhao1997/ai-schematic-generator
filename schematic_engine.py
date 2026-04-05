"""
AI AV Schematic Generator - Core Engine
核心引擎：接收用户需求 → AI 生成设备清单和信号流 → Graphviz 画图 → 输出 PNG

用法：python schematic_engine.py
"""
import os
import json
import graphviz
from dotenv import load_dotenv

# 加载 .env 文件里的 API Key
load_dotenv()

# ============================================================
# Prompt 模板（这是系统的"大脑"）
# ============================================================

SYSTEM_PROMPT = """You are a professional AV system engineer.
Convert user requirements into a structured AV schematic.

You MUST respond with valid JSON only. No other text.

JSON format:
{
  "title": "System name",
  "devices": [
    {"id": "dev1", "name": "Device Name", "type": "input/process/output"}
  ],
  "connections": [
    {"from": "dev1", "to": "dev2", "cable": "HDMI", "signal": "Video"}
  ]
}

Rules:
- Every device must have a unique id (short, no spaces, e.g. "laptop1", "qsys_core")
- type must be one of: input, process, output
- Always include cable type and signal type for connections
- Keep device names short and professional
"""

# ============================================================
# 模拟数据（没有 API Key 时用这个）
# ============================================================

DEMO_RESULT = {
    "title": "Conference Room AV System",
    "devices": [
        {"id": "laptop1", "name": "Laptop (HDMI)", "type": "input"},
        {"id": "mic1", "name": "Wireless Mic", "type": "input"},
        {"id": "cam1", "name": "PTZ Camera", "type": "input"},
        {"id": "switcher", "name": "HDMI Switcher", "type": "process"},
        {"id": "qsys", "name": "QSYS Core", "type": "process"},
        {"id": "amp1", "name": "Amplifier", "type": "process"},
        {"id": "display1", "name": "85\" Display", "type": "output"},
        {"id": "spk1", "name": "Ceiling Speakers", "type": "output"},
        {"id": "codec1", "name": "Zoom Codec", "type": "process"},
    ],
    "connections": [
        {"from": "laptop1", "to": "switcher", "cable": "HDMI", "signal": "Video"},
        {"from": "cam1", "to": "codec1", "cable": "USB 3.0", "signal": "Video"},
        {"from": "switcher", "to": "display1", "cable": "HDMI", "signal": "Video"},
        {"from": "switcher", "to": "codec1", "cable": "HDMI", "signal": "Video"},
        {"from": "mic1", "to": "qsys", "cable": "Dante/CAT6", "signal": "Audio"},
        {"from": "qsys", "to": "amp1", "cable": "XLR", "signal": "Audio"},
        {"from": "qsys", "to": "codec1", "cable": "USB", "signal": "Audio"},
        {"from": "amp1", "to": "spk1", "cable": "Speaker Cable", "signal": "Audio"},
    ]
}


def call_claude_ai(user_input: str) -> dict:
    """
    调用 Claude API 生成设备清单和连接关系
    如果没有 API Key，返回模拟数据
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not api_key or api_key == "your-api-key-here":
        print("[DEMO MODE] No API key found, using demo data.")
        print("[DEMO MODE] To use real AI, add your key to .env file.\n")
        return DEMO_RESULT

    # 真实 API 调用
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_input}
        ]
    )

    # 解析 AI 返回的 JSON
    response_text = message.content[0].text
    return json.loads(response_text)


def generate_diagram(data: dict, output_name: str = "output/schematic") -> str:
    """
    用 Graphviz 把 AI 结果画成原理图
    返回输出文件路径
    """
    # 确保输出文件夹存在
    os.makedirs("output", exist_ok=True)

    # 颜色方案
    colors = {
        "input":   {"fill": "#E3F2FD", "border": "#1565C0", "font": "#0D47A1"},
        "process": {"fill": "#FFF3E0", "border": "#E65100", "font": "#BF360C"},
        "output":  {"fill": "#E8F5E9", "border": "#2E7D32", "font": "#1B5E20"},
    }

    # 创建图
    dot = graphviz.Digraph(
        name="AV_Schematic",
        format="png",
        graph_attr={
            "rankdir": "LR",          # 从左到右排列
            "bgcolor": "#FAFAFA",
            "label": data["title"],
            "labelloc": "t",           # 标题在顶部
            "fontsize": "20",
            "fontname": "Arial Bold",
            "pad": "0.5",
            "nodesep": "0.8",
            "ranksep": "1.2",
        },
        node_attr={
            "fontname": "Arial",
            "fontsize": "11",
            "style": "filled,rounded",
            "shape": "box",
        },
        edge_attr={
            "fontname": "Arial",
            "fontsize": "9",
        }
    )

    # 按类型分组（subgraph）
    groups = {"input": [], "process": [], "output": []}
    for dev in data["devices"]:
        groups.get(dev["type"], []).append(dev)

    group_labels = {"input": "INPUT", "process": "PROCESSING", "output": "OUTPUT"}

    for group_type, devices in groups.items():
        if not devices:
            continue
        c = colors[group_type]
        with dot.subgraph(name=f"cluster_{group_type}") as sub:
            sub.attr(
                label=group_labels[group_type],
                style="dashed",
                color=c["border"],
                fontcolor=c["font"],
                fontsize="14",
            )
            for dev in devices:
                sub.node(
                    dev["id"],
                    label=dev["name"],
                    fillcolor=c["fill"],
                    color=c["border"],
                    fontcolor=c["font"],
                )

    # 添加连接线
    for conn in data["connections"]:
        label = f"{conn['cable']}\n({conn['signal']})"
        dot.edge(
            conn["from"],
            conn["to"],
            label=label,
            color="#555555",
            fontcolor="#333333",
        )

    # 渲染输出
    output_path = dot.render(output_name, cleanup=True)
    return output_path


def main():
    print("=" * 50)
    print("  AI AV Schematic Generator")
    print("=" * 50)
    print()

    # 示例输入
    user_input = (
        "I need a conference room AV system with: "
        "laptop input, wireless microphone, PTZ camera, "
        "HDMI switcher, QSYS audio processor, amplifier, "
        "85 inch display, ceiling speakers, and Zoom codec."
    )

    print(f"User request: {user_input}\n")
    print("Generating schematic...\n")

    # Step 1: AI 生成结构
    result = call_claude_ai(user_input)

    # 打印设备清单
    print(f"System: {result['title']}")
    print(f"Devices: {len(result['devices'])}")
    print(f"Connections: {len(result['connections'])}")
    print()

    for dev in result["devices"]:
        icon = {"input": "[IN]", "process": "[DSP]", "output": "[OUT]"}.get(dev["type"], "[?]")
        print(f"  {icon} {dev['name']}")

    print()

    # Step 2: 画图
    output_path = generate_diagram(result)
    print(f"Diagram saved to: {output_path}")
    print("Done!")


if __name__ == "__main__":
    main()
