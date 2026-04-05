"""
AI AV Schematic Generator - Web App
网页版：在浏览器里输入需求，自动生成原理图

用法：python app.py
然后打开浏览器访问 http://localhost:5000
"""
import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, send_file
from schematic_engine import call_claude_ai, generate_diagram

app = Flask(__name__)


@app.route("/")
def index():
    """首页 - 显示输入表单"""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """
    接收用户需求，生成原理图
    返回 JSON：包含设备清单 + 图片路径
    """
    # 从前端拿到用户输入
    data = request.get_json()
    user_input = data.get("prompt", "").strip()

    if not user_input:
        return jsonify({"error": "Please enter your AV system requirements."}), 400

    # Step 1: AI 生成结构
    result = call_claude_ai(user_input)

    # Step 2: 画图（用唯一文件名避免冲突）
    file_id = uuid.uuid4().hex[:8]
    output_name = f"output/schematic_{file_id}"
    output_path = generate_diagram(result, output_name)

    # 返回结果
    return jsonify({
        "title": result["title"],
        "devices": result["devices"],
        "connections": result["connections"],
        "image": f"/image/{os.path.basename(output_path)}",
        "device_count": len(result["devices"]),
        "connection_count": len(result["connections"]),
    })


@app.route("/image/<filename>")
def get_image(filename):
    """提供生成的图片"""
    filepath = os.path.join("output", filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype="image/png")
    return "Image not found", 404


# 确保 output 文件夹存在（本地和生产环境都需要）
os.makedirs("output", exist_ok=True)

if __name__ == "__main__":
    print("=" * 50)
    print("  AI AV Schematic Generator - Web App")
    print("  Open: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
