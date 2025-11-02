# React + FastAPI 全栈架构与 Vercel / Railway 部署指南

本文档面向希望使用 React 架构前端并部署在 Vercel、以 FastAPI + Python 架构后端并部署在 Railway 的团队，提供可落地的架构设计、目录规范、环境配置、部署流程、CI/CD、监控与安全最佳实践。所有示例与约定均以中文说明，便于团队协作与知识沉淀。

---

## 1. 目标与范围

- 前端：React（推荐 Vite）或可选 Next.js（SSR/SSG），部署在 Vercel。
- 后端：FastAPI + Uvicorn/Gunicorn，数据库以 Postgres 为主（Railway 托管），部署在 Railway。
- 通信：HTTPS + REST（可选 WebSocket），前端通过环境变量指向后端 API 网关域名。
- 形态：支持「单仓 Monorepo」与「双仓 Polyrepo」，并给出对比与推荐。
- 保障：提供配置管理、日志/监控、安全与性能优化建议，附常见文件片段。

---

## 2. 架构总览

```
┌──────────┐      HTTPS       ┌──────────────────────┐
│  Vercel  │  ─────────────▶ │ Frontend: React/Vite │
│  Edge/CDN│                 │   (Static/SSR 可选)   │
└──────────┘                 └───────────▲───────────┘
                                           │ API Base URL
                                           │ (VERCEL 环境变量)
                                           │
                                   ┌───────┴────────┐
                                   │ Railway        │
                                   │ Backend:       │
                                   │ FastAPI +      │
                                   │ Uvicorn/Gunicorn│
                                   └───────▲────────┘
                                           │
                                 ┌─────────┴─────────┐
                                 │ Railway Postgres  │
                                 │ (可选 Redis/对象存储)│
                                 └───────────────────┘
```

---

## 3. 组件清单与版本建议

- 前端
  - 构建：Vite（推荐）或 Next.js（需要 SSR/SSG/Middleware 时）
  - UI：Tailwind CSS / Ant Design / Mantine（按业务需求选型）
  - 状态：React Query + Zustand/Redux（数据获取 + 本地状态）
  - 质量：ESLint + Prettier + Vitest/Jest + Playwright（E2E 可选）
- 后端
  - 框架：FastAPI（Pydantic v2）
  - 服务器：Uvicorn（开发）+ Gunicorn（生产多进程）
  - 数据库：Postgres（Railway 托管）+ SQLAlchemy + Alembic（迁移）
  - 认证：JWT（PyJWT / python-jose）+ OAuth2 Password Flow（可选）
  - 质量：pytest + mypy（可选）+ ruff（代码质量/格式统一）
- 运维与平台
  - Vercel：前端托管（自动 HTTPS、CDN、预览部署、环境变量）
  - Railway：后端与数据库（自动构建、日志、环境变量、域名）
  - 监控：Sentry（前后端统一监控，选配）、Vercel Analytics（前端）

---

## 4. 仓库形态与目录结构

### 4.1 双仓（Polyrepo，默认推荐）

- 适用：前后端迭代节奏不同、独立发布、权限隔离清晰。
- 结构：
  - `frontend/`（单独仓库，Vercel 连接）
  - `backend/`（单独仓库，Railway 连接）

### 4.2 单仓（Monorepo）

- 适用：强耦合需求、共享类型/工具、一次性集成测试。
- 结构示例：

```
repo-root/
  frontend/             # React 应用（Vite/Next.js）
    src/
    public/
    index.html
    vite.config.ts
    package.json
  backend/              # FastAPI 服务
    app/
      api/
      core/
      models/
      schemas/
      services/
      main.py
    alembic/
    requirements.txt
    pyproject.toml (可选)
    Procfile / Dockerfile（其一）
  .github/workflows/    # CI/CD（可选）
  ARCHITECTURE.zh-CN.md # 本文档
```

---

## 5. 前端架构（React）

### 5.1 选型对比

- Vite + React（推荐）
  - 优点：轻量、构建快、适合纯前端 SPA 静态托管；Vercel 支持优秀。
  - 局限：无 SSR/SSG；SEO 依赖 CSR 策略与预渲染工具。
- Next.js（可选）
  - 优点：SSR/SSG、路由/Middleware、一体化优化；Vercel 原生支持最佳。
  - 局限：学习曲线更高；部署流程与约束更多。

