def analyze_code_text(code_text):
    lines = code_text.splitlines()
    num_lines = len(lines)
    functions = code_text.count("def ")
    classes = code_text.count("class ")
    
    score = 100
    issues = []
    suggestions = []
    
    # Simple Logic for Analysis
    if num_lines < 2:
        score -= 20
        issues.append("Code is too short.")
        suggestions.append("Add more logic to your script.")
    
    if "import " not in code_text and num_lines > 5:
        score -= 10
        issues.append("No imports found.")
        suggestions.append("Ensure you import necessary libraries.")
        
    if "def " not in code_text:
        score -= 15
        issues.append("No functions defined.")
        suggestions.append("Encapsulate logic inside functions.")

    return {
        "score": max(0, score),
        "metrics": {"lines": num_lines, "functions": functions, "classes": classes},
        "issues": issues,
        "suggestions": suggestions
    }

def analyze_file(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    return analyze_code_text(content)
