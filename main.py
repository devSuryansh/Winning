from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, gmail_routes, docs_routes

app = FastAPI(
    title="Portia AI Backend",
    description="JWT-based Portia AI services with Gmail and Google Docs integration",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(gmail_routes.router, prefix="/api/gmail", tags=["gmail"])
app.include_router(docs_routes.router, prefix="/api/docs", tags=["google_docs"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "portia-backend"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
