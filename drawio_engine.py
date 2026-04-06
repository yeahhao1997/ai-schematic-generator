"""
Draw.io Schematic Generator
生成专业 AV 原理图的 .drawio XML 文件
参考 NETe2 工程图风格：DSP 端口详细标注、设备图标、专业接线

用法：python drawio_engine.py
"""
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 升级版 Prompt — 生成带端口信息的详细数据
# ============================================================

DRAWIO_SYSTEM_PROMPT = """You are a senior AV system engineer creating professional schematic diagrams.

Convert user requirements into a DETAILED AV schematic with port-level connections.

You MUST respond with valid JSON only. No markdown, no explanation.

JSON format:
{
  "title": "Project Name - Audio/Video Schematic",
  "revision": "R01",
  "devices": [
    {
      "id": "unique_id",
      "name": "Device Name",
      "model": "Model Number",
      "category": "input|processor|output|network|control",
      "ports": [
        {"name": "OUT 1", "type": "output", "signal": "analog_audio|digital_audio|dante|aes67|video|hdmi|control|network"},
        {"name": "IN 1", "type": "input", "signal": "analog_audio"}
      ]
    }
  ],
  "connections": [
    {
      "from_device": "device_id",
      "from_port": "OUT 1",
      "to_device": "device_id",
      "to_port": "IN 1",
      "cable_type": "XLR|CAT6|HDMI|Speaker Cable|RJ45|Dante|USB",
      "signal_type": "analog_audio|digital_audio|dante|video|hdmi|control|network",
      "cable_id": "C-001"
    }
  ]
}

Rules:
- Use REAL model numbers when the user specifies them, otherwise use common professional models
- Every port on a DSP/processor should be listed individually (IN 1, IN 2, OUT 1, OUT 2, etc.)
- Dante connections use CAT6 cable
- Include cable IDs (C-001, C-002, etc.) for professional reference
- Microphones: list each mic separately if quantity specified
- Speakers: group by zone if possible
- DSP devices should show ALL input and output ports
- Always include a network switch if Dante devices are present
- Signal types: analog_audio, digital_audio, dante, aes67, video, hdmi, usb, control, network
"""

# ============================================================
# Draw.io XML 生成器
# ============================================================

# 颜色方案（参照专业 AV 图纸风格）
COLORS = {
    "input":     {"fill": "#dae8fc", "stroke": "#6c8ebf", "font": "#333333"},
    "processor": {"fill": "#fff2cc", "stroke": "#d6b656", "font": "#333333"},
    "output":    {"fill": "#d5e8d4", "stroke": "#82b366", "font": "#333333"},
    "network":   {"fill": "#e1d5e7", "stroke": "#9673a6", "font": "#333333"},
    "control":   {"fill": "#f8cecc", "stroke": "#b85450", "font": "#333333"},
}

# 信号线颜色
SIGNAL_COLORS = {
    "analog_audio":  "#0000FF",
    "digital_audio": "#FF6600",
    "dante":         "#009900",
    "aes67":         "#009900",
    "video":         "#FF0000",
    "hdmi":          "#FF0000",
    "usb":           "#666666",
    "control":       "#999999",
    "network":       "#009900",
}

# 信号线样式
SIGNAL_DASH = {
    "analog_audio":  "0",
    "digital_audio": "0",
    "dante":         "8 4",
    "aes67":         "8 4",
    "video":         "0",
    "hdmi":          "0",
    "usb":           "4 4",
    "control":       "4 2",
    "network":       "8 4",
}


