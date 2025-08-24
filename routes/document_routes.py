from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from models.document_models import GenerateDocumentRequest, GenerateDocumentResponse
from services.document_service import DocumentService
from routes.auth_routes import get_current_user
import os
from pathlib import Path
from datetime import datetime, timedelta

router = APIRouter()

def cleanup_old_files():
    """Delete files older than 24 hours"""
    docs_dir = Path("docs")
    if not docs_dir.exists():
        return
    
    cutoff_time = datetime.now() - timedelta(hours=24)
    deleted_count = 0
    
    for file_path in docs_dir.iterdir():
        if file_path.is_file():
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_time < cutoff_time:
                try:
                    file_path.unlink()  # Delete file
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    
    if deleted_count > 0:
        print(f"Cleaned up {deleted_count} old files from docs directory")

@router.post("/generate-docs", response_model=GenerateDocumentResponse)
async def generate_documentation(
    request: GenerateDocumentRequest, 
    token_data: dict = Depends(get_current_user)
):
    # Clean up old files before generating new ones
    cleanup_old_files()
    
    service = DocumentService(token_data["openai_api_key"], token_data["user_id"])
    result = await service.generate_documentation(
        topic=request.topic,
        urls=request.urls,
        output_format=request.output_format
    )
    
    return GenerateDocumentResponse(
        success=result["success"],
        result=result.get("result"),
        error=result.get("error"),
        user_id=result["user_id"],
        needs_authentication=result.get("needs_oauth", False),
        oauth_url=result.get("oauth_url"),
        needs_input=result.get("needs_input", False),
        file_path=result.get("file_path")
    )

@router.get("/download-docs/{filename}")
async def download_documentation(
    filename: str,
    token_data: dict = Depends(get_current_user)
):
    file_path = Path("docs") / filename
    
    if not file_path.exists():
        return {"error": "File not found or expired"}
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
    )

@router.post("/cleanup-docs")
async def manual_cleanup(token_data: dict = Depends(get_current_user)):
    """Manual cleanup endpoint for testing/admin use"""
    cleanup_old_files()
    return {"message": "Cleanup completed"}