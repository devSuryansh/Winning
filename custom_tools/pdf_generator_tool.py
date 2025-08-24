from pathlib import Path
from typing import Annotated
from portia import tool
import markdown
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import re
from html import unescape

@tool
def pdf_generator_tool(
    markdown_content: Annotated[str, "The markdown content to convert to PDF"],
    filename: Annotated[str, "The output PDF filename (without extension)"],
    title: Annotated[str, "The document title"] = "Generated Documentation"
) -> str:
    """Converts markdown content to a professional PDF document using ReportLab."""
    
    # Create output directory
    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)
    
    pdf_path = output_dir / f"{filename}.pdf"
    
    try:
        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#2c3e50')
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.HexColor('#34495e')
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leftIndent=0,
            rightIndent=0
        )
        
        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Code'],
            fontSize=9,
            spaceAfter=6,
            spaceBefore=6,
            backColor=colors.HexColor('#f8f9fa'),
            borderColor=colors.HexColor('#e9ecef'),
            borderWidth=1,
            borderPadding=6
        )
        
        def clean_text(text):
            """Clean markdown formatting for PDF"""
            # Remove markdown bold/italic
            text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)  # **bold** -> <b>bold</b>
            text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)      # *italic* -> <i>italic</i>
            # Convert markdown links
            text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" color="blue">\1</a>', text)
            # Remove weird symbols
            text = text.replace('■■■', '   ')  # Replace with spaces
            text = text.replace('---', '')     # Remove horizontal rules
            return text
        
        # Parse markdown content
        story = []
        
        # Add title
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        # Split content into lines and process
        lines = markdown_content.split('\n')
        current_paragraph = []
        in_code_block = False
        code_block_content = []
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # Skip horizontal rules and empty decorative lines
            if line in ['---', '■■■', '***', '___'] or not line:
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    if para_text.strip():
                        cleaned_text = clean_text(para_text)
                        story.append(Paragraph(cleaned_text, body_style))
                        story.append(Spacer(1, 6))
                    current_paragraph = []
                continue
            
            # Handle code blocks
            if line.startswith('```') or line.startswith('npx ') or line.startswith('cd ') or line.startswith('npm '):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    if para_text.strip():
                        cleaned_text = clean_text(para_text)
                        story.append(Paragraph(cleaned_text, body_style))
                    current_paragraph = []
                
                if line.startswith('```'):
                    in_code_block = not in_code_block
                    continue
                else:
                    # Single line code
                    story.append(Paragraph(f"<pre>{line}</pre>", code_style))
                    story.append(Spacer(1, 6))
                    continue
            
            if in_code_block:
                code_block_content.append(line)
                continue
            
            # Handle headers
            if line.startswith('### '):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    if para_text.strip():
                        cleaned_text = clean_text(para_text)
                        story.append(Paragraph(cleaned_text, body_style))
                    current_paragraph = []
                
                header_text = clean_text(line[4:].strip())
                story.append(Paragraph(header_text, heading2_style))
                story.append(Spacer(1, 6))
                continue
                
            elif line.startswith('## '):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    if para_text.strip():
                        cleaned_text = clean_text(para_text)
                        story.append(Paragraph(cleaned_text, body_style))
                    current_paragraph = []
                
                header_text = clean_text(line[3:].strip())
                story.append(Paragraph(header_text, heading2_style))
                story.append(Spacer(1, 6))
                continue
                
            elif line.startswith('# '):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    if para_text.strip():
                        cleaned_text = clean_text(para_text)
                        story.append(Paragraph(cleaned_text, body_style))
                    current_paragraph = []
                
                header_text = clean_text(line[2:].strip())
                story.append(Paragraph(header_text, heading1_style))
                story.append(Spacer(1, 10))
                continue
            
            # Handle bullet points
            if line.startswith('• ') or line.startswith('- ') or line.startswith('* '):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    if para_text.strip():
                        cleaned_text = clean_text(para_text)
                        story.append(Paragraph(cleaned_text, body_style))
                    current_paragraph = []
                
                bullet_text = line[2:].strip() if line.startswith('• ') else line[2:].strip()
                cleaned_bullet = clean_text(bullet_text)
                story.append(Paragraph(f"• {cleaned_bullet}", body_style))
                continue
            
            # Regular text
            current_paragraph.append(line)
        
        # Add remaining paragraph
        if current_paragraph:
            para_text = ' '.join(current_paragraph)
            if para_text.strip():
                cleaned_text = clean_text(para_text)
                story.append(Paragraph(cleaned_text, body_style))
        
        # Build PDF
        doc.build(story)
        
        return f"Successfully generated PDF: {pdf_path}"
        
    except Exception as e:
        # Fallback: save as text file
        txt_path = output_dir / f"{filename}.txt"
        txt_path.write_text(f"{title}\n\n{markdown_content}", encoding="utf-8")
        return f"PDF generation failed, saved as text instead: {txt_path}. Error: {str(e)}"