def generate_drawio(data: dict, output_path: str = "output/schematic.drawio") -> str:
    """
    生成 draw.io XML 文件
    """
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else "output", exist_ok=True)

    # 根元素
    mxfile = ET.Element("mxfile", host="app.diagrams.net", type="device")
    diagram = ET.SubElement(mxfile, "diagram", name="AV Schematic", id="av_schematic")
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel",
        dx="1422", dy="762", grid="1", gridSize="10",
        guides="1", tooltips="1", connect="1", arrows="1",
        fold="1", page="1", pageScale="1",
        pageWidth="1600", pageHeight="900",
        math="0", shadow="0"
    )
    root = ET.SubElement(mxGraphModel, "root")

    # 必须有的两个基础 cell
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    cell_id = 100  # ID 计数器

    # ===== 布局计算 =====
    devices = data.get("devices", [])
    connections = data.get("connections", [])

    # 按类别分组
    categories = {}
    for dev in devices:
        cat = dev.get("category", "processor")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(dev)

    # 列位置（从左到右）
    col_order = ["input", "processor", "network", "output", "control"]
    col_x = {"input": 50, "processor": 400, "network": 700, "output": 950, "control": 700}

    # 存储设备和端口的位置，用于画线
    device_positions = {}  # device_id -> {x, y, w, h}
    port_positions = {}    # "device_id:port_name" -> {x, y}

    # ===== 画 Title Block =====
    title_id = cell_id
    cell_id += 1
    title_cell = ET.SubElement(root, "mxCell", id=str(title_id), value="",
        style="rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;",
        vertex="1", parent="1")
    ET.SubElement(title_cell, "mxGeometry", x="50", y="20", width="1500", height="50",
        **{"as": "geometry"})

    title_text_id = cell_id
    cell_id += 1
    title_text = ET.SubElement(root, "mxCell", id=str(title_text_id),
        value=f"<b style='font-size:16px'>{data.get('title', 'AV System Schematic')}</b>"
              f"&nbsp;&nbsp;&nbsp;&nbsp;Rev: {data.get('revision', 'R01')}"
              f"&nbsp;&nbsp;&nbsp;&nbsp;Date: {datetime.now().strftime('%Y-%m-%d')}",
        style="text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];autosize=1;",
        vertex="1", parent="1")
    ET.SubElement(title_text, "mxGeometry", x="400", y="25", width="800", height="40",
        **{"as": "geometry"})

    # ===== 画设备 =====
    for cat in col_order:
        if cat not in categories:
            continue
        devs = categories[cat]
        base_x = col_x.get(cat, 400)
        base_y = 100
        color = COLORS.get(cat, COLORS["processor"])

        for dev in devs:
            dev_id = dev["id"]
            ports = dev.get("ports", [])
            input_ports = [p for p in ports if p["type"] == "input"]
            output_ports = [p for p in ports if p["type"] == "output"]
            max_ports = max(len(input_ports), len(output_ports), 1)

            # 设备尺寸
            dev_w = 220
            port_h = 22
            header_h = 45
            dev_h = header_h + max_ports * port_h + 10

            # 存储设备位置
            device_positions[dev_id] = {"x": base_x, "y": base_y, "w": dev_w, "h": dev_h}

            # 设备外框
            dev_cell_id = cell_id
            cell_id += 1
            style = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={color['fill']};"
                     f"strokeColor={color['stroke']};fontColor={color['font']};"
                     f"verticalAlign=top;fontSize=10;arcSize=8;")
            dev_cell = ET.SubElement(root, "mxCell", id=str(dev_cell_id),
                value=f"<b>{dev['name']}</b><br><i style='font-size:9px;color:#666'>{dev.get('model', '')}</i>",
                style=style, vertex="1", parent="1")
            ET.SubElement(dev_cell, "mxGeometry",
                x=str(base_x), y=str(base_y),
                width=str(dev_w), height=str(dev_h),
                **{"as": "geometry"})

            # 画输入端口（左侧）
            for i, port in enumerate(input_ports):
                port_y = base_y + header_h + i * port_h
                port_key = f"{dev_id}:{port['name']}"

                pid = cell_id
                cell_id += 1
                sig_color = SIGNAL_COLORS.get(port.get("signal", ""), "#333333")
                p_style = (f"rounded=0;whiteSpace=wrap;html=1;fontSize=8;"
                           f"fillColor=#ffffff;strokeColor={sig_color};"
                           f"fontColor=#333333;align=left;spacingLeft=4;")
                p_cell = ET.SubElement(root, "mxCell", id=str(pid),
                    value=f"{port['name']}",
                    style=p_style, vertex="1", parent="1")
                ET.SubElement(p_cell, "mxGeometry",
                    x=str(base_x), y=str(port_y),
                    width="70", height=str(port_h - 2),
                    **{"as": "geometry"})

                port_positions[port_key] = {"x": base_x, "y": port_y + port_h // 2}

            # 画输出端口（右侧）
            for i, port in enumerate(output_ports):
                port_y = base_y + header_h + i * port_h
                port_key = f"{dev_id}:{port['name']}"

                pid = cell_id
                cell_id += 1
                sig_color = SIGNAL_COLORS.get(port.get("signal", ""), "#333333")
                p_style = (f"rounded=0;whiteSpace=wrap;html=1;fontSize=8;"
                           f"fillColor=#ffffff;strokeColor={sig_color};"
                           f"fontColor=#333333;align=right;spacingRight=4;")
                p_cell = ET.SubElement(root, "mxCell", id=str(pid),
                    value=f"{port['name']}",
                    style=p_style, vertex="1", parent="1")
                ET.SubElement(p_cell, "mxGeometry",
                    x=str(base_x + dev_w - 70), y=str(port_y),
                    width="70", height=str(port_h - 2),
                    **{"as": "geometry"})

                port_positions[port_key] = {"x": base_x + dev_w, "y": port_y + port_h // 2}

            base_y += dev_h + 30

    # ===== 画连接线 =====
    for conn in connections:
        from_key = f"{conn['from_device']}:{conn['from_port']}"
        to_key = f"{conn['to_device']}:{conn['to_port']}"

        # 如果端口没有找到，用设备中心点
        if from_key not in port_positions:
            dev_pos = device_positions.get(conn['from_device'])
            if dev_pos:
                from_pos = {"x": dev_pos["x"] + dev_pos["w"], "y": dev_pos["y"] + dev_pos["h"] // 2}
            else:
                continue
        else:
            from_pos = port_positions[from_key]

        if to_key not in port_positions:
            dev_pos = device_positions.get(conn['to_device'])
            if dev_pos:
                to_pos = {"x": dev_pos["x"], "y": dev_pos["y"] + dev_pos["h"] // 2}
            else:
                continue
        else:
            to_pos = port_positions[to_key]

        sig_type = conn.get("signal_type", "analog_audio")
        line_color = SIGNAL_COLORS.get(sig_type, "#333333")
        dash = SIGNAL_DASH.get(sig_type, "0")

        conn_id = cell_id
        cell_id += 1

        label = f"{conn.get('cable_id', '')}\n{conn.get('cable_type', '')}"

        dash_style = f"dashed=1;dashPattern={dash};" if dash != "0" else ""
        edge_style = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;"
                      f"jettySize=auto;html=1;strokeColor={line_color};"
                      f"strokeWidth=1.5;fontSize=7;fontColor=#555555;"
                      f"{dash_style}"
                      f"exitX=1;exitY=0.5;exitDx=0;exitDy=0;"
                      f"entryX=0;entryY=0.5;entryDx=0;entryDy=0;")

        edge = ET.SubElement(root, "mxCell", id=str(conn_id),
            value=label.strip(),
            style=edge_style, edge="1", parent="1",
            source="", target="")
        geo = ET.SubElement(edge, "mxGeometry", relative="1", **{"as": "geometry"})

        # 起点
        source_pt = ET.SubElement(geo, "mxPoint",
            x=str(from_pos["x"]), y=str(from_pos["y"]),
            **{"as": "sourcePoint"})
        # 终点
        target_pt = ET.SubElement(geo, "mxPoint",
            x=str(to_pos["x"]), y=str(to_pos["y"]),
            **{"as": "targetPoint"})

    # ===== 画图例 (Legend) =====
    legend_x = 50
    legend_y = 820
    legend_id = cell_id
    cell_id += 1
    legend_cell = ET.SubElement(root, "mxCell", id=str(legend_id),
        value="<b>SIGNAL LEGEND</b>",
        style="text;html=1;fontSize=9;fontColor=#333333;align=left;",
        vertex="1", parent="1")
    ET.SubElement(legend_cell, "mxGeometry", x=str(legend_x), y=str(legend_y),
        width="120", height="20", **{"as": "geometry"})

    legend_items = [
        ("Analog Audio", "#0000FF", "0"),
        ("Digital/Dante", "#009900", "8 4"),
        ("Video/HDMI", "#FF0000", "0"),
        ("Control", "#999999", "4 2"),
    ]
    for i, (name, color, dash) in enumerate(legend_items):
        lid = cell_id
        cell_id += 1
        dash_part = f"dashed=1;dashPattern={dash};" if dash != "0" else ""
        line = ET.SubElement(root, "mxCell", id=str(lid),
            value=name,
            style=f"endArrow=none;html=1;strokeColor={color};strokeWidth=2;fontSize=8;fontColor=#555;{dash_part}align=left;",
            edge="1", parent="1")
        geo = ET.SubElement(line, "mxGeometry", relative="1", **{"as": "geometry"})
        lx = legend_x + i * 160
        ET.SubElement(geo, "mxPoint", x=str(lx), y=str(legend_y + 35), **{"as": "sourcePoint"})
        ET.SubElement(geo, "mxPoint", x=str(lx + 60), y=str(legend_y + 35), **{"as": "targetPoint"})

    # ===== 写入文件 =====
    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    return output_path


def call_claude_for_drawio(user_input: str) -> dict:
    """
    调用 Claude API，使用 draw.io 专用的详细 prompt
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not api_key or api_key == "your-api-key-here":
        print("[DEMO MODE] Using demo data.")
        return DEMO_DRAWIO_RESULT

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        system=DRAWIO_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_input}]
    )

    text = message.content[0].text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    return json.loads(text)


# ============================================================
# Demo 数据（模拟一个真实 AV 系统）
# ============================================================

DEMO_DRAWIO_RESULT = {
    "title": "Conference Room - Audio Schematic",
    "revision": "R01",
    "devices": [
        {
            "id": "mic_wireless",
            "name": "Wireless Microphone",
            "model": "Shure ULXD4Q",
            "category": "input",
            "ports": [
                {"name": "RF IN", "type": "input", "signal": "analog_audio"},
                {"name": "OUT 1", "type": "output", "signal": "dante"},
                {"name": "OUT 2", "type": "output", "signal": "analog_audio"},
            ]
        },
        {
            "id": "mic_ceiling",
            "name": "Ceiling Microphone",
            "model": "Shure MXA920",
            "category": "input",
            "ports": [
                {"name": "DANTE", "type": "output", "signal": "dante"},
            ]
        },
        {
            "id": "dsp",
            "name": "DSP Processor",
            "model": "QSYS Core 110f",
            "category": "processor",
            "ports": [
                {"name": "IN 1", "type": "input", "signal": "analog_audio"},
                {"name": "IN 2", "type": "input", "signal": "analog_audio"},
                {"name": "IN 3", "type": "input", "signal": "analog_audio"},
                {"name": "DANTE IN", "type": "input", "signal": "dante"},
                {"name": "OUT 1", "type": "output", "signal": "analog_audio"},
                {"name": "OUT 2", "type": "output", "signal": "analog_audio"},
                {"name": "OUT 3", "type": "output", "signal": "analog_audio"},
                {"name": "DANTE OUT", "type": "output", "signal": "dante"},
                {"name": "USB", "type": "output", "signal": "usb"},
            ]
        },
        {
            "id": "switch",
            "name": "Network Switch",
            "model": "Netgear M4250",
            "category": "network",
            "ports": [
                {"name": "PORT 1", "type": "input", "signal": "network"},
                {"name": "PORT 2", "type": "input", "signal": "network"},
                {"name": "PORT 3", "type": "input", "signal": "network"},
                {"name": "PORT 4", "type": "output", "signal": "network"},
            ]
        },
        {
            "id": "amp",
            "name": "Amplifier",
            "model": "QSC CX-Q 2K4",
            "category": "processor",
            "ports": [
                {"name": "IN 1", "type": "input", "signal": "analog_audio"},
                {"name": "IN 2", "type": "input", "signal": "analog_audio"},
                {"name": "OUT 1", "type": "output", "signal": "analog_audio"},
                {"name": "OUT 2", "type": "output", "signal": "analog_audio"},
            ]
        },
        {
            "id": "spk_ceiling",
            "name": "Ceiling Speakers",
            "model": "JBL Control 24CT",
            "category": "output",
            "ports": [
                {"name": "IN +/-", "type": "input", "signal": "analog_audio"},
            ]
        },
        {
            "id": "codec",
            "name": "Video Codec",
            "model": "Zoom Room",
            "category": "output",
            "ports": [
                {"name": "USB IN", "type": "input", "signal": "usb"},
            ]
        },
    ],
    "connections": [
        {"from_device": "mic_wireless", "from_port": "OUT 1", "to_device": "switch", "to_port": "PORT 1", "cable_type": "CAT6", "signal_type": "dante", "cable_id": "C-001"},
        {"from_device": "mic_ceiling", "from_port": "DANTE", "to_device": "switch", "to_port": "PORT 2", "cable_type": "CAT6", "signal_type": "dante", "cable_id": "C-002"},
        {"from_device": "switch", "from_port": "PORT 3", "to_device": "dsp", "to_port": "DANTE IN", "cable_type": "CAT6", "signal_type": "dante", "cable_id": "C-003"},
        {"from_device": "mic_wireless", "from_port": "OUT 2", "to_device": "dsp", "to_port": "IN 1", "cable_type": "XLR", "signal_type": "analog_audio", "cable_id": "C-004"},
        {"from_device": "dsp", "from_port": "OUT 1", "to_device": "amp", "to_port": "IN 1", "cable_type": "XLR", "signal_type": "analog_audio", "cable_id": "C-005"},
        {"from_device": "dsp", "from_port": "OUT 2", "to_device": "amp", "to_port": "IN 2", "cable_type": "XLR", "signal_type": "analog_audio", "cable_id": "C-006"},
        {"from_device": "amp", "from_port": "OUT 1", "to_device": "spk_ceiling", "to_port": "IN +/-", "cable_type": "Speaker Cable", "signal_type": "analog_audio", "cable_id": "C-007"},
        {"from_device": "dsp", "from_port": "USB", "to_device": "codec", "to_port": "USB IN", "cable_type": "USB-B", "signal_type": "usb", "cable_id": "C-008"},
    ]
}


def main():
    print("=" * 50)
    print("  Draw.io AV Schematic Generator")
    print("=" * 50)

    user_input = (
        "Conference room audio system: "
        "Shure ULXD4Q wireless mic receiver, Shure MXA920 ceiling mic, "
        "QSYS Core 110f DSP, QSC CX-Q 2K4 amplifier, "
        "JBL ceiling speakers, Netgear network switch for Dante, "
        "Zoom Room codec with USB audio"
    )

    print(f"\nUser request: {user_input}\n")
    print("Generating draw.io schematic...\n")

    result = call_claude_for_drawio(user_input)

    print(f"System: {result['title']}")
    print(f"Devices: {len(result['devices'])}")
    print(f"Connections: {len(result['connections'])}")
    print()

    for dev in result["devices"]:
        ports = dev.get("ports", [])
        print(f"  [{dev.get('category', '?').upper()[:3]}] {dev['name']} ({dev.get('model', '')}) - {len(ports)} ports")

    output_path = generate_drawio(result)
    print(f"\nDraw.io file saved to: {output_path}")
    print("Open this file in https://app.diagrams.net/ or draw.io desktop app")
    print("Done!")


if __name__ == "__main__":
    main()