### 5.2 目录建议（Vite）

```
frontend/
  src/
    api/             # API 封装（fetch/axios + React Query）
    components/      # 通用组件
    features/        # 业务模块（按领域分层）
    pages/           # 路由页面（react-router）
    hooks/           # 自定义 Hook
    stores/          # 状态（Zustand/Redux）
    utils/           # 工具函数
    main.tsx
  public/
  index.html
  vite.config.ts
  package.json
```

### 5.3 环境变量与 API 基址

- 本地：`VITE_API_URL=http://localhost:8000`（兼容 `VITE_API_BASE_URL`）
- 预览/生产（Vercel）：`VITE_API_URL=https://<railway-service>.up.railway.app`
- 使用示例：

```ts
// src/api/client.ts
const BASE_URL =
  import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL;
export async function get<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { ...init, credentials: "include" });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}
```

### 5.4 Vercel SPA 重写配置（Vite/React-Router）

```json
// frontend/vercel.json
{
  "version": 2,
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/$1" },
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
```

> 说明：若前端需要代理后端 API，建议直接使用环境变量拼接完整后端域名，避免 Vercel 代理跨域复杂度。

---

## 6. 后端架构（FastAPI）

### 6.1 目录建议

```
backend/
  app/
    api/             # 路由层（依赖注入、鉴权）
    core/            # 配置、日志、中间件、CORS、安全
    models/          # SQLAlchemy ORM 模型
    schemas/         # Pydantic 模型（请求/响应）
    services/        # 领域服务（业务逻辑）
    main.py          # 入口（create_app）
  alembic/           # 数据库迁移
  requirements.txt
  Procfile or Dockerfile
```

### 6.2 关键代码片段

```py
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="Example API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应精确到前端域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # TODO: include_router(...) 注册路由
    return app

app = create_app()
```

```py
# Procfile（不使用 Docker 时）
web: gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --workers 2
```

```dockerfile
# Dockerfile（可选：自带依赖与启动命令）
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY app ./app
CMD gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:${PORT:-8000} --workers 2
```

### 6.3 数据库与迁移

- Railway Postgres：在 Railway 控制台创建 Postgres，复制连接串到后端 `DATABASE_URL`。
- Alembic：

```ini
# alembic.ini（关键项）
sqlalchemy.url = ${DATABASE_URL}
```

```bash
alembic init alembic
alembic revision -m "init"
alembic upgrade head
```

---

## 7. API 契约与安全

- 认证：JWT（Access Token 短期 + Refresh Token）或基于 Cookie 的会话（SameSite/HttpOnly）。
- 版本：`/api/v1/...` 进行版本化，便于向前兼容。
- 错误：统一错误响应结构 `{ code, message, details? }`，后端使用异常处理器拦截。
- 安全：
  - CORS 精确到前端域名与方法；
  - 仅通过 HTTPS；
  - 秘钥使用平台环境变量管理（不写入仓库）；
  - 速率限制/防爬（可选：在 API 网关侧或应用中间件实现）。

### 7.1 健康检查规范

- 建议提供 JSON 健康检查端点：`GET /api/v1/health` 返回 `{ "status": "ok" }`；
- 为兼容历史脚本，保留 `GET /health`（纯文本）。

---

## 8. 环境与配置管理

### 8.1 关键环境变量

- 前端（Vercel）
  - `VITE_API_BASE_URL`：后端公开域名（Railway 服务 URL）。
  - `SENTRY_DSN`：可选监控。
- 后端（Railway）
  - `DATABASE_URL`：Postgres 连接串。
  - `SECRET_KEY`：JWT/会话秘钥。
  - `CORS_ORIGINS`：前端允许的来源（逗号分隔）。
  - `PORT`：Railway 注入，Gunicorn 绑定该端口。
  - `PYTHONUNBUFFERED=1`：确保 Python 日志实时输出（强烈推荐）。
  - `DEBUG`/`LOG_LEVEL`：调试与日志级别（可选）。
  - `STORAGE_PATH=/tmp/...`：如需文件上传/落盘，Railway 仅 `/tmp` 可写（可选）。

### 8.2 多环境

