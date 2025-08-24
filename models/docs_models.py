from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class CreateDocRequest(BaseModel):
    title: str
    description: str
    content_type: Optional[str] = (
        "general"  # general, technical, report, proposal, etc.
    )
    formatting_style: Optional[str] = "professional"  # professional, casual, academic
    include_toc: Optional[bool] = False  # table of contents
    include_sections: Optional[bool] = True
    target_length: Optional[str] = "medium"  # short, medium, long


class CreateDocResponse(BaseModel):
    success: bool
    doc_id: Optional[str] = None
    doc_url: Optional[str] = None
    doc_title: Optional[str] = None
    content_preview: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    user_id: str
    service: str = "google_docs"
    action: str = "create_document"
    needs_authentication: bool = False
    oauth_url: Optional[str] = None


class UpdateDocRequest(BaseModel):
    doc_id: str
    title: Optional[str] = None
    additional_content: Optional[str] = None
    instructions: str  # Instructions for what to update/modify


class UpdateDocResponse(BaseModel):
    success: bool
    doc_id: Optional[str] = None
    doc_url: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    user_id: str
    service: str = "google_docs"
    action: str = "update_document"
    needs_authentication: bool = False
    oauth_url: Optional[str] = None


class FormatDocRequest(BaseModel):
    doc_id: str
    formatting_instructions: (
        str  # e.g., "Add headers, bullet points, make it professional"
    )
    style: Optional[str] = "professional"


class FormatDocResponse(BaseModel):
    success: bool
    doc_id: Optional[str] = None
    doc_url: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    user_id: str
    service: str = "google_docs"
    action: str = "format_document"
    needs_authentication: bool = False
    oauth_url: Optional[str] = None


class DocTemplateRequest(BaseModel):
    template_type: str  # meeting_notes, project_proposal, report, resume, etc.
    title: str
    variables: Optional[Dict[str, Any]] = {}  # Template variables to fill in


class DocTemplateResponse(BaseModel):
    success: bool
    doc_id: Optional[str] = None
    doc_url: Optional[str] = None
    doc_title: Optional[str] = None
    template_used: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    user_id: str
    service: str = "google_docs"
    action: str = "create_from_template"
    needs_authentication: bool = False
    oauth_url: Optional[str] = None


class GenerateContentRequest(BaseModel):
    topic: str
    content_type: str  # blog_post, technical_doc, proposal, report, etc.
    key_points: Optional[List[str]] = []
    tone: Optional[str] = "professional"  # professional, casual, technical, creative
    length: Optional[str] = "medium"  # short, medium, long, detailed


class GenerateContentResponse(BaseModel):
    success: bool
    generated_content: Optional[str] = None
    content_outline: Optional[List[str]] = None
    word_count: Optional[int] = None
    result: Optional[str] = None
    error: Optional[str] = None
    user_id: str
    service: str = "content_generation"
    action: str = "generate_content"
