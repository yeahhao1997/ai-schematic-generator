"""
测试文件：验证核心引擎的功能
CI/CD 每次推代码都会自动运行这些测试

用法：python -m pytest test_engine.py -v
"""
import os
import json
import pytest
from schematic_engine import call_claude_ai, generate_diagram, SYSTEM_PROMPT, DEMO_RESULT


# ============================================================
# 测试 1：验证 Demo 模式能正常工作
# ============================================================
def test_demo_mode_returns_data():
    """没有 API Key 时，应该返回模拟数据"""
    # 确保没有 API Key
    os.environ.pop("ANTHROPIC_API_KEY", None)
    result = call_claude_ai("test input")
    assert result == DEMO_RESULT


# ============================================================
# 测试 2：验证返回的数据结构正确
# ============================================================
def test_result_has_required_fields():
    """返回的数据必须包含 title, devices, connections"""
    os.environ.pop("ANTHROPIC_API_KEY", None)
    result = call_claude_ai("test input")

    assert "title" in result
    assert "devices" in result
    assert "connections" in result
    assert isinstance(result["devices"], list)
    assert isinstance(result["connections"], list)


# ============================================================
# 测试 3：验证设备数据格式
# ============================================================
def test_device_format():
    """每个设备必须有 id, name, type"""
    os.environ.pop("ANTHROPIC_API_KEY", None)
    result = call_claude_ai("test input")

    for device in result["devices"]:
        assert "id" in device, f"Device missing 'id': {device}"
        assert "name" in device, f"Device missing 'name': {device}"
        assert "type" in device, f"Device missing 'type': {device}"
        assert device["type"] in ("input", "process", "output"), \
            f"Invalid device type: {device['type']}"


# ============================================================
# 测试 4：验证连接数据格式
# ============================================================
def test_connection_format():
    """每个连接必须有 from, to, cable, signal"""
    os.environ.pop("ANTHROPIC_API_KEY", None)
    result = call_claude_ai("test input")

    for conn in result["connections"]:
        assert "from" in conn, f"Connection missing 'from': {conn}"
        assert "to" in conn, f"Connection missing 'to': {conn}"
        assert "cable" in conn, f"Connection missing 'cable': {conn}"
        assert "signal" in conn, f"Connection missing 'signal': {conn}"


# ============================================================
# 测试 5：验证连接引用的设备存在
# ============================================================
def test_connections_reference_valid_devices():
    """连接中的 from/to 必须指向存在的设备"""
    os.environ.pop("ANTHROPIC_API_KEY", None)
    result = call_claude_ai("test input")

    device_ids = {dev["id"] for dev in result["devices"]}

    for conn in result["connections"]:
        assert conn["from"] in device_ids, \
            f"Connection references unknown device: {conn['from']}"
        assert conn["to"] in device_ids, \
            f"Connection references unknown device: {conn['to']}"


# ============================================================
# 测试 6：验证 Graphviz 能生成图片
# ============================================================
def test_generate_diagram_creates_file():
    """generate_diagram 应该生成 PNG 文件"""
    os.makedirs("output", exist_ok=True)
    output_path = generate_diagram(DEMO_RESULT, "output/test_diagram")

    assert os.path.exists(output_path)
    assert output_path.endswith(".png")

    # 清理测试文件
    os.remove(output_path)


# ============================================================
# 测试 7：验证 System Prompt 包含关键指令
# ============================================================
def test_system_prompt_quality():
    """System Prompt 必须包含关键指令"""
    assert "JSON" in SYSTEM_PROMPT
    assert "devices" in SYSTEM_PROMPT
    assert "connections" in SYSTEM_PROMPT
    assert "input" in SYSTEM_PROMPT
    assert "output" in SYSTEM_PROMPT


# ============================================================
# 测试 8：验证 Web 应用能启动
# ============================================================
def test_flask_app_starts():
    """Flask app 应该能正常创建"""
    from app import app
    assert app is not None

    # 测试首页能访问
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


# ============================================================
# 测试 9：验证 /generate 接口
# ============================================================
def test_generate_endpoint():
    """POST /generate 应该返回正确的 JSON"""
    from app import app
    client = app.test_client()

    response = client.post(
        "/generate",
        json={"prompt": "conference room with display"},
        content_type="application/json",
    )
    assert response.status_code == 200

    data = response.get_json()
    assert "title" in data
    assert "devices" in data
    assert "image" in data


# ============================================================
# 测试 10：验证空输入被拒绝
# ============================================================
def test_empty_input_rejected():
    """空输入应该返回 400 错误"""
    from app import app
    client = app.test_client()

    response = client.post(
        "/generate",
        json={"prompt": ""},
        content_type="application/json",
    )
    assert response.status_code == 400
