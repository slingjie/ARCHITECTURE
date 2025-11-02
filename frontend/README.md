# React + Vite 最小可运行示例

## 本地运行（npm）

```bash
cd frontend
npm install
cp .env.example .env  # 可选，或自行设置 VITE_API_URL（兼容 VITE_API_BASE_URL）
npm run dev
```

## Vercel 部署

- 直接在 Vercel 导入 `frontend/` 目录。
- 构建：`npm run build`，输出目录：`dist`。
- 环境变量：`VITE_API_URL=https://<your-railway-app>.up.railway.app`（兼容 `VITE_API_BASE_URL`）。
- SPA 刷新 404：已提供 `vercel.json` 将所有路由重写到 `index.html`。
