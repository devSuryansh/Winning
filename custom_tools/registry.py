"""Registry containing custom tools for document generation."""

from portia import ToolRegistry
from .extract_tool import ExtractTool
from .crawl_tool import CrawlTool
from .file_writer_tool import file_writer_tool

# Create instances of the tools
extract_tool = ExtractTool()
crawl_tool = CrawlTool()

# Create the custom tool registry
custom_tool_registry = ToolRegistry([
    extract_tool,
    crawl_tool,
    file_writer_tool(),
])