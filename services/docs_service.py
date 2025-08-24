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
from services.portia_client import PortiaClient
import re
import json


class GoogleDocsService:
    def __init__(self, openai_api_key: str, user_id: str):
        self.client = PortiaClient(openai_api_key, user_id)

    def _extract_oauth_url(self, text: str) -> str:
        """Extract OAuth URL from response text"""
        url_patterns = [
            r"https://accounts\.google\.com/o/oauth2/v2/auth[^\s\)]+",
            r"https://accounts\.google\.com[^\s\)]+",
            r"https://docs\.google\.com[^\s\)]+",
        ]

        for pattern in url_patterns:
            url_match = re.search(pattern, text)
            if url_match:
                return url_match.group(0)
        return None

    def _needs_authentication(self, result_text: str) -> bool:
        """Check if the result indicates authentication is needed"""
        auth_indicators = [
            "oauth",
            "authentication",
            "authorize",
            "permission",
            "sign in",
            "login",
            "access denied",
            "clarification",
        ]
        return any(indicator in result_text.lower() for indicator in auth_indicators)

    def _extract_doc_info(self, result_text: str) -> dict:
        """Extract document ID and URL from result text"""
        doc_info = {"doc_id": None, "doc_url": None}

        # Extract Google Docs URL
        doc_url_pattern = r"https://docs\.google\.com/document/d/([a-zA-Z0-9-_]+)"
        url_match = re.search(doc_url_pattern, result_text)
        if url_match:
            doc_info["doc_url"] = url_match.group(0)
            doc_info["doc_id"] = url_match.group(1)

        # Alternative: Extract document ID
        if not doc_info["doc_id"]:
            doc_id_pattern = r"document.*id[:\s]+([a-zA-Z0-9-_]+)"
            id_match = re.search(doc_id_pattern, result_text, re.IGNORECASE)
            if id_match:
                doc_info["doc_id"] = id_match.group(1)

        return doc_info

    async def create_document(self, request: CreateDocRequest) -> CreateDocResponse:
        """Create a new Google Docs document with AI-generated content"""
        try:
            # Build the task prompt
            task = f"""
            Create a new Google Docs document with the following specifications:
            
            Title: {request.title}
            Description/Purpose: {request.description}
            Content Type: {request.content_type}
            Formatting Style: {request.formatting_style}
            Target Length: {request.target_length}
            Include Table of Contents: {request.include_toc}
            Include Sections: {request.include_sections}
            
            Please:
            1. Create a new Google Docs document with the specified title
            2. Generate comprehensive, well-structured content based on the description
            3. Apply appropriate formatting ({request.formatting_style} style)
            4. {"Include a table of contents at the beginning" if request.include_toc else ""}
            5. {"Structure the content with clear sections and headers" if request.include_sections else ""}
            6. Make the content {request.target_length} length and engaging
            7. Ensure the content is relevant to the topic: {request.description}
            
            The document should be professional, well-formatted, and ready for use.
            Return the document URL and ID when created.
            """

            result = await self.client.run_task(task)
            result_text = str(result.get("result", ""))

            # Check for authentication needs
            needs_auth = self._needs_authentication(result_text)
            oauth_url = None
            if needs_auth:
                oauth_url = self._extract_oauth_url(result_text)
                if not oauth_url and result.get("error"):
                    oauth_url = self._extract_oauth_url(str(result.get("error", "")))

            # Extract document information
            doc_info = self._extract_doc_info(result_text)

            # Extract content preview (first 200 characters)
            content_preview = None
            if result.get("success") and result_text:
                # Try to extract actual content from the result
                lines = result_text.split("\n")
                content_lines = [
                    line.strip()
                    for line in lines
                    if line.strip() and not line.startswith("http")
                ]
                if content_lines:
                    content_preview = (
                        " ".join(content_lines)[:200] + "..."
                        if len(" ".join(content_lines)) > 200
                        else " ".join(content_lines)
                    )

            return CreateDocResponse(
                success=result.get("success", False),
                doc_id=doc_info["doc_id"],
                doc_url=doc_info["doc_url"],
                doc_title=request.title,
                content_preview=content_preview,
                result=result_text,
                error=result.get("error"),
                user_id=self.client.user_id,
                needs_authentication=needs_auth,
                oauth_url=oauth_url,
            )

        except Exception as e:
            return CreateDocResponse(
                success=False,
                error=str(e),
                user_id=self.client.user_id,
            )

    async def update_document(self, request: UpdateDocRequest) -> UpdateDocResponse:
        """Update an existing Google Docs document"""
        try:
            task = f"""
            Update the Google Docs document with ID: {request.doc_id}
            
            Instructions: {request.instructions}
            
            {f"New Title: {request.title}" if request.title else ""}
            {f"Additional Content to Add: {request.additional_content}" if request.additional_content else ""}
            
            Please:
            1. Open the existing document
            2. Apply the requested changes/updates
            3. Maintain the existing formatting style
            4. Ensure the updates are well-integrated with existing content
            5. Save the changes
            
            Return confirmation of the updates made.
            """

            result = await self.client.run_task(task)
            result_text = str(result.get("result", ""))

            needs_auth = self._needs_authentication(result_text)
            oauth_url = None
            if needs_auth:
                oauth_url = self._extract_oauth_url(result_text)

            doc_info = self._extract_doc_info(result_text)

            return UpdateDocResponse(
                success=result.get("success", False),
                doc_id=request.doc_id,
                doc_url=doc_info["doc_url"]
                or f"https://docs.google.com/document/d/{request.doc_id}",
                result=result_text,
                error=result.get("error"),
                user_id=self.client.user_id,
                needs_authentication=needs_auth,
                oauth_url=oauth_url,
            )

        except Exception as e:
            return UpdateDocResponse(
                success=False,
                error=str(e),
                user_id=self.client.user_id,
            )

    async def format_document(self, request: FormatDocRequest) -> FormatDocResponse:
        """Apply formatting to an existing Google Docs document"""
        try:
            task = f"""
            Format the Google Docs document with ID: {request.doc_id}
            
            Formatting Instructions: {request.formatting_instructions}
            Style: {request.style}
            
            Please:
            1. Open the existing document
            2. Apply the requested formatting changes
            3. Use {request.style} styling throughout
            4. Ensure consistent formatting and professional appearance
            5. Maintain content while improving presentation
            6. Save the formatting changes
            
            Focus on making the document visually appealing and well-structured.
            """

            result = await self.client.run_task(task)
            result_text = str(result.get("result", ""))

            needs_auth = self._needs_authentication(result_text)
            oauth_url = None
            if needs_auth:
                oauth_url = self._extract_oauth_url(result_text)

            doc_info = self._extract_doc_info(result_text)

            return FormatDocResponse(
                success=result.get("success", False),
                doc_id=request.doc_id,
                doc_url=doc_info["doc_url"]
                or f"https://docs.google.com/document/d/{request.doc_id}",
                result=result_text,
                error=result.get("error"),
                user_id=self.client.user_id,
                needs_authentication=needs_auth,
                oauth_url=oauth_url,
            )

        except Exception as e:
            return FormatDocResponse(
                success=False,
                error=str(e),
                user_id=self.client.user_id,
            )

    async def create_from_template(
        self, request: DocTemplateRequest
    ) -> DocTemplateResponse:
        """Create a document from a predefined template"""
        try:
            # Convert variables to a formatted string
            variables_text = ""
            if request.variables:
                variables_text = "\n".join(
                    [f"{key}: {value}" for key, value in request.variables.items()]
                )

            task = f"""
            Create a new Google Docs document using the {request.template_type} template.
            
            Document Title: {request.title}
            Template Type: {request.template_type}
            
            Template Variables:
            {variables_text}
            
            Please:
            1. Create a new Google Docs document with the specified title
            2. Use the {request.template_type} template structure
            3. Fill in the template with the provided variables
            4. Apply appropriate formatting for this type of document
            5. Include all necessary sections for a {request.template_type}
            6. Make it professional and complete
            
            Template types available: meeting_notes, project_proposal, technical_report, 
            business_plan, resume, cover_letter, invoice, contract, memo, presentation_outline
            
            Return the document URL and confirmation of creation.
            """

            result = await self.client.run_task(task)
            result_text = str(result.get("result", ""))

            needs_auth = self._needs_authentication(result_text)
            oauth_url = None
            if needs_auth:
                oauth_url = self._extract_oauth_url(result_text)

            doc_info = self._extract_doc_info(result_text)

            return DocTemplateResponse(
                success=result.get("success", False),
                doc_id=doc_info["doc_id"],
                doc_url=doc_info["doc_url"],
                doc_title=request.title,
                template_used=request.template_type,
                result=result_text,
                error=result.get("error"),
                user_id=self.client.user_id,
                needs_authentication=needs_auth,
                oauth_url=oauth_url,
            )

        except Exception as e:
            return DocTemplateResponse(
                success=False,
                error=str(e),
                user_id=self.client.user_id,
            )

    async def generate_content(
        self, request: GenerateContentRequest
    ) -> GenerateContentResponse:
        """Generate content for a document (without creating the actual Google Doc)"""
        try:
            key_points_text = ""
            if request.key_points:
                key_points_text = "\n".join(
                    [f"- {point}" for point in request.key_points]
                )

            task = f"""
            Generate {request.content_type} content on the topic: {request.topic}
            
            Requirements:
            - Content Type: {request.content_type}
            - Tone: {request.tone}
            - Length: {request.length}
            
            Key Points to Include:
            {key_points_text}
            
            Please:
            1. Create a comprehensive content outline
            2. Generate well-structured content with clear sections
            3. Use the specified tone ({request.tone})
            4. Make it {request.length} length as requested
            5. Include relevant examples and details
            6. Ensure the content is engaging and informative
            7. Structure with headers, subheaders, and paragraphs
            
            Return both the content outline and the full generated content.
            """

            result = await self.client.run_task(task)
            result_text = str(result.get("result", ""))

            # Try to extract outline and content
            content_outline = []
            generated_content = result_text
            word_count = len(result_text.split()) if result_text else 0

            # Simple outline extraction (look for headers)
            lines = result_text.split("\n")
            for line in lines:
                line = line.strip()
                if line and (
                    line.startswith("#") or line.isupper() or line.endswith(":")
                ):
                    content_outline.append(line.replace("#", "").strip())

            return GenerateContentResponse(
                success=result.get("success", False),
                generated_content=generated_content,
                content_outline=content_outline if content_outline else None,
                word_count=word_count,
                result=result_text,
                error=result.get("error"),
                user_id=self.client.user_id,
            )

        except Exception as e:
            return GenerateContentResponse(
                success=False,
                error=str(e),
                user_id=self.client.user_id,
            )
