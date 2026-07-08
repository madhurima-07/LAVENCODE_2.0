def analyze_code_text(code_text):
    lines = code_text.splitlines()
    num_lines = len([line for line in lines if line.strip() != ""])
    functions = code_text.count("def ")
    classes = code_text.count("class ")
    
    # ஆரம்ப ஸ்கோர் 100
    score = 100
    issues = []
    suggestions = []
    
    # அனலைசிஸ் லாஜிக்
    if num_lines < 3:
        score -= 20
        issues.append("Code is too short.")
        suggestions.append("Add more logic to your script to make it functional.")
    
    if "import" not in code_text:
        score -= 15
        issues.append("No imports found.")
        suggestions.append("Import necessary libraries to support your code.")
        
    if "def " not in code_text and "class " not in code_text:
        score -= 20
        issues.append("No structure detected.")
        suggestions.append("Encapsulate your code in functions or classes.")

    if "print" not in code_text and "return" not in code_text:
        score -= 25
        issues.append("No output mechanism.")
        suggestions.append("Include print() or return statements to display results.")

    return {
        "score": max(0, score),
        "metrics": {
            "lines": num_lines,
            "functions": functions,
            "classes": classes
        },
        "issues": issues,
        "suggestions": suggestions
    }

def analyze_file(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    return analyze_code_text(content)
