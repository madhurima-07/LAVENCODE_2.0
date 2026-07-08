def analyze_code_text(code_text):
    lines = code_text.splitlines()
    num_lines = len(lines)
    functions = code_text.count("def ")
    classes = code_text.count("class ")
    
    # ஆரம்ப ஸ்கோர் 100
    score = 100
    issues = []
    suggestions = []
    
    # லாஜிக் செக்கிங்
    if num_lines < 3:
        score -= 20
        issues.append("Code is too short.")
        suggestions.append("Add more logic to your script.")
    
    if "print" not in code_text and "return" not in code_text:
        score -= 30
        issues.append("No output mechanism.")
        suggestions.append("Add a print() or return statement.")
        
    if "def " not in code_text:
        score -= 15
        issues.append("No functions defined.")
        suggestions.append("Encapsulate logic inside functions for better structure.")

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
