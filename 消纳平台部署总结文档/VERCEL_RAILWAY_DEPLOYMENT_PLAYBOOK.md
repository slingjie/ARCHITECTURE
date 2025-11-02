# Vercel + Railway 全链路部署作战手册

> 更新时间：2025-11-02  
> 适用对象：负责光伏电站消纳计算平台部署、运维与故障处理的工程师

---

## 1. 手册目标与适用范围

- 明确「Vercel 前端 + Railway 后端」的生产级部署架构与职责划分
- 提供从准备、部署、联调到运维的完整流程与操作要点
- 收敛常见问题的根因排查路径与解决手段，确保可以快速恢复服务
- 帮助团队成员在没有额外背景的情况下独立完成部署与运维

本手册基于仓库既有文档（`DEPLOYMENT_COMPLETE.md`、`VERCEL_RAILWAY_DEPLOYMENT.md`、`RAILWAY_*` 系列等）与核心配置文件（`vercel.json`、`Procfile`、`backend/app/core/config.py`）整理而成，信息全面覆盖且去重整合。

---

## 2. 总体架构与职责划分

```
┌──────────────────────────────────────────┐
│                终端用户浏览器             │
└───────────────┬─────────────────────────┘
                │HTTPS
        ┌───────▼────────┐
        │ Vercel (前端)   │ 静态产物 + CDN 加速
        │ - Vite 构建     │ 负责 UI、路由、静态资源
        │ - React/TS      │ 引用环境变量调用后端
        └───────┬────────┘
                │REST API
        ┌───────▼────────┐
        │ Railway (后端)  │ 持续运行的 FastAPI 服务
        │ - Python 3.11   │ 搭载业务逻辑、调度算法
        │ - SQLite/MySQL  │ 管理数据与文件读写
        │ - /tmp 持久化   │ 临时存储上传文件
        └───────┬────────┘
                │内部依赖
        ┌───────▼────────┐
        │ SQLite/未来云库 │ 数据持久层（可拓展至 PG）
        └────────────────┘
```

### 核心原则

- **前端即静态站点**：`vercel.json` 明确仅构建 `frontend`，通过 `rewrites` 将所有路由回落到 `index.html`。
- **后端常驻服务**：`Procfile` 指定 Uvicorn 常驻进程，Railway 负责生命周期与水平扩展。
- **API 通过环境变量耦合**：前端读取 `VITE_API_URL`，后端通过 `CORS_ORIGINS`、`ALLOWED_ORIGINS` 控制跨域。
- **GitHub 作为事实来源**：对 `feature/...` 或 `main` 分支的推送自动触发 Vercel/Railway 的 CI/CD。

---

## 3. 全流程快照

1. **准备阶段**
   - 完成账号注册：GitHub、Vercel、Railway。
   - 确认代码仓库最新，确保 `vercel.json`、`Procfile` 等配置有效。
2. **Vercel 构建前端**
   - 仪表盘导入仓库或使用 CLI 部署。
   - 核验 `buildCommand`、`outputDirectory`、`framework` 三大参数。
3. **Railway 构建后端**
   - 通过 GitHub Repo 自动部署。
   - 设置环境变量、构建/启动命令。
4. **前后端联通**
   - 在 Vercel 设置 `VITE_API_URL`。
   - 在 Railway 设置 `CORS_ORIGINS`/`ALLOWED_ORIGINS`。
   - 使用 `/api/v1/health` 验证链接。
5. **运维与优化**
   - 监控日志、构建历史、资源开销。
   - 根据业务量扩容数据库/存储，并建立备份策略。

---

## 4. 部署前准备

### 4.1 账号与权限
- **GitHub**：具备仓库 `slingjie/xiaonajisuan` 的读写权限。
- **Vercel**：已绑定 GitHub，具备项目创建与环境变量管理权限。
- **Railway**：已绑定 GitHub，具备服务创建、变量编辑、日志查看权限。

### 4.2 代码准备
- 默认分支：`feature/work-mode-adjustment`（可切换到主分支）。
- 关键文件：
  - 前端配置：`vercel.json`
  - 后端启动：`Procfile`
  - 后端配置：`backend/app/core/config.py`
- 确认所有改动已经 `git push`，以触发云端构建。

### 4.3 本地验证（可选但推荐）

```bash
# 前端本地打包
cd frontend
npm install
npm run build

# 后端本地启动
cd ../backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/api/v1/health  # 期望 {"status": "ok"}
```

### 4.4 GitHub Webhook 检查
- 确认 Vercel 与 Railway 均已在项目设置中启用自动构建（首次导入后自动开启）。
- 若需暂停自动部署，可在各平台手动关闭 Auto Deploy。

---