- 本地 `.env`（不提交）：`dotenv`/`pydantic-settings` 加载。
- Vercel/ Railway 分别配置 `Development/Preview/Production` 变量，实现预览环境联调。

---

## 9. 本地开发流程

- 前端
  - `npm i && npm run dev`
  - 指向本地后端：`VITE_API_BASE_URL=http://localhost:8000`
- 后端
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload --port 8000`
- 端到端联调：确保 CORS 允许本地前端地址（如 `http://localhost:5173`）。

---

## 10. 部署到 Vercel（前端）

1) 连接仓库：在 Vercel 导入 `frontend` 仓库或 Monorepo 的 `frontend/` 子目录。
2) 构建设置（两种方式其一）：
   - 项目设置（推荐）：
     - Framework Preset: `Vite`
     - Build Command: `cd frontend && npm install && npm run build`
     - Output Directory: `frontend/dist`
     - Install Command（可选）: `npm --prefix=frontend install`
   - 使用默认工作目录为 `frontend/` 时：
     - Build Command: `npm run build`
     - Output Dir: `dist`
3) 环境变量：在 Vercel 的 Project Settings 中设置 `VITE_API_BASE_URL` 等；预览/生产区分。
4) 路由：若是 SPA，提供 `vercel.json` 重写到 `index.html`。
5) 自定义域名：按需绑定域名，开启强制 HTTPS。

提示：也可在 `vercel.json` 中添加 SPA 重写；如配置响应头（如 CORS）仅作用于前端静态资源，不会替代后端的跨域配置。

---

## 11. 部署到 Railway（后端）

1) 连接仓库：在 Railway 新建服务并绑定 `backend` 仓库或 Monorepo `backend/` 路径。
2) 启动命令：
   - 非 Docker（方式一，使用本仓库 `backend/Procfile`）：在 Railway Dashboard 指定 Start Command：
     - `cd backend && pip install -r requirements.txt && gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --workers 2`
   - 非 Docker（方式二，根目录提供 `Procfile`）：`web: cd backend && gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --workers 2`
   - Docker：提供 `backend/Dockerfile`，Railway 将使用 Docker 构建与启动。
3) 环境变量：配置 `DATABASE_URL/SECRET_KEY/CORS_ORIGINS` 等；`PORT` 由平台注入。
4) 数据库：Railway 控制台创建 Postgres，并将连接串粘贴至 `DATABASE_URL`；首次迁移后 `alembic upgrade head`。
5) 域名：使用 Railway 分配的 `<service>.up.railway.app`，或绑定自定义域名。

常见陷阱：
- `crashed` 但无日志：多为 `Procfile` 编码/BOM 或启动命令错误；优先在 Dashboard 显式指定 Start Command；
- 端口冲突：始终使用 `$PORT` 环境变量，不要写死 8000；
- 无法写文件：Railway 仅 `/tmp` 可写，生产建议改为对象存储；
- 日志不滚动：设置 `PYTHONUNBUFFERED=1`。

---

## 12. CI/CD（可选）

- GitHub Actions（Monorepo 示例，已内置）：
  - `frontend-ci.yml`：对 `frontend/**` 变更执行类型检查与构建；当分支为 `main` 且配置了 `VERCEL_DEPLOY_HOOK_URL`（GitHub Secrets）时，自动触发 Vercel 生产部署。
  - `backend-ci.yml`：对 `backend/**` 变更执行依赖安装、语法检查与字节码编译；当分支为 `main` 且配置了 `RAILWAY_TOKEN`（及可选 `RAILWAY_PROJECT_ID`、`RAILWAY_ENV_ID`、`RAILWAY_SERVICE`）时，调用 Railway CLI 进行部署。
- 变量与密钥：
  - `VERCEL_DEPLOY_HOOK_URL`：在 Vercel 项目 → Settings → Deploy Hooks 创建 Production Hook，复制 URL 至 GitHub Secrets。
  - `RAILWAY_TOKEN`：在 Railway 生成 Account Token，存入 GitHub Secrets；如需指定项目/环境/服务，追加 `RAILWAY_PROJECT_ID`、`RAILWAY_ENV_ID`、`RAILWAY_SERVICE`。
- 分流触发：工作流已按路径过滤（`frontend/**`、`backend/**`）。

---

## 13. 监控、日志与可观测性

