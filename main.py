from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Portia AI Backend",
    description="API for Portia AI services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
# app.include_router(github_routes.router, prefix="/api/github", tags=["github"])
# app.include_router(gmail_routes.router, prefix="/api/gmail", tags=["gmail"])
# app.include_router(docs_routes.router, prefix="/api/docs", tags=["docs"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "portia-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)