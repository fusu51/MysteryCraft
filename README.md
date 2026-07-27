<p align="center">
  <h1 align="center">🎭 MysteryCraft</h1>
  <p align="center"><b>多智能体协作的剧本杀创作引擎</b></p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/React-18-61dafb.svg" alt="React">
    <img src="https://img.shields.io/badge/FastAPI-0.129.2-green.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/LangChain-1.2.10-orange.svg" alt="LangChain">
    <img src="https://img.shields.io/badge/Docker-ready-2496ed.svg" alt="Docker">
  </p>
</p>

---

## 🎯 这是什么

**MysteryCraft** 是一个基于 **[deep-search-pro](https://github.com/waseens/deep-search-pro)** 开发的前后端分离的多智能体协作系统。输入一句话需求（如"写一个民国背景的 6 人本格推理本"），系统自动调度三个子智能体——素材搜集、剧本结构、逻辑校验——协同创作，最终产出完整剧本包：DM 手册、角色剧本、线索卡汇总、案件时间线。

前端 React + TypeScript 提供交互式创作面板，WebSocket 实时推送创作进度。

---

## 🖼️ 效果

基于下述技术栈，从前端输入需求到生成完整剧本包的端到端流程：

```
用户输入: "写一个 6 人本格推理剧本，民国上海背景，密室杀人"
    │
    ▼
🎭 MysteryCraft Web UI (React + TypeScript)
    │
    ▼
FastAPI → 主智能体 (deepagents) → 并行调度
    ├── 素材搜集助手 (Tavily 搜索，≤6 次)
    ├── 剧本结构助手 (SQLite 知识库，4 次查询)
    └── 逻辑校验助手 (LLM 反思，≤2 轮)
    │
    ▼
输出 9 个文件: DM_手册 + 6 份角色剧本 + 线索卡汇总 + 案件时间线
```

---

## 🏗️ 架构

```
mysterycraft-web (React + Vite + TypeScript)
    │
    ▼
Nginx (:9005)
    ├── /          → 前端静态文件
    ├── /api/*     → proxy → FastAPI
    └── /ws/*      → WebSocket proxy
        │
        ▼
FastAPI (Uvicorn)
    │
    ▼
主智能体 (deepagents + LangChain)
    ├── 素材搜集助手 — Tavily 网络搜索
    ├── 剧本结构助手 — SQLite 知识库 (25 角色 + 18 诡计 + 10 剧情)
    └── 逻辑校验助手 — LLM 六维逻辑审查
        │
        ▼
剧本输出: DM 手册 / 角色剧本 / 线索卡 / 时间线
```

---

## 🔧 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + TypeScript + Vite + Tailwind CSS |
| Web 框架 | FastAPI + Uvicorn |
| Agent 框架 | deepagents (LangChain 官方) |
| LLM | DeepSeek / OpenAI 兼容协议 |
| 搜索引擎 | Tavily API |
| 数据库 | SQLite (剧本知识库) |
| 实时通信 | 原生 WebSocket |
| 部署 | Docker + Nginx + Supervisor |

---

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Node.js 20+
- DeepSeek API Key（或其他 OpenAI 兼容 API）
- Tavily API Key

### 本地开发

```bash
# 1. 克隆
git clone https://github.com/你的用户名/MysteryCraft.git
cd MysteryCraft

# 2. 后端
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API 密钥
python data/script_db.py     # 初始化数据库
python api/server.py         # 启动后端 :8000

# 3. 前端（新终端）
cd mysterycraft-web
npm install
npm run dev                  # 启动前端 :5173

# 4. 浏览器打开 http://localhost:5173
```

### Docker 部署

```bash
cp .env.example .env
# 编辑 .env 填入 API 密钥
docker compose up -d --build
# 访问 http://服务器IP:9005
```

---

## 📁 项目结构

```
MysteryCraft/
├── agent/                          # 智能体层
│   ├── llm.py                      # 模型初始化
│   ├── prompts.py                  # YAML 提示词加载
│   ├── main_agent.py               # 主智能体 + 异步执行引擎
│   └── subagents/
│       ├── network_search_agent.py # 素材搜集助手
│       ├── script_structure_agent.py # 剧本结构助手
│       └── logic_validator_agent.py  # 逻辑校验助手
│
├── api/                            # Web 接口层
│   ├── server.py                   # FastAPI 入口
│   ├── context.py                  # ContextVar 协程隔离
│   └── monitor.py                  # WebSocket + 监控
│
├── tools/                          # 工具层
│   ├── tavily_tool.py              # 网络搜索
│   ├── script_db_tools.py          # 剧本知识库查询
│   ├── script_tools.py             # 剧本生成工具 (角色卡/线索卡/时间线/DM手册)
│   ├── markdown_tools.py           # Markdown 生成
│   ├── pdf_tools.py                # PDF 转换
│   └── upload_file_read_tool.py    # 文件读取
│
├── data/                           # 数据层
│   └── script_db.py                # SQLite 建表 + 预置数据 (59条)
│
├── prompt/
│   └── prompts.yml                 # 4 个 Agent 的 System Prompt
│
├── mysterycraft-web/               # 前端
│   └── src/
│       ├── components/             # 14 个 React 组件
│       ├── hooks/                  # useWebSocket / useSessions
│       ├── context/                # AppContext (useReducer)
│       ├── services/               # API 封装
│       └── types/                  # TypeScript 类型定义
│
├── docker/                         # Docker 配置
│   ├── nginx.conf
│   └── supervisord.conf
├── Dockerfile
├── docker-compose.yml
└── .env.example
