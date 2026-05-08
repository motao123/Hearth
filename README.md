# Hearth

> 家庭生活管理中心 — 任务、餐食、购物、预算、日历，一个全搞定。数据留在家中。

Hearth 是一个自部署的家庭生活管理 Web 应用，把日常家务事集中到一个私密的地方——无需云账号、无需订阅、数据不出家门。

## 为什么做 Hearth？

每个家庭都在处理同样的事：谁做什么、今天吃什么、买什么、花了多少。大多数家庭把这些散落在微信群、共享备忘录、五六个不同的 App 里。Hearth 把一切归拢到一个地方，跑在你自己的服务器上。

**相比现有方案的优势：**

- **隐私优先** — 数据本地加密存储，零遥测，完全自部署
- **中国本土化** — 农历节日、红包记账、微信推送
- **家务积分** — 孩子做家务赚积分，月度排行
- **Docker + 桌面双端** — 服务器部署 + 桌面客户端
- **中文优先** — 界面和文档以中文为主

## 功能模块

| 模块 | 说明 | 状态 |
|------|------|------|
| 任务 | 共享任务、看板、优先级、子任务、循环任务、家务积分 | 🚧 开发中 |
| 购物清单 | 协作购物列表、按通道分类、从菜谱一键导入 | 🚧 开发中 |
| 餐食计划 | 周计划拖拽、配料一键导出到购物清单 | 🚧 开发中 |
| 菜谱 | 创建/复制/缩放菜谱、预填餐位 | 🚧 开发中 |
| 日历 | CalDAV/ICS 同步、农历、中国节假日 | 🚧 开发中 |
| 预算 | 收支追踪、月度趋势、红包人情记账 | 🚧 开发中 |
| 便签 | 彩色便签 + Markdown | 🚧 开发中 |
| 家庭 | 成员档案、角色、积分排行 | 🚧 开发中 |

## 相比 Oikos 的增强

| 方向 | 说明 |
|------|------|
| 微信集成 | 机器人推送购物清单/提醒到家庭群 |
| 农历 + 中国节假日 | 春节/中秋自动提醒，生日支持农历 |
| 红包记账 | 婚丧嫁娶人情往来追踪 |
| 家务积分系统 | 孩子完成任务赚积分，周/月排行 |
| 月度家庭报告 | 消费趋势、任务完成率统计 |
| 家居维护追踪 | 保洁排班、家电保修期提醒 |
| 桌面客户端 | Tauri 打包 Win/Mac 桌面 App |

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | **FastAPI** + SQLAlchemy + aiosqlite |
| 前端 | **Vue 3** + Vite + Tailwind CSS + Pinia |
| 数据库 | SQLite（支持 SQLCipher 加密） |
| 认证 | JWT + bcrypt |
| 部署 | Docker + docker-compose |
| 桌面端 | Tauri（Rust） |
| PWA | vite-plugin-pwa，支持离线安装 |

## 快速开始

```bash
git clone https://github.com/yourname/hearth.git && cd hearth
cp .env.example .env
docker compose up -d
```

打开 `http://localhost:8090`，创建管理员账号即可使用。

## 本地开发

```bash
# 后端
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8090

# 前端
cd frontend
npm install
npm run dev
```

## 项目结构

```
hearth/
├── backend/                 # Python 后端
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── core/            # 配置、数据库、安全
│   │   ├── models/          # SQLAlchemy 数据模型
│   │   ├── api/             # API 路由
│   │   │   ├── auth.py
│   │   │   ├── tasks.py
│   │   │   ├── shopping.py
│   │   │   ├── meals.py
│   │   │   ├── budget.py
│   │   │   ├── calendar.py
│   │   │   └── notes.py
│   │   └── services/        # 业务逻辑
│   ├── migrations/
│   ├── tests/
│   └── pyproject.toml
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── pages/           # 页面组件
│   │   ├── components/      # 共享组件
│   │   ├── composables/     # 组合式函数
│   │   ├── locales/         # 国际化
│   │   ├── styles/          # CSS
│   │   └── utils/           # 工具函数
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── desktop/                 # Tauri 桌面客户端
│   └── src/
├── docker/
│   └── Dockerfile
├── docs/
├── scripts/
├── docker-compose.yml
└── .env.example
```

## License

MIT
