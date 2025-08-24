# from pathlib import Path
# from typing import Annotated
# from portia import tool
# from fpdf import FPDF
# import re

# @tool
# def pdf_generator_tool(
#     markdown_content: Annotated[str, "The markdown content to convert to PDF"],
#     filename: Annotated[str, "The output PDF filename (without extension)"],
#     title: Annotated[str, "The document title"] = "Generated Documentation"
# ) -> str:
#     """Converts markdown content to a professional PDF document using fpdf2."""
    
#     # Create output directory
#     output_dir = Path("docs")
#     output_dir.mkdir(exist_ok=True)
    
#     pdf_path = output_dir / f"{filename}.pdf"
    
#     try:
#         # Pre-clean the entire markdown content first
#         markdown_content = markdown_content.replace('•', '-')
#         markdown_content = markdown_content.replace('●', '-')
#         markdown_content = markdown_content.replace('◦', '-')
#         markdown_content = markdown_content.replace('‣', '-')
#         markdown_content = markdown_content.replace('⁃', '-')
#         markdown_content = markdown_content.replace('–', '-')
#         markdown_content = markdown_content.replace('—', '-')
#         markdown_content = markdown_content.replace(''', "'")
#         markdown_content = markdown_content.replace(''', "'")
#         markdown_content = markdown_content.replace('"', '"')
#         markdown_content = markdown_content.replace('"', '"')
#         markdown_content = markdown_content.replace('…', '...')
        
#         # Remove any non-ASCII characters from the entire content
#         markdown_content = ''.join(char if ord(char) < 128 else '?' for char in markdown_content)
        
#         # Create PDF document
#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_auto_page_break(auto=True, margin=15)
        
#         # Add title (also clean it)
#         clean_title = ''.join(char if ord(char) < 128 else '?' for char in title)
#         pdf.set_font("Helvetica", "B", 16)
#         pdf.cell(200, 15, clean_title, align="C")
#         pdf.ln(20)
        
#         # Clean the content first
#         def clean_text(text):
#             """Clean text for PDF compatibility"""
#             # Replace Unicode characters with ASCII equivalents - be more aggressive
#             text = text.replace('•', '-')
#             text = text.replace('●', '-')
#             text = text.replace('◦', '-')
#             text = text.replace('‣', '-')
#             text = text.replace('⁃', '-')
#             text = text.replace('–', '-')
#             text = text.replace('—', '-')
#             text = text.replace(''', "'")
#             text = text.replace(''', "'")
#             text = text.replace('"', '"')
#             text = text.replace('"', '"')
#             text = text.replace('…', '...')
            
#             # Remove any remaining non-ASCII characters
#             text = ''.join(char if ord(char) < 128 else '?' for char in text)
            
#             # Remove markdown formatting
#             text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
#             text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
#             text = re.sub(r'`([^`]+)`', r'\1', text)        # `code`
            
#             # Handle links
#             text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', text)
            
#             # Remove code block markers
#             text = re.sub(r'```[^\n]*\n', '', text)
#             text = re.sub(r'```', '', text)
            
#             return text
        
#         # Process content line by line
#         lines = markdown_content.split('\n')
        
#         for line in lines:
#             line = line.strip()
            
#             # Skip empty lines and separators
#             if not line or line in ['---', '***', '___']:
#                 pdf.ln(5)
#                 continue
            
#             # Clean the line
#             clean_line = clean_text(line)
            
#             # Handle headers
#             if line.startswith('# '):
#                 pdf.set_font("Helvetica", "B", 14)
#                 pdf.ln(5)
#                 pdf.cell(200, 10, clean_line[2:].strip())
#                 pdf.ln(10)
                
#             elif line.startswith('## '):
#                 pdf.set_font("Helvetica", "B", 12)
#                 pdf.ln(4)
#                 pdf.cell(200, 8, clean_line[3:].strip())
#                 pdf.ln(8)
                
#             elif line.startswith('### '):
#                 pdf.set_font("Helvetica", "B", 11)
#                 pdf.ln(3)
#                 pdf.cell(200, 7, clean_line[4:].strip())
#                 pdf.ln(7)
                
#             # Handle bullet points
#             elif line.startswith(('- ', '* ', '• ')):
#                 pdf.set_font("Helvetica", "", 10)
#                 bullet_text = f"- {clean_line[2:].strip()}"
#                 # Split long bullet points into multiple lines
#                 if len(bullet_text) > 80:
#                     words = bullet_text.split()
#                     current_line = ""
#                     for word in words:
#                         if len(current_line + " " + word) < 80:
#                             current_line = current_line + " " + word if current_line else word
#                         else:
#                             pdf.cell(200, 6, current_line)
#                             pdf.ln(6)
#                             current_line = "  " + word  # Indent continuation
#                     if current_line:
#                         pdf.cell(200, 6, current_line)
#                         pdf.ln(6)
#                 else:
#                     pdf.cell(200, 6, bullet_text)
#                     pdf.ln(6)
                
#             # Handle regular text
#             elif clean_line:
#                 pdf.set_font("Helvetica", "", 10)
#                 # Split long lines
#                 if len(clean_line) > 80:
#                     words = clean_line.split()
#                     current_line = ""
#                     for word in words:
#                         if len(current_line + " " + word) < 80:
#                             current_line = current_line + " " + word if current_line else word
#                         else:
#                             pdf.cell(200, 6, current_line)
#                             pdf.ln(6)
#                             current_line = word
#                     if current_line:
#                         pdf.cell(200, 6, current_line)
#                         pdf.ln(6)
#                 else:
#                     pdf.cell(200, 6, clean_line)
#                     pdf.ln(6)
        
#         # Save PDF
#         pdf.output(str(pdf_path))
#         return f"Successfully generated PDF: {pdf_path}"
        
#     except Exception as e:
#         # Fallback: save as text file
#         txt_path = output_dir / f"{filename}.txt"
#         txt_path.write_text(f"{title}\n\n{markdown_content}", encoding="utf-8")
#         return f"PDF generation failed, saved as text instead: {txt_path}. Error: {str(e)}"