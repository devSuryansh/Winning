from portia import (
    ActionClarification,
    InputClarification,
    MultipleChoiceClarification,
    PlanRunState,
    Portia,
    PortiaToolRegistry,
    default_config,
)
from custom_tools import custom_tool_registry
import os

class DocumentService:
    def __init__(self, openai_api_key: str, user_id: str):
        self.openai_api_key = openai_api_key
        self.user_id = user_id
        os.environ["OPENAI_API_KEY"] = openai_api_key
        if os.getenv("PORTIA_API_KEY"):
            os.environ["PORTIA_API_KEY"] = os.getenv("PORTIA_API_KEY")
    
    def create_portia_instance(self):
        # Combine default tools with custom tools
        complete_tool_registry = PortiaToolRegistry(default_config()) + custom_tool_registry
        return Portia(tools=complete_tool_registry)
    
    async def generate_documentation(self, topic: str, urls: list[str] = None, output_format: str = "markdown"):
        try:
            portia = self.create_portia_instance()
            
            # Build the task based on whether URLs are provided
            if urls:
                urls_str = ", ".join(urls[:3])  # Limit to 3 URLs max
                if output_format.lower() == "pdf":
                    task = f"""
                    Create comprehensive, detailed documentation about '{topic}' by:
                    1. Extracting ALL relevant information from these URLs: {urls_str}
                    2. Researching additional sources to fill gaps in knowledge
                    3. Creating a complete, thorough guide (minimum 1500 words) in markdown format
                    4. MUST use the pdf_generator_tool to convert the markdown content to PDF with filename '{topic.replace(' ', '_').lower()}_documentation' and title '{topic}: Complete Guide'
                    
                    IMPORTANT: Create a COMPLETE guide with these sections:
                    
                    # {topic}: Complete Guide
                    
                    ## Introduction
                    - What is {topic}?
                    - Why is it important/useful?
                    - Who should use this guide?
                    
                    ## Getting Started
                    - Prerequisites and requirements
                    - Installation steps with code examples
                    - Initial setup and configuration
                    
                    ## Core Concepts
                    - Key concepts explained in detail
                    - Important terminology
                    - How things work under the hood
                    
                    ## Step-by-Step Tutorial
                    - Detailed walkthrough with code examples
                    - Common use cases and scenarios
                    - Best practices and tips
                    
                    ## Advanced Topics
                    - Advanced features and techniques
                    - Performance considerations
                    - Troubleshooting common issues
                    
                    ## Resources & References
                    - YouTube tutorial links (with titles)
                    - Blog posts and articles (with titles and URLs)
                    - Official documentation links
                    - GitHub repositories with examples
                    - Online courses or tutorials
                    
                    ## Conclusion
                    - Summary of key points
                    - Next steps for learning
                    
                    Make sure to include plenty of code examples, explanations, and practical tips. This should be a complete reference guide, not just a brief overview.
                    
                    CRITICAL: After creating the markdown content, you MUST call pdf_generator_tool with:
                    - markdown_content: the full markdown content you created
                    - filename: '{topic.replace(' ', '_').lower()}_documentation'  
                    - title: '{topic}: Complete Guide'
                    
                    Do not just write markdown - you must convert it to PDF using the pdf_generator_tool.
                    """
                else:
                    task = f"""
                    Create comprehensive documentation about '{topic}' by:
                    1. Extracting key information from these URLs: {urls_str}
                    2. Finding additional relevant resources (YouTube videos, blog posts, tutorials)
                    3. Writing a structured document to 'docs/{topic.replace(' ', '_').lower()}_documentation.{output_format}'
                    
                    Include these sections:
                    - Brief introduction (2-3 sentences)
                    - 3-4 main content sections with key points
                    - Simple examples if needed
                    - Resources & References section with:
                      * YouTube tutorial links (with titles)
                      * Blog posts and articles (with titles and URLs)
                      * Official documentation links
                      * GitHub repositories
                      * Online courses or tutorials
                    - Short conclusion
                    
                    Format all links properly in markdown: [Link Title](URL)
                    """
            else:
                if output_format.lower() == "pdf":
                    task = f"""
                    Create comprehensive documentation about '{topic}' by:
                    1. Researching and finding reliable sources about the topic
                    2. Extracting key information and organizing it well
                    3. Finding additional learning resources (YouTube videos, blog posts, tutorials)
                    4. Creating complete markdown content
                    5. MUST use pdf_generator_tool to convert markdown to PDF with filename '{topic.replace(' ', '_').lower()}_documentation' and title '{topic}: Complete Guide'
                    
                    IMPORTANT: You must actually call the pdf_generator_tool function, not just mention it. The final step should be calling pdf_generator_tool(markdown_content=your_content, filename='{topic.replace(' ', '_').lower()}_documentation', title='{topic}: Complete Guide')
                    
                    Include these sections:
                    - Brief introduction (2-3 sentences)
                    - 3-4 main content sections with key points
                    - Simple examples if needed
                    - Resources & References section with:
                      * YouTube tutorial links (with titles)
                      * Blog posts and articles (with titles and URLs)
                      * Official documentation links
                      * GitHub repositories
                      * Online courses or tutorials
                    - Short conclusion
                    
                    Format all links properly in markdown: [Link Title](URL)
                    """
                else:
                    task = f"""
                    Create comprehensive documentation about '{topic}' by:
                    1. Researching and finding reliable sources about the topic
                    2. Extracting key information and organizing it well
                    3. Finding additional learning resources (YouTube videos, blog posts, tutorials)
                    4. Writing a structured document to 'docs/{topic.replace(' ', '_').lower()}_documentation.{output_format}'
                    
                    Include these sections:
                    - Brief introduction (2-3 sentences)
                    - 3-4 main content sections with key points
                    - Simple examples if needed
                    - Resources & References section with:
                      * YouTube tutorial links (with titles)
                      * Blog posts and articles (with titles and URLs)
                      * Official documentation links
                      * GitHub repositories
                      * Online courses or tutorials
                    - Short conclusion
                    
                    Format all links properly in markdown: [Link Title](URL)
                    """
            
            plan = portia.plan(task)
            plan_run = portia.run_plan(plan, end_user=self.user_id)
            
            # Handle clarifications if needed
            while plan_run.state == PlanRunState.NEED_CLARIFICATION:
                for clarification in plan_run.get_outstanding_clarifications():
                    if isinstance(clarification, ActionClarification):
                        return {
                            "success": False,
                            "error": "Authentication required",
                            "result": f"Auth required: {clarification.user_guidance}",
                            "needs_oauth": True,
                            "oauth_url": str(clarification.action_url),
                            "user_id": self.user_id
                        }
                    
                    elif isinstance(clarification, (InputClarification, MultipleChoiceClarification)):
                        return {
                            "success": False,
                            "error": "User input required",
                            "result": f"Input needed: {clarification.user_guidance}",
                            "needs_input": True,
                            "user_id": self.user_id
                        }
                
                break
            
            file_extension = "pdf" if output_format.lower() == "pdf" else output_format
            return {
                "success": True,
                "result": str(plan_run.outputs.final_output),
                "user_id": self.user_id,
                "file_path": f"docs/{topic.replace(' ', '_').lower()}_documentation.{file_extension}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "user_id": self.user_id
            }