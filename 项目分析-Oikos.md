# Oikos 项目分析

> 来源：github.com/ulsklyc/oikos | 508 Stars | 20 Forks | MIT License

## 基本信息

- **创建时间**：2026-03-24
- **语言**：JavaScript（前后端均为 Vanilla JS）
- **大小**：114MB（含 node_modules 风格的大文件）
- **部署方式**：Docker 单容器
- **许可证**：MIT
- **Topics**：docker, family, family-planner, home-automation, open-source, planner-app, privacy-first, progressive-web-app, pwa, self-hosted

## 技术栈

### 后端
- Express 5.2
- better-sqlite3 12.9（SQLCipher AES-256 加密数据库）
- bcrypt 6.0（密码哈希）
- express-session + helmet（安全中间件）
- node-cron 4.2（定时任务，如自动备份）
- node-fetch 3.3（CalDAV/ICS 外部请求）

### 前端
- 纯 Vanilla JS（ES Modules），零构建步骤
- 纯 CSS（Liquid Glass UI 风格，毛玻璃+弹簧动画）
- PWA（Service Worker 离线支持）
- Lucide 图标库
- 15 种语言国际化

### 部署
- Docker + docker-compose
- Nginx 反向代理
- 环境变量配置（.env）

## 功能模块详解

| 模块 | 前端文件大小 | 后端路由文件 | 核心功能 |
|------|------------|------------|---------|
| Tasks | 71KB | 14.5KB | 看板、子任务、循环任务、优先级、归档 |
| Calendar | 78KB | 37.9KB | CalDAV 双向同步、Google Calendar OAuth、ICS 订阅、文件附件 |
| Budget | 56KB | 37.8KB | 收支追踪、35 预设分类+自定义、15 种货币、贷款追踪 |
| Meals | 38KB | 17.7KB | 周计划拖拽、配料一键导入购物清单 |
| Shopping | 32KB | 16.7KB | 按通道分类、协作编辑、从菜谱导入 |
| Settings | 119KB | — | 系统设置、备份恢复、API Token、用户管理 |
| Dashboard | 54KB | 7.8KB | 总览仪表盘 |
| Documents | 18KB | 10.6KB | 文件上传（5MB）、14 类标签、可见性控制 |
| Contacts | 17KB | 20.1KB | CardDAV 同步、vCard 导入导出 |
| Birthdays | 21KB | 6.8KB | 自动年度日历事件、年龄显示、提醒 |
| Notes | 23KB | 5.1KB | 彩色便签、Markdown |
| Recipes | 15KB | 6.3KB | 创建/复制/缩放菜谱、预填餐位 |
| Weather | — | 5.6KB | 天气数据 |

## 架构特点

1. **零构建步骤**：没有 Webpack/Vite/Babel，纯 ES Module 加载，开发体验极简
2. **单数据库文件**：SQLite + SQLCipher，一个文件包含所有数据，备份恢复简单
3. **模块独立**：每个功能模块有独立的路由文件和前端页面，耦合度低
4. **SPA 路由**：前端 router.js (56KB) 实现客户端路由
5. **API 规范**：OpenAPI 3.0 规范，支持 API Token 外部集成

## 开放 Issues（改进机会）

| # | 标题 | 类型 |
|---|------|------|
| 136 | Polish locale | 本地化 |
| 135 | Housekeeping tracking feature | 新功能 |
| 133 | iCal integration | 新功能 |
| 34 | Household Reports & Statistics | 新功能 |
| 27 | Reward System for Task Completion | 新功能 |

## 优势

1. **隐私优先** — SQLCipher 加密 + 零遥测，数据完全自控
2. **部署简单** — Docker 一键启动，Web 安装向导
3. **PWA 支持** — 手机/平板可像原生 App 安装使用
4. **功能全面** — 13 个模块覆盖家庭日常几乎所有需求
5. **无框架依赖** — 不依赖 React/Vue 等框架，长期维护成本低
6. **Liquid Glass UI** — 视觉效果出众，类 Apple 设计语言

## 劣势/可改进点

1. **无中国本土化** — 不支持农历、微信推送、国内节假日
2. **无移动端原生体验** — PWA 在国内使用习惯不如微信小程序
3. **无社交/通知推送** — 没有微信/钉钉/飞书集成，提醒靠浏览器
4. **无数据统计** — 缺少月度报告、消费趋势分析
5. **无游戏化机制** — 缺少孩子做家务的激励系统
6. **单语言代码** — 前端文件巨大（calendar.js 78KB, tasks.js 71KB），无组件化拆分
7. **无多人权限细化** — 家庭角色仅有基本区分

## Hearth 的差异化方向

1. **微信生态集成** — 机器人推送购物清单/提醒到家庭群
2. **农历 + 中国节假日** — 春节/中秋自动提醒，生日支持农历
3. **红包记账** — 婚丧嫁娶人情往来追踪
4. **家务积分系统** — 孩子完成任务赚积分，周/月排行
5. **月度家庭报告** — 消费趋势、任务完成率、伙食多样性评分
6. **家居维护追踪** — 保洁排班、家电保修期、滤芯更换提醒
7. **微信小程序** — 国内用户首选入口，而非 PWA
