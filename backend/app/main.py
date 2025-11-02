import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title="Example API", version="1.0.0")

    cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    if not cors_origins:
        cors_origins = ["*"]  # 生产建议配置为前端域名，避免通配

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> str:
        # 兼容旧健康检查（纯文本）
        return "ok"

    @app.get("/api/v1/health")
    def api_health():
        return {"status": "ok", "service": "example-api"}

    @app.get("/api/v1/hello")
    def hello(name: str = "world"):
        return {"message": f"Hello, {name}!"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
