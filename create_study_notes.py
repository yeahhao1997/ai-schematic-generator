"""
生成学习笔记 Word 文档
每完成一步就运行这个脚本更新笔记
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime

doc = Document()

# ===== 封面 =====
doc.add_paragraph()
doc.add_paragraph()
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("AI AV Schematic Generator")
run.font.size = Pt(28)
run.bold = True
run.font.color.rgb = RGBColor(0, 102, 204)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run("从零搭建 AI 自动画原理图系统\n学习笔记")
run.font.size = Pt(16)
run.font.color.rgb = RGBColor(100, 100, 100)

date_para = doc.add_paragraph()
date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = date_para.add_run(f"开始日期: {datetime.now().strftime('%Y-%m-%d')}")
run.font.size = Pt(12)

doc.add_page_break()

# ===== 目录 =====
doc.add_heading("项目总览", level=1)
doc.add_paragraph(
    "本项目目标：搭建一个 AI 驱动的 AV 原理图自动生成系统，\n"
    "同时学习 CI/CD、Git、部署等开发技能。"
)

doc.add_heading("学习路线图", level=2)
stages = [
    ("阶段 1", "搭建 AI 画图核心", "Python + Claude API + Graphviz"),
    ("阶段 2", "加 Web 界面", "Flask/FastAPI + HTML"),
    ("阶段 3", "放到 GitHub", "Git 基础操作"),
    ("阶段 4", "搭 CI/CD", "GitHub Actions 自动测试+部署"),
    ("阶段 5", "部署上线", "云服务器 / Vercel"),
]

table = doc.add_table(rows=1, cols=3, style="Light Grid Accent 1")
hdr = table.rows[0].cells
hdr[0].text = "阶段"
hdr[1].text = "内容"
hdr[2].text = "技术栈"
for stage, content, tech in stages:
    row = table.add_row().cells
    row[0].text = stage
    row[1].text = content
    row[2].text = tech

doc.add_page_break()

# ===== 阶段 1 =====
doc.add_heading("阶段 1：搭建 AI 画图核心", level=1)

# --- Step 1.1 ---
doc.add_heading("Step 1.1：环境检查", level=2)
doc.add_paragraph("目的：确认电脑上已安装必要工具。")

doc.add_heading("什么是这些工具？", level=3)
tools_explanation = [
    ("Python", "编程语言，我们写代码用的主要语言"),
    ("pip", "Python 的包管理器，用来安装第三方库（类似 App Store）"),
    ("Git", "版本控制工具，记录代码的每次修改（类似游戏存档）"),
    ("Node.js", "JavaScript 运行环境（后面做 Web 界面会用到）"),
    ("VS Code", "代码编辑器（写代码的地方）"),
]
for tool, explanation in tools_explanation:
    p = doc.add_paragraph()
    run = p.add_run(f"{tool}：")
    run.bold = True
    p.add_run(explanation)

doc.add_heading("检查命令", level=3)
doc.add_paragraph("在终端（Terminal）里输入以下命令：", style="List Bullet")

commands = [
    ("python --version", "查看 Python 版本"),
    ("pip --version", "查看 pip 版本"),
    ("git --version", "查看 Git 版本"),
    ("node --version", "查看 Node.js 版本"),
]
for cmd, desc in commands:
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(cmd)
    run.font.name = "Consolas"
    run.font.size = Pt(10)
    p.add_run(f"  — {desc}")

doc.add_heading("你的检查结果", level=3)
results = [
    ("Python", "3.11.9", "OK"),
    ("Git", "2.53.0", "OK"),
    ("Node.js", "22.21.0", "OK"),
    ("pip", "26.0", "OK"),
    ("VS Code", "1.113.0", "OK"),
    ("Docker", "未安装", "后面再装"),
    ("GitHub CLI", "未安装", "后面再装"),
]
table2 = doc.add_table(rows=1, cols=3, style="Light Grid Accent 1")
hdr2 = table2.rows[0].cells
hdr2[0].text = "工具"
hdr2[1].text = "版本"
hdr2[2].text = "状态"
for tool, ver, status in results:
    row = table2.add_row().cells
    row[0].text = tool
    row[1].text = ver
    row[2].text = status

doc.add_paragraph()
doc.add_paragraph("Step 1.1 完成！").bold = True

doc.add_page_break()

# --- Step 1.2 ---
doc.add_heading("Step 1.2：创建项目 & 安装依赖", level=2)
doc.add_paragraph("目的：创建项目文件夹，安装需要用到的 Python 库。")

doc.add_heading("关键概念", level=3)
concepts = [
    ("项目文件夹", "所有代码放在一个文件夹里，方便管理"),
    ("依赖/库 (Library)", "别人写好的代码，我们直接拿来用，不用重新造轮子"),
    ("pip install", "安装 Python 库的命令"),
    ("requirements.txt", "记录项目需要哪些库（类似购物清单）"),
]
for concept, explanation in concepts:
    p = doc.add_paragraph()
    run = p.add_run(f"{concept}：")
    run.bold = True
    p.add_run(explanation)

doc.add_heading("我们要安装的库", level=3)
libs = [
    ("anthropic", "Anthropic 官方 SDK，用来调用 Claude AI 的 API"),
    ("graphviz", "画图库，把文字描述变成图片"),
    ("python-dotenv", "读取 .env 文件，安全存储 API 密钥"),
]
for lib, desc in libs:
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(lib)
    run.bold = True
    p.add_run(f" — {desc}")

doc.add_heading("操作步骤", level=3)
steps = [
    "打开终端 (Terminal)",
    "创建项目文件夹：mkdir ai-schematic-generator",
    "进入文件夹：cd ai-schematic-generator",
    "安装依赖：pip install anthropic graphviz python-dotenv",
    "创建 requirements.txt 记录依赖",
]
for i, step in enumerate(steps, 1):
    doc.add_paragraph(f"{i}. {step}")

doc.add_heading("什么是 API Key？", level=3)
doc.add_paragraph(
    "API Key 就像一把钥匙，让你的程序可以访问 Claude AI。\n"
    "每次你的程序发请求给 Claude，都需要带上这把钥匙证明身份。\n\n"
    "重要：API Key 绝对不能公开！不能放到 GitHub 上！\n"
    "所以我们用 .env 文件来存储，并且用 .gitignore 忽略它。"
)

doc.add_heading("如何获取 Claude API Key", level=3)
api_steps = [
    "打开 https://console.anthropic.com/",
    "注册/登录账号",
    "点击左边菜单 'API Keys'",
    "点击 'Create Key'",
    "复制生成的 Key（只显示一次！）",
    "粘贴到项目的 .env 文件里",
]
for i, step in enumerate(api_steps, 1):
    doc.add_paragraph(f"{i}. {step}")

doc.add_paragraph()
p = doc.add_paragraph()
run = p.add_run("等你拿到 API Key，我们就进入 Step 1.3：写核心代码！")
run.bold = True

doc.add_page_break()

# --- Step 1.3 ---
doc.add_heading("Step 1.3：核心代码 - schematic_engine.py", level=2)
doc.add_paragraph("目的：写出系统的核心代码，实现 用户需求 → AI 分析 → 自动画图。")

doc.add_heading("整体流程", level=3)
doc.add_paragraph(
    "1. 用户输入 AV 系统需求（文字描述）\n"
    "2. 程序把需求发给 Claude AI\n"
    "3. Claude AI 返回 JSON 格式的设备清单和连接关系\n"
    "4. 程序用 Graphviz 把 JSON 画成原理图\n"
    "5. 输出 PNG 图片"
)

doc.add_heading("关键概念", level=3)
concepts_13 = [
    ("API (Application Programming Interface)",
     "程序之间沟通的接口。我们的程序通过 API 跟 Claude AI 对话。"),
    ("JSON (JavaScript Object Notation)",
     "一种数据格式，类似一张表格。AI 返回的数据用 JSON 格式，方便程序读取。"),
    ("Graphviz",
     "开源画图工具。我们告诉它'有哪些方块、怎么连线'，它自动排版画图。"),
    ("System Prompt",
     "给 AI 的'角色设定'。告诉 AI 它是 AV 工程师，要按特定格式回答。"),
    ("Demo Mode（模拟模式）",
     "没有 API Key 时，用预设数据运行，方便开发和测试。"),
    (".env 文件",
     "存储敏感信息（如 API Key）的文件，不会上传到 GitHub。"),
]
for concept, explanation in concepts_13:
    p = doc.add_paragraph()
    run = p.add_run(f"{concept}：")
    run.bold = True
    p.add_run(f"\n{explanation}")

doc.add_heading("代码结构解读", level=3)
doc.add_paragraph(
    "schematic_engine.py 文件分为 4 个部分：\n\n"
    "1. SYSTEM_PROMPT（系统提示词）\n"
    "   - 告诉 AI 它的角色是 AV 工程师\n"
    "   - 规定 AI 必须返回 JSON 格式\n"
    "   - 定义 JSON 的结构（devices + connections）\n\n"
    "2. DEMO_RESULT（模拟数据）\n"
    "   - 没有 API Key 时用的假数据\n"
    "   - 包含会议室 AV 系统的完整示例\n\n"
    "3. call_claude_ai() 函数\n"
    "   - 检查有没有 API Key\n"
    "   - 没有 → 返回模拟数据\n"
    "   - 有 → 调用 Claude API，获取真实回答\n\n"
    "4. generate_diagram() 函数\n"
    "   - 接收 JSON 数据\n"
    "   - 用 Graphviz 创建图：\n"
    "     * 蓝色方块 = INPUT 设备\n"
    "     * 橙色方块 = PROCESSING 设备\n"
    "     * 绿色方块 = OUTPUT 设备\n"
    "   - 箭头上标注线材类型和信号类型\n"
    "   - 输出 PNG 图片到 output/ 文件夹"
)

doc.add_heading("运行命令", level=3)
p = doc.add_paragraph()
run = p.add_run("python schematic_engine.py")
run.font.name = "Consolas"
run.font.size = Pt(10)

doc.add_heading("输出结果", level=3)
doc.add_paragraph(
    "运行后会在 output/ 文件夹生成 schematic.png\n"
    "这就是自动画出来的 AV 原理图！\n\n"
    "图中包含：\n"
    "- INPUT 区域（蓝色）：Laptop, Wireless Mic, PTZ Camera\n"
    "- PROCESSING 区域（橙色）：HDMI Switcher, QSYS Core, Amplifier, Zoom Codec\n"
    "- OUTPUT 区域（绿色）：85\" Display, Ceiling Speakers\n"
    "- 连接线标注：HDMI(Video), Dante/CAT6(Audio), XLR(Audio) 等"
)

doc.add_heading("切换到真实 AI 模式", level=3)
doc.add_paragraph(
    "当你拿到 Anthropic API Key 后：\n"
    "1. 打开 .env 文件\n"
    "2. 把 your-api-key-here 替换成你的真实 Key\n"
    "3. 重新运行 python schematic_engine.py\n"
    "4. 这时 AI 会根据你的输入实时生成原理图！"
)

doc.add_paragraph()
p = doc.add_paragraph()
run = p.add_run("Step 1.3 完成！阶段 1 全部完成！")
run.bold = True

doc.add_page_break()

# ===== 阶段 2 =====
doc.add_heading("阶段 2：Web 界面", level=1)

doc.add_heading("Step 2.1：什么是 Web 应用？", level=2)
doc.add_paragraph(
    "之前我们在终端（黑窗口）里运行程序，只有你自己能用。\n"
    "加上 Web 界面后，打开浏览器就能用，以后还能给客户用。\n\n"
    "Web 应用分两部分：\n"
    "- 前端 (Frontend)：用户看到的网页界面（HTML + CSS + JavaScript）\n"
    "- 后端 (Backend)：处理请求的服务器程序（Python + Flask）"
)

doc.add_heading("关键概念", level=3)
web_concepts = [
    ("Flask", "Python 的 Web 框架，帮你快速搭建网站后端。类似一个'骨架'，你往里面填内容就行。"),
    ("路由 (Route)", "URL 地址和功能的对应关系。比如访问 / 显示首页，访问 /generate 生成图。"),
    ("HTML", "网页的骨架语言，定义页面有哪些元素（标题、按钮、输入框等）。"),
    ("CSS", "网页的样式语言，定义元素长什么样（颜色、大小、位置等）。"),
    ("JavaScript", "网页的动作语言，定义用户操作时发生什么（点按钮→发请求→显示结果）。"),
    ("API 接口", "前端和后端之间的沟通方式。前端发 JSON 请求，后端返回 JSON 结果。"),
    ("JSON", "数据交换格式，像一个结构化的'信封'，前后端都能读懂。"),
    ("localhost:5000", "本地服务器地址。localhost = 你自己的电脑，5000 = 端口号（门牌号）。"),
]
for concept, explanation in web_concepts:
    p = doc.add_paragraph()
    run = p.add_run(f"{concept}：")
    run.bold = True
    p.add_run(f"\n{explanation}")

doc.add_heading("Step 2.2：项目文件结构", level=2)
doc.add_paragraph(
    "ai-schematic-generator/\n"
    "  app.py                  -- Web 服务器（后端）\n"
    "  schematic_engine.py     -- AI 核心引擎（阶段1写的）\n"
    "  requirements.txt        -- 依赖清单\n"
    "  .env                    -- API Key\n"
    "  templates/\n"
    "    index.html            -- 网页界面（前端）\n"
    "  static/                 -- 静态文件（图片、CSS等）\n"
    "  output/                 -- 生成的原理图"
)

doc.add_heading("Step 2.3：后端代码解读 (app.py)", level=2)
doc.add_paragraph(
    "app.py 做了 3 件事：\n\n"
    "1. @app.route('/')  --  首页路由\n"
    "   用户访问 http://localhost:5000 时，显示 index.html 页面\n\n"
    "2. @app.route('/generate')  --  生成路由\n"
    "   接收用户的 AV 需求（JSON 格式）\n"
    "   调用 schematic_engine.py 里的函数\n"
    "   返回设备清单 + 图片路径\n\n"
    "3. @app.route('/image/<filename>')  --  图片路由\n"
    "   提供生成的 PNG 图片给浏览器显示"
)

doc.add_heading("Step 2.4：前端代码解读 (index.html)", level=2)
doc.add_paragraph(
    "index.html 是一个单页面应用，包含：\n\n"
    "HTML 部分（骨架）：\n"
    "- 顶部导航栏：显示标题和模式标识\n"
    "- 输入区域：文本框 + 示例按钮 + 生成按钮\n"
    "- 结果区域：统计卡片 + 原理图 + 设备清单\n\n"
    "CSS 部分（样式）：\n"
    "- 深色主题设计（专业感）\n"
    "- 响应式布局（手机也能用）\n"
    "- 动画效果（加载中旋转图标）\n\n"
    "JavaScript 部分（动作）：\n"
    "- generate() 函数：点击按钮时发送请求到后端\n"
    "- showResult() 函数：收到结果后更新页面\n"
    "- fillExample() 函数：点击示例按钮填入预设需求\n"
    "- Ctrl+Enter 快捷键提交"
)

doc.add_heading("Step 2.5：如何运行", level=2)
doc.add_paragraph(
    "1. 打开终端，进入项目文件夹\n"
    "   cd ai-schematic-generator\n\n"
    "2. 启动 Web 服务器\n"
    "   python app.py\n\n"
    "3. 打开浏览器，访问\n"
    "   http://localhost:5000\n\n"
    "4. 在文本框输入 AV 需求（或点击示例按钮）\n\n"
    "5. 点击 Generate Schematic\n\n"
    "6. 等待几秒，原理图就出来了！\n\n"
    "7. 点击 Download PNG 下载图片\n\n"
    "8. 要停止服务器：在终端按 Ctrl+C"
)

doc.add_heading("前后端交互流程", level=3)
doc.add_paragraph(
    "用户点击按钮\n"
    "    |\n"
    "    v\n"
    "JavaScript 发送 POST 请求到 /generate\n"
    "（带着用户输入的文字）\n"
    "    |\n"
    "    v\n"
    "Flask 后端接收请求\n"
    "    |\n"
    "    v\n"
    "调用 call_claude_ai() 获取 AI 结果\n"
    "    |\n"
    "    v\n"
    "调用 generate_diagram() 画图\n"
    "    |\n"
    "    v\n"
    "返回 JSON（设备清单 + 图片路径）\n"
    "    |\n"
    "    v\n"
    "JavaScript 更新页面显示结果"
)

doc.add_paragraph()
p = doc.add_paragraph()
run = p.add_run("阶段 2 完成！你现在有了一个可以在浏览器里使用的 AI 画图系统！")
run.bold = True

# ===== 保存 =====
output_path = r"C:\Users\User\ai-schematic-generator\Study_Notes_AI_Schematic.docx"
doc.save(output_path)
print("Done!")
