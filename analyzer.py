import re

def analyze_code_text(code_string, filename="Direct_Input.py"):
    lines = code_string.splitlines()
    total_lines = len(lines)
    functions = 0
    classes = 0
    issues = []
    suggestions = []
    score = 100
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("def "):
            functions += 1
        elif stripped.startswith("class "):
            classes += 1
            
        # Check 1: PEP 8 Line Length
        if len(line) > 79:
            issues.append(f"Line {i}: Line too long ({len(line)} characters)")
            score -= 5
            suggestions.append(f"💡 Line {i}: Try splitting this long line into multiple lines.")
            
        # Check 2: Raw input warning
        if "raw_input(" in line:
            issues.append(f"Line {i}: Found deprecated 'raw_input'")
            score -= 10
            suggestions.append(f"💡 Line {i}: Replace 'raw_input()' with 'input()' for Python 3.")

        # Check 3: Missing docstring
        if stripped.startswith("def "):
            next_line = lines[i].strip() if i < len(lines) else ""
            if not (next_line.startswith('"""') or next_line.startswith("'''")):
                issues.append(f"Line {i}: Function missing docstring")
                score -= 2
                suggestions.append(f"💡 Line {i}: Add a standard double-quote docstring (\"\"\" Description \"\"\").")

    if not issues:
        issues = ["Code quality is pristine! Zero syntax flaws or warnings detected."]
        suggestions = ["✨ Your architecture follows great patterns. No immediate optimization needed!"]
        
    score = max(0, score)
    if total_lines == 0:
        score = 0
    
    return {
        "score": score,
        "metrics": {"lines": total_lines, "functions": functions, "classes": classes},
        "issues": issues,
        "suggestions": suggestions
    }

def analyze_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        code_string = f.read()
    return analyze_code_text(code_string, file_path)
