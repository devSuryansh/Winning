from pathlib import Path
from typing import Annotated
from portia import tool

@tool
def file_writer_tool(
    filename: Annotated[str, "The location where the file should be written to"],
    content: Annotated[str, "The content to write to the file"]
) -> str:
    """Writes content to a local file on disk."""
    file_path = Path(filename)
    
    # Create parent directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write content to file
    file_path.write_text(content, encoding="utf-8")
    
    return f"Successfully wrote content to {filename}"