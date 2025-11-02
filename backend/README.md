# FastAPI 最小可运行示例

## 本地运行

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export CORS_ORIGINS=http://localhost:5173
uvicorn app.main:app --reload --port 8000
```

## Railway 部署

- 已提供 `Procfile`（非 Docker）与 `Dockerfile`（Docker 模式二选一）。
- 绑定仓库后，设置环境变量（可选）：
  - `CORS_ORIGINS=https://<your-vercel-domain>`
  - `PYTHONUNBUFFERED=1`（实时日志推荐）
  - `STORAGE_PATH=/tmp/your-app`（如需落盘上传文件）
- Railway 会注入 `PORT`，无需手动设置。

### 启动命令建议

若链接的是仓库根目录，推荐在 Railway 的 Start Command 中显式切换目录并安装依赖：

```bash
cd backend && pip install -r requirements.txt && gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --workers 2
```

如果你在仓库根目录放置 `Procfile`，也可以写成：

```
web: cd backend && gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --workers 2
```

注意：`/tmp` 目录可写，其他路径不保证持久；生产建议迁移到对象存储或挂载 Volume。