## 5. Vercel 前端部署指引

### 5.1 运行时定位
- 静态站点：React + Vite 编译结果（`frontend/dist`）。
- 服务方式：CDN + Edge Network，自动提供 HTTPS。
- 构建配置（来自 `vercel.json`）：
  ```json
  {
    "buildCommand": "cd frontend && npm install && npm run build",
    "outputDirectory": "frontend/dist",
    "framework": "vite",
    "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
    "headers": [{
      "source": "/(.*)",
      "headers": [
        {"key": "Access-Control-Allow-Origin", "value": "*"},
        {"key": "Access-Control-Allow-Methods", "value": "GET,POST,PUT,DELETE,OPTIONS"},
        {"key": "Access-Control-Allow-Headers", "value": "Content-Type,Authorization"}
      ]
    }]
  }
  ```
  - `rewrites` 确保前端路由回退到单页应用。
  - `headers` 解决基本 CORS 预检需求（后端仍需验证域名白名单）。

### 5.2 Dashboard 部署流程（推荐）
1. 访问 <https://vercel.com/new> 并登录。
2. 选择 **Import Git Repository** → 指向对应仓库。
3. 配置参数：
   - Framework Preset: `Vite`
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
   - Install Command（可选）: `npm --prefix=frontend install`
4. 部署完成后记录生产域名，例如 `https://xiaonajisuan.vercel.app`。

### 5.3 CLI 部署流程（可选）

```bash
npm i -g vercel
vercel login
cd /Users/shilingjie/Desktop/ai/1017光伏电站消纳计算平台
vercel --prod         # 根据提示确认项目、分支、环境变量
```

### 5.4 环境变量管理
- 前端依赖的关键变量：`VITE_API_URL`（后端 API 根地址）。
- 其他变量（可选）：可按需设置 `VITE_SENTRY_DSN` 等。
- 操作路径：Project → Settings → Environment Variables → `Add New`。

### 5.5 部署验证
- 访问部署域名，检查页面是否加载。
- 浏览器控制台执行：
  ```javascript
  fetch(`${window.origin}/health-check-proxy`, { method: "HEAD" }) // 自定义测试
  ```
- 如启用了 `VITE_API_URL`，执行：
  ```javascript
  fetch(import.meta.env.VITE_API_URL + "/api/v1/health")
    .then(r => r.json())
    .then(console.log)
    .catch(console.error);
  ```

### 5.6 运维与回滚
- 查看日志：Dashboard → Deployments → 选中实例 → View Build Logs。
- 回滚部署：在 Deployments 列表中对旧版本执行 **Promote to Production**。
- 本地复现生产构建：
  ```bash
  npm i -g vercel
  vercel build
  vercel start
  ```

### 5.7 常见问题与修复

| 问题 | 症状 | 修复步骤 |
|------|------|----------|
| 构建失败 | Build Logs 报错，产物缺失 | 核对 `vercel.json` 命令；确保 `frontend/package.json` 依赖正确；必要时先 `npm install --legacy-peer-deps` |
| 访问 404 | 页面空白或 404 | 确认 `rewrites` 生效，产物目录为 `frontend/dist` |
| CORS 错误 | 控制台出现 CORS 报错 | 在 Railway 配置 `CORS_ORIGINS`；更新后端 `allowed_origins`（见 `backend/app/core/config.py`）；再次部署 |
| 后端请求失败 | API 返回 404 或 5xx | 检查 `VITE_API_URL` 是否指向正确的 Railway URL；手动 `fetch` 验证 |
| 文件上传失败 | 前端提示上传失败 | 确认后端 `STORAGE_PATH` 配置为 `/tmp/pv_storage` 或云存储 |

---

## 6. Railway 后端部署指引

### 6.1 运行时定位
- 框架：FastAPI + Uvicorn。
- Python：建议 3.11；Railway 会基于 `Procfile` 推断运行时。
- 启动命令（`Procfile`）：
  ```
  web: cd backend && /app/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
  - `/app/.venv/bin/python` 为 Railway 默认虚拟环境。
  - 若需切换，可改为 `python -m uvicorn ...` 并在 Build Command 安装依赖。

### 6.2 环境变量（必填）

| 变量名 | 示例值 | 说明 |
|--------|--------|------|
| `DATABASE_URL` | `sqlite:///./pv_consumption.db` | 默认 SQLite，可切换为云数据库 |
| `DEBUG` | `false` | 控制调试模式 |
| `LOG_LEVEL` | `INFO` | 日志等级 |
| `STORAGE_PATH` | `/tmp/pv_storage` | 文件上传落盘目录，Railway 上仅 `/tmp` 可写 |
| `PYTHONUNBUFFERED` | `1` | 确保日志实时输出 |
| `CORS_ORIGINS` | `https://xiaonajisuan.vercel.app` | 允许访问的前端域名，多个以逗号分隔 |
| `ALLOWED_ORIGINS` | `["https://example.com"]` | 可选；JSON 数组形式，后端会自动合入 |

