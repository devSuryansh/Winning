from fastapi import APIRouter, Depends, HTTPException, status
from models.docs_models import (
    CreateDocRequest,
    CreateDocResponse,
    UpdateDocRequest,
    UpdateDocResponse,
    FormatDocRequest,
    FormatDocResponse,
    DocTemplateRequest,
    DocTemplateResponse,
    GenerateContentRequest,
    GenerateContentResponse,
)
from services.docs_service import GoogleDocsService
from routes.auth_routes import get_current_user

router = APIRouter()


@router.post("/create-document", response_model=CreateDocResponse)
async def create_document(
    request: CreateDocRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a new Google Docs document with AI-generated content"""
    try:
        service = GoogleDocsService(
            openai_api_key=current_user["openai_api_key"],
            user_id=current_user["user_id"],
        )
        return await service.create_document(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document: {str(e)}",
        )


@router.post("/update-document", response_model=UpdateDocResponse)
async def update_document(
    request: UpdateDocRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update an existing Google Docs document"""
    try:
        service = GoogleDocsService(
            openai_api_key=current_user["openai_api_key"],
            user_id=current_user["user_id"],
        )
        return await service.update_document(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document: {str(e)}",
        )


@router.post("/format-document", response_model=FormatDocResponse)
async def format_document(
    request: FormatDocRequest,
    current_user: dict = Depends(get_current_user),
):
    """Apply formatting to an existing Google Docs document"""
    try:
        service = GoogleDocsService(
            openai_api_key=current_user["openai_api_key"],
            user_id=current_user["user_id"],
        )
        return await service.format_document(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to format document: {str(e)}",
        )


@router.post("/create-from-template", response_model=DocTemplateResponse)
async def create_from_template(
    request: DocTemplateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a document from a predefined template"""
    try:
        service = GoogleDocsService(
            openai_api_key=current_user["openai_api_key"],
            user_id=current_user["user_id"],
        )
        return await service.create_from_template(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document from template: {str(e)}",
        )


@router.post("/generate-content", response_model=GenerateContentResponse)
async def generate_content(
    request: GenerateContentRequest,
    current_user: dict = Depends(get_current_user),
):
    """Generate content for a document (without creating the actual Google Doc)"""
    try:
        service = GoogleDocsService(
            openai_api_key=current_user["openai_api_key"],
            user_id=current_user["user_id"],
        )
        return await service.generate_content(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {str(e)}",
        )


# Convenience endpoints for common operations


@router.post("/quick-create")
async def quick_create_document(
    title: str,
    description: str,
    content_type: str = "general",
    current_user: dict = Depends(get_current_user),
):
    """Quick endpoint to create a document with just title and description"""
    request = CreateDocRequest(
        title=title,
        description=description,
        content_type=content_type,
    )

    service = GoogleDocsService(
        openai_api_key=current_user["openai_api_key"],
        user_id=current_user["user_id"],
    )
    return await service.create_document(request)


@router.post("/quick-template")
async def quick_template_document(
    title: str,
    template_type: str,
    current_user: dict = Depends(get_current_user),
):
    """Quick endpoint to create a document from a template"""
    request = DocTemplateRequest(
        title=title,
        template_type=template_type,
    )

    service = GoogleDocsService(
        openai_api_key=current_user["openai_api_key"],
        user_id=current_user["user_id"],
    )
    return await service.create_from_template(request)


@router.get("/templates")
async def list_available_templates():
    """List all available document templates"""
    templates = {
        "business": [
            "business_plan",
            "project_proposal",
            "meeting_notes",
            "memo",
            "invoice",
            "contract",
        ],
        "personal": ["resume", "cover_letter", "personal_statement"],
        "academic": [
            "technical_report",
            "research_paper",
            "thesis_outline",
            "case_study",
        ],
        "creative": [
            "blog_post",
            "article",
            "creative_writing",
            "presentation_outline",
        ],
    }

    return {
        "success": True,
        "templates": templates,
        "total_templates": sum(len(category) for category in templates.values()),
    }


@router.get("/content-types")
async def list_content_types():
    """List all available content types for document generation"""
    content_types = {
        "business": [
            "business_plan",
            "marketing_strategy",
            "financial_report",
            "project_proposal",
            "meeting_minutes",
        ],
        "technical": [
            "technical_documentation",
            "api_documentation",
            "user_manual",
            "system_requirements",
            "architecture_design",
        ],
        "academic": [
            "research_paper",
            "literature_review",
            "thesis",
            "case_study",
            "lab_report",
        ],
        "creative": ["blog_post", "article", "story", "script", "social_media_content"],
        "general": [
            "general",
            "informational",
            "instructional",
            "promotional",
            "educational",
        ],
    }

    return {
        "success": True,
        "content_types": content_types,
        "total_types": sum(len(category) for category in content_types.values()),
    }
