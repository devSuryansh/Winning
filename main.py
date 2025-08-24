from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, gmail_routes, document_routes

app = FastAPI(
    title="Portia AI Backend",
    description="JWT-based Portia AI services with Gmail integration",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(gmail_routes.router, prefix="/api", tags=["gmail"])
app.include_router(document_routes.router, prefix="/api", tags=["documents"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "portia-backend"}

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)