### 6.3 部署流程（Dashboard）
1. 访问 <https://railway.app> → Start New Project。
2. 选择 **Deploy from GitHub** → 绑定仓库与分支。
3. Build & Start 配置：
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - 如依赖 Procfile，可将 Start Command 留空，Railway 自动读取。
4. 添加环境变量（详见上表）。
5. 触发部署并等待状态变为 **Active**。
6. 记录服务 URL，例如 `https://xiaonajisuan-backend-prod-xxx.railway.app`。

### 6.4 日志与重新部署
- 仪表盘查看：Service → Deployments → View Logs。
- CLI（建议）：
  ```bash
  npm i -g @railway/cli
  railway login
  cd /Users/shilingjie/Desktop/ai/1017光伏电站消纳计算平台
  railway link
  railway logs --tail 100
  ```
- 强制重新部署：Dashboard → Redeploy / Re-trigger Build；或 CLI `railway redeploy`。

### 6.5 常见故障诊断

| 现象 | 典型日志 | 排查路径 | 解决方案 |
|------|----------|----------|----------|
| 状态显示 `crashed` 且无日志 | - | Procfile 不生效或启动命令错误 | 确认 `Procfile` 无 BOM/空行；必要时改用 Dashboard Start Command |
| `ModuleNotFoundError` | `No module named app` | 依赖或工作目录错误 | Build Command 指向 `backend/requirements.txt`；Start Command 中 `cd backend` |
| `Address already in use` | - | 固定端口冲突 | 使用 `$PORT` 环境变量而非写死端口 |
| 日志停在 `Killed` / 无错误 | - | 内存不足或初始化超时 | 减少启动开销；升级服务规格 |
| 无法访问静态文件/上传失败 | - | 文件写入路径错误 | 确认 `STORAGE_PATH=/tmp/pv_storage`，并在 `backend/app/core/config.py` 创建目录 |

### 6.6 运行后验证

```bash
# 健康检查
curl https://<railway-url>/api/v1/health

# 业务检测，示例
curl -X POST https://<railway-url>/api/v1/calculation \
  -H "Content-Type: application/json" \
  -d '{"task_id": "smoke-test"}'
```

### 6.7 扩展建议
- 升级数据库：Railway 内置 PostgreSQL，可在 Project → Add Plugin → PostgreSQL 进行绑定，并更新 `DATABASE_URL`。
- 文件持久化：为避免 `/tmp` 清空，可挂载 Railway Volume 或迁移至 S3/OSS。
- Python 版本固定：在仓库根添加 `.python-version` 或 `.tool-versions` 保障一致性。

---

## 7. 前后端联调与配置要点

1. **前端环境变量**
   - `VITE_API_URL` 指向 Railway 公网地址，必须以 `https://` 开头。
   - 变更后需在 Vercel 重新部署（自动触发）。
2. **后端跨域配置**
   - `CORS_ORIGINS` / `ALLOWED_ORIGINS` 中添加 Vercel 域名。
   - 后端 `backend/app/core/config.py` 会自动合并 `VERCEL_URL`、`CORS_ORIGINS`、`ALLOWED_ORIGINS`。
3. **健康检查**
   - 推荐统一使用 `/api/v1/health`。
   - 前端调试可在浏览器控制台执行：
     ```javascript
     fetch(import.meta.env.VITE_API_URL + "/api/v1/health")
       .then(r => r.json())
       .then(d => console.log("后端状态", d))
       .catch(console.error);
     ```
4. **流水线联动**
   - 推送到 GitHub → Vercel/VRailway 自动构建。
   - 对于重要变更，建议串行发布：先部署后端，确认健康，再更新前端地址。

---

## 8. 运维、优化与安全

### 8.1 环境管理
- 所有敏感信息写入平台环境变量，不直接提交 `.env`。
- 定期备份 Vercel/Railway 环境变量配置（导出 JSON 或记录于安全仓库）。
- 对生产使用单独环境（如 Vercel Production / Railway prod），避免测试污染。

### 8.2 性能与成本
- **Vercel**：Hobby 计划免费，需关注函数调用上限；长耗时任务建议迁移到后端。
- **Railway**：每日使用计算在 $5 额度内；若长期运行，建议绑定支付方式或迁移至 Render 等替代方案。
- **后端超时**：对重计算任务，可引入后台队列或异步任务（如 Celery + Redis）。