- 前端：Vercel Analytics、Sentry（Source Maps 上传）、性能指标（LCP/CLS/FID）。
- 后端：Railway 日志（构建/运行）、Sentry Python SDK、结构化日志（JSON 格式，便于检索）。
- 指标：可选接入 OpenTelemetry（Tracing/Logs/Metrics）到供应商（如 Grafana Cloud）。

---

## 14. 安全与合规最佳实践

- 秘钥与凭证：全部使用平台环境变量，禁止提交至仓库。
- CORS：生产环境精确到前端域名与必要方法头；预览环境可通过通配策略放宽。
- 认证：JWT 设置合理过期；刷新令牌与登出机制；敏感接口务必鉴权与鉴权中间件。
- 依赖：启用 Dependabot/Snyk；定期升级依赖；锁定版本（`package-lock.json`/`poetry.lock`）。
- 输入验证：Pydantic 模型校验；后端异常统一处理。

---

## 15. 性能优化

- 前端
  - 按需加载、代码分割（Route-level Split）、减少关键路径资源；
  - 静态资源缓存（CDN 长缓存 + 文件指纹）；
  - 图片优化（适配 Vercel Images 或第三方）；
  - 数据缓存：React Query 缓存策略与预取。
- 后端
  - Gunicorn 进程数：`workers = CPU * 2 + 1`（按实例核数微调）；
  - 数据库索引与慢查询分析；
  - 连接池配置（SQLAlchemy engine pool_size/max_overflow）；
  - 缓存层（可选 Redis）与异步任务队列（Celery/RQ/APScheduler）。

---

## 16. 常见问题（FAQ）

- 前端 404 刷新问题（SPA）：确保 `vercel.json` 将任意路由重写到 `index.html`。
- 跨域：确认后端 CORS `allow_origins` 包含前端域名；或使用精确通配并限制方法与头。
- 预览环境：Vercel Preview 与 Railway Preview 域名不同，前端 `VITE_API_BASE_URL` 请在 Preview 环境中配置对应后端 URL。
- 端口：Railway 使用 `PORT` 环境变量；不要在生产写死 8000。

---

## 17. 路线图与扩展

- 切换 Next.js：需要 SSR/SSG/Edge Middleware 或 SEO 强需求时。
- 多服务：按领域划分后端微服务或模块化单体；在 Railway 建立多服务并通过 API 网关聚合。
- WebSocket：使用 FastAPI WebSocket + 前端 `ws(s)` 客户端；在平台上开启对 WebSocket 的支持。
- 文件存储：迁移到对象存储（S3 兼容）；签名 URL 下载与上传直传。

---

## 18. 附录：关键示例文件

```json
// frontend/vercel.json（SPA）
{
  "version": 2,
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/$1" },
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
```

```json
// frontend/package.json（Vite 示例）
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

```txt
# backend/requirements.txt
fastapi
uvicorn[standard]
gunicorn
sqlalchemy
psycopg[binary]
pydantic
alembic
python-jose[cryptography]
passlib[bcrypt]
python-dotenv
```

```procfile
# backend/Procfile（非 Docker）
web: gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --workers 2
```

```dockerfile
# backend/Dockerfile（Docker 部署）
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY app ./app
EXPOSE 8000
CMD gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:${PORT:-8000} --workers 2
```

```env
# backend/.env（本地示例，不提交）
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/app
SECRET_KEY=please-change-me
CORS_ORIGINS=http://localhost:5173
```

---

## 19. 验收清单（Checklist）

- [ ] Vercel 前端部署成功，预览/生产域名可访问
- [ ] Railway 后端部署成功，健康检查通过
- [ ] 前端环境变量 `VITE_API_BASE_URL` 指向后端域名
- [ ] CORS 配置允许前端域名
- [ ] 数据库迁移执行成功（`alembic upgrade head`）
- [ ] 日志与监控接入（至少平台日志可用）
- [ ] CI 在 PR 运行基础检查（lint/test/build）

---

## 20. 备注

如需我为该项目仓库生成最小可运行脚手架（前端 Vite + 后端 FastAPI + Railway/Vercel 配置），请告知采用「单仓/双仓」偏好与包管理器（npm/pnpm/yarn），我可在当前仓库中直接补齐示例代码、配置与脚本。
