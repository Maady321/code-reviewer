import os

SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".go": "Go",
}

def is_supported_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in SUPPORTED_EXTENSIONS

def split_large_file(code: str, max_lines: int = 500) -> list[str]:
    lines = code.splitlines()
    chunks = []
    current_chunk = []
    
    for i, line in enumerate(lines):
        current_chunk.append(line)
        if len(current_chunk) >= max_lines:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    return chunks

def format_prompt(code: str) -> str:
    return f"""You are a senior software engineer performing a code review.

Analyze the following code and identify:
- Bugs
- Security vulnerabilities
- Performance issues
- Code quality improvements

Return output in JSON format:
{{
  "issues": [
    {{
      "line_number": 42,
      "severity": "high", 
      "type": "security",
      "description": "Hardcoded API key",
      "suggestion": "Use environment variables"
    }}
  ],
  "score": 7.5
}}

Ensure ONLY valid JSON is returned, without markdown formatting blocks like ```json.
Code:
{code}
"""