### 8.3 监控与告警
- Vercel：Deployments 日志 + Analytics；可集成 Sentry。
- Railway：Logs、Metrics（CPU、内存、请求数）；必要时接入外部监控（Prometheus/LogDNA）。
- 建议新增 `/api/v1/health` 扩展字段（如依赖状态），便于巡检。

### 8.4 数据与存储策略
- SQLite 仅适合轻量使用；生产建议迁移到 PostgreSQL（如 Vercel + Neon、Railway PG）。
- 上传文件存储到 `/tmp/pv_storage`，需定期清理或迁移到对象存储。
- 若引入云数据库，更新 `DATABASE_URL` 并在部署前验证迁移脚本。

### 8.5 安全加固
- 限制跨域来源，避免使用通配 `*`；生产环境建议精确列出域名。
- 使用 HTTPS，杜绝明文 HTTP。
- 后端如需鉴权，可扩展 JWT/Token 校验，并在前端配置 Authorization 头。

---

## 9. 部署检查清单（打印张贴）

| 阶段 | 检查项 | 结果 |
|------|--------|------|
| 前期准备 | GitHub 代码已推送至主分支或指定分支 | ☐ |
|        | `vercel.json`、`Procfile` 内容确认无误 | ☐ |
| Vercel 部署 | Dashboard 导入仓库成功 | ☐ |
|        | Build 命令执行通过，产物目录存在 | ☐ |
|        | 访问 Vercel 域名页面加载正常 | ☐ |
| Railway 部署 | 环境变量全部填写且无手误 | ☐ |
|        | Build/Start 命令执行成功，状态为 Active | ☐ |
| 联调 | `/api/v1/health` 返回 `{"status":"ok"}` | ☐ |
|        | 前端调用后端接口无跨域/404 | ☐ |
| 运维 | 日志无异常、资源使用稳定 | ☐ |
|        | 关键 URL、变量、账号已归档 | ☐ |

---

## 10. 常用命令速查

| 场景 | 命令 |
|------|------|
| 查看 Vercel 最新部署 | `vercel ls` / Dashboard → Deployments |
| 本地模拟 Vercel 产物 | `vercel build && vercel start` |
| 安装/更新 Railway CLI | `npm i -g @railway/cli` |
| 查看 Railway 实时日志 | `railway logs --tail 100` |
| 手动重新部署 Railway | Dashboard → Redeploy / `railway redeploy` |
| 后端本地健康检查 | `curl http://localhost:8000/api/v1/health` |
| 核验 Procfile | `cat Procfile` |
| 检索部署文档 | `rg "部署" -g"*.md"` |

---

## 11. 常见问题 FAQ

1. **Vercel 构建提示 `Function Runtimes` 错误?**  
   - 已通过纯前端部署规避；若再次出现，确认未向 Vercel 部署 Python Serverless。

2. **Railway 显示 `crashed` 但无日志?**  
   - 多为 Procfile 解析失败或启动命令异常。清理空行/BOM，或直接在 Dashboard 指定 Start Command。

3. **前端调用后端返回 404?**  
   - 检查 `VITE_API_URL` 是否带尾 `/`、域名是否复制完整；确认 Railway 服务已 Active。

4. **文件上传体积大导致失败?**  
   - Railway `/tmp` 空间有限；建议在前端限制大小，同时在后端接入云对象存储。

5. **如何回滚到上一版本?**  
   - Vercel：Deployments → 选中旧版本 → Promote。  
   - Railway：Deployments → 选中旧版本 → Rollback（或重新部署旧提交）。

---

## 12. 参考资料与扩展阅读

- 项目 README：`README.md`
- 快速部署指引：`QUICK_DEPLOY.md`
- 全量部署指南：`DEPLOYMENT_COMPLETE.md`
- 前后端联动详解：`VERCEL_RAILWAY_DEPLOYMENT.md`
- Railway 故障排查：`RAILWAY_CRASH_DIAGNOSIS.md`、`RAILWAY_PYTHON_ERROR_FIX.md`、`RAILWAY_QUICK_FIX.md`、`RAILWAY_REDEPLOY_STEPS.md`
- Vercel 配置参考：`VERCEL_DEPLOYMENT.md`、`VERCEL_ERROR_ANALYSIS.md`、`VERCEL_FULLSTACK_DEPLOYMENT.md`
- 核心配置文件：`vercel.json`、`Procfile`、`backend/app/core/config.py`
- 官方文档：  
  - Vercel Docs <https://vercel.com/docs>  
  - Railway Docs <https://docs.railway.app>  
  - FastAPI Deployment <https://fastapi.tiangolo.com/deployment/>

---

> 若需扩展或定制，请在本手册基础上更新对应章节，并同步至仓库根目录，确保团队共享最新最佳实践。
