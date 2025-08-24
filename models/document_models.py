from pydantic import BaseModel
from typing import Optional, List

class GenerateDocumentRequest(BaseModel):
    topic: str
    urls: Optional[List[str]] = None
    output_format: str = "pdf"

class GenerateDocumentResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    user_id: str
    service: str = "document_generator"
    action: str = "generate_documentation"
    needs_authentication: bool = False
    oauth_url: Optional[str] = None
    needs_input: bool = False
    file_path: Optional[str] = None